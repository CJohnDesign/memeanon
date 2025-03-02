#!/usr/bin/env python3
"""
Solana DexTools Demo

This script demonstrates how to use the Solana DexTools API utilities to fetch and analyze
Solana token data. It includes examples of fetching hot pairs, gainers, losers, and new tokens.
"""

import os
import asyncio
import json
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional

# Import our Solana-specific utilities
from solana_dextools_api import SolanaDexToolsAPI
from prompts.solana_token_analysis_prompt import (
    get_solana_token_analysis_prompt,
    get_solana_hot_pairs_prompt,
    get_solana_new_tokens_prompt,
    SolanaTokenData
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("solana_dextools_demo.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('solana_dextools_demo')

class SolanaDexToolsDemo:
    """Demo class for Solana DexTools API integration"""
    
    def __init__(self, api_key: str):
        """
        Initialize the Solana DexTools Demo
        
        Args:
            api_key: DexTools API key
        """
        self.api_key = api_key
        self.solana_api = SolanaDexToolsAPI(api_key=api_key, plan="trial")
        logger.info("Initialized Solana DexTools Demo with trial plan")
        
    async def get_solana_info(self):
        """Get information about the Solana blockchain"""
        logger.info("Fetching Solana blockchain information")
        blockchain_info = await self.solana_api.get_solana_blockchains()
        
        if isinstance(blockchain_info, dict) and "id" in blockchain_info:
            logger.info(f"Successfully fetched Solana blockchain information: {blockchain_info.get('name')}")
            print("\n=== Solana Blockchain Information ===")
            print(f"Name: {blockchain_info.get('name')}")
            print(f"ID: {blockchain_info.get('id')}")
            print(f"Symbol: {blockchain_info.get('symbol')}")
            print(f"Explorer URL: {blockchain_info.get('explorerUrl')}")
            return blockchain_info
        else:
            logger.error(f"Failed to fetch Solana blockchain information: {blockchain_info}")
            print("\n=== Failed to fetch Solana blockchain information ===")
            return None
    
    async def get_hot_pairs(self, limit: int = 10):
        """
        Get hot trading pairs on Solana
        
        Args:
            limit: Maximum number of pairs to return
        """
        logger.info(f"Fetching top {limit} hot pairs on Solana")
        hot_pairs = await self.solana_api.get_solana_hot_pairs(limit=limit)
        
        if hot_pairs:
            logger.info(f"Successfully fetched {len(hot_pairs)} hot pairs on Solana")
            print(f"\n=== Top {len(hot_pairs)} Hot Pairs on Solana ===")
            for i, pair in enumerate(hot_pairs, 1):
                print(f"{i}. {pair['pair_name']} on {pair['dex_platform']}")
                print(f"   Price: ${pair['price']}")
                print(f"   24h Change: {pair['price_change_24h']}%")
                print(f"   24h Volume: ${pair['volume_24h']}")
                print(f"   Liquidity: ${pair['liquidity']}")
                print(f"   Created: {pair['created_at']}")
                print(f"   Token: {pair['main_token']['name']} ({pair['main_token']['symbol']})")
                print(f"   Address: {pair['main_token']['address']}")
                print()
            
            # Generate a prompt for analyzing these hot pairs
            hot_pairs_prompt = get_solana_hot_pairs_prompt(limit=limit)
            logger.info("Generated hot pairs analysis prompt")
            
            return hot_pairs
        else:
            logger.error("Failed to fetch hot pairs on Solana")
            print("\n=== Failed to fetch hot pairs on Solana ===")
            return []
    
    async def get_gainers_and_losers(self, limit: int = 5):
        """
        Get top gainers and losers on Solana
        
        Args:
            limit: Maximum number of pairs to return for each category
        """
        logger.info(f"Fetching top {limit} gainers and losers on Solana")
        
        # Get gainers
        gainers = await self.solana_api.get_solana_gainers(limit=limit)
        
        if gainers:
            logger.info(f"Successfully fetched {len(gainers)} gainers on Solana")
            print(f"\n=== Top {len(gainers)} Gainers on Solana ===")
            for i, pair in enumerate(gainers, 1):
                print(f"{i}. {pair['pair_name']} on {pair['dex_platform']}")
                print(f"   Price: ${pair['price']}")
                print(f"   24h Change: {pair['price_change_24h']}%")
                print(f"   24h Volume: ${pair['volume_24h']}")
                print()
        else:
            logger.error("Failed to fetch gainers on Solana")
            print("\n=== Failed to fetch gainers on Solana ===")
        
        # Get losers
        losers = await self.solana_api.get_solana_losers(limit=limit)
        
        if losers:
            logger.info(f"Successfully fetched {len(losers)} losers on Solana")
            print(f"\n=== Top {len(losers)} Losers on Solana ===")
            for i, pair in enumerate(losers, 1):
                print(f"{i}. {pair['pair_name']} on {pair['dex_platform']}")
                print(f"   Price: ${pair['price']}")
                print(f"   24h Change: {pair['price_change_24h']}%")
                print(f"   24h Volume: ${pair['volume_24h']}")
                print()
        else:
            logger.error("Failed to fetch losers on Solana")
            print("\n=== Failed to fetch losers on Solana ===")
        
        return {"gainers": gainers, "losers": losers}
    
    async def get_new_tokens(self, max_age_hours: int = 24, limit: int = 10):
        """
        Get newly created tokens on Solana
        
        Args:
            max_age_hours: Maximum age of tokens to include (in hours)
            limit: Maximum number of tokens to return
        """
        logger.info(f"Fetching {limit} new tokens on Solana created in the last {max_age_hours} hours")
        new_tokens = await self.solana_api.get_solana_new_tokens(max_age_hours=max_age_hours, limit=limit)
        
        if new_tokens:
            logger.info(f"Successfully fetched {len(new_tokens)} new tokens on Solana")
            print(f"\n=== New Tokens on Solana (last {max_age_hours} hours) ===")
            for i, pair in enumerate(new_tokens, 1):
                print(f"{i}. {pair['main_token']['name']} ({pair['main_token']['symbol']})")
                print(f"   Pair: {pair['pair_name']} on {pair['dex_platform']}")
                print(f"   Price: ${pair['price']}")
                print(f"   Liquidity: ${pair['liquidity']}")
                print(f"   Created: {pair['created_at']}")
                print(f"   Address: {pair['main_token']['address']}")
                print()
            
            # Generate a prompt for analyzing these new tokens
            new_tokens_prompt = get_solana_new_tokens_prompt(max_age_hours=max_age_hours, limit=limit)
            logger.info("Generated new tokens analysis prompt")
            
            return new_tokens
        else:
            logger.error("Failed to fetch new tokens on Solana")
            print("\n=== Failed to fetch new tokens on Solana ===")
            return []
    
    async def analyze_token(self, token_address: str):
        """
        Analyze a specific Solana token
        
        Args:
            token_address: The address/mint of the token to analyze
        """
        logger.info(f"Analyzing Solana token: {token_address}")
        token_info = await self.solana_api.get_solana_token_info(token_address)
        
        if token_info:
            logger.info(f"Successfully fetched information for token: {token_info.get('symbol')}")
            print("\n=== Solana Token Analysis ===")
            print(f"Name: {token_info.get('name')}")
            print(f"Symbol: {token_info.get('symbol')}")
            print(f"Address: {token_info.get('address')}")
            print(f"Price: ${token_info.get('price')}")
            print(f"24h Change: {token_info.get('price_change_24h')}%")
            print(f"Liquidity: ${token_info.get('liquidity')}")
            print(f"24h Volume: ${token_info.get('volume_24h')}")
            print(f"Created: {token_info.get('created_at')}")
            print(f"Decimals: {token_info.get('decimals')}")
            
            # Generate a prompt for analyzing this token
            token_data: SolanaTokenData = {
                "name": token_info.get('name', 'Unknown'),
                "symbol": token_info.get('symbol', 'UNKNOWN'),
                "address": token_info.get('address', ''),
                "mint": token_info.get('mint', ''),
                "price": token_info.get('price'),
                "price_change_24h": token_info.get('price_change_24h'),
                "liquidity": token_info.get('liquidity'),
                "volume_24h": token_info.get('volume_24h'),
                "market_cap": token_info.get('market_cap'),
                "created_at": token_info.get('created_at'),
                "total_supply": token_info.get('total_supply'),
                "decimals": token_info.get('decimals'),
                "holder_count": token_info.get('holder_count')
            }
            
            token_analysis_prompt = get_solana_token_analysis_prompt(token_data)
            logger.info("Generated token analysis prompt")
            
            return token_info
        else:
            logger.error(f"Failed to fetch information for token: {token_address}")
            print("\n=== Failed to fetch token information ===")
            return None

async def main():
    """Main function to run the Solana DexTools Demo"""
    # Load API key from environment variable
    api_key = os.getenv("DEXTOOLS_API_KEY")
    if not api_key:
        logger.error("DEXTOOLS_API_KEY environment variable not set")
        print("Error: DEXTOOLS_API_KEY environment variable not set")
        return
    
    # Initialize the demo
    demo = SolanaDexToolsDemo(api_key=api_key)
    logger.info("Starting Solana DexTools Demo")
    
    # Get Solana blockchain information
    await demo.get_solana_info()
    
    # Get hot pairs on Solana
    await demo.get_hot_pairs(limit=5)
    
    # Get gainers and losers on Solana
    await demo.get_gainers_and_losers(limit=3)
    
    # Get new tokens on Solana
    new_tokens = await demo.get_new_tokens(max_age_hours=48, limit=5)
    
    # If we found any new tokens, analyze the first one
    if new_tokens and len(new_tokens) > 0:
        first_token_address = new_tokens[0]['main_token']['address']
        logger.info(f"Analyzing first new token: {first_token_address}")
        await demo.analyze_token(first_token_address)
    
    logger.info("Solana DexTools Demo completed")

if __name__ == "__main__":
    asyncio.run(main()) 