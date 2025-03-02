#!/usr/bin/env python3
"""
DexTools API Demo v2 - Using the dextools-python library
This script demonstrates connectivity with the DexTools API
to fetch cryptocurrency token data and display it in the console.
"""

import os
import json
import time
import logging
import asyncio
from typing import TypedDict, List, Dict, Any, Optional, Union
from dotenv import load_dotenv
from dextools_python import AsyncDextoolsAPIV2

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('dextools_v2_demo')

# Load environment variables
load_dotenv()

# Type definitions
class TokenData(TypedDict):
    id: str
    name: str
    symbol: str
    address: str
    chain: str
    price: Optional[float]
    volume24h: Optional[float]

class ApiResponse(TypedDict):
    success: bool
    data: Any
    message: Optional[str]

class DexToolsDemo:
    """Demo class for interacting with the DexTools API using dextools-python library"""
    
    def __init__(self):
        """Initialize the DexTools API client"""
        self.api_key = os.getenv('DEXTOOLS_API_KEY')
        if not self.api_key:
            logger.error("API key not found. Please set DEXTOOLS_API_KEY in .env file")
            raise ValueError("API key not found")
            
        logger.info("Initializing DexTools API client")
        logger.info(f"Using API key: {self.api_key[:5]}...{self.api_key[-5:] if len(self.api_key) > 10 else ''}")
        
        # Initialize the client with the "trial" plan which was found to work
        self.client = AsyncDextoolsAPIV2(api_key=self.api_key, plan="trial")
        logger.info("DexTools API client initialized with 'trial' plan")
    
    async def get_blockchains(self) -> Dict[str, Any]:
        """
        Get list of supported blockchains
        
        Returns:
            Dict containing supported blockchains
        """
        logger.info("Fetching supported blockchains")
        try:
            blockchains = await self.client.get_blockchains()
            return blockchains
        except Exception as e:
            logger.error(f"Failed to fetch blockchains: {str(e)}")
            raise
    
    async def get_hot_pairs(self, chain: str = 'ether') -> Dict[str, Any]:
        """
        Get hot pairs for a specific chain
        
        Args:
            chain: Chain ID (default: ether)
            
        Returns:
            Dict containing hot pairs
        """
        logger.info(f"Fetching hot pairs for chain: {chain}")
        try:
            hot_pairs = await self.client.get_ranking_hotpools(chain)
            return hot_pairs
        except Exception as e:
            logger.error(f"Failed to fetch hot pairs for chain {chain}: {str(e)}")
            raise
    
    async def get_pair_info(self, chain: str, pair_address: str) -> Dict[str, Any]:
        """
        Get detailed information about a specific trading pair
        
        Args:
            chain: Chain ID (e.g., 'ether', 'bsc')
            pair_address: Address of the pair to query
            
        Returns:
            Dict containing pair details
        """
        logger.info(f"Fetching info for pair: {pair_address} on chain: {chain}")
        try:
            pair_info = await self.client.get_pool(chain, pair_address)
            return pair_info
        except Exception as e:
            logger.error(f"Failed to fetch pair info for {pair_address} on chain {chain}: {str(e)}")
            raise
    
    async def get_token_info(self, chain: str, token_address: str) -> Dict[str, Any]:
        """
        Get detailed information about a specific token
        
        Args:
            chain: Chain ID (e.g., 'ether', 'bsc')
            token_address: Address of the token to query
            
        Returns:
            Dict containing token details
        """
        logger.info(f"Fetching info for token: {token_address} on chain: {chain}")
        try:
            token_info = await self.client.get_token(chain, token_address)
            return token_info
        except Exception as e:
            logger.error(f"Failed to fetch token info for {token_address} on chain {chain}: {str(e)}")
            raise
    
    async def get_gainers(self, chain: str = 'ether') -> Dict[str, Any]:
        """
        Get top gainers on a specific chain
        
        Args:
            chain: Chain ID (default: ether)
            
        Returns:
            Dict containing top gainers
        """
        logger.info(f"Fetching top gainers for chain: {chain}")
        try:
            gainers = await self.client.get_ranking_gainers(chain)
            return gainers
        except Exception as e:
            logger.error(f"Failed to fetch top gainers for chain {chain}: {str(e)}")
            raise
    
    async def get_losers(self, chain: str = 'ether') -> Dict[str, Any]:
        """
        Get top losers on a specific chain
        
        Args:
            chain: Chain ID (default: ether)
            
        Returns:
            Dict containing top losers
        """
        logger.info(f"Fetching top losers for chain: {chain}")
        try:
            losers = await self.client.get_ranking_losers(chain)
            return losers
        except Exception as e:
            logger.error(f"Failed to fetch top losers for chain {chain}: {str(e)}")
            raise
    
    async def get_recent_pools(self, chain: str = 'ether', limit: int = 10) -> Dict[str, Any]:
        """
        Get recently created pools on a specific chain
        
        Args:
            chain: Chain ID (default: ether)
            limit: Number of pools to retrieve (default: 10)
            
        Returns:
            Dict containing recent pools
        """
        logger.info(f"Fetching {limit} recent pools for chain: {chain}")
        try:
            # Get current time in milliseconds
            current_time = int(time.time() * 1000)
            # Get time 30 days ago in milliseconds
            thirty_days_ago = current_time - (30 * 24 * 60 * 60 * 1000)
            
            # Format dates as ISO strings with timezone
            from datetime import datetime, timezone
            
            # Convert milliseconds to ISO 8601 format with timezone
            from_date = datetime.fromtimestamp(thirty_days_ago / 1000, tz=timezone.utc).isoformat()
            to_date = datetime.fromtimestamp(current_time / 1000, tz=timezone.utc).isoformat()
            
            logger.info(f"Date range: from {from_date} to {to_date}")
            
            # Add retry logic with exponential backoff for rate limiting
            max_retries = 3
            retry_delay = 2  # Initial delay in seconds
            
            for retry in range(max_retries):
                try:
                    recent_pools = await self.client.get_pools(
                        chain, 
                        from_=from_date, 
                        to=to_date, 
                        order="desc", 
                        sort="creationTime", 
                        pageSize=limit
                    )
                    
                    # Check if we got a rate limit response
                    if isinstance(recent_pools, dict) and recent_pools.get("message") == "Too Many Requests":
                        if retry < max_retries - 1:
                            wait_time = retry_delay * (2 ** retry)
                            logger.warning(f"Rate limited. Retrying in {wait_time} seconds (attempt {retry + 1}/{max_retries})")
                            await asyncio.sleep(wait_time)
                            continue
                        else:
                            logger.error("Maximum retries reached for rate limiting")
                    
                    return recent_pools
                    
                except Exception as e:
                    if retry < max_retries - 1:
                        wait_time = retry_delay * (2 ** retry)
                        logger.warning(f"Request failed. Retrying in {wait_time} seconds (attempt {retry + 1}/{max_retries}): {str(e)}")
                        await asyncio.sleep(wait_time)
                    else:
                        logger.error(f"Maximum retries reached: {str(e)}")
                        raise
            
            # If we get here, all retries failed
            return {"error": "Maximum retries reached", "message": "Failed to fetch recent pools after multiple attempts"}
            
        except Exception as e:
            logger.error(f"Failed to fetch recent pools for chain {chain}: {str(e)}")
            raise
    
    async def get_pair_price(self, chain: str, pair_address: str) -> Dict[str, Any]:
        """
        Get price information for a specific pair
        
        Args:
            chain: Chain ID (e.g., 'ether', 'bsc')
            pair_address: Address of the pair to query
            
        Returns:
            Dict containing price information
        """
        logger.info(f"Fetching price for pair: {pair_address} on chain: {chain}")
        try:
            price_info = await self.client.get_pool_price(chain, pair_address)
            return price_info
        except Exception as e:
            logger.error(f"Failed to fetch price for {pair_address} on chain {chain}: {str(e)}")
            raise

def pretty_print_json(data: Dict[str, Any]) -> None:
    """Print JSON data in a readable format"""
    print(json.dumps(data, indent=2))

async def run_demo() -> None:
    """Main function to run the DexTools API demo"""
    logger.info("Starting DexTools API Demo v2...")
    
    try:
        # Initialize API client
        demo = DexToolsDemo()
        
        # Step 1: Get supported blockchains
        logger.info("Step 1: Fetching supported blockchains")
        try:
            blockchains = await demo.get_blockchains()
            print("\n=== Supported Blockchains ===")
            pretty_print_json(blockchains)
        except Exception as e:
            logger.error(f"Failed to fetch blockchains: {str(e)}")
            logger.info("Continuing with other endpoints...")
        
        # Step 2: Get hot pairs for Ethereum
        logger.info("Step 2: Fetching hot pairs for Ethereum")
        try:
            hot_pairs = await demo.get_hot_pairs('ether')
            print("\n=== Hot Ethereum Pairs ===")
            pretty_print_json(hot_pairs)
            
            # If we have pairs, get details for the first one
            if hot_pairs and isinstance(hot_pairs, dict) and hot_pairs.get('data') and len(hot_pairs['data']) > 0:
                first_pair = hot_pairs['data'][0]
                pair_address = first_pair.get('poolAddress')
                
                if pair_address:
                    logger.info(f"Selected pair for detailed analysis: {pair_address}")
                    
                    # Step 3: Get detailed info for this pair
                    logger.info("Step 3: Fetching detailed pair info")
                    try:
                        pair_info = await demo.get_pair_info('ether', pair_address)
                        print(f"\n=== Pair Info for {pair_address} ===")
                        pretty_print_json(pair_info)
                        
                        # Step 4: Get price info for this pair
                        logger.info("Step 4: Fetching price info for pair")
                        try:
                            price_info = await demo.get_pair_price('ether', pair_address)
                            print(f"\n=== Price Info for {pair_address} ===")
                            pretty_print_json(price_info)
                        except Exception as e:
                            logger.error(f"Failed to fetch price info: {str(e)}")
                    except Exception as e:
                        logger.error(f"Failed to fetch pair info: {str(e)}")
            else:
                logger.warning("No hot pairs found or API returned an error")
        except Exception as e:
            logger.error(f"Failed to fetch hot pairs: {str(e)}")
        
        # Step 5: Get top gainers for Ethereum
        logger.info("Step 5: Fetching top gainers for Ethereum")
        try:
            gainers = await demo.get_gainers('ether')
            print("\n=== Top Ethereum Gainers ===")
            pretty_print_json(gainers)
        except Exception as e:
            logger.error(f"Failed to fetch top gainers: {str(e)}")
        
        # Step 6: Get top losers for Ethereum
        logger.info("Step 6: Fetching top losers for Ethereum")
        try:
            losers = await demo.get_losers('ether')
            print("\n=== Top Ethereum Losers ===")
            pretty_print_json(losers)
        except Exception as e:
            logger.error(f"Failed to fetch top losers: {str(e)}")
        
        # Step 7: Get recent pools for Ethereum
        logger.info("Step 7: Fetching recent pools for Ethereum")
        try:
            recent_pools = await demo.get_recent_pools('ether', 5)
            print("\n=== Recent Ethereum Pools ===")
            pretty_print_json(recent_pools)
            
            # If we have pools, get token info for the first one
            if recent_pools and isinstance(recent_pools, dict) and recent_pools.get('data') and len(recent_pools['data']) > 0:
                first_pool = recent_pools['data'][0]
                token_address = first_pool.get('token0', {}).get('address')
                
                if token_address:
                    logger.info(f"Selected token for detailed analysis: {token_address}")
                    
                    # Step 8: Get detailed info for this token
                    logger.info("Step 8: Fetching detailed token info")
                    try:
                        token_info = await demo.get_token_info('ether', token_address)
                        print(f"\n=== Token Info for {token_address} ===")
                        pretty_print_json(token_info)
                    except Exception as e:
                        logger.error(f"Failed to fetch token info: {str(e)}")
        except Exception as e:
            logger.error(f"Failed to fetch recent pools: {str(e)}")
        
        logger.info("Demo completed.")
        
    except Exception as e:
        logger.error(f"Demo failed: {str(e)}", exc_info=True)
    finally:
        # Close the client session
        if hasattr(demo, 'client') and hasattr(demo.client, 'close'):
            await demo.client.close()

if __name__ == "__main__":
    asyncio.run(run_demo()) 