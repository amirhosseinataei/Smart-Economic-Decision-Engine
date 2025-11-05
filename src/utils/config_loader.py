"""
Configuration loader utility
"""

import yaml
import os
from pathlib import Path
from typing import Dict, Any, Optional


def load_config(config_path: Optional[str] = None) -> Dict[str, Any]:
    """
    Load configuration from YAML file
    
    Args:
        config_path: Path to config file
        
    Returns:
        Configuration dictionary
    """
    if config_path is None:
        config_path = os.getenv('SEDE_CONFIG', 'config/config.yaml')
    
    config_file = Path(config_path)
    
    if not config_file.exists():
        # Return default config
        return get_default_config()
    
    with open(config_file, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    
    # Merge with environment variables
    config = merge_env_vars(config)
    
    return config


def get_default_config() -> Dict[str, Any]:
    """Get default configuration"""
    return {
        'app': {
            'name': 'SEDE',
            'version': '1.0.0',
            'debug': False
        },
        'chatbot': {
            'model_type': 'hybrid',
            'max_context_length': 2048,
            'temperature': 0.7,
            'confidence_threshold': 0.75
        },
        'crawler': {
            'concurrent_requests': 16,
            'download_delay': 1.0,
            'retry_times': 3,
            'max_workers': 5
        }
    }


def merge_env_vars(config: Dict[str, Any]) -> Dict[str, Any]:
    """Merge environment variables into config"""
    # Database
    if os.getenv('DATABASE_URL'):
        config.setdefault('database', {})['url'] = os.getenv('DATABASE_URL')
    
    # Redis
    if os.getenv('REDIS_URL'):
        config.setdefault('redis', {})['url'] = os.getenv('REDIS_URL')
    
    return config

