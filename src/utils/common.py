"""
Common utility functions for the DexTools Solana API project.
"""

import json
import logging
from typing import Dict, Any

logger = logging.getLogger('dextools_utils')

def pretty_print_json(data: Dict[str, Any]) -> None:
    """
    Print JSON data in a readable format
    
    Args:
        data: The JSON data to print
    """
    print(json.dumps(data, indent=2))

def setup_logging(log_file: str, log_level: int = logging.INFO) -> None:
    """
    Set up logging configuration
    
    Args:
        log_file: Path to the log file
        log_level: Logging level (default: INFO)
    """
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()
        ]
    )
    logger.info("Logging initialized") 