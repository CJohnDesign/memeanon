#!/usr/bin/env python3
"""
DexTools API Demo - Python Implementation
This script demonstrates basic connectivity with the DexTools API
to fetch cryptocurrency token data from the Solana blockchain and display it in the console.
"""

import os
import json
import time
import random
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
    
    # List of common user agents to rotate through
    USER_AGENTS = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.0 Safari/605.1.15',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:90.0) Gecko/20100101 Firefox/90.0',
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36'
    ]
    
    def __init__(self):
        """Initialize the DexTools API client"""
        self.api_key = os.getenv('DEXTOOLS_API_KEY')
        if not self.api_key:
            logger.error("API key not found. Please set DEXTOOLS_API_KEY in .env file")
            raise ValueError("API key not found")
            
        # Base URL from the latest documentation
        self.base_url = 'https://api.dextools.io/v1'
        
        # Alternative base URLs to try if the main one fails
        self.alternative_base_urls = [
            'https://api.dextools.io/v2',
            'https://api.dextools.io/api/v1',
            'https://api.dextools.io/api'
        ]
        
        # Set up headers with browser-like information to bypass Cloudflare
        self.headers = self._generate_headers()
        
        logger.info("DexTools API client initialized")
        logger.info(f"Using API key: {self.api_key[:5]}...{self.api_key[-5:] if len(self.api_key) > 10 else ''}")
    
    def _generate_headers(self) -> Dict[str, str]:
        """Generate headers that mimic a browser to help bypass Cloudflare"""
        user_agent = random.choice(self.USER_AGENTS)
        
        return {
            'X-API-Key': self.api_key,
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'en-US,en;q=0.9',
            'User-Agent': user_agent,
            'Referer': 'https://www.dextools.io/',
            'Origin': 'https://www.dextools.io',
            'sec-ch-ua': '"Chromium";v="92", " Not A;Brand";v="99", "Google Chrome";v="92"',
            'sec-ch-ua-mobile': '?0',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-site',
            'Connection': 'keep-alive'
        }
    
    def _make_request(self, endpoint: str, params: Optional[Dict[str, Any]] = None, 
                     max_retries: int = 3, base_delay: float = 2.0) -> Dict[str, Any]:
        """
        Make a request to the API with retry logic and exponential backoff
        
        Args:
            endpoint: API endpoint to call (without base URL)
            params: Query parameters to include
            max_retries: Maximum number of retry attempts
            base_delay: Base delay between retries in seconds
            
        Returns:
            API response as dictionary
        """
        # Try with the main base URL first, then fall back to alternatives
        urls_to_try = [f"{self.base_url}{endpoint}"] + [f"{url}{endpoint}" for url in self.alternative_base_urls]
        
        last_exception = None
        
        for url in urls_to_try:
            # Refresh headers with a new random user agent for each base URL
            self.headers = self._generate_headers()
            
            for attempt in range(max_retries):
                try:
                    # Add a small random delay to avoid detection patterns
                    time.sleep(random.uniform(0.5, 1.5))
                    
                    logger.info(f"Making request to {url} (Attempt {attempt+1}/{max_retries})")
                    response = requests.get(
                        url,
                        headers=self.headers,
                        params=params
                    )
                    
                    # Log response headers for debugging
                    logger.debug(f"Response headers: {response.headers}")
                    
                    # Check for Cloudflare specific headers/responses
                    if 'cf-ray' in response.headers:
                        logger.info(f"Cloudflare Ray ID: {response.headers.get('cf-ray')}")
                    
                    response.raise_for_status()
                    
                    # If we get here, the request was successful
                    return response.json() if response.text else {"status": "ok"}
                    
                except requests.exceptions.RequestException as e:
                    last_exception = e
                    logger.warning(f"Request to {url} failed: {str(e)}")
                    
                    # Check if we should retry
                    if attempt < max_retries - 1:
                        # Calculate delay with exponential backoff and jitter
                        delay = base_delay * (2 ** attempt) + random.uniform(0, 1)
                        logger.info(f"Retrying in {delay:.2f} seconds...")
                        time.sleep(delay)
                    else:
                        logger.error(f"All attempts to {url} failed")
        
        # If we get here, all URLs and retries failed
        logger.error("All API endpoints failed")
        if last_exception:
            if hasattr(last_exception, 'response') and last_exception.response:
                logger.error(f"Last response status: {last_exception.response.status_code}")
                logger.error(f"Last response data: {last_exception.response.text}")
        
        raise Exception("Failed to connect to any DexTools API endpoint")
    
    def get_api_info(self) -> Dict[str, Any]:
        """
        Get API information to verify connectivity
        
        Returns:
            Dict containing API information
        """
        logger.info("Fetching API information")
        
        # Try different endpoints to check connectivity
        endpoints = [
            "/info",
            "/status",
            "/health",
            "/version",
            "/ping",
            "/"
        ]
        
        for endpoint in endpoints:
            try:
                return self._make_request(endpoint)
            except Exception as e:
                logger.warning(f"Endpoint {endpoint} failed: {str(e)}")
                continue
        
        # If we get here, all endpoints failed
        raise Exception("All API info endpoints failed")
    
    def get_solana_hot_pairs(self) -> Dict[str, Any]:
        """
        Get hot pairs specifically for the Solana blockchain
        
        Returns:
            Dict containing hot pairs on Solana
        """
        logger.info("Fetching hot pairs for Solana blockchain")
        
        # The chain ID for Solana might be 'solana', 'sol', or something else
        # Try different possible chain IDs
        chain_ids = ['solana', 'sol', 'slna']
        
        # Try different possible endpoints for hot pairs
        endpoint_templates = [
            "/pair/{}/hot",
            "/pairs/{}/hot",
            "/pool/{}/hot",
            "/pools/{}/hot",
            "/dex/{}/pairs/hot"
        ]
        
        for chain_id in chain_ids:
            for template in endpoint_templates:
                endpoint = template.format(chain_id)
                try:
                    return self._make_request(endpoint)
                except Exception as e:
                    logger.warning(f"Solana hot pairs endpoint {endpoint} failed: {str(e)}")
                    continue
        
        raise Exception("Failed to fetch hot pairs for Solana from any endpoint")
    
    def get_solana_tokens(self, limit: int = 10) -> Dict[str, Any]:
        """
        Get popular tokens on the Solana blockchain
        
        Args:
            limit: Number of tokens to retrieve (default: 10)
            
        Returns:
            Dict containing Solana tokens
        """
        logger.info(f"Fetching {limit} popular tokens on Solana blockchain")
        
        # The chain ID for Solana might be 'solana', 'sol', or something else
        # Try different possible chain IDs
        chain_ids = ['solana', 'sol', 'slna']
        
        # Try different possible endpoints for tokens
        endpoint_templates = [
            "/token/{}/list",
            "/tokens/{}/list",
            "/token/{}/popular",
            "/tokens/{}/popular",
            "/dex/{}/tokens"
        ]
        
        params = {
            'limit': limit,
            'sort': 'volume'  # Sort by volume to get popular tokens
        }
        
        for chain_id in chain_ids:
            for template in endpoint_templates:
                endpoint = template.format(chain_id)
                try:
                    return self._make_request(endpoint, params=params)
                except Exception as e:
                    logger.warning(f"Solana tokens endpoint {endpoint} failed: {str(e)}")
                    continue
        
        raise Exception("Failed to fetch tokens for Solana from any endpoint")
    
    def get_solana_pair_info(self, pair_address: str) -> Dict[str, Any]:
        """
        Get detailed information about a specific Solana trading pair
        
        Args:
            pair_address: Address of the Solana pair to query
            
        Returns:
            Dict containing pair details
        """
        logger.info(f"Fetching info for Solana pair: {pair_address}")
        
        # The chain ID for Solana might be 'solana', 'sol', or something else
        # Try different possible chain IDs
        chain_ids = ['solana', 'sol', 'slna']
        
        # Try different possible endpoints for pair info
        endpoint_templates = [
            "/pair/{}/{}",
            "/pairs/{}/{}",
            "/pair/{}/info/{}",
            "/pairs/{}/info/{}",
            "/pool/{}/{}",
            "/pools/{}/{}"
        ]
        
        for chain_id in chain_ids:
            for template in endpoint_templates:
                endpoint = template.format(chain_id, pair_address)
                try:
                    return self._make_request(endpoint)
                except Exception as e:
                    logger.warning(f"Solana pair info endpoint {endpoint} failed: {str(e)}")
                    continue
        
        raise Exception(f"Failed to fetch pair info for {pair_address} on Solana from any endpoint")

def pretty_print_json(data: Dict[str, Any]) -> None:
    """Print JSON data in a readable format"""
    print(json.dumps(data, indent=2))

def run_demo() -> None:
    """Main function to run the DexTools API demo for Solana blockchain"""
    logger.info("Starting DexTools API Demo for Solana Blockchain...")
    
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
            logger.info("Continuing with Solana endpoints despite connectivity test failure...")
        
        # Step 2: Try to get hot pairs for Solana
        logger.info("Step 2: Attempting to fetch hot pairs for Solana")
        try:
            solana_hot_pairs = api.get_solana_hot_pairs()
            print("\n=== Hot Solana Pairs ===")
            pretty_print_json(solana_hot_pairs)
            
            # If we have pairs, get details for the first one
            if solana_hot_pairs.get('success') and solana_hot_pairs.get('data') and len(solana_hot_pairs['data']) > 0:
                first_pair = solana_hot_pairs['data'][0]
                pair_address = first_pair.get('id')
                
                if pair_address:
                    logger.info(f"Selected Solana pair for detailed analysis: {pair_address}")
                    
                    # Step 3: Get detailed info for this pair
                    logger.info("Step 3: Fetching detailed Solana pair info")
                    try:
                        pair_info = api.get_solana_pair_info(pair_address)
                        print(f"\n=== Solana Pair Info for {pair_address} ===")
                        pretty_print_json(pair_info)
                    except Exception as e:
                        logger.error(f"Failed to fetch Solana pair info: {str(e)}")
            else:
                logger.warning("No hot Solana pairs found or API returned an error")
        except Exception as e:
            logger.error(f"Failed to fetch hot Solana pairs: {str(e)}")
        
        # Step 4: Try to get popular tokens on Solana
        logger.info("Step 4: Attempting to fetch popular tokens on Solana")
        try:
            solana_tokens = api.get_solana_tokens()
            print("\n=== Popular Solana Tokens ===")
            pretty_print_json(solana_tokens)
        except Exception as e:
            logger.error(f"Failed to fetch Solana tokens: {str(e)}")
        
        logger.info("Solana demo completed. Some endpoints may have failed due to Cloudflare restrictions or API changes.")
        logger.info("Consider using a browser to inspect network requests on the DexTools website to understand the correct API structure for Solana.")
    except Exception as e:
        logger.error(f"Solana demo failed: {str(e)}", exc_info=True)

if __name__ == "__main__":
    run_demo() 