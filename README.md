# DexTools Solana API Demo

A simple Python script to demonstrate connectivity with the DexTools API, specifically for fetching data from the Solana blockchain.

## Features

- Tests API connectivity
- Fetches hot trading pairs on Solana
- Gets detailed information about specific pairs
- Retrieves popular tokens on Solana

## Requirements

- Python 3.6+
- `requests` library
- `python-dotenv` library

## Installation

1. Clone this repository
2. Install the required packages:

```bash
pip install requests python-dotenv
```

3. Copy the `.env.example` file to `.env`:

```bash
cp .env.example .env
```

4. Edit the `.env` file and add your DexTools API key:

```
DEXTOOLS_API_KEY=your_actual_api_key_here
```

## Usage

Simply run the script:

```bash
python dextools_demo.py
```

The script will:
1. Test API connectivity
2. Fetch hot pairs on Solana
3. Get detailed information about the first hot pair
4. Retrieve popular tokens on Solana

All results will be displayed in the console.

## Troubleshooting

If you encounter issues:

1. Verify your API key is correct
2. Check your internet connection
3. The DexTools API might have changed - inspect network requests on the DexTools website to understand the current API structure
4. The script tries multiple possible endpoints and chain IDs for Solana, as the exact values may change

## Note

This script includes retry logic and fallback mechanisms to handle potential API changes or Cloudflare restrictions. It attempts to mimic browser behavior to improve success rates. 