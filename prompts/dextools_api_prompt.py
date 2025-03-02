#!/usr/bin/env python3
"""
DexTools API Integration Prompt

This file contains the prompt for interacting with the DexTools API.
It provides guidance on how to fetch cryptocurrency token data and process it.
"""

from typing import TypedDict, Dict, Any, List, Optional, Union

class DexToolsAPIPrompt(TypedDict):
    """TypedDict for the DexTools API prompt structure"""
    system_message: str
    user_message: str
    examples: List[Dict[str, Any]]
    parameters: Dict[str, Any]

def get_dextools_api_prompt(
    chain_id: str = 'ether',
    endpoint_type: str = 'hot_pairs',
    limit: int = 10,
    include_details: bool = True
) -> DexToolsAPIPrompt:
    """
    Generate a prompt for the DexTools API integration
    
    Args:
        chain_id: The blockchain to query (e.g., 'ether', 'bsc', 'solana')
        endpoint_type: The type of data to fetch ('hot_pairs', 'gainers', 'losers', 'recent_pools')
        limit: Maximum number of results to return
        include_details: Whether to include detailed information for each result
        
    Returns:
        A structured prompt for the DexTools API integration
    """
    
    # Define the system message
    system_message = """
You are a cryptocurrency data analyst assistant. Your task is to analyze token data from the DexTools API
and provide insights about the tokens. Focus on identifying promising tokens with good metrics while
highlighting potential risks.

When analyzing tokens, consider the following factors:
1. Liquidity - Higher is better, minimum $10K is recommended
2. Market cap - Consider if the valuation is reasonable
3. Price action - Look for stable or upward trends
4. Transaction patterns - Healthy buy/sell ratio
5. Holder distribution - Avoid tokens with high concentration

Present your analysis in a clear, structured format with sections for:
- Token Overview (name, symbol, price)
- Key Metrics (liquidity, volume, market cap)
- Technical Analysis (price trends, trading patterns)
- Risk Assessment (red flags, warning signs)
- Recommendation (whether the token appears promising)

Always include appropriate disclaimers about cryptocurrency investment risks.
"""

    # Define the user message based on the endpoint type
    endpoint_descriptions = {
        'hot_pairs': f"Analyze the top {limit} hot trading pairs on {chain_id}",
        'gainers': f"Analyze the top {limit} gainers on {chain_id} in the last 24 hours",
        'losers': f"Analyze the top {limit} losers on {chain_id} in the last 24 hours",
        'recent_pools': f"Analyze the {limit} most recently created pools on {chain_id}"
    }
    
    detail_request = " Include detailed metrics and technical analysis for each token." if include_details else ""
    
    user_message = f"{endpoint_descriptions.get(endpoint_type, 'Analyze token data from DexTools')}.{detail_request} Highlight any tokens that look particularly promising or concerning."

    # Example responses
    examples = [
        {
            "token_name": "Example Token",
            "symbol": "EXT",
            "price": 0.0012,
            "price_change_24h": 15.2,
            "liquidity": 25000,
            "volume_24h": 12500,
            "market_cap": 1200000,
            "analysis": "This token shows promising metrics with good liquidity and trading volume. The price has increased steadily over 24 hours with healthy buy/sell patterns. Risk level appears moderate.",
            "recommendation": "Potentially interesting for further research, but conduct thorough due diligence before any investment."
        }
    ]

    # Parameters for the API call
    parameters = {
        "chain_id": chain_id,
        "endpoint_type": endpoint_type,
        "limit": limit,
        "include_details": include_details,
        "plan": "trial",  # Use the trial plan which was found to work well
        "temperature": 0.7,  # Lower temperature for more factual analysis
        "max_tokens": 1500  # Adjust based on how detailed you want the analysis
    }

    return {
        "system_message": system_message,
        "user_message": user_message,
        "examples": examples,
        "parameters": parameters
    }

def get_token_analysis_prompt(
    token_data: Dict[str, Any],
    chain_id: str = 'ether'
) -> DexToolsAPIPrompt:
    """
    Generate a prompt for analyzing a specific token
    
    Args:
        token_data: Data about the token to analyze
        chain_id: The blockchain the token is on
        
    Returns:
        A structured prompt for token analysis
    """
    
    system_message = """
You are a cryptocurrency token analyst specializing in on-chain metrics and technical analysis.
Your task is to provide a detailed analysis of a specific token based on the data provided.

Your analysis should include:
1. Token Overview - Basic information about the token
2. Liquidity Analysis - Assessment of the token's liquidity
3. Price Analysis - Technical analysis of price movements
4. Volume Analysis - Trading volume patterns and implications
5. Holder Analysis - Distribution of tokens among holders (if data available)
6. Risk Assessment - Identification of potential red flags
7. Conclusion - Overall assessment and recommendation

Be objective and data-driven in your analysis. Highlight both positive aspects and potential concerns.
"""

    # Create a user message that includes key token data
    token_name = token_data.get('name', 'Unknown Token')
    token_symbol = token_data.get('symbol', 'UNKNOWN')
    token_address = token_data.get('address', 'No address provided')
    
    user_message = f"""
Please analyze the following token on the {chain_id} blockchain:

Token Name: {token_name}
Symbol: {token_symbol}
Address: {token_address}

Key metrics:
- Price: {token_data.get('price', 'Unknown')}
- Price Change (24h): {token_data.get('price_change_24h', 'Unknown')}%
- Liquidity: ${token_data.get('liquidity', 'Unknown')}
- Volume (24h): ${token_data.get('volume_24h', 'Unknown')}
- Market Cap: ${token_data.get('market_cap', 'Unknown')}
- Created: {token_data.get('created_at', 'Unknown')}

Provide a comprehensive analysis of this token, including its potential and risks.
"""

    # Example response
    examples = [
        {
            "analysis_sections": {
                "overview": "Brief overview of the token",
                "liquidity": "Analysis of liquidity metrics",
                "price": "Technical price analysis",
                "volume": "Volume pattern analysis",
                "holders": "Token distribution analysis",
                "risks": "Potential red flags",
                "conclusion": "Overall assessment"
            }
        }
    ]

    parameters = {
        "token_address": token_data.get('address'),
        "chain_id": chain_id,
        "temperature": 0.5,  # Lower temperature for more factual analysis
        "max_tokens": 2000  # Detailed analysis requires more tokens
    }

    return {
        "system_message": system_message,
        "user_message": user_message,
        "examples": examples,
        "parameters": parameters
    }

def get_multi_chain_comparison_prompt(
    token_data_list: List[Dict[str, Any]],
    chains: List[str]
) -> DexToolsAPIPrompt:
    """
    Generate a prompt for comparing tokens across multiple chains
    
    Args:
        token_data_list: List of token data to compare
        chains: List of blockchains to include in the comparison
        
    Returns:
        A structured prompt for multi-chain token comparison
    """
    
    system_message = """
You are a cross-chain cryptocurrency analyst specializing in comparing token metrics across different blockchains.
Your task is to analyze token data from multiple chains and provide insights on:

1. Performance Comparison - How tokens are performing across different chains
2. Liquidity Differences - Comparison of liquidity across chains
3. Trading Volume Analysis - Volume patterns on different chains
4. Market Trends - Emerging trends specific to each blockchain
5. Opportunity Identification - Potential opportunities based on cross-chain analysis

Present your analysis in a clear, comparative format that highlights the differences and similarities
between tokens on different blockchains.
"""

    user_message = f"""
Please compare token performance across the following blockchains: {', '.join(chains)}

For each blockchain, analyze the top tokens based on:
- Price performance
- Liquidity levels
- Trading volume
- Market trends

Identify any notable patterns or differences between the chains. Are certain types of tokens performing
better on specific chains? Is there a difference in liquidity or trading behavior across chains?

Conclude with insights about the current state of the market across these different blockchains.
"""

    examples = [
        {
            "comparison_structure": {
                "chain_summaries": "Brief overview of each chain's market",
                "performance_comparison": "Comparison of token performance metrics",
                "liquidity_analysis": "Cross-chain liquidity comparison",
                "volume_patterns": "Trading volume differences",
                "market_trends": "Emerging trends by blockchain",
                "opportunities": "Potential opportunities identified",
                "conclusion": "Overall cross-chain market assessment"
            }
        }
    ]

    parameters = {
        "chains": chains,
        "token_count_per_chain": len(token_data_list) // len(chains) if chains else 0,
        "temperature": 0.6,
        "max_tokens": 2500  # Cross-chain analysis is complex and requires more tokens
    }

    return {
        "system_message": system_message,
        "user_message": user_message,
        "examples": examples,
        "parameters": parameters
    }

# Logging configuration guidance
"""
When implementing the DexTools API integration, ensure comprehensive logging:

1. Configure logging at the start of your script:
   ```python
   import logging
   
   logging.basicConfig(
       level=logging.INFO,
       format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
       handlers=[
           logging.FileHandler("dextools_api.log"),
           logging.StreamHandler()
       ]
   )
   logger = logging.getLogger('dextools_api')
   ```

2. Log all API requests:
   ```python
   logger.info(f"Making request to {endpoint} with parameters: {params}")
   ```

3. Log responses (but be careful with sensitive data):
   ```python
   logger.info(f"Received response with status code: {response.status_code}")
   logger.debug(f"Response data: {response.json()}")
   ```

4. Log errors with detailed information:
   ```python
   logger.error(f"API request failed: {str(e)}", exc_info=True)
   ```

5. Log rate limiting and retries:
   ```python
   logger.warning(f"Rate limited. Retrying in {delay} seconds (attempt {attempt}/{max_retries})")
   ```

6. Log successful operations:
   ```python
   logger.info(f"Successfully processed {len(tokens)} tokens from {chain_id}")
   ```
"""

# Example usage
if __name__ == "__main__":
    import json
    
    # Example 1: Get a prompt for hot pairs on Ethereum
    hot_pairs_prompt = get_dextools_api_prompt(chain_id='ether', endpoint_type='hot_pairs', limit=5)
    print("Hot Pairs Prompt:")
    print(json.dumps(hot_pairs_prompt, indent=2))
    
    # Example 2: Get a prompt for analyzing a specific token
    example_token_data = {
        "name": "Example Token",
        "symbol": "EXT",
        "address": "0x1234567890abcdef1234567890abcdef12345678",
        "price": 0.0015,
        "price_change_24h": 12.5,
        "liquidity": 50000,
        "volume_24h": 25000,
        "market_cap": 1500000,
        "created_at": "2023-01-15T12:00:00Z"
    }
    token_analysis_prompt = get_token_analysis_prompt(example_token_data)
    print("\nToken Analysis Prompt:")
    print(json.dumps(token_analysis_prompt, indent=2))
    
    # Example 3: Get a prompt for multi-chain comparison
    multi_chain_prompt = get_multi_chain_comparison_prompt(
        token_data_list=[{} for _ in range(10)],  # Placeholder for 10 tokens
        chains=['ether', 'bsc', 'solana', 'polygon', 'avalanche']
    )
    print("\nMulti-Chain Comparison Prompt:")
    print(json.dumps(multi_chain_prompt, indent=2)) 