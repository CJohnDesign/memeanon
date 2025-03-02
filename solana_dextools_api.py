#!/usr/bin/env python3
"""
Solana DexTools API Utility

This file provides utility functions for making Solana-specific API calls to the DexTools API.
It includes functions for fetching Solana token data, hot pairs, and new tokens.
"""

import os
import time
import logging
import json
from typing import Dict, List, Any, Optional, TypedDict, Union
from datetime import datetime, timezone, timedelta
import asyncio

# Import the AsyncDextoolsAPIV2 client - Fixed import path
from dextools_python import AsyncDextoolsAPIV2

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("solana_dextools_api.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('solana_dextools_api')

class SolanaTokenInfo(TypedDict):
    """TypedDict for Solana token information"""
    name: str
    symbol: str
    address: str
    mint: str
    price: Optional[float]
    price_change_24h: Optional[float]
    liquidity: Optional[float]
    volume_24h: Optional[float]
    market_cap: Optional[float]
    created_at: Optional[str]
    total_supply: Optional[int]
    decimals: Optional[int]
    holder_count: Optional[int]

class SolanaPairInfo(TypedDict):
    """TypedDict for Solana trading pair information"""
    pair_name: str
    dex_platform: str
    price: Optional[float]
    volume_24h: Optional[float]
    liquidity: Optional[float]
    price_change_24h: Optional[float]
    created_at: Optional[str]
    main_token: SolanaTokenInfo
    side_token: SolanaTokenInfo

class SolanaDexToolsAPI:
    """Utility class for making Solana-specific API calls to the DexTools API"""
    
    def __init__(self, api_key: str, plan: str = "trial", max_retries: int = 3, retry_delay: int = 2):
        """
        Initialize the Solana DexTools API utility
        
        Args:
            api_key: DexTools API key
            plan: API plan to use (default: "trial")
            max_retries: Maximum number of retries for API calls
            retry_delay: Initial delay between retries in seconds
        """
        self.api_key = api_key
        self.plan = plan
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.chain_id = "solana"  # Solana chain ID for DexTools API
        
        logger.info(f"Initializing Solana DexTools API with plan: {plan}")
        
        # Initialize the client immediately instead of lazily
        self.client = AsyncDextoolsAPIV2(api_key=self.api_key, plan=self.plan)
        logger.info("AsyncDextoolsAPIV2 client initialized")
    
    async def initialize(self):
        """Initialize the AsyncDextoolsAPIV2 client"""
        # This method is kept for backward compatibility but is now a no-op
        # since we initialize the client in __init__
        if not self.client:
            logger.info(f"Creating AsyncDextoolsAPIV2 client with {self.plan} plan")
            self.client = AsyncDextoolsAPIV2(api_key=self.api_key, plan=self.plan)
            
    async def _make_api_call(self, api_func, retries: int = 3) -> Optional[Dict[str, Any]]:
        """
        Make an API call with retry logic
        
        Args:
            api_func: Function to call the API
            retries: Number of retries if the API call fails
            
        Returns:
            API response or None if all retries fail
        """
        max_attempts = retries + 1
        attempt = 1
        
        while attempt <= max_attempts:
            try:
                logger.info(f"Making API call to {api_func.__name__} (attempt {attempt}/{max_attempts})")
                response = await api_func()
                return response
            except Exception as e:
                logger.error(f"Error in API call to {api_func.__name__}: {str(e)}")
                
                if attempt < max_attempts:
                    # Exponential backoff: 2^attempt seconds
                    wait_time = 2 ** attempt
                    logger.info(f"Retrying in {wait_time}s... ({attempt}/{retries})")
                    await asyncio.sleep(wait_time)
                    attempt += 1
                else:
                    logger.error(f"All {retries} retries failed for API call to {api_func.__name__}")
                    return None
    
    def _extract_pair_info(self, pair_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Extract and format pair information from API response
        
        Args:
            pair_data: Raw pair data from API response
            
        Returns:
            Formatted pair information or None if extraction fails
        """
        try:
            # Extract token information
            main_token = pair_data.get("mainToken", {})
            side_token = pair_data.get("sideToken", {})
            
            if not main_token or not side_token:
                logger.warning("Missing token information in pair data")
                return None
            
            # Extract basic pair information
            pair_info = {
                "pair_name": f"{main_token.get('symbol', 'Unknown')}/{side_token.get('symbol', 'Unknown')}",
                "dex_platform": pair_data.get("dex", {}).get("name", "Unknown"),
                "price": pair_data.get("price"),
                "volume_24h": pair_data.get("volume24h"),
                "liquidity": pair_data.get("liquidity"),
                "price_change_24h": pair_data.get("priceChange24h"),
                "created_at": pair_data.get("creationTime"),
                
                # Main token information
                "name": main_token.get("name", "Unknown"),
                "symbol": main_token.get("symbol", "Unknown"),
                "address": main_token.get("address", "Unknown"),
                "tokenAddress": main_token.get("address", "Unknown"),  # For compatibility
                "decimals": main_token.get("decimals"),
                
                # Additional information from the pair
                "side_token_symbol": side_token.get("symbol", "Unknown"),
                "side_token_address": side_token.get("address", "Unknown"),
            }
            
            return pair_info
            
        except Exception as e:
            logger.error(f"Error extracting pair info: {str(e)}")
            return None
    
    async def get_solana_blockchains(self):
        """
        Get information about the Solana blockchain from DexTools API
        
        Returns:
            Information about the Solana blockchain
        """
        logger.info("Fetching Solana blockchain information")
        response = await self._make_api_call(self.client.get_blockchains)
        
        # Check if response is a dictionary with results
        if isinstance(response, dict) and "results" in response.get("data", {}):
            # Look for Solana in the results
            for blockchain in response["data"]["results"]:
                if blockchain.get("id") == self.chain_id:
                    logger.info("Successfully fetched Solana blockchain information")
                    return blockchain
            
            # If we've gone through all pages and still haven't found Solana
            logger.warning("Solana blockchain information not found in response")
            return response
        else:
            logger.warning("Unexpected response format from get_blockchains")
            return response
    
    async def get_solana_hot_pairs(self, limit: int = 10, retries: int = 3) -> List[Dict[str, Any]]:
        """
        Get hot pairs on Solana
        
        Note: The API does not support the limit parameter directly.
        We fetch all results and limit them after receiving.
        
        Args:
            limit: Maximum number of pairs to return
            retries: Number of retries if the API call fails
            
        Returns:
            List of hot pairs on Solana
        """
        logger.info(f"Fetching hot pairs on Solana")
        
        try:
            # Create a function that doesn't take retries parameter
            async def api_call():
                return await self.client.get_ranking_hotpools("solana")
                
            response = await self._make_api_call(
                api_call,
                retries=retries
            )
            
            # Debug: Print response format
            logger.info(f"Response type: {type(response)}")
            if response:
                logger.info(f"Response keys: {response.keys() if isinstance(response, dict) else 'Not a dict'}")
                if isinstance(response, dict) and "data" in response:
                    logger.info(f"Data keys: {response['data'].keys() if isinstance(response['data'], dict) else 'Data not a dict'}")
                    if isinstance(response['data'], dict) and "results" in response['data']:
                        logger.info(f"Results type: {type(response['data']['results'])}")
                        logger.info(f"Results length: {len(response['data']['results'])}")
                        if response['data']['results'] and len(response['data']['results']) > 0:
                            logger.info(f"First result keys: {response['data']['results'][0].keys() if isinstance(response['data']['results'][0], dict) else 'First result not a dict'}")
            
            if response and isinstance(response, dict) and "data" in response:
                pairs = []
                for pair_data in response["data"].get("results", [])[:limit]:
                    try:
                        pair_info = self._extract_pair_info(pair_data)
                        if pair_info:
                            pairs.append(pair_info)
                    except Exception as e:
                        logger.error(f"Error extracting pair info: {str(e)}")
                
                logger.info(f"Successfully fetched {len(pairs)} hot pairs on Solana")
                return pairs
            else:
                logger.warning(f"Unexpected response format when fetching hot pairs on Solana")
                return []
                
        except Exception as e:
            logger.error(f"Error fetching hot pairs on Solana: {str(e)}")
            return []
    
    async def get_solana_gainers(self, limit: int = 10, retries: int = 3) -> List[Dict[str, Any]]:
        """
        Get the top gainers on Solana
        
        Note: The API does not support the limit parameter directly.
        We fetch all results and limit them after receiving.
        
        Args:
            limit: Maximum number of pairs to return
            retries: Number of retries if the API call fails
            
        Returns:
            List of top gainer pairs on Solana
        """
        logger.info(f"Fetching gainers on Solana")
        
        try:
            # Create a function that doesn't take retries parameter
            async def api_call():
                return await self.client.get_ranking_gainers("solana")
                
            response = await self._make_api_call(
                api_call,
                retries=retries
            )
            
            if response and isinstance(response, dict) and "data" in response:
                pairs = []
                for pair_data in response["data"].get("results", [])[:limit]:
                    try:
                        pair_info = self._extract_pair_info(pair_data)
                        if pair_info:
                            pairs.append(pair_info)
                    except Exception as e:
                        logger.error(f"Error extracting pair info: {str(e)}")
                
                logger.info(f"Successfully fetched {len(pairs)} gainers on Solana")
                return pairs
            else:
                logger.warning(f"Unexpected response format when fetching gainers on Solana")
                return []
                
        except Exception as e:
            logger.error(f"Error fetching gainers on Solana: {str(e)}")
            return []
    
    async def get_solana_losers(self, limit: int = 10, retries: int = 3) -> List[Dict[str, Any]]:
        """
        Get the top losers on Solana
        
        Note: The API does not support the limit parameter directly.
        We fetch all results and limit them after receiving.
        
        Args:
            limit: Maximum number of pairs to return
            retries: Number of retries if the API call fails
            
        Returns:
            List of top loser pairs on Solana
        """
        logger.info(f"Fetching losers on Solana")
        
        try:
            # Create a function that doesn't take retries parameter
            async def api_call():
                return await self.client.get_ranking_losers("solana")
                
            response = await self._make_api_call(
                api_call,
                retries=retries
            )
            
            if response and isinstance(response, dict) and "data" in response:
                pairs = []
                for pair_data in response["data"].get("results", [])[:limit]:
                    try:
                        pair_info = self._extract_pair_info(pair_data)
                        if pair_info:
                            pairs.append(pair_info)
                    except Exception as e:
                        logger.error(f"Error extracting pair info: {str(e)}")
                
                logger.info(f"Successfully fetched {len(pairs)} losers on Solana")
                return pairs
            else:
                logger.warning(f"Unexpected response format when fetching losers on Solana")
                return []
                
        except Exception as e:
            logger.error(f"Error fetching losers on Solana: {str(e)}")
            return []
    
    async def get_solana_new_tokens(self, max_age_hours: int = 24, limit: int = 10) -> List[SolanaPairInfo]:
        """
        Get newly created tokens on Solana
        
        Args:
            max_age_hours: Maximum age of tokens to include (in hours)
            limit: Maximum number of tokens to return
            
        Returns:
            List of newly created tokens on Solana
        """
        logger.info(f"Fetching {limit} new tokens on Solana created in the last {max_age_hours} hours")
        
        # Calculate date range
        to_date = datetime.now(timezone.utc)
        from_date = to_date - timedelta(hours=max_age_hours)
        
        # Format dates as ISO 8601 strings with timezone
        from_date_str = from_date.isoformat()
        to_date_str = to_date.isoformat()
        
        logger.info(f"Date range: {from_date_str} to {to_date_str}")
        
        response = await self._make_api_call(
            self.client.get_pools,
            chain=self.chain_id,
            from_date=from_date_str,
            to_date=to_date_str,
            limit=limit,
            sort="created"  # Sort by creation time
        )
        
        if isinstance(response, dict) and "data" in response:
            pairs = []
            for pair_data in response["data"]:
                try:
                    # Extract and format pair information (similar to hot pairs)
                    main_token = pair_data.get("mainToken", {})
                    side_token = pair_data.get("sideToken", {})
                    
                    pair_info: SolanaPairInfo = {
                        "pair_name": f"{main_token.get('symbol', 'Unknown')}/{side_token.get('symbol', 'Unknown')}",
                        "dex_platform": pair_data.get("dex", {}).get("name", "Unknown"),
                        "price": pair_data.get("price"),
                        "volume_24h": pair_data.get("volume24h"),
                        "liquidity": pair_data.get("liquidity"),
                        "price_change_24h": pair_data.get("priceChange24h"),
                        "created_at": pair_data.get("creationTime"),
                        "main_token": {
                            "name": main_token.get("name", "Unknown"),
                            "symbol": main_token.get("symbol", "Unknown"),
                            "address": main_token.get("address", "Unknown"),
                            "mint": main_token.get("address", "Unknown"),
                            "price": pair_data.get("price"),
                            "price_change_24h": pair_data.get("priceChange24h"),
                            "liquidity": pair_data.get("liquidity"),
                            "volume_24h": pair_data.get("volume24h"),
                            "market_cap": None,
                            "created_at": pair_data.get("creationTime"),
                            "total_supply": None,
                            "decimals": main_token.get("decimals"),
                            "holder_count": None
                        },
                        "side_token": {
                            "name": side_token.get("name", "Unknown"),
                            "symbol": side_token.get("symbol", "Unknown"),
                            "address": side_token.get("address", "Unknown"),
                            "mint": side_token.get("address", "Unknown"),
                            "price": None,
                            "price_change_24h": None,
                            "liquidity": None,
                            "volume_24h": None,
                            "market_cap": None,
                            "created_at": None,
                            "total_supply": None,
                            "decimals": side_token.get("decimals"),
                            "holder_count": None
                        }
                    }
                    pairs.append(pair_info)
                except Exception as e:
                    logger.error(f"Error processing new token data: {str(e)}")
            
            logger.info(f"Successfully fetched {len(pairs)} new tokens on Solana")
            return pairs
        
        logger.warning("Failed to fetch new tokens on Solana")
        return []
    
    async def get_solana_token_info(self, token_address: str) -> Optional[SolanaTokenInfo]:
        """
        Get detailed information about a specific Solana token
        
        Args:
            token_address: The address/mint of the token
            
        Returns:
            Detailed information about the token or None if not found
        """
        logger.info(f"Fetching information for Solana token: {token_address}")
        
        # First, try to get the token pair information
        response = await self._make_api_call(
            self.client.get_pool_by_token,
            chain=self.chain_id,
            token=token_address
        )
        
        if isinstance(response, dict) and "data" in response:
            try:
                pair_data = response["data"]
                main_token = pair_data.get("mainToken", {})
                
                # Check if this is the token we're looking for
                if main_token.get("address") == token_address:
                    token_info: SolanaTokenInfo = {
                        "name": main_token.get("name", "Unknown"),
                        "symbol": main_token.get("symbol", "Unknown"),
                        "address": main_token.get("address", "Unknown"),
                        "mint": main_token.get("address", "Unknown"),  # In Solana, address is the mint
                        "price": pair_data.get("price"),
                        "price_change_24h": pair_data.get("priceChange24h"),
                        "liquidity": pair_data.get("liquidity"),
                        "volume_24h": pair_data.get("volume24h"),
                        "market_cap": None,  # Not provided in this endpoint
                        "created_at": pair_data.get("creationTime"),
                        "total_supply": None,  # Not provided in this endpoint
                        "decimals": main_token.get("decimals"),
                        "holder_count": None  # Not provided in this endpoint
                    }
                    
                    logger.info(f"Successfully fetched information for Solana token: {token_address}")
                    return token_info
            except Exception as e:
                logger.error(f"Error processing token data: {str(e)}")
        
        logger.warning(f"Failed to fetch information for Solana token: {token_address}")
        return None
    
    async def get_recent_solana_tokens(
        self, 
        limit: int = 10, 
        min_liquidity: float = 5000.0,
        from_date: Optional[int] = None,
        retries: int = 3
    ) -> List[Dict[str, Any]]:
        """
        Get recently created tokens on Solana
        
        Args:
            limit: Maximum number of tokens to return
            min_liquidity: Minimum liquidity in USD
            from_date: Timestamp in milliseconds to fetch tokens created after this date
            retries: Number of retries if the API call fails
            
        Returns:
            List of recently created tokens on Solana
        """
        logger.info(f"Fetching recent tokens on Solana (limit: {limit}, min liquidity: ${min_liquidity})")
        
        # Calculate from_ and to timestamps
        to_timestamp = int(datetime.now().timestamp() * 1000)  # Current time in milliseconds
        
        # If from_date is not provided, default to 48 hours ago
        if from_date is None:
            from_timestamp = int((datetime.now() - timedelta(hours=48)).timestamp() * 1000)
        else:
            from_timestamp = from_date
        
        logger.info(f"Fetching tokens created between {datetime.fromtimestamp(from_timestamp/1000)} and {datetime.fromtimestamp(to_timestamp/1000)}")
        
        # Prepare parameters for the API call
        params = {
            "chain": "solana",
            "from_": from_timestamp,
            "to": to_timestamp,
            "sort": "creationTime",
            "order": "desc"  # Most recent first
        }
        
        try:
            # Call the get_pools endpoint to fetch recent tokens
            # Create a function that doesn't take retries parameter
            async def api_call():
                return await self.client.get_pools(**params)
                
            response = await self._make_api_call(
                api_call,
                retries=retries
            )
            
            if response and isinstance(response, dict) and "data" in response:
                # Filter and process the results
                recent_tokens = []
                count = 0
                
                for pool_data in response["data"].get("results", []):
                    # Skip if we've reached the limit
                    if count >= limit:
                        break
                    
                    try:
                        # Extract token data
                        token_info = self._extract_pair_info(pool_data)
                        
                        # Apply filters
                        if token_info:
                            # Check liquidity
                            if token_info.get("liquidity", 0) < min_liquidity:
                                continue
                            
                            # Add to results
                            recent_tokens.append(token_info)
                            count += 1
                            
                    except Exception as e:
                        logger.error(f"Error processing token data: {str(e)}")
                
                logger.info(f"Successfully fetched {len(recent_tokens)} recent tokens on Solana")
                return recent_tokens
            else:
                logger.warning(f"Unexpected response format when fetching recent tokens on Solana")
                return []
                
        except Exception as e:
            logger.error(f"Error fetching recent tokens on Solana: {str(e)}")
            return []

# Example usage
async def main():
    # Load API key from environment variable
    api_key = os.getenv("DEXTOOLS_API_KEY")
    if not api_key:
        logger.error("DEXTOOLS_API_KEY environment variable not set")
        return
    
    # Initialize the Solana DexTools API
    solana_api = SolanaDexToolsAPI(api_key=api_key, plan="trial")
    
    # Get Solana blockchain information
    blockchain_info = await solana_api.get_solana_blockchains()
    print("Solana Blockchain Info:")
    print(json.dumps(blockchain_info, indent=2))
    
    # Get hot pairs on Solana
    hot_pairs = await solana_api.get_solana_hot_pairs(limit=5)
    print("\nHot Pairs on Solana:")
    for pair in hot_pairs:
        print(f"- {pair['pair_name']} on {pair['dex_platform']}: ${pair['price']} (24h change: {pair['price_change_24h']}%)")
    
    # Get new tokens on Solana
    new_tokens = await solana_api.get_solana_new_tokens(max_age_hours=48, limit=5)
    print("\nNew Tokens on Solana (last 48 hours):")
    for pair in new_tokens:
        print(f"- {pair['main_token']['name']} ({pair['main_token']['symbol']}): Created at {pair['created_at']}")

if __name__ == "__main__":
    asyncio.run(main()) 