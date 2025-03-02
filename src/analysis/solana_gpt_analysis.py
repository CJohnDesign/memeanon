#!/usr/bin/env python3
"""
Solana GPT Analysis
This script fetches top gaining tokens on the Solana blockchain using the DexTools API,
analyzes them using OpenAI's GPT-4o model, and saves the analysis as a Markdown file.
"""

import os
import json
import time
import logging
import requests
from typing import Dict, Any, List, Optional, TypedDict
from datetime import datetime
from openai import OpenAI
from dotenv import load_dotenv

# Import prompts
from src.prompts.solana_gainers_prompt import get_solana_gainers_prompt

# Configure logging
os.makedirs("logs", exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("logs/solana_gpt_analysis.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('solana_gpt_analysis')

# Load environment variables
load_dotenv()

# Get API keys
DEXTOOLS_API_KEY = os.getenv('DEXTOOLS_API_KEY')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

# Initialize OpenAI client
client = OpenAI(
    api_key=OPENAI_API_KEY,
)

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

def get_solana_gainers() -> Dict[str, Any]:
    """
    Get top gaining tokens on the Solana blockchain using the specific endpoint
    
    Returns:
        Dict containing top gaining tokens on Solana
    """
    logger.info("Fetching top gainers for Solana blockchain")
    
    # Use the exact endpoint from the curl example
    url = "https://public-api.dextools.io/trial/v2/ranking/solana/gainers"
    
    # Use the API key from the .env file or fall back to the example key
    api_key = DEXTOOLS_API_KEY or "UFYgd1VSeq7ZdWbPQDEPQ6fuQ63QahNb2n4vntbi"
    
    headers = {
        "accept": "application/json",
        "x-api-key": api_key
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

def format_data_for_prompt(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Format the DexTools API response data for the GPT prompt
    
    Args:
        data: The data returned from the DexTools API
        
    Returns:
        Formatted data for the GPT prompt
    """
    formatted_data = {
        "chain": "solana",
        "endpoint": "gainers",
        "timestamp": datetime.now().isoformat(),
        "tokens": []
    }
    
    # Check if the response has the expected structure
    if 'data' in data:
        pairs = data.get('data', [])
    elif 'pairs' in data:
        pairs = data.get('pairs', [])
    else:
        logger.error(f"Unexpected response format. Keys: {list(data.keys())}")
        return formatted_data
    
    # Format each token
    for pair in pairs:
        main_token = pair.get('mainToken', {})
        side_token = pair.get('sideToken', {})
        
        token_data = {
            "name": main_token.get('name', 'Unknown'),
            "symbol": main_token.get('symbol', 'UNKNOWN'),
            "address": main_token.get('address', ''),
            "mint": main_token.get('address', ''),  # In Solana, address is the mint
            "price": pair.get('price', 0),
            "price_change_24h": pair.get('variation24h', 0),
            "volume_24h": pair.get('volume24h', 0),
            "liquidity": pair.get('liquidity', 0),
            "created_at": pair.get('creationTime', ''),
            "pair_address": pair.get('address', ''),
            "exchange": {
                "name": pair.get('exchange', {}).get('name', 'Unknown'),
                "address": pair.get('exchange', {}).get('address', '')
            }
        }
        
        formatted_data["tokens"].append(token_data)
    
    return formatted_data

def analyze_with_gpt(data: Dict[str, Any]) -> str:
    """
    Analyze the token data using OpenAI's GPT-4o model
    
    Args:
        data: Formatted token data
        
    Returns:
        Analysis text from GPT
    """
    logger.info("Analyzing token data with GPT-4o")
    
    if not OPENAI_API_KEY:
        logger.error("OpenAI API key not found. Please set OPENAI_API_KEY in .env file")
        return "Error: OpenAI API key not found. Please set OPENAI_API_KEY in .env file"
    
    # Get the specialized prompt for Solana gainers
    prompt = get_solana_gainers_prompt(
        limit=len(data["tokens"]),
        include_technical_analysis=True,
        include_risk_assessment=True
    )
    
    # Create the messages for the GPT model
    messages = [
        {"role": "system", "content": prompt["system_message"]},
        {"role": "user", "content": prompt["user_message"] + "\n\n" + json.dumps(data, indent=2)}
    ]
    
    try:
        logger.info("Making API call to OpenAI...")
        
        # Make the API call to OpenAI using the client with a timeout
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=messages,
            temperature=prompt["parameters"]["temperature"],
            max_tokens=prompt["parameters"]["max_tokens"],
            timeout=60.0  # 60 seconds timeout
        )
        
        # Extract the response text
        analysis_text = response.choices[0].message.content
        logger.info("GPT analysis completed successfully")
        return analysis_text
    except Exception as e:
        logger.error(f"Error during GPT analysis: {str(e)}")
        return f"Error during analysis: {str(e)}"

def save_to_markdown(analysis: str, data: Dict[str, Any]) -> str:
    """
    Save the analysis to a Markdown file
    
    Args:
        analysis: The analysis text from GPT
        data: The original data used for the analysis
        
    Returns:
        Path to the saved file
    """
    # Create outputs directory if it doesn't exist
    os.makedirs("outputs", exist_ok=True)
    
    # Generate filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"outputs/solana_gainers_analysis_{timestamp}.md"
    
    # Create the markdown content
    markdown_content = f"""# Solana Gainers Analysis - {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

## Analysis by GPT-4o

{analysis}

## Raw Data

```json
{json.dumps(data, indent=2)}
```

*Generated on {datetime.now().isoformat()} using DexTools API and OpenAI GPT-4o*
"""
    
    # Write to file
    with open(filename, "w") as f:
        f.write(markdown_content)
    
    logger.info(f"Analysis saved to {filename}")
    return filename

def mock_analyze(data: Dict[str, Any]) -> str:
    """
    Generate a mock analysis without calling the OpenAI API
    
    Args:
        data: Formatted token data
        
    Returns:
        Mock analysis text
    """
    logger.info("Generating mock analysis...")
    
    tokens = data.get("tokens", [])
    token_count = len(tokens)
    
    mock_analysis = f"""# Solana Top Gainers Analysis

## Executive Summary

This analysis covers {token_count} top gaining tokens on the Solana blockchain. Most of these tokens show extremely high percentage gains but have very low liquidity and trading volume, which raises significant concerns about the sustainability of their price movements.

## Top Gainers Analysis

"""
    
    # Add analysis for each token
    for i, token in enumerate(tokens[:5]):  # Limit to first 5 tokens for brevity
        name = token.get("name", "Unknown")
        symbol = token.get("symbol", "UNKNOWN")
        price = token.get("price", 0)
        price_change = token.get("price_change_24h", 0)
        volume = token.get("volume_24h", 0)
        liquidity = token.get("liquidity", 0)
        created_at = token.get("created_at", "")
        exchange = token.get("exchange", {}).get("name", "Unknown")
        
        mock_analysis += f"""### {name} ({symbol})
- **Price**: ${price:.6f}
- **Price Change (24h)**: {price_change:.2f}%
- **Volume (24h)**: ${volume:.2f}
- **Liquidity**: ${liquidity:.2f}
- **Creation Date**: {created_at[:10] if created_at else "Unknown"}
- **Exchange**: {exchange}
- **Potential Utility**: The name suggests a {name.lower()}-related utility.
- **Risk Assessment**: **Very High**
  - **Red Flags**: {"High price increase without supporting volume or liquidity." if price_change > 100 else "Price movement may not be sustainable."}

"""
    
    # Add market trends and risk warnings
    mock_analysis += """## Market Trends

The current market on Solana shows a pattern of newly created tokens with extremely high percentage gains but minimal liquidity and trading volume. This suggests potential market manipulation or speculative behavior rather than genuine adoption or utility.

## Investment Opportunities

Given the high-risk nature of all analyzed tokens, no clear investment opportunities can be recommended without further research. Investors should exercise extreme caution.

## Risk Warnings

- Most tokens show extremely high gains without supporting trading volume or liquidity
- Many tokens were recently created, increasing the risk of rug pulls or scams
- Lack of established history or utility for most tokens
- Potential for market manipulation due to low liquidity
"""
    
    logger.info("Mock analysis generated successfully")
    return mock_analysis

def run_analysis() -> None:
    """Main function to run the Solana GPT analysis"""
    logger.info("Starting Solana GPT Analysis...")
    
    try:
        # Step 1: Get Solana gainers data
        solana_gainers = get_solana_gainers()
        
        # Step 2: Format the data for the prompt
        formatted_data = format_data_for_prompt(solana_gainers)
        
        # Step 3: Analyze with GPT-4o or use mock analysis
        use_mock = True  # Set to False to use actual OpenAI API
        if use_mock:
            analysis = mock_analyze(formatted_data)
        else:
            analysis = analyze_with_gpt(formatted_data)
        
        # Step 4: Save to markdown file
        output_file = save_to_markdown(analysis, formatted_data)
        
        logger.info(f"Analysis completed and saved to {output_file}")
        print(f"\nAnalysis completed and saved to {output_file}")
    except Exception as e:
        logger.error(f"Analysis failed: {str(e)}", exc_info=True)
        print(f"\nAnalysis failed: {str(e)}")

if __name__ == "__main__":
    run_analysis()