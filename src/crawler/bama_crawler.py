"""
Bama Crawler - Crawler for Bama.ir (vehicle marketplace)
"""

from typing import List, Dict, Any, Optional
import logging
from urllib.parse import urlencode

from bs4 import BeautifulSoup

from .base_crawler import BaseCrawler
from .schemas import CrawledItem

logger = logging.getLogger(__name__)


class BamaCrawler(BaseCrawler):
    """
    Crawler for Bama.ir
    Specialized for vehicle searches
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize Bama crawler"""
        super().__init__(config)
        self.site_name = 'bama'
        self.base_url = self.config.get('base_url', 'https://bama.ir')
        self._use_selenium = True
    
    def build_search_url(self, filters: Dict[str, Any]) -> str:
        """Build Bama search URL"""
        search_type = filters.get('search_type', 'purchase')
        
        if search_type == 'lease':
            url = f"{self.base_url}/lease"
        else:
            url = f"{self.base_url}/car"
        
        params = {}
        if filters.get('price_min'):
            params['price-min'] = int(filters['price_min'] * 1000000)
        if filters.get('price_max'):
            params['price-max'] = int(filters['price_max'] * 1000000)
        if filters.get('lease_monthly_max'):
            params['lease-monthly-max'] = int(filters['lease_monthly_max'] * 1000000)
        
        if params:
            url += '?' + urlencode(params)
        
        return url
    
    def extract_items(self, html_content: str) -> List[Dict[str, Any]]:
        """Extract vehicle items from Bama HTML"""
        items = []
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Bama specific selectors
        item_cards = soup.find_all('div', class_='car-item')
        
        for card in item_cards:
            try:
                item = {}
                
                # Title and URL
                title_elem = card.find('h2', class_='car-title')
                if title_elem:
                    link = title_elem.find('a', href=True)
                    if link:
                        item['title'] = link.get_text(strip=True)
                        item['url'] = self.base_url + link['href']
                        item['item_id'] = link['href'].split('/')[-1]
                
                # Price
                price_elem = card.find('div', class_='car-price')
                if price_elem:
                    price_text = price_elem.get_text(strip=True)
                    item['price_text'] = price_text
                    item['price'] = self.parse_price(price_text)
                
                # Additional info
                info_elem = card.find('div', class_='car-info')
                if info_elem:
                    item['description'] = info_elem.get_text(strip=True)
                
                # Image
                img_elem = card.find('img', src=True)
                if img_elem:
                    item['thumbnail'] = img_elem.get('src', '')
                    item['images'] = [img_elem.get('src', '')]
                
                if item.get('title') and item.get('url'):
                    items.append(item)
            
            except Exception as e:
                logger.warning(f"Error extracting Bama item: {str(e)}")
                continue
        
        return items
    
    def normalize_item(self, raw_item: Dict[str, Any], goal_id: Optional[int] = None) -> CrawledItem:
        """Normalize Bama item"""
        return CrawledItem(
            item_id=raw_item.get('item_id', ''),
            source_site='bama',
            title=raw_item.get('title', ''),
            description=raw_item.get('description'),
            url=raw_item.get('url', ''),
            price=raw_item.get('price'),
            price_text=raw_item.get('price_text'),
            price_type='نقدی',
            images=raw_item.get('images', []),
            thumbnail=raw_item.get('thumbnail'),
            properties={
                'vehicle_type': 'car',
                'raw_data': raw_item
            },
            goal_id=goal_id,
            confidence_score=0.9
        )

