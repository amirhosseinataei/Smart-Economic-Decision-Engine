"""
Integration Module - Connects Chatbot and Crawler systems
"""

from typing import Dict, Any, Optional
import logging

from .chatbot import ChatbotEngine
from .chatbot.schemas import ChatbotResponse
from .crawler import CrawlerManager
from .crawler.schemas import CrawlBatchResult

logger = logging.getLogger(__name__)


class SEDEIntegration:
    """
    Main integration class that connects chatbot and crawler
    Provides end-to-end functionality
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize SEDE integration
        
        Args:
            config: Configuration dictionary
        """
        self.config = config or {}
        self.chatbot = ChatbotEngine(self.config.get('chatbot', {}))
        self.crawler_manager = CrawlerManager(self.config.get('crawler', {}))
    
    def process_user_request(
        self,
        user_message: str,
        session_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Process user request end-to-end:
        1. Understand user intent via chatbot
        2. Generate search queries
        3. Execute crawlers
        4. Return results
        
        Args:
            user_message: User input message
            session_id: Optional session ID
            
        Returns:
            Complete response with chatbot analysis and crawl results
        """
        try:
            # Step 1: Process through chatbot
            chatbot_response: ChatbotResponse = self.chatbot.process_message(
                user_message,
                session_id
            )
            
            if not chatbot_response.success:
                return {
                    'success': False,
                    'message': chatbot_response.message,
                    'errors': chatbot_response.errors
                }
            
            # If clarification needed, return chatbot response only
            if chatbot_response.requires_clarification:
                return {
                    'success': True,
                    'requires_clarification': True,
                    'message': chatbot_response.message,
                    'clarification_questions': chatbot_response.clarification_questions,
                    'confidence': chatbot_response.confidence
                }
            
            # Step 2: Generate search queries
            if not chatbot_response.query:
                return {
                    'success': False,
                    'message': 'نتوانستیم درخواست شما را به درستی درک کنیم.'
                }
            
            structured_query = chatbot_response.query
            query_generator = self.chatbot.query_generator
            search_queries = query_generator.generate_queries(structured_query)
            query_json = query_generator.generate_query_json(search_queries)
            
            # Step 3: Execute crawlers
            crawl_results = self.crawler_manager.crawl_from_query_json(query_json, normalize=True)
            
            # Step 4: Combine results
            return {
                'success': True,
                'chatbot_response': chatbot_response.dict(),
                'structured_query': structured_query.dict(),
                'search_queries': query_json,
                'crawl_results': crawl_results,
                'summary': self._generate_summary(chatbot_response, crawl_results)
            }
        
        except Exception as e:
            logger.error(f"Error in process_user_request: {str(e)}", exc_info=True)
            return {
                'success': False,
                'message': 'خطایی در پردازش درخواست شما رخ داد.',
                'errors': [str(e)]
            }
    
    def _generate_summary(
        self,
        chatbot_response: ChatbotResponse,
        crawl_results: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate summary of results"""
        return {
            'user_budget': chatbot_response.query.user_profile.total_budget if chatbot_response.query else None,
            'total_items_found': crawl_results.get('total_items', 0),
            'sources_crawled': crawl_results.get('sources', []),
            'confidence': chatbot_response.confidence,
            'execution_time': crawl_results.get('metadata', {}).get('execution_time', 0)
        }
    
    def cleanup(self):
        """Cleanup resources"""
        self.crawler_manager.cleanup()

