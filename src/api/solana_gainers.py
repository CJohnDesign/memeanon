#!/usr/bin/env python3
"""
Simple DexTools Solana Gainers Demo
This script demonstrates a simple request to the DexTools API
to fetch top gaining tokens on the Solana blockchain and display them in the console.
"""

import json
import requests
import logging
from typing import Dict, Any

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('solana_gainers')

def get_solana_gainers() -> Dict[str, Any]:
    """
    Get top gaining tokens on the Solana blockchain using the specific endpoint
    
    Returns:
        Dict containing top gaining tokens on Solana
    """
    logger.info("Fetching top gainers for Solana blockchain")
    
    # Use the exact endpoint from the curl example
    url = "https://public-api.dextools.io/trial/v2/ranking/solana/gainers"
    
    # Use the API key from the curl example
    headers = {
        "accept": "application/json",
        "x-api-key": "UFYgd1VSeq7ZdWbPQDEPQ6fuQ63QahNb2n4vntbi"
    }
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to fetch Solana gainers: {str(e)}")
        if hasattr(e, 'response') and e.response:
            logger.error(f"Response status: {e.response.status_code}")
            logger.error(f"Response data: {e.response.text}")
        raise Exception("Failed to fetch Solana gainers")

def pretty_print_json(data: Dict[str, Any]) -> None:
    """Print JSON data in a readable format"""
    print(json.dumps(data, indent=2))

def run_demo() -> None:
    """Main function to run the DexTools Solana Gainers demo"""
    logger.info("Starting DexTools Solana Gainers Demo...")
    
    try:
        # Get Solana gainers
        solana_gainers = get_solana_gainers()
        print("\n=== Solana Gainers ===")
        pretty_print_json(solana_gainers)
        
        logger.info("Demo completed successfully.")
    except Exception as e:
        logger.error(f"Demo failed: {str(e)}", exc_info=True)

if __name__ == "__main__":
    run_demo() 