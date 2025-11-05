"""
Crawler Manager - Manages multiple crawlers and coordinates crawling operations
"""

from typing import List, Dict, Any, Optional
import logging
import time
import asyncio
from concurrent.futures import ThreadPoolExecutor, as_completed

from .base_crawler import BaseCrawler
from .divar_crawler import DivarCrawler
from .sheypoor_crawler import SheypoorCrawler
from .bama_crawler import BamaCrawler
from .torob_crawler import TorobCrawler
from .digikala_crawler import DigikalaCrawler
from .data_normalizer import DataNormalizer
from .schemas import CrawlResult, CrawlBatchResult, CrawledItem

logger = logging.getLogger(__name__)


class CrawlerManager:
    """
    Manages multiple crawlers and coordinates batch crawling operations
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize crawler manager
        
        Args:
            config: Configuration dictionary
        """
        self.config = config or {}
        self.crawlers: Dict[str, BaseCrawler] = {}
        self.normalizer = DataNormalizer()
        self.max_workers = self.config.get('max_workers', 5)
        self._initialize_crawlers()
    
    def _initialize_crawlers(self):
        """Initialize all available crawlers"""
        crawler_configs = {
            'divar': {
                'site_name': 'divar',
                'base_url': 'https://divar.ir',
                'use_selenium': True,
            },
            'sheypoor': {
                'site_name': 'sheypoor',
                'base_url': 'https://www.sheypoor.com',
                'use_selenium': True,
            },
            'bama': {
                'site_name': 'bama',
                'base_url': 'https://bama.ir',
                'use_selenium': True,
            },
            'torob': {
                'site_name': 'torob',
                'base_url': 'https://torob.com',
                'use_selenium': False,
            },
            'digikala': {
                'site_name': 'digikala',
                'base_url': 'https://www.digikala.com',
                'use_selenium': True,
            },
        }
        
        # Merge with provided config
        for site_name, default_config in crawler_configs.items():
            site_config = self.config.get(site_name, {})
            merged_config = {**default_config, **site_config}
            
            if site_name == 'divar':
                self.crawlers[site_name] = DivarCrawler(merged_config)
            elif site_name == 'sheypoor':
                self.crawlers[site_name] = SheypoorCrawler(merged_config)
            elif site_name == 'bama':
                self.crawlers[site_name] = BamaCrawler(merged_config)
            elif site_name == 'torob':
                self.crawlers[site_name] = TorobCrawler(merged_config)
            elif site_name == 'digikala':
                self.crawlers[site_name] = DigikalaCrawler(merged_config)
    
    def get_crawler(self, site_name: str) -> Optional[BaseCrawler]:
        """Get crawler by site name"""
        return self.crawlers.get(site_name)
    
    def crawl_site(
        self,
        site_name: str,
        filters: Dict[str, Any],
        goal_id: Optional[int] = None
    ) -> CrawlResult:
        """
        Crawl a single site
        
        Args:
            site_name: Name of the site to crawl
            filters: Search filters
            goal_id: Optional goal ID
            
        Returns:
            CrawlResult object
        """
        crawler = self.get_crawler(site_name)
        if not crawler:
            return CrawlResult(
                success=False,
                site_name=site_name,
                items=[],
                total_items=0,
                execution_time=0.0,
                errors=[f"Crawler not found for site: {site_name}"]
            )
        
        return crawler.crawl(filters, goal_id)
    
    def crawl_batch(
        self,
        queries: List[Dict[str, Any]],
        parallel: bool = True
    ) -> CrawlBatchResult:
        """
        Crawl multiple sites in batch
        
        Args:
            queries: List of query dictionaries with 'site', 'filters', 'goal_id'
            parallel: Whether to crawl in parallel
            
        Returns:
            CrawlBatchResult object
        """
        start_time = time.time()
        results = []
        
        if parallel and len(queries) > 1:
            results = self._crawl_parallel(queries)
        else:
            results = self._crawl_sequential(queries)
        
        execution_time = time.time() - start_time
        
        # Calculate total items
        total_items = sum(result.total_items for result in results)
        
        return CrawlBatchResult(
            success=any(r.success for r in results),
            results=results,
            total_items=total_items,
            execution_time=execution_time
        )
    
    def _crawl_sequential(self, queries: List[Dict[str, Any]]) -> List[CrawlResult]:
        """Crawl sites sequentially"""
        results = []
        
        for query in queries:
            site_name = query.get('site')
            filters = query.get('filters', {})
            goal_id = query.get('goal_id')
            
            result = self.crawl_site(site_name, filters, goal_id)
            results.append(result)
        
        return results
    
    def _crawl_parallel(self, queries: List[Dict[str, Any]]) -> List[CrawlResult]:
        """Crawl sites in parallel using ThreadPoolExecutor"""
        results = []
        
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Submit all tasks
            future_to_query = {
                executor.submit(
                    self.crawl_site,
                    query.get('site'),
                    query.get('filters', {}),
                    query.get('goal_id')
                ): query for query in queries
            }
            
            # Collect results as they complete
            for future in as_completed(future_to_query):
                try:
                    result = future.result()
                    results.append(result)
                except Exception as e:
                    logger.error(f"Error in parallel crawl: {str(e)}")
                    query = future_to_query[future]
                    results.append(CrawlResult(
                        success=False,
                        site_name=query.get('site', 'unknown'),
                        items=[],
                        total_items=0,
                        execution_time=0.0,
                        errors=[str(e)]
                    ))
        
        return results
    
    def crawl_from_query_json(
        self,
        query_json: Dict[str, Any],
        normalize: bool = True
    ) -> Dict[str, Any]:
        """
        Crawl based on query JSON from chatbot
        
        Args:
            query_json: Query JSON from QueryGenerator
            normalize: Whether to normalize results
            
        Returns:
            Dictionary with normalized results or raw CrawlBatchResult
        """
        queries = query_json.get('queries', [])
        
        # Convert to crawler format
        crawl_queries = []
        for query in queries:
            crawl_queries.append({
                'site': query['site'],
                'filters': query['filters'],
                'goal_id': query.get('goal_id')
            })
        
        # Execute batch crawl
        batch_result = self.crawl_batch(crawl_queries, parallel=True)
        
        if normalize:
            # Normalize results
            normalized = self.normalizer.normalize_batch(batch_result)
            return normalized
        else:
            # Return raw results
            return {
                'success': batch_result.success,
                'results': [r.dict() for r in batch_result.results],
                'total_items': batch_result.total_items,
                'execution_time': batch_result.execution_time,
                'timestamp': batch_result.timestamp.isoformat()
            }
    
    def cleanup(self):
        """Cleanup all crawlers"""
        for crawler in self.crawlers.values():
            try:
                crawler.close_driver()
            except Exception as e:
                logger.warning(f"Error closing crawler: {str(e)}")
    
    def __del__(self):
        """Cleanup on destruction"""
        self.cleanup()

