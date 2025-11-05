"""
Tests for chatbot module
"""

import pytest
from src.chatbot import ChatbotEngine, NLUProcessor, EntityExtractor


def test_entity_extractor():
    """Test entity extraction"""
    extractor = EntityExtractor()
    
    text = "من 600 میلیون نقد دارم و می‌خواهم خانه در تهران اکباتان رهن کنم"
    entities = extractor.extract_all_entities(text)
    
    assert entities.get('primary_liquidity') == 600.0
    assert len(entities.get('locations', [])) > 0


def test_chatbot_engine():
    """Test chatbot engine"""
    engine = ChatbotEngine()
    
    response = engine.process_message(
        "من 60 میلیون پول دارم چطور می‌توانم یک مدل گوشی مناسب تهیه کنم"
    )
    
    assert response.success
    assert response.query is not None
    assert response.query.user_profile.liquidity > 0


if __name__ == "__main__":
    pytest.main([__file__])

