#!/usr/bin/env python3
"""
Solana Token Analyzer

This script fetches recent tokens from the Solana blockchain using the DexTools API,
analyzes them with a language model, and saves the results in markdown format.
"""

import os
import asyncio
import json
import logging
import aiohttp
import argparse
from datetime import datetime, timedelta
from typing import TypedDict, List, Dict, Any, Optional, Union
from pathlib import Path

# Import our modules
from solana_dextools_api import SolanaDexToolsAPI
from prompts.solana_token_analysis_prompt import (
    SolanaTokenData,
    get_solana_token_analysis_prompt,
    get_solana_new_tokens_prompt
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("solana_token_analyzer.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('solana_token_analyzer')

class TokenAnalysisResult(TypedDict):
    """TypedDict for token analysis results"""
    token_data: SolanaTokenData
    analysis: str
    timestamp: str
    prompt: Dict[str, Any]

class SolanaTokenAnalyzer:
    """Class to analyze Solana tokens using DexTools API and LLM"""
    
    def __init__(
        self, 
        api_key: str = "", 
        plan: str = "trial",
        openai_api_key: Optional[str] = None,
        output_dir: str = "outputs"
    ):
        """
        Initialize the Solana token analyzer
        
        Args:
            api_key: DexTools API key (optional for trial plan)
            plan: DexTools API plan (trial, basic, pro)
            openai_api_key: OpenAI API key for token analysis
            output_dir: Directory to save analysis results
        """
        logger.info(f"Initializing Solana token analyzer with plan: {plan}")
        self.dextools_api = SolanaDexToolsAPI(api_key=api_key, plan=plan)
        self.openai_api_key = openai_api_key or os.environ.get("OPENAI_API_KEY", "")
        
        if not self.openai_api_key:
            logger.warning("No OpenAI API key provided. Set OPENAI_API_KEY environment variable or pass it as a parameter.")
        
        # Create output directory if it doesn't exist
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"Analysis results will be saved to: {self.output_dir.absolute()}")
    
    async def analyze_token(self, token_data: SolanaTokenData) -> TokenAnalysisResult:
        """
        Analyze a single token using the LLM
        
        Args:
            token_data: Data about the token to analyze
            
        Returns:
            Analysis result including the token data and LLM analysis
        """
        token_symbol = token_data.get('symbol', 'UNKNOWN')
        logger.info(f"Analyzing token: {token_symbol}")
        
        # Generate the prompt for token analysis
        prompt = get_solana_token_analysis_prompt(
            token_data=token_data,
            include_technical_analysis=True,
            include_social_metrics=False
        )
        
        # Call the OpenAI API to analyze the token
        analysis = await self._call_openai_api(
            system_message=prompt["system_message"],
            user_message=prompt["user_message"]
        )
        
        # Create the result
        result: TokenAnalysisResult = {
            "token_data": token_data,
            "analysis": analysis,
            "timestamp": datetime.now().isoformat(),
            "prompt": prompt
        }
        
        logger.info(f"Analysis completed for token: {token_symbol}")
        return result
    
    async def analyze_recent_tokens(
        self, 
        hours: int = 48, 
        limit: int = 10,
        min_liquidity: float = 5000.0
    ) -> List[TokenAnalysisResult]:
        """
        Fetch and analyze recent tokens from Solana
        
        Args:
            hours: Look for tokens created in the last X hours
            limit: Maximum number of tokens to analyze
            min_liquidity: Minimum liquidity in USD
            
        Returns:
            List of token analysis results
        """
        logger.info(f"Fetching recent tokens from the last {hours} hours (limit: {limit}, min liquidity: ${min_liquidity})")
        
        # Get recent tokens from DexTools API
        from_date = datetime.now() - timedelta(hours=hours)
        from_timestamp = int(from_date.timestamp() * 1000)  # Convert to milliseconds
        
        try:
            # Fetch recent tokens
            recent_tokens = await self.dextools_api.get_recent_solana_tokens(
                limit=limit,
                min_liquidity=min_liquidity,
                from_date=from_timestamp
            )
            
            if not recent_tokens:
                logger.warning(f"No recent tokens found in the last {hours} hours with minimum liquidity of ${min_liquidity}")
                return []
            
            logger.info(f"Found {len(recent_tokens)} recent tokens to analyze")
            
            # Analyze each token
            results = []
            for token in recent_tokens:
                try:
                    # Convert DexTools token data to our SolanaTokenData format
                    token_data = self._convert_to_token_data(token)
                    
                    # Analyze the token
                    result = await self.analyze_token(token_data)
                    results.append(result)
                    
                    # Save the result to a file
                    self._save_analysis_to_file(result)
                    
                    # Sleep briefly to avoid rate limits
                    await asyncio.sleep(1)
                    
                except Exception as e:
                    logger.error(f"Error analyzing token {token.get('symbol', 'UNKNOWN')}: {str(e)}")
            
            return results
            
        except Exception as e:
            logger.error(f"Error fetching recent tokens: {str(e)}")
            return []
    
    async def analyze_hot_pairs(self, limit: int = 5) -> List[TokenAnalysisResult]:
        """
        Fetch and analyze hot trading pairs on Solana
        
        Args:
            limit: Maximum number of hot pairs to analyze
            
        Returns:
            List of token analysis results
        """
        logger.info(f"Fetching top {limit} hot pairs on Solana")
        
        try:
            # Fetch hot pairs
            hot_pairs = await self.dextools_api.get_solana_hot_pairs(limit=limit)
            
            if not hot_pairs:
                logger.warning(f"No hot pairs found on Solana")
                return []
            
            logger.info(f"Found {len(hot_pairs)} hot pairs to analyze")
            
            # Analyze each token in the hot pairs
            results = []
            for pair in hot_pairs:
                try:
                    # Convert pair data to our SolanaTokenData format
                    token_data = self._convert_to_token_data(pair)
                    
                    # Analyze the token
                    result = await self.analyze_token(token_data)
                    results.append(result)
                    
                    # Save the result to a file
                    self._save_analysis_to_file(result)
                    
                    # Sleep briefly to avoid rate limits
                    await asyncio.sleep(1)
                    
                except Exception as e:
                    logger.error(f"Error analyzing hot pair {pair.get('symbol', 'UNKNOWN')}: {str(e)}")
            
            return results
            
        except Exception as e:
            logger.error(f"Error fetching hot pairs: {str(e)}")
            return []
    
    def _convert_to_token_data(self, api_token_data: Dict[str, Any]) -> SolanaTokenData:
        """
        Convert DexTools API token data to our SolanaTokenData format
        
        Args:
            api_token_data: Token data from DexTools API
            
        Returns:
            Converted token data in our format
        """
        # Extract token data from the API response
        # The structure may vary depending on the endpoint (hot pairs, recent tokens, etc.)
        
        # Default values
        token_data: SolanaTokenData = {
            "name": api_token_data.get("name", "Unknown"),
            "symbol": api_token_data.get("symbol", "UNKNOWN"),
            "address": api_token_data.get("address", ""),
            "mint": api_token_data.get("tokenAddress", api_token_data.get("address", "")),
            "price": None,
            "price_change_24h": None,
            "liquidity": None,
            "volume_24h": None,
            "market_cap": None,
            "created_at": None,
            "total_supply": None,
            "decimals": None,
            "holder_count": None
        }
        
        # Try to extract more data if available
        if "price" in api_token_data:
            token_data["price"] = api_token_data["price"]
        
        if "priceChange" in api_token_data:
            token_data["price_change_24h"] = api_token_data["priceChange"]
        
        if "liquidity" in api_token_data:
            token_data["liquidity"] = api_token_data["liquidity"]
        
        if "volume" in api_token_data:
            token_data["volume_24h"] = api_token_data["volume"]
        
        if "marketCap" in api_token_data:
            token_data["market_cap"] = api_token_data["marketCap"]
        
        if "createdAt" in api_token_data:
            token_data["created_at"] = api_token_data["createdAt"]
        
        if "totalSupply" in api_token_data:
            token_data["total_supply"] = api_token_data["totalSupply"]
        
        if "decimals" in api_token_data:
            token_data["decimals"] = api_token_data["decimals"]
        
        if "holderCount" in api_token_data:
            token_data["holder_count"] = api_token_data["holderCount"]
        
        return token_data
    
    async def _call_openai_api(self, system_message: str, user_message: str) -> str:
        """
        Call the OpenAI API to analyze a token
        
        Args:
            system_message: System message for the LLM
            user_message: User message containing token data
            
        Returns:
            LLM analysis response
        """
        if not self.openai_api_key:
            logger.error("No OpenAI API key provided")
            return "Error: No OpenAI API key provided"
        
        logger.info("Calling OpenAI API for token analysis")
        
        try:
            async with aiohttp.ClientSession() as session:
                headers = {
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {self.openai_api_key}"
                }
                
                payload = {
                    "model": "gpt-4o",  # Using the most up-to-date model
                    "messages": [
                        {"role": "system", "content": system_message},
                        {"role": "user", "content": user_message}
                    ],
                    "temperature": 0.5,
                    "max_tokens": 2000
                }
                
                async with session.post(
                    "https://api.openai.com/v1/chat/completions",
                    headers=headers,
                    json=payload
                ) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        logger.error(f"OpenAI API error: {response.status} - {error_text}")
                        return f"Error: OpenAI API returned status code {response.status}"
                    
                    data = await response.json()
                    analysis = data["choices"][0]["message"]["content"]
                    logger.info("Successfully received analysis from OpenAI API")
                    return analysis
                    
        except Exception as e:
            logger.error(f"Error calling OpenAI API: {str(e)}")
            return f"Error: {str(e)}"
    
    def _save_analysis_to_file(self, result: TokenAnalysisResult) -> None:
        """
        Save token analysis to a markdown file
        
        Args:
            result: Token analysis result
        """
        token_symbol = result["token_data"]["symbol"]
        token_name = result["token_data"]["name"]
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Create a safe filename
        safe_symbol = "".join(c if c.isalnum() else "_" for c in token_symbol)
        filename = f"{timestamp}_{safe_symbol}.md"
        filepath = self.output_dir / filename
        
        logger.info(f"Saving analysis for {token_symbol} to {filepath}")
        
        try:
            with open(filepath, "w") as f:
                # Write markdown header
                f.write(f"# Analysis of {token_name} ({token_symbol})\n\n")
                f.write(f"**Analysis Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}\n\n")
                
                # Write token data section
                f.write("## Token Information\n\n")
                f.write(f"- **Name:** {token_name}\n")
                f.write(f"- **Symbol:** {token_symbol}\n")
                f.write(f"- **Address:** {result['token_data']['address']}\n")
                f.write(f"- **Mint Address:** {result['token_data']['mint']}\n")
                
                if result["token_data"].get("created_at"):
                    f.write(f"- **Created:** {result['token_data']['created_at']}\n")
                
                f.write("\n## Key Metrics\n\n")
                
                if result["token_data"].get("price") is not None:
                    f.write(f"- **Price:** ${result['token_data']['price']:.6f}\n")
                
                if result["token_data"].get("price_change_24h") is not None:
                    f.write(f"- **24h Price Change:** {result['token_data']['price_change_24h']:.2f}%\n")
                
                if result["token_data"].get("liquidity") is not None:
                    f.write(f"- **Liquidity:** ${result['token_data']['liquidity']:,.2f}\n")
                
                if result["token_data"].get("volume_24h") is not None:
                    f.write(f"- **24h Volume:** ${result['token_data']['volume_24h']:,.2f}\n")
                
                if result["token_data"].get("market_cap") is not None:
                    f.write(f"- **Market Cap:** ${result['token_data']['market_cap']:,.2f}\n")
                
                if result["token_data"].get("total_supply") is not None:
                    f.write(f"- **Total Supply:** {result['token_data']['total_supply']:,}\n")
                
                if result["token_data"].get("decimals") is not None:
                    f.write(f"- **Decimals:** {result['token_data']['decimals']}\n")
                
                if result["token_data"].get("holder_count") is not None:
                    f.write(f"- **Holder Count:** {result['token_data']['holder_count']:,}\n")
                
                # Write analysis section
                f.write("\n## Analysis\n\n")
                f.write(result["analysis"])
                
                logger.info(f"Analysis saved to {filepath}")
                
        except Exception as e:
            logger.error(f"Error saving analysis to file: {str(e)}")

async def main():
    """Main function to run the Solana token analyzer"""
    parser = argparse.ArgumentParser(description="Analyze Solana tokens using DexTools API and LLM")
    parser.add_argument("--api-key", type=str, default="", help="DexTools API key (optional for trial plan)")
    parser.add_argument("--plan", type=str, default="trial", choices=["trial", "basic", "pro"], help="DexTools API plan")
    parser.add_argument("--hours", type=int, default=48, help="Look for tokens created in the last X hours")
    parser.add_argument("--limit", type=int, default=10, help="Maximum number of tokens to analyze")
    parser.add_argument("--min-liquidity", type=float, default=5000.0, help="Minimum liquidity in USD")
    parser.add_argument("--output-dir", type=str, default="outputs", help="Directory to save analysis results")
    parser.add_argument("--hot-pairs", action="store_true", help="Analyze hot pairs instead of recent tokens")
    parser.add_argument("--hot-pairs-limit", type=int, default=5, help="Number of hot pairs to analyze")
    
    args = parser.parse_args()
    
    # Get OpenAI API key from environment variable
    openai_api_key = os.environ.get("OPENAI_API_KEY", "")
    
    # Initialize the analyzer
    analyzer = SolanaTokenAnalyzer(
        api_key=args.api_key,
        plan=args.plan,
        openai_api_key=openai_api_key,
        output_dir=args.output_dir
    )
    
    # Run the analysis
    if args.hot_pairs:
        logger.info(f"Analyzing top {args.hot_pairs_limit} hot pairs on Solana")
        results = await analyzer.analyze_hot_pairs(limit=args.hot_pairs_limit)
    else:
        logger.info(f"Analyzing recent tokens from the last {args.hours} hours (limit: {args.limit}, min liquidity: ${args.min_liquidity})")
        results = await analyzer.analyze_recent_tokens(
            hours=args.hours,
            limit=args.limit,
            min_liquidity=args.min_liquidity
        )
    
    # Print summary
    if results:
        logger.info(f"Analysis completed for {len(results)} tokens")
        print(f"\nAnalysis completed for {len(results)} tokens")
        print(f"Results saved to: {os.path.abspath(args.output_dir)}")
        
        # Print token names and symbols
        print("\nAnalyzed tokens:")
        for i, result in enumerate(results, 1):
            token_name = result["token_data"]["name"]
            token_symbol = result["token_data"]["symbol"]
            print(f"{i}. {token_name} ({token_symbol})")
    else:
        logger.warning("No tokens were analyzed")
        print("\nNo tokens were analyzed. Check the logs for details.")

if __name__ == "__main__":
    asyncio.run(main()) 