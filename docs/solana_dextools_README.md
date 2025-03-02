# Solana DexTools API Integration

This project provides utilities and demos for integrating with the DexTools API specifically for Solana blockchain data. It includes specialized prompt templates for AI-assisted analysis of Solana tokens and trading pairs.

## Features

- Fetch Solana blockchain information from DexTools API
- Get hot trading pairs on Solana with detailed metrics
- Retrieve top gainers and losers on Solana
- Find newly created tokens on Solana within a specified time range
- Analyze specific Solana tokens with detailed metrics
- Generate AI prompts for in-depth token and pair analysis
- Robust error handling with retry logic and rate limit management
- Comprehensive logging throughout the application

## Prerequisites

- Python 3.7+
- DexTools API key with "trial" plan or higher
- Required Python packages (see requirements.txt)

## Setup

1. Clone this repository
2. Install the required packages:
   ```
   pip install -r requirements.txt
   ```
3. Set your DexTools API key as an environment variable:
   ```
   export DEXTOOLS_API_KEY="your_api_key_here"
   ```

## Project Structure

- `solana_dextools_api.py` - Core utility for making Solana-specific API calls
- `solana_dextools_demo.py` - Demo script showcasing the API functionality
- `prompts/solana_token_analysis_prompt.py` - AI prompt templates for Solana token analysis
- `solana_dextools_README.md` - This documentation file

## Usage

### Running the Demo

To run the demo script which showcases all the main features:

```bash
python solana_dextools_demo.py
```

This will:
1. Fetch Solana blockchain information
2. Get hot trading pairs on Solana
3. Retrieve top gainers and losers
4. Find newly created tokens
5. Analyze a specific token

### Using the API Utilities

```python
import asyncio
from solana_dextools_api import SolanaDexToolsAPI

async def example():
    # Initialize the API with your key and the trial plan
    api = SolanaDexToolsAPI(api_key="your_api_key", plan="trial")
    
    # Get hot pairs on Solana
    hot_pairs = await api.get_solana_hot_pairs(limit=5)
    
    # Print the results
    for pair in hot_pairs:
        print(f"{pair['pair_name']}: ${pair['price']}")

# Run the async function
asyncio.run(example())
```

### Using the Prompt Templates

```python
from prompts.solana_token_analysis_prompt import get_solana_token_analysis_prompt, SolanaTokenData

# Create token data
token_data = SolanaTokenData(
    name="Example Token",
    symbol="EX",
    address="ExampleAddress123",
    mint="ExampleMint123",
    price=1.23,
    price_change_24h=5.67,
    liquidity=1000000,
    volume_24h=500000,
    market_cap=10000000,
    created_at="2023-01-01T00:00:00Z",
    total_supply=1000000000,
    decimals=9,
    holder_count=1000
)

# Generate a prompt for token analysis
prompt = get_solana_token_analysis_prompt(token_data)

# The prompt can now be used with an AI model
print(prompt["system_message"])
print(prompt["user_message"])
```

## API Endpoints

The following DexTools API endpoints are supported for Solana:

- `get_solana_blockchains()` - Get information about the Solana blockchain
- `get_solana_hot_pairs(limit)` - Get hot trading pairs on Solana
- `get_solana_gainers(limit)` - Get top gainers on Solana
- `get_solana_losers(limit)` - Get top losers on Solana
- `get_solana_new_tokens(max_age_hours, limit)` - Get newly created tokens on Solana
- `get_solana_token_info(token_address)` - Get detailed information about a specific Solana token

## Prompt Templates

The following prompt templates are available:

- `get_solana_token_analysis_prompt(token_data)` - Generate a prompt for analyzing a specific Solana token
- `get_solana_hot_pairs_prompt(limit, include_details, filter_by_volume)` - Generate a prompt for analyzing hot trading pairs on Solana
- `get_solana_new_tokens_prompt(max_age_hours, limit, min_liquidity)` - Generate a prompt for analyzing newly created tokens on Solana

## Error Handling

The API utilities include robust error handling:

- Automatic retries with exponential backoff for failed API calls
- Rate limit detection and handling
- Comprehensive logging of all API interactions
- Graceful handling of missing or invalid data

## Logging

Logging is configured to output to both console and log files:

- `solana_dextools_api.log` - Logs from the API utility
- `solana_token_analysis.log` - Logs from the prompt templates
- `solana_dextools_demo.log` - Logs from the demo script

## Current Status

The integration has been tested with the DexTools API using the "trial" plan and successfully connects to retrieve Solana blockchain data. The following endpoints are working:

- Blockchain information
- Hot pairs
- Gainers and losers
- New tokens (with proper date formatting)
- Token information

## Troubleshooting

- **API Key Issues**: Ensure your API key is set correctly as an environment variable
- **Rate Limiting**: The DexTools API has rate limits. The utility includes retry logic, but you may need to wait if you hit limits
- **Date Format**: When fetching new tokens, ensure dates are in ISO 8601 format with timezone information
- **Missing Data**: Some token fields may be missing in the API response. The utility handles this gracefully with default values

## Next Steps

- Add support for more Solana-specific endpoints as they become available
- Enhance token analysis with additional on-chain data
- Implement caching to reduce API calls
- Add support for batch operations to analyze multiple tokens efficiently

## Resources

- [DexTools API Documentation](https://docs.dextools.io/)
- [Solana Developer Documentation](https://docs.solana.com/)
- [Python AsyncIO Documentation](https://docs.python.org/3/library/asyncio.html) 