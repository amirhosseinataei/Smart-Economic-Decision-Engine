"""
Chatbot Engine - Main orchestration engine for chatbot functionality
"""

from typing import Dict, Any, Optional, List
import logging
from datetime import datetime

from .nlu import NLUProcessor
from .query_generator import QueryGenerator
from .schemas import ChatbotResponse, StructuredQuery

logger = logging.getLogger(__name__)


class ChatbotEngine:
    """
    Main chatbot engine that orchestrates:
    - Natural Language Understanding
    - Query generation
    - Response formatting
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize chatbot engine
        
        Args:
            config: Optional configuration dictionary
        """
        self.config = config or {}
        self.nlu_processor = NLUProcessor()
        self.query_generator = QueryGenerator()
        self.conversation_history: Dict[str, List[Dict[str, Any]]] = {}
    
    def process_message(
        self,
        message: str,
        session_id: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> ChatbotResponse:
        """
        Process user message and return structured response
        
        Args:
            message: User input message
            session_id: Optional session identifier for conversation tracking
            context: Optional conversation context
            
        Returns:
            ChatbotResponse with structured query and metadata
        """
        try:
            # Get conversation context if session exists
            if session_id:
                conversation_context = self._get_conversation_context(session_id)
                if context:
                    conversation_context.update(context)
                context = conversation_context
            
            # Process message through NLU
            nlu_result = self.nlu_processor.process(message, context)
            
            # Check if clarification is needed
            if nlu_result['requires_clarification']:
                return ChatbotResponse(
                    success=True,
                    message=self._generate_clarification_message(nlu_result['clarification_questions']),
                    confidence=nlu_result['confidence'],
                    requires_clarification=True,
                    clarification_questions=nlu_result['clarification_questions']
                )
            
            # Build structured query
            structured_query = self.nlu_processor.build_structured_query(nlu_result)
            structured_query.timestamp = datetime.now().isoformat()
            
            # Generate search queries
            search_queries = self.query_generator.generate_queries(structured_query)
            query_json = self.query_generator.generate_query_json(search_queries)
            
            # Store conversation history
            if session_id:
                self._update_conversation_history(session_id, message, structured_query)
            
            # Generate response message
            response_message = self._generate_response_message(structured_query, nlu_result)
            
            return ChatbotResponse(
                success=True,
                query=structured_query,
                message=response_message,
                confidence=nlu_result['confidence'],
                requires_clarification=False
            )
        
        except Exception as e:
            logger.error(f"Error processing message: {str(e)}", exc_info=True)
            return ChatbotResponse(
                success=False,
                message="متأسفانه خطایی در پردازش درخواست شما رخ داد. لطفاً دوباره تلاش کنید.",
                confidence=0.0,
                errors=[str(e)]
            )
    
    def _get_conversation_context(self, session_id: str) -> Dict[str, Any]:
        """Get conversation context for a session"""
        if session_id in self.conversation_history:
            history = self.conversation_history[session_id]
            # Extract context from last interaction
            if history:
                last_interaction = history[-1]
                return last_interaction.get('context', {})
        return {}
    
    def _update_conversation_history(
        self,
        session_id: str,
        message: str,
        structured_query: StructuredQuery
    ):
        """Update conversation history"""
        if session_id not in self.conversation_history:
            self.conversation_history[session_id] = []
        
        self.conversation_history[session_id].append({
            'message': message,
            'query': structured_query.dict(),
            'timestamp': datetime.now().isoformat(),
            'context': {
                'user_profile': structured_query.user_profile.dict(),
                'search_goals': [g.dict() for g in structured_query.search_goals]
            }
        })
    
    def _generate_clarification_message(self, questions: List[str]) -> str:
        """Generate clarification message"""
        if not questions:
            return "لطفاً اطلاعات بیشتری در مورد درخواست خود ارائه دهید."
        
        message = "برای ارائه بهترین پیشنهاد، لطفاً به سؤالات زیر پاسخ دهید:\n\n"
        for i, question in enumerate(questions, 1):
            message += f"{i}. {question}\n"
        
        return message
    
    def _generate_response_message(
        self,
        structured_query: StructuredQuery,
        nlu_result: Dict[str, Any]
    ) -> str:
        """Generate human-readable response message"""
        message_parts = []
        
        # Summarize user profile
        user_profile = structured_query.user_profile
        if user_profile.total_budget > 0:
            message_parts.append(
                f"بودجه کل شما: {user_profile.total_budget:,.0f} میلیون تومان"
            )
        if user_profile.max_monthly_payment > 0:
            message_parts.append(
                f"توان پرداخت ماهیانه: {user_profile.max_monthly_payment:,.0f} میلیون تومان"
            )
        
        # Summarize search goals
        message_parts.append(f"\n{len(structured_query.search_goals)} هدف جستجو شناسایی شد:")
        for goal in structured_query.search_goals:
            goal_desc = f"• {goal.type.value}"
            if goal.target_location:
                goal_desc += f" در {goal.target_location}"
            if goal.max_price:
                goal_desc += f" (تا {goal.max_price:,.0f} میلیون تومان)"
            message_parts.append(goal_desc)
        
        message_parts.append("\nدر حال جستجو در سایت‌های مرتبط...")
        
        return "\n".join(message_parts)
    
    def clear_session(self, session_id: str):
        """Clear conversation history for a session"""
        if session_id in self.conversation_history:
            del self.conversation_history[session_id]
    
    def get_conversation_summary(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get summary of conversation for a session"""
        if session_id not in self.conversation_history:
            return None
        
        history = self.conversation_history[session_id]
        if not history:
            return None
        
        return {
            'session_id': session_id,
            'total_messages': len(history),
            'last_message': history[-1]['message'],
            'last_query': history[-1]['query'],
            'timestamp': history[-1]['timestamp']
        }

