"""
Entity Extractor - Extracts entities from user input using multiple approaches
"""

import re
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
import logging

from .schemas import UserProfile, SearchGoal, SearchGoalType, BudgetSource, Priority

logger = logging.getLogger(__name__)


@dataclass
class ExtractedEntity:
    """Represents an extracted entity"""
    entity_type: str
    value: Any
    confidence: float
    start_pos: int
    end_pos: int
    raw_text: str


class EntityExtractor:
    """
    Advanced entity extractor using hybrid approach:
    1. Regex patterns for common entities
    2. Rule-based extraction for financial terms
    3. ML-based extraction (can be integrated with transformers)
    """
    
    def __init__(self):
        """Initialize entity extractor with patterns"""
        self._initialize_patterns()
        self._initialize_financial_patterns()
        self._initialize_location_patterns()
    
    def _initialize_patterns(self):
        """Initialize regex patterns for common entities"""
        # Money patterns (Tomans)
        self.money_patterns = [
            r'(\d+(?:\.\d+)?)\s*(?:میلیون|ملیون|م|M)\s*(?:تومان|تومن)?',
            r'(\d+(?:\.\d+)?)\s*(?:هزار|k)\s*(?:تومان|تومن)?',
            r'(\d+(?:\.\d+)?)\s*(?:میلیارد|بیلیون|b)\s*(?:تومان|تومن)?',
            r'(\d+(?:,\d{3})*(?:\.\d+)?)\s*(?:تومان|تومن)',
        ]
        
        # Monthly payment patterns
        self.monthly_patterns = [
            r'ماهی\s*(\d+(?:\.\d+)?)\s*(?:میلیون|ملیون|م|M)',
            r'ماهانه\s*(\d+(?:\.\d+)?)\s*(?:میلیون|ملیون|م|M)',
            r'قسط\s*(\d+(?:\.\d+)?)\s*(?:میلیون|ملیون|م|M)',
        ]
        
        # Loan patterns
        self.loan_patterns = [
            r'وام\s*(\d+(?:\.\d+)?)\s*(?:میلیون|ملیون|م|M)',
            r'(\d+(?:\.\d+)?)\s*(?:میلیون|ملیون|م|M)\s*وام',
            r'قرض\s*(\d+(?:\.\d+)?)\s*(?:میلیون|ملیون|م|M)',
        ]
        
        # Time patterns
        self.time_patterns = [
            r'(\d+)\s*ماه\s*(?:دیگه|دیگر|آینده|بعد)',
            r'(\d+)\s*ماه\s*(?:بعد|بعدا)',
            r'تا\s*(\d+)\s*ماه\s*(?:دیگه|دیگر|آینده)',
        ]
    
    def _initialize_financial_patterns(self):
        """Initialize patterns for financial terms"""
        self.financial_keywords = {
            'liquidity': ['نقد', 'نقدینگی', 'پول نقد', 'موجودی', 'دارم', 'داریم'],
            'loan': ['وام', 'قرض', 'تسهیلات', 'اعتبار'],
            'monthly_payment': ['ماهی', 'ماهانه', 'قسط', 'اقساط', 'لیزینگ'],
            'rent': ['رهن', 'اجاره', 'رهن کامل', 'رهن و اجاره'],
            'purchase': ['خرید', 'تهیه', 'بگیرم', 'بگیریم'],
        }
    
    def _initialize_location_patterns(self):
        """Initialize patterns for location extraction"""
        self.location_keywords = [
            'تهران', 'اکباتان', 'ولیعصر', 'تجریش', 'ونک', 'پاسداران',
            'شهرک غرب', 'سعادت آباد', 'میرداماد', 'گیشا', 'جنت آباد'
        ]
        
        self.location_patterns = [
            r'(?:در|از|به)\s*(.+?)(?:\s|$|،|،|\.)',
            r'منطقه\s*(.+?)(?:\s|$|،|،|\.)',
            r'محله\s*(.+?)(?:\s|$|،|،|\.)',
        ]
    
    def _normalize_money(self, value: str, unit: str = 'million') -> float:
        """Normalize money values to Tomans (millions)"""
        try:
            num_value = float(value.replace(',', ''))
            
            if 'هزار' in unit.lower() or 'k' in unit.lower():
                return num_value / 1000.0
            elif 'میلیارد' in unit.lower() or 'b' in unit.lower():
                return num_value * 1000.0
            else:
                return num_value
        except (ValueError, AttributeError):
            return 0.0
    
    def extract_money_entities(self, text: str) -> List[ExtractedEntity]:
        """Extract money-related entities"""
        entities = []
        
        for pattern in self.money_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                value_str = match.group(1)
                unit = match.group(0)
                value = self._normalize_money(value_str, unit)
                
                entities.append(ExtractedEntity(
                    entity_type='money',
                    value=value,
                    confidence=0.9,
                    start_pos=match.start(),
                    end_pos=match.end(),
                    raw_text=match.group(0)
                ))
        
        return entities
    
    def extract_loan_info(self, text: str) -> Tuple[float, int]:
        """Extract loan amount and availability time"""
        loan_amount = 0.0
        loan_months = 0
        
        # Extract loan amount
        for pattern in self.loan_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                value_str = match.group(1)
                loan_amount = self._normalize_money(value_str)
                break
        
        # Extract loan availability time
        for pattern in self.time_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                loan_months = int(match.group(1))
                break
        
        return loan_amount, loan_months
    
    def extract_monthly_payment(self, text: str) -> float:
        """Extract monthly payment amount"""
        monthly_payment = 0.0
        
        for pattern in self.monthly_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                value_str = match.group(1)
                monthly_payment = self._normalize_money(value_str)
                break
        
        return monthly_payment
    
    def extract_location(self, text: str) -> List[str]:
        """Extract location entities"""
        locations = []
        
        # Direct keyword matching
        for keyword in self.location_keywords:
            if keyword in text:
                locations.append(keyword)
        
        # Pattern-based extraction
        for pattern in self.location_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                location = match.group(1).strip()
                if location and len(location) > 2:
                    locations.append(location)
        
        return list(set(locations))  # Remove duplicates
    
    def extract_search_type(self, text: str) -> Dict[str, Any]:
        """Extract search type and related information"""
        search_info = {
            'type': None,
            'search_type': '',
            'is_rent': False,
            'is_purchase': False,
            'is_lease': False,
        }
        
        text_lower = text.lower()
        
        # Check for rent
        if any(keyword in text_lower for keyword in ['رهن', 'اجاره', 'رهن کامل']):
            search_info['is_rent'] = True
            search_info['type'] = SearchGoalType.RESIDENTIAL_RENT
            if 'رهن کامل' in text_lower:
                search_info['search_type'] = 'رهن کامل'
            else:
                search_info['search_type'] = 'رهن و اجاره'
        
        # Check for purchase
        if any(keyword in text_lower for keyword in ['خرید', 'تهیه', 'بگیرم']):
            search_info['is_purchase'] = True
            if not search_info['type']:
                search_info['type'] = SearchGoalType.RESIDENTIAL_PURCHASE
        
        # Check for vehicle
        if any(keyword in text_lower for keyword in ['ماشین', 'خودرو', 'اتومبیل']):
            if search_info['is_purchase']:
                search_info['type'] = SearchGoalType.VEHICLE_PURCHASE
            elif search_info['is_lease']:
                search_info['type'] = SearchGoalType.VEHICLE_LEASE
        
        # Check for lease
        if any(keyword in text_lower for keyword in ['لیزینگ', 'قسط', 'اقساط']):
            search_info['is_lease'] = True
            if 'ماشین' in text_lower or 'خودرو' in text_lower:
                search_info['type'] = SearchGoalType.VEHICLE_LEASE
        
        return search_info
    
    def extract_all_entities(self, text: str) -> Dict[str, Any]:
        """
        Extract all entities from text
        Returns a comprehensive dictionary of extracted information
        """
        entities = {
            'money_entities': self.extract_money_entities(text),
            'locations': self.extract_location(text),
            'loan_info': self.extract_loan_info(text),
            'monthly_payment': self.extract_monthly_payment(text),
            'search_type': self.extract_search_type(text),
        }
        
        # Extract primary liquidity
        money_entities = entities['money_entities']
        if money_entities:
            # First money entity is usually the main liquidity
            entities['primary_liquidity'] = money_entities[0].value
        
        return entities
    
    def build_user_profile(self, entities: Dict[str, Any]) -> UserProfile:
        """Build user profile from extracted entities"""
        loan_amount, loan_months = entities.get('loan_info', (0.0, 0))
        monthly_payment = entities.get('monthly_payment', 0.0)
        primary_liquidity = entities.get('primary_liquidity', 0.0)
        
        return UserProfile(
            liquidity=primary_liquidity,
            loan_amount=loan_amount,
            loan_availability_months=loan_months,
            max_monthly_payment=monthly_payment
        )
    
    def build_search_goals(self, entities: Dict[str, Any], user_profile: UserProfile) -> List[SearchGoal]:
        """Build search goals from extracted entities"""
        goals = []
        search_info = entities.get('search_type', {})
        locations = entities.get('locations', [])
        
        goal_id = 1
        
        # Determine search type
        search_type = search_info.get('type')
        if not search_type:
            # Default to general search
            search_type = SearchGoalType.GENERAL
        
        # Determine budget source
        if user_profile.loan_amount > 0 and user_profile.liquidity > 0:
            budget_source = BudgetSource.LIQUIDITY_LOAN
        elif user_profile.loan_amount > 0:
            budget_source = BudgetSource.LOAN
        elif user_profile.max_monthly_payment > 0:
            budget_source = BudgetSource.MONTHLY_PAYMENT
        else:
            budget_source = BudgetSource.LIQUIDITY
        
        # Create goals for each location
        if locations:
            for location in locations:
                goal = SearchGoal(
                    goal_id=goal_id,
                    type=search_type,
                    target_location=location,
                    budget_source=budget_source,
                    priority=Priority.HIGH if goal_id == 1 else Priority.MEDIUM,
                    search_type=search_info.get('search_type', 'عمومی'),
                    max_price=user_profile.total_budget if user_profile.total_budget > 0 else None,
                    max_monthly_lease_payment=user_profile.max_monthly_payment if user_profile.max_monthly_payment > 0 else None
                )
                goals.append(goal)
                goal_id += 1
        else:
            # Create a general goal if no specific location
            goal = SearchGoal(
                goal_id=goal_id,
                type=search_type,
                target_location="",
                budget_source=budget_source,
                priority=Priority.HIGH,
                search_type=search_info.get('search_type', 'عمومی'),
                max_price=user_profile.total_budget if user_profile.total_budget > 0 else None,
                max_monthly_lease_payment=user_profile.max_monthly_payment if user_profile.max_monthly_payment > 0 else None
            )
            goals.append(goal)
        
        return goals

