# DexTools Solana API Demo

A simple Python script to demonstrate connectivity with the DexTools API, specifically for fetching data from the Solana blockchain.

## Features

- Tests API connectivity
- Fetches top gaining tokens on Solana (using `/ranking/solana/gainers` endpoint)
- Fetches hot trading pairs on Solana
- Gets detailed information about specific pairs
- Retrieves popular tokens on Solana
- Analyzes Solana gainers using OpenAI's GPT-4o model and saves results as Markdown

## Requirements

- Python 3.6+
- `requests` library
- `python-dotenv` library
- `openai` library

## Installation

1. Clone this repository
2. Install the required packages:

```bash
pip install -r requirements.txt
```

3. Copy the `.env.example` file to `.env`:

```bash
cp .env.example .env
```

4. Edit the `.env` file and add your DexTools API key and OpenAI API key:

```
DEXTOOLS_API_KEY=your_actual_api_key_here
OPENAI_API_KEY=your_openai_api_key_here
```

You can use the example DexTools API key from the curl command for testing: `UFYgd1VSeq7ZdWbPQDEPQ6fuQ63QahNb2n4vntbi`

## Usage

### Basic Demo

Run the basic demo script:

```bash
python dextools_demo.py
```

The script will:
1. Test API connectivity
2. Fetch top gaining tokens on Solana (using the specific endpoint from the curl example)
3. Fetch hot pairs on Solana
4. Get detailed information about the first hot pair
5. Retrieve popular tokens on Solana

All results will be displayed in the console.

### Simple Gainers Script

For a simpler version that only fetches top gaining tokens:

```bash
python solana_gainers.py
```

### GPT Analysis Script

To analyze Solana gainers using OpenAI's GPT-4o model and save the results as a Markdown file:

```bash
python solana_gpt_analysis.py
```

This script will:
1. Fetch top gaining tokens on Solana
2. Format the data for the GPT prompt
3. Analyze the data using OpenAI's GPT-4o model
4. Save the analysis as a Markdown file in the `outputs` directory

## API Endpoints Used

The script primarily uses the following endpoints:

```
https://public-api.dextools.io/trial/v2/ranking/solana/gainers
https://public-api.dextools.io/trial/v2/ranking/solana/hot
https://public-api.dextools.io/trial/v2/tokens/solana/list
https://public-api.dextools.io/trial/v2/pair/solana/{pair_address}
```

## Troubleshooting

If you encounter issues:

1. Verify your API keys are correct
2. Check your internet connection
3. The DexTools API might have changed - inspect network requests on the DexTools website to understand the current API structure
4. The script tries multiple possible endpoints and chain IDs for Solana, as the exact values may change

## Note

This script includes retry logic and fallback mechanisms to handle potential API changes or Cloudflare restrictions. It attempts to mimic browser behavior to improve success rates. 