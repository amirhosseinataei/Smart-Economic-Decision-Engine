"""
Digikala Crawler - Crawler for Digikala.com
"""

from typing import List, Dict, Any, Optional
import logging
from urllib.parse import urlencode

from bs4 import BeautifulSoup

from .base_crawler import BaseCrawler
from .schemas import CrawledItem

logger = logging.getLogger(__name__)


class DigikalaCrawler(BaseCrawler):
    """
    Crawler for Digikala.com
    E-commerce product search
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize Digikala crawler"""
        super().__init__(config)
        self.site_name = 'digikala'
        self.base_url = self.config.get('base_url', 'https://www.digikala.com')
        self._use_selenium = True
    
    def build_search_url(self, filters: Dict[str, Any]) -> str:
        """Build Digikala search URL"""
        product_name = filters.get('product_name', '')
        
        url = f"{self.base_url}/search/"
        if product_name:
            url += product_name.replace(' ', '-')
        
        params = {}
        if filters.get('price_min'):
            params['price-min'] = int(filters['price_min'] * 1000000)
        if filters.get('price_max'):
            params['price-max'] = int(filters['price_max'] * 1000000)
        
        if params:
            url += '?' + urlencode(params)
        
        return url
    
    def extract_items(self, html_content: str) -> List[Dict[str, Any]]:
        """Extract products from Digikala HTML"""
        items = []
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Digikala specific selectors
        product_cards = soup.find_all('article', class_='c-product-box')
        
        for card in product_cards:
            try:
                item = {}
                
                # Title and URL
                title_elem = card.find('h3', class_='c-product-box__title')
                if title_elem:
                    link = title_elem.find('a', href=True)
                    if link:
                        item['title'] = link.get_text(strip=True)
                        item['url'] = self.base_url + link['href']
                        item['item_id'] = link['href'].split('/')[-1]
                
                # Price
                price_elem = card.find('div', class_='c-product-box__price')
                if price_elem:
                    price_text = price_elem.get_text(strip=True)
                    item['price_text'] = price_text
                    item['price'] = self.parse_price(price_text)
                
                # Image
                img_elem = card.find('img', src=True)
                if img_elem:
                    item['thumbnail'] = img_elem.get('src', '')
                    item['images'] = [img_elem.get('src', '')]
                
                if item.get('title') and item.get('url'):
                    items.append(item)
            
            except Exception as e:
                logger.warning(f"Error extracting Digikala item: {str(e)}")
                continue
        
        return items
    
    def normalize_item(self, raw_item: Dict[str, Any], goal_id: Optional[int] = None) -> CrawledItem:
        """Normalize Digikala item"""
        return CrawledItem(
            item_id=raw_item.get('item_id', ''),
            source_site='digikala',
            title=raw_item.get('title', ''),
            url=raw_item.get('url', ''),
            price=raw_item.get('price'),
            price_text=raw_item.get('price_text'),
            price_type='نقدی',
            images=raw_item.get('images', []),
            thumbnail=raw_item.get('thumbnail'),
            properties={
                'product_type': 'electronics',
                'raw_data': raw_item
            },
            goal_id=goal_id,
            confidence_score=0.9
        )

