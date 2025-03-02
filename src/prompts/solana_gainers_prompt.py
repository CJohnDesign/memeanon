#!/usr/bin/env python3
"""
Solana Gainers Analysis Prompt

This file contains the prompt for analyzing top gaining tokens on the Solana blockchain.
It provides structured prompts for analyzing gainers data from the DexTools API.
"""

import logging
from typing import TypedDict, Dict, List, Any, Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('solana_gainers_prompt')

class SolanaGainersPrompt(TypedDict):
    """TypedDict for the Solana gainers analysis prompt structure"""
    system_message: str
    user_message: str
    examples: List[Dict[str, Any]]
    parameters: Dict[str, Any]

def get_solana_gainers_prompt(
    limit: int = 10,
    include_technical_analysis: bool = True,
    include_risk_assessment: bool = True
) -> SolanaGainersPrompt:
    """
    Generate a prompt for analyzing top gaining tokens on Solana
    
    Args:
        limit: Maximum number of tokens to analyze
        include_technical_analysis: Whether to include technical analysis
        include_risk_assessment: Whether to include risk assessment
        
    Returns:
        A structured prompt for analyzing Solana gainers
    """
    
    # Define the system message
    system_message = """
You are a cryptocurrency analyst specializing in Solana tokens. Your task is to analyze top gaining tokens on the Solana blockchain
and provide insights about their potential and risks. Focus on identifying promising tokens with good metrics while
highlighting potential red flags and risks.

When analyzing tokens, consider the following factors:
1. Price action - Analyze the price movement and whether it's sustainable
2. Volume - Check if the volume supports the price action
3. Liquidity - Higher is better, minimum $10K is recommended
4. Creation time - Newer tokens are generally riskier
5. Exchange information - Which DEX the token is trading on
6. Token utility and purpose - Based on the name and any available information

Present your analysis in a clear, structured Markdown format with the following sections:
- Executive Summary: Brief overview of the top gainers and market trends
- Top Gainers Analysis: Detailed analysis of each top gainer, including:
  - Token name and symbol
  - Price and price change
  - Trading volume and liquidity
  - Creation date
  - Exchange information
  - Potential utility (based on name/symbol)
  - Risk assessment
- Market Trends: Identify patterns across the top gainers
- Investment Opportunities: Highlight tokens that might be worth further research
- Risk Warnings: Highlight common red flags and risks

Your analysis should be balanced, highlighting both potential opportunities and risks. Be specific about why certain tokens
might be interesting or concerning. Use bullet points and tables where appropriate to make the information easy to digest.
"""

    # Define the user message
    user_message = f"""
Please analyze the following top {limit} gaining tokens on the Solana blockchain. 

For each token, provide:
1. A brief overview of what the token might be (based on its name and symbol)
2. An analysis of its price movement and whether it appears sustainable
3. An assessment of its trading volume and liquidity
4. Information about when it was created and which exchange it's trading on
5. A risk rating (Low, Medium, High, Very High) with explanation

{"Include technical analysis for tokens showing interesting patterns." if include_technical_analysis else ""}
{"Provide a detailed risk assessment for each token, highlighting potential red flags." if include_risk_assessment else ""}

Conclude with an overall market trend analysis and any investment opportunities or warnings.

Here is the data:
"""

    # Define example analyses (optional)
    examples = []
    
    # Define parameters
    parameters = {
        "limit": limit,
        "include_technical_analysis": include_technical_analysis,
        "include_risk_assessment": include_risk_assessment,
        "temperature": 0.7,
        "max_tokens": 4000
    }
    
    return {
        "system_message": system_message,
        "user_message": user_message,
        "examples": examples,
        "parameters": parameters
    } 