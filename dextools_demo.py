#!/usr/bin/env python3
"""
DexTools API Demo - Python Implementation
This script demonstrates basic connectivity with the DexTools API
to fetch cryptocurrency token data and display it in the console.
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

class DexToolsAPI:
    """Client for interacting with the DexTools API"""
    
    def __init__(self):
        """Initialize the DexTools API client"""
        self.api_key = os.getenv('DEXTOOLS_API_KEY')
        if not self.api_key:
            logger.error("API key not found. Please set DEXTOOLS_API_KEY in .env file")
            raise ValueError("API key not found")
            
        # Base URL from the latest documentation
        self.base_url = 'https://api.dextools.io/v1'
        
        # Headers for authentication
        self.headers = {
            'X-API-Key': self.api_key,
            'Accept': 'application/json'
        }
        
        logger.info("DexTools API client initialized")
        logger.info(f"Using API key: {self.api_key[:5]}...{self.api_key[-5:] if len(self.api_key) > 10 else ''}")
    
    def get_api_info(self) -> Dict[str, Any]:
        """
        Get API information to verify connectivity
        
        Returns:
            Dict containing API information
        """
        logger.info("Fetching API information")
        
        try:
            # Try different endpoints to check connectivity
            endpoints = [
                "/info",
                "/status",
                "/health"
            ]
            
            for endpoint in endpoints:
                try:
                    logger.info(f"Trying endpoint: {endpoint}")
                    response = requests.get(
                        f"{self.base_url}{endpoint}",
                        headers=self.headers
                    )
                    response.raise_for_status()
                    data = response.json() if response.text else {"status": "ok"}
                    logger.info(f"API connection successful via {endpoint}")
                    return data
                except requests.exceptions.RequestException as e:
                    logger.warning(f"Endpoint {endpoint} failed: {str(e)}")
                    continue
            
            # If we get here, all endpoints failed
            raise Exception("All API info endpoints failed")
        except Exception as e:
            logger.error(f"Error fetching API information: {str(e)}")
            raise
    
    def get_supported_chains(self) -> Dict[str, Any]:
        """
        Get list of supported chains
        
        Returns:
            Dict containing supported chains
        """
        logger.info("Fetching supported chains")
        
        try:
            response = requests.get(
                f"{self.base_url}/chain",
                headers=self.headers
            )
            response.raise_for_status()
            data = response.json()
            
            logger.info(f"Successfully retrieved supported chains")
            return data
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching supported chains: {str(e)}")
            if hasattr(e, 'response') and e.response:
                logger.error(f"Response status: {e.response.status_code}")
                logger.error(f"Response data: {e.response.text}")
            raise
    
    def get_hot_pairs(self, chain: str = 'ether') -> Dict[str, Any]:
        """
        Get hot pairs for a specific chain
        
        Args:
            chain: Chain ID (default: ether)
            
        Returns:
            Dict containing hot pairs
        """
        logger.info(f"Fetching hot pairs for chain: {chain}")
        
        try:
            response = requests.get(
                f"{self.base_url}/pair/{chain}/hot",
                headers=self.headers
            )
            response.raise_for_status()
            data = response.json()
            
            logger.info(f"Successfully retrieved hot pairs for chain: {chain}")
            return data
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching hot pairs for chain {chain}: {str(e)}")
            if hasattr(e, 'response') and e.response:
                logger.error(f"Response status: {e.response.status_code}")
                logger.error(f"Response data: {e.response.text}")
            raise
    
    def search_tokens(self, query: str) -> Dict[str, Any]:
        """
        Search for tokens by name or symbol
        
        Args:
            query: Search query
            
        Returns:
            Dict containing search results
        """
        logger.info(f"Searching for tokens with query: {query}")
        
        try:
            response = requests.get(
                f"{self.base_url}/token/search",
                headers=self.headers,
                params={
                    'query': query
                }
            )
            response.raise_for_status()
            data = response.json()
            
            logger.info(f"Successfully searched for tokens with query: {query}")
            return data
        except requests.exceptions.RequestException as e:
            logger.error(f"Error searching for tokens: {str(e)}")
            if hasattr(e, 'response') and e.response:
                logger.error(f"Response status: {e.response.status_code}")
                logger.error(f"Response data: {e.response.text}")
            raise
    
    def get_token_info(self, chain: str, token_address: str) -> Dict[str, Any]:
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
            response = requests.get(
                f"{self.base_url}/token/{chain}/{token_address}",
                headers=self.headers
            )
            response.raise_for_status()
            data = response.json()
            
            logger.info(f"Successfully retrieved info for token: {token_address}")
            return data
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching token info for {token_address}: {str(e)}")
            if hasattr(e, 'response') and e.response:
                logger.error(f"Response status: {e.response.status_code}")
                logger.error(f"Response data: {e.response.text}")
            raise
    
    def get_pair_info(self, chain: str, pair_address: str) -> Dict[str, Any]:
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
            response = requests.get(
                f"{self.base_url}/pair/{chain}/{pair_address}",
                headers=self.headers
            )
            response.raise_for_status()
            data = response.json()
            
            logger.info(f"Successfully retrieved info for pair: {pair_address}")
            return data
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching pair info for {pair_address}: {str(e)}")
            if hasattr(e, 'response') and e.response:
                logger.error(f"Response status: {e.response.status_code}")
                logger.error(f"Response data: {e.response.text}")
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
        
        # Step 1: Test API connectivity
        logger.info("Step 1: Testing API connectivity")
        try:
            api_info = api.get_api_info()
            print("\n=== API Information ===")
            pretty_print_json(api_info)
        except Exception as e:
            logger.error(f"Failed to connect to API: {str(e)}")
            return
        
        # Step 2: Get supported chains
        logger.info("Step 2: Fetching supported chains")
        try:
            chains = api.get_supported_chains()
            print("\n=== Supported Chains ===")
            pretty_print_json(chains)
        except Exception as e:
            logger.error(f"Failed to fetch chains: {str(e)}")
        
        # Step 3: Get hot pairs for Ethereum
        logger.info("Step 3: Fetching hot pairs for Ethereum")
        try:
            hot_pairs = api.get_hot_pairs('ether')
            print("\n=== Hot Ethereum Pairs ===")
            pretty_print_json(hot_pairs)
            
            # If we have pairs, get details for the first one
            if hot_pairs.get('success') and hot_pairs.get('data') and len(hot_pairs['data']) > 0:
                first_pair = hot_pairs['data'][0]
                pair_address = first_pair.get('id')
                
                if pair_address:
                    logger.info(f"Selected pair for detailed analysis: {pair_address}")
                    
                    # Step 4: Get detailed info for this pair
                    logger.info("Step 4: Fetching detailed pair info")
                    try:
                        pair_info = api.get_pair_info('ether', pair_address)
                        print(f"\n=== Pair Info for {pair_address} ===")
                        pretty_print_json(pair_info)
                    except Exception as e:
                        logger.error(f"Failed to fetch pair info: {str(e)}")
            else:
                logger.warning("No hot pairs found or API returned an error")
        except Exception as e:
            logger.error(f"Failed to fetch hot pairs: {str(e)}")
        
        # Step 5: Search for a popular token
        logger.info("Step 5: Searching for tokens")
        try:
            search_results = api.search_tokens('ethereum')
            print("\n=== Token Search Results for 'ethereum' ===")
            pretty_print_json(search_results)
            
            # If we have search results, get details for the first one
            if search_results.get('success') and search_results.get('data') and len(search_results['data']) > 0:
                first_token = search_results['data'][0]
                token_address = first_token.get('address')
                token_chain = first_token.get('chain')
                
                if token_address and token_chain:
                    logger.info(f"Selected token for detailed analysis: {token_address} on chain {token_chain}")
                    
                    # Step 6: Get detailed info for this token
                    logger.info("Step 6: Fetching detailed token info")
                    try:
                        token_info = api.get_token_info(token_chain, token_address)
                        print(f"\n=== Token Info for {token_address} ===")
                        pretty_print_json(token_info)
                    except Exception as e:
                        logger.error(f"Failed to fetch token info: {str(e)}")
        except Exception as e:
            logger.error(f"Failed to search for tokens: {str(e)}")
        
        logger.info("Demo completed successfully!")
    except Exception as e:
        logger.error(f"Demo failed: {str(e)}", exc_info=True)

if __name__ == "__main__":
    run_demo() 