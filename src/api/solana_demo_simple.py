#!/usr/bin/env python3
"""
Simple DexTools Solana Demo
This script demonstrates a simple request to the DexTools API
to fetch cryptocurrency token data from the Solana blockchain and display it in the console.
"""

import json
import requests
import logging
from typing import Dict, Any, List, Optional, TypedDict

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('solana_demo_simple')

# Type definitions
class TokenInfo(TypedDict):
    name: str
    symbol: str
    address: str

class PairData(TypedDict):
    rank: int
    price: float
    price24h: float
    variation24h: float
    address: str
    mainToken: TokenInfo
    sideToken: TokenInfo

class SolanaData(TypedDict):
    pairs: List[PairData]

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

def display_top_gainers(data: Dict[str, Any], limit: int = 10) -> None:
    """
    Display the top gaining tokens in a readable format
    
    Args:
        data: The data returned from the API
        limit: Number of tokens to display (default: 10)
    """
    if not data:
        logger.error("Invalid data format received")
        return
    
    # Check if the response has the expected structure
    if 'data' in data:
        pairs = data.get('data', [])
    elif 'pairs' in data:
        pairs = data.get('pairs', [])
    else:
        logger.error(f"Unexpected response format. Keys: {list(data.keys())}")
        return
    
    if not pairs:
        logger.warning("No pairs found in the data")
        return
    
    print("\n=== Top Solana Gainers ===")
    print(f"{'Rank':<5} {'Symbol':<10} {'Name':<30} {'Price':<15} {'24h Change':<15}")
    print("-" * 80)
    
    for i, pair in enumerate(pairs[:limit]):
        main_token = pair.get('mainToken', {})
        symbol = main_token.get('symbol', 'N/A')
        name = main_token.get('name', 'N/A')
        price = pair.get('price', 0)
        variation = pair.get('variation24h', 0)
        
        print(f"{i+1:<5} {symbol:<10} {name[:30]:<30} ${price:<15.8f} {variation:<15.2f}%")

def run_demo() -> None:
    """Main function to run the DexTools Solana demo"""
    logger.info("Starting DexTools Solana Demo...")
    
    try:
        # Get Solana gainers
        solana_gainers = get_solana_gainers()
        
        # Display top gainers in a readable format
        display_top_gainers(solana_gainers)
        
        logger.info("Demo completed successfully.")
    except Exception as e:
        logger.error(f"Demo failed: {str(e)}", exc_info=True)

if __name__ == "__main__":
    run_demo() 