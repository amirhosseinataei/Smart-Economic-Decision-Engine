"""
Base Crawler - Abstract base class for all crawlers
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
import logging
import time
from datetime import datetime

import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from .schemas import CrawledItem, CrawlResult

logger = logging.getLogger(__name__)


class BaseCrawler(ABC):
    """
    Abstract base class for all website crawlers
    Provides common functionality and interface
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize base crawler
        
        Args:
            config: Configuration dictionary
        """
        self.config = config or {}
        self.site_name = self.config.get('site_name', 'unknown')
        self.base_url = self.config.get('base_url', '')
        self.user_agent = self.config.get(
            'user_agent',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        )
        self.download_delay = self.config.get('download_delay', 1.0)
        self.retry_times = self.config.get('retry_times', 3)
        self.timeout = self.config.get('timeout', 30)
        
        # Selenium setup (lazy initialization)
        self._driver = None
        self._use_selenium = self.config.get('use_selenium', False)
    
    @abstractmethod
    def build_search_url(self, filters: Dict[str, Any]) -> str:
        """
        Build search URL from filters
        
        Args:
            filters: Search filters dictionary
            
        Returns:
            Complete search URL
        """
        pass
    
    @abstractmethod
    def extract_items(self, html_content: str) -> List[Dict[str, Any]]:
        """
        Extract items from HTML content
        
        Args:
            html_content: HTML content of search results page
            
        Returns:
            List of raw item dictionaries
        """
        pass
    
    @abstractmethod
    def normalize_item(self, raw_item: Dict[str, Any], goal_id: Optional[int] = None) -> CrawledItem:
        """
        Normalize raw item to CrawledItem schema
        
        Args:
            raw_item: Raw item dictionary from extract_items
            goal_id: Optional goal ID
            
        Returns:
            CrawledItem object
        """
        pass
    
    def get_driver(self):
        """Get or create Selenium WebDriver"""
        if not self._use_selenium:
            return None
        
        if self._driver is None:
            chrome_options = Options()
            chrome_options.add_argument('--headless')
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument(f'--user-agent={self.user_agent}')
            chrome_options.add_argument('--disable-blink-features=AutomationControlled')
            
            self._driver = webdriver.Chrome(options=chrome_options)
        
        return self._driver
    
    def close_driver(self):
        """Close Selenium WebDriver"""
        if self._driver:
            self._driver.quit()
            self._driver = None
    
    def fetch_page(self, url: str, use_selenium: Optional[bool] = None) -> Optional[str]:
        """
        Fetch page content
        
        Args:
            url: URL to fetch
            use_selenium: Whether to use Selenium (overrides config)
            
        Returns:
            HTML content or None if failed
        """
        use_sel = use_selenium if use_selenium is not None else self._use_selenium
        
        if use_sel:
            return self._fetch_with_selenium(url)
        else:
            return self._fetch_with_requests(url)
    
    def _fetch_with_requests(self, url: str) -> Optional[str]:
        """Fetch page using requests library"""
        headers = {
            'User-Agent': self.user_agent,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'fa-IR,fa;q=0.9,en-US;q=0.8,en;q=0.7',
        }
        
        for attempt in range(self.retry_times):
            try:
                response = requests.get(url, headers=headers, timeout=self.timeout)
                response.raise_for_status()
                response.encoding = 'utf-8'
                return response.text
            except Exception as e:
                logger.warning(f"Attempt {attempt + 1} failed for {url}: {str(e)}")
                if attempt < self.retry_times - 1:
                    time.sleep(self.download_delay * (attempt + 1))
                else:
                    logger.error(f"Failed to fetch {url} after {self.retry_times} attempts")
                    return None
        
        return None
    
    def _fetch_with_selenium(self, url: str) -> Optional[str]:
        """Fetch page using Selenium"""
        driver = self.get_driver()
        if not driver:
            return None
        
        try:
            driver.get(url)
            # Wait for page to load
            time.sleep(2)
            return driver.page_source
        except Exception as e:
            logger.error(f"Selenium fetch failed for {url}: {str(e)}")
            return None
    
    def parse_price(self, price_text: str) -> Optional[float]:
        """
        Parse price text to float (in millions of Tomans)
        
        Args:
            price_text: Price as text
            
        Returns:
            Price in millions or None
        """
        if not price_text:
            return None
        
        try:
            # Remove common text
            price_text = price_text.replace('تومان', '').replace('تومن', '').strip()
            price_text = price_text.replace(',', '').replace('،', '')
            
            # Extract number
            import re
            numbers = re.findall(r'\d+(?:\.\d+)?', price_text)
            if not numbers:
                return None
            
            price = float(numbers[0])
            
            # Check for unit
            if 'میلیارد' in price_text or 'بیلیون' in price_text:
                price *= 1000
            elif 'هزار' in price_text:
                price /= 1000
            
            return price
        except (ValueError, AttributeError):
            return None
    
    def crawl(self, filters: Dict[str, Any], goal_id: Optional[int] = None) -> CrawlResult:
        """
        Main crawl method
        
        Args:
            filters: Search filters
            goal_id: Optional goal ID
            
        Returns:
            CrawlResult object
        """
        start_time = time.time()
        items = []
        errors = []
        
        try:
            # Build search URL
            search_url = self.build_search_url(filters)
            logger.info(f"Crawling {self.site_name}: {search_url}")
            
            # Fetch page
            html_content = self.fetch_page(search_url)
            if not html_content:
                errors.append("Failed to fetch page content")
                return CrawlResult(
                    success=False,
                    site_name=self.site_name,
                    items=[],
                    total_items=0,
                    execution_time=time.time() - start_time,
                    errors=errors
                )
            
            # Extract items
            raw_items = self.extract_items(html_content)
            logger.info(f"Extracted {len(raw_items)} raw items from {self.site_name}")
            
            # Normalize items
            for raw_item in raw_items:
                try:
                    normalized_item = self.normalize_item(raw_item, goal_id)
                    if normalized_item:
                        items.append(normalized_item)
                except Exception as e:
                    logger.warning(f"Failed to normalize item: {str(e)}")
                    errors.append(f"Normalization error: {str(e)}")
            
            execution_time = time.time() - start_time
            
            return CrawlResult(
                success=True,
                site_name=self.site_name,
                items=items,
                total_items=len(items),
                execution_time=execution_time,
                errors=errors
            )
        
        except Exception as e:
            logger.error(f"Error during crawl: {str(e)}", exc_info=True)
            errors.append(str(e))
            return CrawlResult(
                success=False,
                site_name=self.site_name,
                items=[],
                total_items=0,
                execution_time=time.time() - start_time,
                errors=errors
            )
    
    def __del__(self):
        """Cleanup on destruction"""
        self.close_driver()

