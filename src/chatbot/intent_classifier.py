"""
Intent Classifier - Classifies user intent using multiple approaches
"""

import re
from typing import Dict, List, Optional, Tuple
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class IntentType(str, Enum):
    """Types of user intents"""
    SEARCH = "search"
    COMPARE = "compare"
    ADVICE = "advice"
    CALCULATE = "calculate"
    CLARIFY = "clarify"
    GREETING = "greeting"
    UNKNOWN = "unknown"


class IntentClassifier:
    """
    Hybrid intent classifier using:
    1. Keyword-based classification
    2. Pattern matching
    3. Rule-based logic
    (Can be extended with ML models)
    """
    
    def __init__(self):
        """Initialize intent classifier"""
        self._initialize_keywords()
        self._initialize_patterns()
    
    def _initialize_keywords(self):
        """Initialize keyword dictionaries for intent classification"""
        self.intent_keywords = {
            IntentType.SEARCH: [
                'می‌خواهم', 'بخواهم', 'بخواهیم', 'بررسی', 'جستجو', 'پیدا کنم',
                'خرید', 'تهیه', 'بگیرم', 'نگاه کنم', 'ببینم', 'چک کنم'
            ],
            IntentType.COMPARE: [
                'مقایسه', 'مقایسه کن', 'باهم', 'کدوم بهتر', 'تفاوت',
                'کدام', 'کدامیک', 'بهتره', 'بهترین'
            ],
            IntentType.ADVICE: [
                'پیشنهاد', 'نظر', 'راهنمایی', 'کمک', 'مشاوره',
                'چطور', 'چگونه', 'راه', 'بهترین راه'
            ],
            IntentType.CALCULATE: [
                'محاسبه', 'حساب', 'چقدر', 'میشه', 'میتونم',
                'میتوانم', 'توانایی', 'قدرت خرید'
            ],
            IntentType.GREETING: [
                'سلام', 'درود', 'صبح بخیر', 'عصر بخیر', 'خوبی',
                'چطوری', 'چطوره', 'هی'
            ],
        }
    
    def _initialize_patterns(self):
        """Initialize regex patterns for intent detection"""
        self.patterns = {
            IntentType.SEARCH: [
                r'می‌خواهم\s+(.+?)\s+(?:بخواهم|بگیرم|پیدا کنم|خرید)',
                r'بخواهم\s+(.+?)\s+(?:بررسی|جستجو)',
                r'چطور\s+(?:میتونم|میتوانم)\s+(.+?)\s+(?:بگیرم|تهیه کنم)',
            ],
            IntentType.COMPARE: [
                r'مقایسه\s+(.+?)\s+با\s+(.+)',
                r'کدوم\s+(.+?)\s+بهتر',
                r'تفاوت\s+(.+?)\s+با\s+(.+)',
            ],
            IntentType.ADVICE: [
                r'پیشنهاد\s+(.+?)',
                r'چطور\s+(.+?)\s+(?:بکنم|انجام بدهم)',
                r'بهترین\s+(.+?)\s+برای\s+(.+)',
            ],
            IntentType.CALCULATE: [
                r'چقدر\s+(?:میتونم|میتوانم)\s+(.+?)\s+(?:بگیرم|خرید)',
                r'با\s+(.+?)\s+چقدر\s+(?:میشه|میتونم)',
                r'محاسبه\s+(.+?)',
            ],
        }
    
    def classify_by_keywords(self, text: str) -> List[Tuple[IntentType, float]]:
        """Classify intent based on keywords"""
        text_lower = text.lower()
        scores = {}
        
        for intent_type, keywords in self.intent_keywords.items():
            matches = sum(1 for keyword in keywords if keyword in text_lower)
            if matches > 0:
                # Score based on number of matches
                scores[intent_type] = min(matches / len(keywords) * 2, 1.0)
        
        # Sort by score
        sorted_intents = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        return sorted_intents
    
    def classify_by_patterns(self, text: str) -> List[Tuple[IntentType, float]]:
        """Classify intent based on regex patterns"""
        scores = {}
        
        for intent_type, patterns in self.patterns.items():
            for pattern in patterns:
                if re.search(pattern, text, re.IGNORECASE):
                    scores[intent_type] = 0.9  # High confidence for pattern match
                    break
        
        sorted_intents = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        return sorted_intents
    
    def classify(self, text: str) -> Tuple[IntentType, float]:
        """
        Classify user intent with confidence score
        Returns: (IntentType, confidence_score)
        """
        if not text or len(text.strip()) < 2:
            return IntentType.UNKNOWN, 0.0
        
        # Combine keyword and pattern classification
        keyword_results = self.classify_by_keywords(text)
        pattern_results = self.classify_by_patterns(text)
        
        # Merge results
        combined_scores = {}
        
        # Add keyword scores
        for intent, score in keyword_results:
            combined_scores[intent] = combined_scores.get(intent, 0.0) + score * 0.6
        
        # Add pattern scores (higher weight)
        for intent, score in pattern_results:
            combined_scores[intent] = combined_scores.get(intent, 0.0) + score * 0.4
        
        # Normalize scores
        if combined_scores:
            max_score = max(combined_scores.values())
            for intent in combined_scores:
                combined_scores[intent] = min(combined_scores[intent] / max_score, 1.0)
        
        # Determine final intent
        if combined_scores:
            best_intent = max(combined_scores.items(), key=lambda x: x[1])
            return best_intent[0], best_intent[1]
        
        # Default to search if no clear intent but text contains search indicators
        if any(word in text.lower() for word in ['می‌خواهم', 'بخواهم', 'خرید', 'تهیه']):
            return IntentType.SEARCH, 0.7
        
        return IntentType.UNKNOWN, 0.3
    
    def requires_clarification(self, intent: IntentType, confidence: float) -> bool:
        """Determine if clarification is needed"""
        if confidence < 0.5:
            return True
        if intent == IntentType.UNKNOWN:
            return True
        return False
    
    def get_clarification_questions(self, intent: IntentType, text: str) -> List[str]:
        """Generate clarification questions based on intent"""
        questions = []
        
        if intent == IntentType.SEARCH:
            if 'بودجه' not in text.lower() and 'پول' not in text.lower():
                questions.append("بودجه شما چقدر است؟")
            if 'مکان' not in text.lower() and 'منطقه' not in text.lower():
                questions.append("در چه منطقه‌ای جستجو کنیم؟")
        
        elif intent == IntentType.COMPARE:
            questions.append("کدام موارد را می‌خواهید مقایسه کنیم؟")
        
        elif intent == IntentType.ADVICE:
            questions.append("در مورد چه موضوعی نیاز به مشاوره دارید؟")
        
        elif intent == IntentType.UNKNOWN:
            questions.append("لطفاً به صورت دقیق‌تر توضیح دهید که چه می‌خواهید؟")
        
        return questions

