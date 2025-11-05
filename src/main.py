"""
Main entry point for SEDE application
"""

import sys
import argparse
from pathlib import Path

from .integration import SEDEIntegration
from .utils.config_loader import load_config
from .utils.logger import setup_logging


def main():
    """Main function"""
    parser = argparse.ArgumentParser(description='SEDE - Smart Economic Decision Engine')
    parser.add_argument('--config', type=str, help='Path to config file')
    parser.add_argument('--log-level', type=str, default='INFO', help='Logging level')
    parser.add_argument('--message', type=str, help='User message to process')
    parser.add_argument('--interactive', action='store_true', help='Interactive mode')
    
    args = parser.parse_args()
    
    # Setup logging
    setup_logging(level=args.log_level, log_file='logs/sede.log')
    
    # Load config
    config = load_config(args.config)
    
    # Initialize SEDE
    sede = SEDEIntegration(config)
    
    try:
        if args.message:
            # Process single message
            result = sede.process_user_request(args.message)
            print(result)
        
        elif args.interactive:
            # Interactive mode
            print("SEDE - Smart Economic Decision Engine")
            print("Type 'exit' to quit\n")
            
            session_id = "interactive_session"
            
            while True:
                try:
                    user_input = input("You: ").strip()
                    
                    if user_input.lower() in ['exit', 'quit', 'خروج']:
                        break
                    
                    if not user_input:
                        continue
                    
                    result = sede.process_user_request(user_input, session_id)
                    
                    if result.get('requires_clarification'):
                        print(f"\nSEDE: {result.get('message')}\n")
                    elif result.get('success'):
                        print(f"\nSEDE: Found {result.get('crawl_results', {}).get('total_items', 0)} items\n")
                    else:
                        print(f"\nSEDE: {result.get('message', 'Error occurred')}\n")
                
                except KeyboardInterrupt:
                    break
                except Exception as e:
                    print(f"\nError: {str(e)}\n")
        
        else:
            parser.print_help()
    
    finally:
        sede.cleanup()


if __name__ == "__main__":
    main()

