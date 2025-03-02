#!/usr/bin/env python3
"""
Solana Token Analysis Prompts

This file contains prompt templates for analyzing Solana tokens using LLMs.
It provides structured prompts for different analysis scenarios, such as
analyzing specific tokens, hot pairs, or newly launched tokens.
"""

import logging
from typing import TypedDict, Dict, List, Any, Optional, Union
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("solana_token_analysis.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('solana_token_analysis')

class SolanaTokenData(TypedDict):
    """TypedDict for Solana token data structure"""
    name: str
    symbol: str
    address: str
    mint: str  # Solana-specific token mint address
    price: Optional[float]
    price_change_24h: Optional[float]
    liquidity: Optional[float]
    volume_24h: Optional[float]
    market_cap: Optional[float]
    created_at: Optional[str]
    total_supply: Optional[int]
    decimals: Optional[int]
    holder_count: Optional[int]

class SolanaTokenAnalysisPrompt(TypedDict):
    """TypedDict for the Solana token analysis prompt structure"""
    system_message: str
    user_message: str
    examples: List[Dict[str, Any]]
    parameters: Dict[str, Any]

def get_solana_token_analysis_prompt(
    token_data: SolanaTokenData,
    include_technical_analysis: bool = True,
    include_social_metrics: bool = False
) -> SolanaTokenAnalysisPrompt:
    """
    Generate a prompt for analyzing a specific Solana token
    
    Args:
        token_data: Data about the token to analyze
        include_technical_analysis: Whether to include technical analysis in the prompt
        include_social_metrics: Whether to include social media metrics in the prompt
        
    Returns:
        A structured prompt for Solana token analysis
    """
    logger.info(f"Generating token analysis prompt for {token_data['symbol']}")
    
    # Define the system message
    system_message = """
You are a cryptocurrency analyst specializing in Solana tokens. Your task is to analyze a specific token
based on the provided data and give an assessment of its potential and risks.

Your analysis should include:

1. TOKEN OVERVIEW
   - Basic information about the token
   - Purpose and use case (if discernible from the name or other information)

2. METRICS ANALYSIS
   - Price analysis
   - Liquidity assessment (is it sufficient?)
   - Volume analysis (is there healthy trading activity?)
   - Market cap evaluation (if available)

3. RISK ASSESSMENT
   - Identify potential red flags
   - Assess liquidity risks
   - Evaluate price manipulation risks
   - Consider age of token (newer tokens are generally riskier)

4. POTENTIAL EVALUATION
   - Assess growth potential
   - Evaluate market positioning
   - Consider uniqueness factors

5. CONCLUSION
   - Provide a RISK SCORE on a scale of 1-10 (1 = lowest risk, 10 = highest risk)
   - Provide a POTENTIAL SCORE on a scale of 1-10 (1 = lowest potential, 10 = highest potential)
   - Give a clear RECOMMENDATION (Avoid, High Risk, Speculative, Interesting, Promising)
   - List specific RED FLAGS in bullet points

Remember that Solana tokens, especially newly launched ones, can be extremely volatile and risky.
Be appropriately cautious in your assessment, and highlight both positive aspects and concerns.

Format your response with clear headings and structured sections. Use bullet points where appropriate.
"""

    # Create a user message that includes key token data
    # Format price and other numeric values for better readability
    price_str = f"${token_data['price']:.6f}" if token_data.get('price') is not None else "Unknown"
    price_change_str = f"{token_data['price_change_24h']:.2f}%" if token_data.get('price_change_24h') is not None else "Unknown"
    liquidity_str = f"${token_data['liquidity']:,.2f}" if token_data.get('liquidity') is not None else "Unknown"
    volume_str = f"${token_data['volume_24h']:,.2f}" if token_data.get('volume_24h') is not None else "Unknown"
    market_cap_str = f"${token_data['market_cap']:,.2f}" if token_data.get('market_cap') is not None else "Unknown"
    
    # Format creation date
    created_at_str = "Unknown"
    if token_data.get('created_at'):
        try:
            # Try to parse the date string and format it
            if 'T' in token_data['created_at']:
                created_date = datetime.fromisoformat(token_data['created_at'].replace('Z', '+00:00'))
                created_at_str = created_date.strftime("%Y-%m-%d %H:%M:%S UTC")
            else:
                created_at_str = token_data['created_at']
        except (ValueError, TypeError):
            created_at_str = token_data['created_at']
    
    user_message = f"""
Please analyze the following Solana token:

TOKEN INFORMATION:
- Name: {token_data['name']}
- Symbol: {token_data['symbol']}
- Address: {token_data['address']}
- Mint Address: {token_data['mint']}
- Created: {created_at_str}

KEY METRICS:
- Current Price: {price_str}
- 24h Price Change: {price_change_str}
- Liquidity: {liquidity_str}
- 24h Trading Volume: {volume_str}
- Market Cap: {market_cap_str}
"""

    if token_data.get('total_supply') is not None:
        user_message += f"- Total Supply: {token_data['total_supply']:,}\n"
    
    if token_data.get('decimals') is not None:
        user_message += f"- Decimals: {token_data['decimals']}\n"
    
    if token_data.get('holder_count') is not None:
        user_message += f"- Holder Count: {token_data['holder_count']:,}\n"
    
    user_message += """
Please provide a comprehensive analysis of this token, including:
1. An overview of the token
2. Analysis of its key metrics
3. Risk assessment
4. Potential evaluation
5. A clear conclusion with RISK SCORE, POTENTIAL SCORE, and RECOMMENDATION

Be sure to highlight any RED FLAGS that investors should be aware of.
"""

    if include_technical_analysis:
        user_message += "\nPlease include technical analysis of the price action if sufficient data is available.\n"
    
    if include_social_metrics:
        user_message += "\nPlease consider potential social media activity and community engagement in your assessment.\n"

    # Example response structure
    examples = [
        {
            "structure": {
                "overview": "Brief overview of the token",
                "metrics_analysis": "Analysis of key metrics",
                "risk_assessment": "Evaluation of risks",
                "potential_evaluation": "Assessment of growth potential",
                "conclusion": {
                    "risk_score": 7,
                    "potential_score": 6,
                    "recommendation": "Speculative",
                    "red_flags": ["Low liquidity", "Recently created", "Unknown team"]
                }
            }
        }
    ]

    # Parameters for the API call
    parameters = {
        "token_address": token_data['address'],
        "include_technical_analysis": include_technical_analysis,
        "include_social_metrics": include_social_metrics,
        "temperature": 0.5,  # Lower temperature for more factual analysis
        "max_tokens": 2000  # Detailed analysis requires more tokens
    }

    logger.info(f"Token analysis prompt generated for {token_data['symbol']}")
    
    return {
        "system_message": system_message,
        "user_message": user_message,
        "examples": examples,
        "parameters": parameters
    }

def get_solana_hot_pairs_prompt(
    limit: int = 10,
    include_details: bool = True,
    filter_by_volume: Optional[float] = None
) -> SolanaTokenAnalysisPrompt:
    """
    Generate a prompt for analyzing hot trading pairs on Solana
    
    Args:
        limit: Maximum number of pairs to analyze
        include_details: Whether to include detailed analysis for each pair
        filter_by_volume: Minimum 24h volume to include (in USD)
        
    Returns:
        A structured prompt for hot pairs analysis
    """
    logger.info(f"Generating hot pairs analysis prompt for Solana with limit: {limit}")
    
    # Define the system message
    system_message = """
You are a cryptocurrency market analyst specializing in Solana tokens. Your task is to analyze the
current hot trading pairs on the Solana blockchain and provide insights about market trends and
potential opportunities.

Your analysis should include:

1. MARKET OVERVIEW
   - General assessment of the Solana token market
   - Current trends and patterns
   - Notable observations about the hot pairs

2. HOT PAIRS ANALYSIS
   - Brief analysis of each hot pair
   - Comparison of metrics across pairs
   - Identification of standout tokens

3. OPPORTUNITY ASSESSMENT
   - Potential opportunities among the hot pairs
   - Risk factors to consider
   - Comparative ranking of the pairs

4. CONCLUSION
   - Summary of findings
   - Key takeaways for traders and investors
   - Watchlist recommendations

Remember that hot pairs can be volatile and high-risk. Be appropriately cautious in your assessment,
and highlight both positive aspects and concerns for each pair.

Format your response with clear headings and structured sections. Use bullet points and tables where appropriate.
"""

    # Create a user message
    volume_filter = f" with minimum 24h volume of ${filter_by_volume:,.2f}" if filter_by_volume else ""
    detail_request = " Please include detailed metrics and analysis for each pair." if include_details else " Provide a summary overview rather than detailed analysis of each pair."
    
    user_message = f"""
Please analyze the top {limit} hot trading pairs on the Solana blockchain{volume_filter}.

For each pair, consider:
- Price and price movement
- Trading volume and liquidity
- Age of the token/pair
- Potential use case or category
- Risk factors

{detail_request}

Conclude with a summary of the current Solana market trends based on these hot pairs, and identify any
tokens that might be particularly interesting for further research (with appropriate risk disclaimers).
"""

    # Example response structure
    examples = [
        {
            "structure": {
                "market_overview": "General assessment of Solana market",
                "hot_pairs_analysis": [
                    {
                        "pair": "TOKEN/SOL",
                        "price": "$0.12345",
                        "volume": "$123,456",
                        "liquidity": "$234,567",
                        "analysis": "Brief analysis of this pair"
                    }
                ],
                "opportunity_assessment": "Analysis of potential opportunities",
                "conclusion": "Summary and recommendations"
            }
        }
    ]

    # Parameters for the API call
    parameters = {
        "chain_id": "solana",
        "endpoint_type": "hot_pairs",
        "limit": limit,
        "include_details": include_details,
        "filter_by_volume": filter_by_volume,
        "plan": "trial",
        "temperature": 0.7,
        "max_tokens": 2000
    }

    logger.info(f"Hot pairs prompt generated with parameters: {parameters}")
    
    return {
        "system_message": system_message,
        "user_message": user_message,
        "examples": examples,
        "parameters": parameters
    }

def get_solana_new_tokens_prompt(
    max_age_hours: int = 24,
    limit: int = 10,
    min_liquidity: Optional[float] = 5000
) -> SolanaTokenAnalysisPrompt:
    """
    Generate a prompt for analyzing newly created tokens on Solana
    
    Args:
        max_age_hours: Maximum age of tokens to include (in hours)
        limit: Maximum number of tokens to analyze
        min_liquidity: Minimum liquidity to include (in USD)
        
    Returns:
        A structured prompt for new tokens analysis
    """
    logger.info(f"Generating new tokens analysis prompt for Solana (max age: {max_age_hours}h, limit: {limit})")
    
    # Define the system message
    system_message = """
You are a cryptocurrency analyst specializing in identifying promising new token launches on the Solana blockchain.
Your task is to analyze recently created tokens and assess their potential and risks.

Your analysis should include:

1. NEW TOKEN LANDSCAPE
   - Overview of recent token launches on Solana
   - Trends in new token categories or themes
   - General quality assessment of recent launches

2. INDIVIDUAL TOKEN ANALYSIS
   - Brief analysis of each new token
   - Initial metrics assessment (price, liquidity, volume)
   - Red flags identification
   - Potential use case or category

3. RISK ASSESSMENT
   - Common risk factors across new tokens
   - Specific risks for highlighted tokens
   - Liquidity and rugpull risk evaluation

4. OPPORTUNITY IDENTIFICATION
   - Potential gems among the new tokens
   - Comparative ranking of opportunities
   - Factors that distinguish promising projects

5. CONCLUSION
   - Summary of findings
   - Watchlist recommendations
   - Risk management advice for new token investments

Remember that newly launched tokens are extremely high-risk investments. Be appropriately cautious in your
assessment, and emphasize the speculative nature of these opportunities. Highlight both potential and significant risks.

Format your response with clear headings and structured sections. Use bullet points and tables where appropriate.
"""

    # Create a user message
    liquidity_filter = f" with minimum liquidity of ${min_liquidity:,.2f}" if min_liquidity else ""
    
    user_message = f"""
Please analyze the top {limit} newly created tokens on Solana from the past {max_age_hours} hours{liquidity_filter}.

For each token, consider:
- Initial price and price movement
- Initial liquidity and volume
- Potential use case or category based on name and any available information
- Red flags or concerning patterns
- Comparative potential versus other new launches

Provide a detailed analysis of the most interesting tokens, and a briefer overview of the others.

Conclude with a summary of the current trends in new Solana token launches, and identify any tokens
that might be worth adding to a watchlist for further research (with appropriate risk disclaimers).
"""

    # Example response structure
    examples = [
        {
            "structure": {
                "new_token_landscape": "Overview of recent Solana token launches",
                "individual_token_analysis": [
                    {
                        "token": "TOKEN (TKN)",
                        "created": "2023-06-15 14:30 UTC",
                        "initial_price": "$0.00123",
                        "current_price": "$0.00456",
                        "liquidity": "$12,345",
                        "volume": "$6,789",
                        "analysis": "Brief analysis of this token",
                        "red_flags": ["Flag 1", "Flag 2"],
                        "potential": "Assessment of potential"
                    }
                ],
                "risk_assessment": "Analysis of risks across new tokens",
                "opportunity_identification": "Potential opportunities among new tokens",
                "conclusion": "Summary and recommendations"
            }
        }
    ]

    # Parameters for the API call
    parameters = {
        "chain_id": "solana",
        "endpoint_type": "new_tokens",
        "max_age_hours": max_age_hours,
        "limit": limit,
        "min_liquidity": min_liquidity,
        "plan": "trial",
        "temperature": 0.7,
        "max_tokens": 2500
    }

    logger.info(f"New tokens prompt generated with parameters: {parameters}")
    
    return {
        "system_message": system_message,
        "user_message": user_message,
        "examples": examples,
        "parameters": parameters
    }

# Example usage
if __name__ == "__main__":
    # Example token data
    example_token_data: SolanaTokenData = {
        "name": "Example Token",
        "symbol": "EX",
        "address": "ExampleAddress123",
        "mint": "ExampleMint123",
        "price": 0.00123,
        "price_change_24h": 5.67,
        "liquidity": 10000,
        "volume_24h": 5000,
        "market_cap": 100000,
        "created_at": "2023-06-15T14:30:00Z",
        "total_supply": 1000000000,
        "decimals": 9,
        "holder_count": 100
    }
    
    # Generate example prompts
    token_prompt = get_solana_token_analysis_prompt(example_token_data)
    hot_pairs_prompt = get_solana_hot_pairs_prompt(limit=5)
    new_tokens_prompt = get_solana_new_tokens_prompt(max_age_hours=24, limit=5)
    
    print("Example prompts generated successfully!")
    print(f"Token analysis prompt length: {len(token_prompt['system_message']) + len(token_prompt['user_message'])}")
    print(f"Hot pairs prompt length: {len(hot_pairs_prompt['system_message']) + len(hot_pairs_prompt['user_message'])}")
    print(f"New tokens prompt length: {len(new_tokens_prompt['system_message']) + len(new_tokens_prompt['user_message'])}") 