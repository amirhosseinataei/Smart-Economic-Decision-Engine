"""
Natural Language Understanding (NLU) Processor
Combines entity extraction and intent classification
"""

from typing import Dict, Any, Optional
import logging

from .entity_extractor import EntityExtractor
from .intent_classifier import IntentClassifier, IntentType
from .schemas import StructuredQuery, UserProfile, SearchGoal

logger = logging.getLogger(__name__)


class NLUProcessor:
    """
    Main NLU processor that combines:
    - Intent classification
    - Entity extraction
    - Query structuring
    """
    
    def __init__(self):
        """Initialize NLU processor"""
        self.entity_extractor = EntityExtractor()
        self.intent_classifier = IntentClassifier()
    
    def process(self, text: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Process user input and extract structured information
        
        Args:
            text: User input text
            context: Optional conversation context
            
        Returns:
            Dictionary containing:
            - intent: IntentType
            - confidence: float
            - entities: Dict of extracted entities
            - user_profile: UserProfile
            - search_goals: List[SearchGoal]
            - requires_clarification: bool
            - clarification_questions: List[str]
        """
        if context is None:
            context = {}
        
        # Classify intent
        intent, intent_confidence = self.intent_classifier.classify(text)
        
        # Extract entities
        entities = self.entity_extractor.extract_all_entities(text)
        
        # Build user profile
        user_profile = self.entity_extractor.build_user_profile(entities)
        
        # Build search goals
        search_goals = self.entity_extractor.build_search_goals(entities, user_profile)
        
        # Check if clarification is needed
        requires_clarification = self.intent_classifier.requires_clarification(intent, intent_confidence)
        clarification_questions = []
        
        if requires_clarification:
            clarification_questions = self.intent_classifier.get_clarification_questions(intent, text)
        
        # Calculate overall confidence
        overall_confidence = self._calculate_confidence(intent_confidence, entities, user_profile)
        
        return {
            'intent': intent,
            'confidence': overall_confidence,
            'entities': entities,
            'user_profile': user_profile,
            'search_goals': search_goals,
            'requires_clarification': requires_clarification,
            'clarification_questions': clarification_questions,
            'is_multi_goal': len(search_goals) > 1,
        }
    
    def _calculate_confidence(
        self,
        intent_confidence: float,
        entities: Dict[str, Any],
        user_profile: UserProfile
    ) -> float:
        """Calculate overall confidence score"""
        # Base confidence from intent
        confidence = intent_confidence * 0.4
        
        # Add confidence from entities
        entity_confidence = 0.0
        
        # Money entities found
        if entities.get('money_entities'):
            entity_confidence += 0.3
        
        # Location found
        if entities.get('locations'):
            entity_confidence += 0.2
        
        # Search type identified
        search_info = entities.get('search_type', {})
        if search_info.get('type'):
            entity_confidence += 0.1
        
        confidence += entity_confidence * 0.6
        
        # Penalize if user profile is incomplete
        if user_profile.total_budget == 0 and user_profile.max_monthly_payment == 0:
            confidence *= 0.7
        
        return min(confidence, 1.0)
    
    def build_structured_query(self, nlu_result: Dict[str, Any]) -> StructuredQuery:
        """
        Build structured query from NLU result
        
        Args:
            nlu_result: Result from process() method
            
        Returns:
            StructuredQuery object
        """
        return StructuredQuery(
            user_profile=nlu_result['user_profile'],
            search_goals=nlu_result['search_goals'],
            is_multi_goal=nlu_result['is_multi_goal'],
            context={},
            confidence=nlu_result['confidence']
        )

