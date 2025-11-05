"""
Data Normalizer - Normalizes and unifies data from different sources
"""

from typing import List, Dict, Any
import logging
from datetime import datetime
import json

from .schemas import CrawledItem, CrawlBatchResult

logger = logging.getLogger(__name__)


class DataNormalizer:
    """
    Normalizes crawled data from different sources
    Ensures consistency and quality
    """
    
    def __init__(self):
        """Initialize data normalizer"""
        self.normalization_rules = self._initialize_rules()
    
    def _initialize_rules(self) -> Dict[str, Any]:
        """Initialize normalization rules"""
        return {
            'price_normalization': True,
            'location_normalization': True,
            'duplicate_detection': True,
            'quality_scoring': True,
        }
    
    def normalize_batch(self, batch_result: CrawlBatchResult) -> Dict[str, Any]:
        """
        Normalize a batch of crawl results
        
        Args:
            batch_result: CrawlBatchResult from multiple crawlers
            
        Returns:
            Normalized JSON structure
        """
        all_items = []
        
        # Collect all items
        for result in batch_result.results:
            if result.success:
                all_items.extend(result.items)
        
        # Apply normalization
        normalized_items = []
        seen_urls = set()
        
        for item in all_items:
            # Remove duplicates
            if item.url in seen_urls:
                continue
            seen_urls.add(item.url)
            
            # Normalize item
            normalized = self._normalize_item(item)
            if normalized:
                normalized_items.append(normalized)
        
        # Sort by relevance/quality
        normalized_items.sort(
            key=lambda x: (
                x.get('confidence_score', 0),
                x.get('completeness_score', 0)
            ),
            reverse=True
        )
        
        return {
            'success': True,
            'total_items': len(normalized_items),
            'items': normalized_items,
            'sources': list(set(item.get('source_site') for item in normalized_items)),
            'timestamp': datetime.now().isoformat(),
            'metadata': {
                'normalization_applied': True,
                'duplicates_removed': len(all_items) - len(normalized_items)
            }
        }
    
    def _normalize_item(self, item: CrawledItem) -> Dict[str, Any]:
        """Normalize a single item"""
        try:
            normalized = {
                'item_id': item.item_id,
                'source_site': item.source_site,
                'title': self._normalize_text(item.title),
                'description': self._normalize_text(item.description) if item.description else None,
                'url': item.url,
                'price': item.price,
                'price_text': item.price_text,
                'price_type': item.price_type,
                'location': self._normalize_location(item.location) if item.location else None,
                'city': item.city,
                'district': item.district,
                'images': item.images,
                'thumbnail': item.thumbnail,
                'properties': item.properties,
                'goal_id': item.goal_id,
                'confidence_score': item.confidence_score,
                'completeness_score': self._calculate_completeness(item),
                'crawled_at': item.crawled_at.isoformat() if isinstance(item.crawled_at, datetime) else item.crawled_at,
            }
            
            # Remove None values for cleaner JSON
            normalized = {k: v for k, v in normalized.items() if v is not None}
            
            return normalized
        
        except Exception as e:
            logger.warning(f"Error normalizing item: {str(e)}")
            return None
    
    def _normalize_text(self, text: str) -> str:
        """Normalize text (clean, remove extra spaces, etc.)"""
        if not text:
            return ''
        
        # Remove extra whitespace
        text = ' '.join(text.split())
        
        # Remove special characters if needed
        # text = re.sub(r'[^\w\s]', '', text)
        
        return text.strip()
    
    def _normalize_location(self, location: str) -> str:
        """Normalize location names"""
        if not location:
            return ''
        
        # Common location normalizations
        location_map = {
            'تهران': 'تهران',
            'tehran': 'تهران',
            'tehran city': 'تهران',
        }
        
        location_lower = location.lower()
        if location_lower in location_map:
            return location_map[location_lower]
        
        return location.strip()
    
    def _calculate_completeness(self, item: CrawledItem) -> float:
        """Calculate data completeness score"""
        score = 0.0
        max_score = 10.0
        
        # Required fields
        if item.title:
            score += 1.0
        if item.url:
            score += 1.0
        if item.price or item.price_text:
            score += 1.5
        
        # Important fields
        if item.location:
            score += 1.0
        if item.images:
            score += 1.0
        if item.description:
            score += 0.5
        
        # Additional fields
        if item.city:
            score += 0.5
        if item.district:
            score += 0.5
        if item.properties:
            score += 1.0
        
        # Normalize to 0-1 range
        return min(score / max_score, 1.0)
    
    def save_to_json(self, normalized_data: Dict[str, Any], filepath: str):
        """Save normalized data to JSON file"""
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(normalized_data, f, ensure_ascii=False, indent=2)
            logger.info(f"Saved normalized data to {filepath}")
        except Exception as e:
            logger.error(f"Error saving to JSON: {str(e)}")
            raise

