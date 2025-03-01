#!/usr/bin/env python3
"""
DexTools API Demo - Python Implementation
This script demonstrates basic connectivity with the DexTools API
to fetch cryptocurrency token data from Solana and display it in the console.
"""

import os
import json
import time
import logging
from typing import TypedDict, List, Dict, Any, Optional
import requests
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('dextools_demo')

# Load environment variables
load_dotenv()

# Type definitions
class PoolData(TypedDict):
    id: str
    name: str
    symbol: str
    created: int
    createdStr: str
    verified: bool
    scam: bool
    volume24h: float

class ApiResponse(TypedDict):
    success: bool
    data: List[PoolData]
    message: Optional[str]

class PoolInfoData(TypedDict):
    address: str
    name: str
    symbol: str
    decimals: int
    totalSupply: str
    holders: int
    transactions: int
    price: float
    liquidity: float
    volume24h: float
    priceChange24h: float

class PoolInfoResponse(TypedDict):
    success: bool
    data: PoolInfoData
    message: Optional[str]

class PricePoint(TypedDict):
    timestamp: int
    price: float
    volume: float

class PriceDataResponse(TypedDict):
    success: bool
    data: List[PricePoint]
    message: Optional[str]

class DexToolsAPI:
    """Client for interacting with the DexTools API"""
    
    def __init__(self):
        """Initialize the DexTools API client"""
        self.api_key = os.getenv('DEXTOOLS_API_KEY')
        if not self.api_key:
            logger.error("API key not found. Please set DEXTOOLS_API_KEY in .env file")
            raise ValueError("API key not found")
            
        self.base_url = 'https://api.dextools.io/v1'
        self.headers = {
            'X-API-Key': self.api_key,
            'Accept': 'application/json'
        }
        logger.info("DexTools API client initialized")
    
    def get_recent_solana_pools(self, limit: int = 10) -> ApiResponse:
        """
        Fetch recently created pools on Solana
        
        Args:
            limit: Number of pools to retrieve (default: 10)
            
        Returns:
            ApiResponse containing list of recent pools
        """
        logger.info(f"Fetching {limit} recent Solana pools")
        
        try:
            response = requests.get(
                f"{self.base_url}/pool/solana/created",
                headers=self.headers,
                params={
                    'limit': limit,
                    'sort': 'created'
                }
            )
            response.raise_for_status()
            data = response.json()
            
            logger.info(f"Successfully retrieved {len(data.get('data', []))} Solana pools")
            return data
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching recent Solana pools: {str(e)}")
            if hasattr(e, 'response') and e.response:
                logger.error(f"Response status: {e.response.status_code}")
                logger.error(f"Response data: {e.response.text}")
            raise
    
    def get_pool_info(self, pool_address: str) -> PoolInfoResponse:
        """
        Get detailed information about a specific pool
        
        Args:
            pool_address: Address of the pool to query
            
        Returns:
            PoolInfoResponse containing pool details
        """
        logger.info(f"Fetching info for pool: {pool_address}")
        
        try:
            response = requests.get(
                f"{self.base_url}/pool/solana/{pool_address}/info",
                headers=self.headers
            )
            response.raise_for_status()
            data = response.json()
            
            logger.info(f"Successfully retrieved info for pool: {pool_address}")
            return data
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching pool info for {pool_address}: {str(e)}")
            raise
    
    def get_pool_price_data(self, pool_address: str, hours: int = 24) -> PriceDataResponse:
        """
        Get price data for a specific pool
        
        Args:
            pool_address: Address of the pool to query
            hours: Number of hours of historical data to retrieve (default: 24)
            
        Returns:
            PriceDataResponse containing historical price data
        """
        logger.info(f"Fetching {hours}h price data for pool: {pool_address}")
        
        current_time = int(time.time())
        from_time = current_time - (hours * 3600)
        
        try:
            response = requests.get(
                f"{self.base_url}/pool/solana/{pool_address}/prices",
                headers=self.headers,
                params={
                    'from': from_time,
                    'to': current_time
                }
            )
            response.raise_for_status()
            data = response.json()
            
            logger.info(f"Successfully retrieved price data for pool: {pool_address}")
            return data
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching price data for {pool_address}: {str(e)}")
            raise

def pretty_print_json(data: Dict[str, Any]) -> None:
    """Print JSON data in a readable format"""
    print(json.dumps(data, indent=2))

def run_demo() -> None:
    """Main function to run the DexTools API demo"""
    logger.info("Starting DexTools API Demo...")
    
    try:
        # Initialize API client
        api = DexToolsAPI()
        
        # Step 1: Get recent pools
        logger.info("Step 1: Fetching recent Solana pools")
        recent_pools = api.get_recent_solana_pools()
        print("\n=== Recent Solana Pools ===")
        pretty_print_json(recent_pools)
        
        # Step 2: If we have pools, get details for the first one
        if recent_pools.get('success') and recent_pools.get('data') and len(recent_pools['data']) > 0:
            first_pool = recent_pools['data'][0]
            pool_address = first_pool['id']
            
            logger.info(f"Selected pool for detailed analysis: {pool_address}")
            
            # Step 3: Get detailed info for this pool
            logger.info("Step 3: Fetching detailed pool info")
            pool_info = api.get_pool_info(pool_address)
            print(f"\n=== Pool Info for {pool_address} ===")
            pretty_print_json(pool_info)
            
            # Step 4: Get price data for this pool
            logger.info("Step 4: Fetching price data")
            price_data = api.get_pool_price_data(pool_address)
            print(f"\n=== Price Data for {pool_address} ===")
            pretty_print_json(price_data)
        else:
            logger.warning("No pools found or API returned an error")
        
        logger.info("Demo completed successfully!")
    except Exception as e:
        logger.error(f"Demo failed: {str(e)}", exc_info=True)

if __name__ == "__main__":
    run_demo() 