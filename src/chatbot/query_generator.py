"""
Query Generator - Converts structured queries to search queries for crawlers
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass
import logging

from .schemas import StructuredQuery, SearchGoal, SearchGoalType, BudgetSource

logger = logging.getLogger(__name__)


@dataclass
class SearchQuery:
    """Represents a search query for a specific website"""
    site_name: str
    goal_id: int
    search_type: str
    filters: Dict[str, Any]
    priority: int
    metadata: Dict[str, Any]


class QueryGenerator:
    """
    Generates search queries for different websites based on structured query
    """
    
    def __init__(self):
        """Initialize query generator"""
        self.site_mappings = self._initialize_site_mappings()
    
    def _initialize_site_mappings(self) -> Dict[str, Dict[str, Any]]:
        """Initialize mappings for different websites"""
        return {
            'divar': {
                'supports': [SearchGoalType.RESIDENTIAL_RENT, SearchGoalType.RESIDENTIAL_PURCHASE, SearchGoalType.VEHICLE_PURCHASE],
                'search_fields': ['category', 'location', 'price_min', 'price_max', 'rent_type'],
            },
            'sheypoor': {
                'supports': [SearchGoalType.RESIDENTIAL_RENT, SearchGoalType.RESIDENTIAL_PURCHASE, SearchGoalType.VEHICLE_PURCHASE],
                'search_fields': ['category', 'location', 'price_min', 'price_max'],
            },
            'bama': {
                'supports': [SearchGoalType.VEHICLE_PURCHASE, SearchGoalType.VEHICLE_LEASE],
                'search_fields': ['vehicle_type', 'price_min', 'price_max', 'lease_monthly'],
            },
            'torob': {
                'supports': [SearchGoalType.ELECTRONICS, SearchGoalType.GENERAL],
                'search_fields': ['product_name', 'price_min', 'price_max'],
            },
            'digikala': {
                'supports': [SearchGoalType.ELECTRONICS, SearchGoalType.GENERAL],
                'search_fields': ['product_name', 'price_min', 'price_max'],
            },
        }
    
    def generate_queries(self, structured_query: StructuredQuery) -> List[SearchQuery]:
        """
        Generate search queries for all goals in structured query
        
        Args:
            structured_query: Structured query from NLU
            
        Returns:
            List of SearchQuery objects for different websites
        """
        all_queries = []
        
        for goal in structured_query.search_goals:
            queries = self._generate_queries_for_goal(goal, structured_query.user_profile)
            all_queries.extend(queries)
        
        # Sort by priority
        all_queries.sort(key=lambda x: x.priority, reverse=True)
        
        return all_queries
    
    def _generate_queries_for_goal(
        self,
        goal: SearchGoal,
        user_profile: Any
    ) -> List[SearchQuery]:
        """Generate queries for a specific goal"""
        queries = []
        
        # Determine which sites support this goal type
        supported_sites = [
            site for site, config in self.site_mappings.items()
            if goal.type in config['supports']
        ]
        
        for site in supported_sites:
            query = self._build_site_query(site, goal, user_profile)
            if query:
                queries.append(query)
        
        return queries
    
    def _build_site_query(
        self,
        site: str,
        goal: SearchGoal,
        user_profile: Any
    ) -> Optional[SearchQuery]:
        """Build query for a specific site"""
        filters = {}
        
        # Base filters based on site
        if site in ['divar', 'sheypoor']:
            filters = self._build_real_estate_filters(goal, user_profile)
        elif site == 'bama':
            filters = self._build_vehicle_filters(goal, user_profile)
        elif site in ['torob', 'digikala']:
            filters = self._build_product_filters(goal, user_profile)
        
        if not filters:
            return None
        
        # Determine priority
        priority = 3 if goal.priority.value == 'high' else 2 if goal.priority.value == 'medium' else 1
        
        return SearchQuery(
            site_name=site,
            goal_id=goal.goal_id,
            search_type=self._map_search_type(site, goal),
            filters=filters,
            priority=priority,
            metadata={
                'goal_type': goal.type.value,
                'target_location': goal.target_location,
                'budget_source': goal.budget_source.value,
            }
        )
    
    def _build_real_estate_filters(
        self,
        goal: SearchGoal,
        user_profile: Any
    ) -> Dict[str, Any]:
        """Build filters for real estate sites (Divar, Sheypoor)"""
        filters = {}
        
        # Location
        if goal.target_location:
            filters['location'] = goal.target_location
        
        # Price range
        if goal.max_price:
            filters['price_max'] = int(goal.max_price)
        if goal.min_price:
            filters['price_min'] = int(goal.min_price)
        elif goal.max_price:
            # Set min price as 80% of max for better results
            filters['price_min'] = int(goal.max_price * 0.8)
        
        # Search type (rent/purchase)
        if goal.type == SearchGoalType.RESIDENTIAL_RENT:
            filters['category'] = 'apartment-rent'
            if 'رهن کامل' in goal.search_type:
                filters['rent_type'] = 'full_deposit'
            else:
                filters['rent_type'] = 'deposit_rent'
        elif goal.type == SearchGoalType.RESIDENTIAL_PURCHASE:
            filters['category'] = 'apartment-sell'
        
        return filters
    
    def _build_vehicle_filters(
        self,
        goal: SearchGoal,
        user_profile: Any
    ) -> Dict[str, Any]:
        """Build filters for vehicle sites (Bama)"""
        filters = {}
        
        # Price range
        if goal.max_price:
            filters['price_max'] = int(goal.max_price)
        if goal.min_price:
            filters['price_min'] = int(goal.min_price)
        
        # Lease information
        if goal.max_monthly_lease_payment:
            filters['lease_monthly_max'] = int(goal.max_monthly_lease_payment)
        
        # Vehicle type
        if goal.type == SearchGoalType.VEHICLE_LEASE:
            filters['search_type'] = 'lease'
        else:
            filters['search_type'] = 'purchase'
        
        return filters
    
    def _build_product_filters(
        self,
        goal: SearchGoal,
        user_profile: Any
    ) -> Dict[str, Any]:
        """Build filters for product sites (Torob, Digikala)"""
        filters = {}
        
        # Price range
        if goal.max_price:
            filters['price_max'] = int(goal.max_price)
        if goal.min_price:
            filters['price_min'] = int(goal.min_price)
        
        # Product name from additional filters
        if goal.additional_filters.get('product_name'):
            filters['product_name'] = goal.additional_filters['product_name']
        
        return filters
    
    def _map_search_type(self, site: str, goal: SearchGoal) -> str:
        """Map goal search type to site-specific search type"""
        if site in ['divar', 'sheypoor']:
            if goal.type == SearchGoalType.RESIDENTIAL_RENT:
                return 'rent'
            elif goal.type == SearchGoalType.RESIDENTIAL_PURCHASE:
                return 'purchase'
        
        elif site == 'bama':
            if goal.type == SearchGoalType.VEHICLE_LEASE:
                return 'lease'
            else:
                return 'purchase'
        
        return 'general'
    
    def generate_query_json(self, search_queries: List[SearchQuery]) -> Dict[str, Any]:
        """
        Convert search queries to JSON format for crawler
        
        Args:
            search_queries: List of SearchQuery objects
            
        Returns:
            JSON dictionary ready for crawler
        """
        result = {
            'queries': [],
            'total_queries': len(search_queries),
            'sites': list(set(q.site_name for q in search_queries))
        }
        
        for query in search_queries:
            query_dict = {
                'site': query.site_name,
                'goal_id': query.goal_id,
                'search_type': query.search_type,
                'filters': query.filters,
                'priority': query.priority,
                'metadata': query.metadata
            }
            result['queries'].append(query_dict)
        
        return result

