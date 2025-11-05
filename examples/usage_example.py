"""
Example usage of SEDE system
"""

import sys
import os
import json
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.integration import SEDEIntegration
from src.chatbot import ChatbotEngine
from src.crawler import CrawlerManager


def example_complex_request():
    """Example of processing a complex user request"""
    
    print("=" * 80)
    print("SEDE - Example: Complex User Request")
    print("=" * 80)
    
    # Initialize integration
    sede = SEDEIntegration()
    
    # Complex user request
    user_message = """
    سلام من 600 میلیون نقد دارم و می‌توانم 200 میلیون هم وام بگیرم تا 2 ماه آینده به دستم برسد.
    می‌خواهم بررسی کنم با این مبلغ خانه در تهران اکباتان رهن کنم.
    اگر نمی‌توانم در کدام منطقه مناسب می‌توانم منزل برای رهن پیدا کنم.
    همچنین اگر پول من نمی‌رسد برای ماشین چطور می‌توانم ماشین مناسبی با این مبلغ تهیه کنم.
    همچنین چه برای اجاره و چه برای قسط ماشین لیزینگ می‌توانم ماهی 15 میلیون بدهم بجز نقدینگی و مبلغ وامم.
    """
    
    print(f"\nUser Message:\n{user_message}\n")
    print("-" * 80)
    
    # Process request
    result = sede.process_user_request(user_message, session_id="example_session_1")
    
    # Display results
    print("\nResults:")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    
    # Save to file
    output_file = "data/crawl_results_example.json"
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    
    print(f"\nResults saved to: {output_file}")
    
    # Cleanup
    sede.cleanup()


def example_simple_request():
    """Example of processing a simple user request"""
    
    print("\n" + "=" * 80)
    print("SEDE - Example: Simple User Request")
    print("=" * 80)
    
    # Initialize chatbot only (no crawling)
    chatbot = ChatbotEngine()
    
    # Simple user request
    user_message = "من 60 میلیون پول دارم چطور می‌توانم یک مدل گوشی مناسب تهیه کنم"
    
    print(f"\nUser Message:\n{user_message}\n")
    print("-" * 80)
    
    # Process message
    response = chatbot.process_message(user_message, session_id="example_session_2")
    
    # Display response
    print("\nChatbot Response:")
    print(f"Success: {response.success}")
    print(f"Message: {response.message}")
    print(f"Confidence: {response.confidence}")
    
    if response.query:
        print(f"\nStructured Query:")
        print(f"  Budget: {response.query.user_profile.total_budget:,.0f} million")
        print(f"  Goals: {len(response.query.search_goals)}")
        for goal in response.query.search_goals:
            print(f"    - {goal.type.value}: {goal.target_location or 'Any'}")


def example_crawler_only():
    """Example of using crawler directly"""
    
    print("\n" + "=" * 80)
    print("SEDE - Example: Direct Crawler Usage")
    print("=" * 80)
    
    # Initialize crawler manager
    crawler_manager = CrawlerManager()
    
    # Define search queries
    queries = [
        {
            'site': 'divar',
            'filters': {
                'category': 'apartment-rent',
                'location': 'تهران',
                'price_max': 800,
                'rent_type': 'full_deposit'
            },
            'goal_id': 1
        },
        {
            'site': 'bama',
            'filters': {
                'search_type': 'purchase',
                'price_max': 800
            },
            'goal_id': 2
        }
    ]
    
    print(f"\nCrawling {len(queries)} sites...")
    
    # Execute crawl
    batch_result = crawler_manager.crawl_batch(queries, parallel=True)
    
    print(f"\nResults:")
    print(f"  Success: {batch_result.success}")
    print(f"  Total Items: {batch_result.total_items}")
    print(f"  Execution Time: {batch_result.execution_time:.2f}s")
    
    for result in batch_result.results:
        print(f"\n  {result.site_name}:")
        print(f"    Items: {result.total_items}")
        print(f"    Time: {result.execution_time:.2f}s")
        if result.errors:
            print(f"    Errors: {len(result.errors)}")
    
    # Cleanup
    crawler_manager.cleanup()


if __name__ == "__main__":
    # Run examples
    try:
        example_simple_request()
        # Uncomment to run other examples (requires internet connection)
        # example_complex_request()
        # example_crawler_only()
    except KeyboardInterrupt:
        print("\n\nInterrupted by user")
    except Exception as e:
        print(f"\n\nError: {str(e)}")
        import traceback
        traceback.print_exc()

