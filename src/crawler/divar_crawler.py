"""
Divar Crawler - Crawler for Divar.ir website
"""

from typing import List, Dict, Any, Optional
import re
import logging
from urllib.parse import urlencode, quote

from bs4 import BeautifulSoup

from .base_crawler import BaseCrawler
from .schemas import CrawledItem

logger = logging.getLogger(__name__)


class DivarCrawler(BaseCrawler):
    """
    Crawler for Divar.ir
    Supports apartment rent, purchase, and vehicle searches
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize Divar crawler"""
        super().__init__(config)
        self.site_name = 'divar'
        self.base_url = self.config.get('base_url', 'https://divar.ir')
        self._use_selenium = True  # Divar uses JavaScript
    
    def build_search_url(self, filters: Dict[str, Any]) -> str:
        """Build Divar search URL"""
        # Divar uses a specific URL structure
        category = filters.get('category', 'apartment-rent')
        location = filters.get('location', 'تهران')
        
        # Build base URL
        url = f"{self.base_url}/s/tehran/{category}"
        
        # Add query parameters
        params = {}
        
        if filters.get('price_min'):
            params['price-min'] = int(filters['price_min'] * 1000000)  # Convert to Tomans
        if filters.get('price_max'):
            params['price-max'] = int(filters['price_max'] * 1000000)
        
        if filters.get('rent_type') == 'full_deposit':
            params['rent-type'] = 'full_deposit'
        
        if params:
            url += '?' + urlencode(params)
        
        return url
    
    def extract_items(self, html_content: str) -> List[Dict[str, Any]]:
        """Extract items from Divar HTML"""
        items = []
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Divar uses specific CSS selectors
        # This is a simplified version - actual implementation may need adjustment
        item_cards = soup.find_all('div', class_='kt-post-card')
        
        for card in item_cards:
            try:
                item = {}
                
                # Title
                title_elem = card.find('h2', class_='kt-post-card__title')
                item['title'] = title_elem.get_text(strip=True) if title_elem else ''
                
                # URL
                link_elem = card.find('a', href=True)
                if link_elem:
                    item['url'] = self.base_url + link_elem['href']
                    item['item_id'] = link_elem['href'].split('/')[-1]
                
                # Price
                price_elem = card.find('div', class_='kt-post-card__description')
                if price_elem:
                    price_text = price_elem.get_text(strip=True)
                    item['price_text'] = price_text
                    item['price'] = self.parse_price(price_text)
                
                # Location
                location_elem = card.find('span', class_='kt-post-card__bottom-description')
                if location_elem:
                    item['location'] = location_elem.get_text(strip=True)
                
                # Thumbnail
                img_elem = card.find('img', src=True)
                if img_elem:
                    item['thumbnail'] = img_elem.get('src', '')
                    item['images'] = [img_elem.get('src', '')]
                
                if item.get('title') and item.get('url'):
                    items.append(item)
            
            except Exception as e:
                logger.warning(f"Error extracting Divar item: {str(e)}")
                continue
        
        return items
    
    def normalize_item(self, raw_item: Dict[str, Any], goal_id: Optional[int] = None) -> CrawledItem:
        """Normalize Divar item to schema"""
        # Extract location components
        location = raw_item.get('location', '')
        city = 'تهران'  # Default for Divar searches
        district = location if location else None
        
        # Determine item type from URL
        item_type = 'general'
        if 'apartment-rent' in raw_item.get('url', ''):
            item_type = 'residential_rent'
        elif 'apartment-sell' in raw_item.get('url', ''):
            item_type = 'residential_purchase'
        
        return CrawledItem(
            item_id=raw_item.get('item_id', ''),
            source_site='divar',
            title=raw_item.get('title', ''),
            description=None,
            url=raw_item.get('url', ''),
            price=raw_item.get('price'),
            price_text=raw_item.get('price_text'),
            price_type=None,
            location=location,
            city=city,
            district=district,
            images=raw_item.get('images', []),
            thumbnail=raw_item.get('thumbnail'),
            properties={
                'raw_data': raw_item
            },
            goal_id=goal_id,
            confidence_score=0.9
        )

