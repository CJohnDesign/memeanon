# DexTools API Demo

This repository contains a simple demonstration of integrating with the DexTools API to fetch cryptocurrency token data from the Solana blockchain.

## Overview

The demo shows how to:
1. Connect to the DexTools API
2. Fetch recently created token pools on Solana
3. Get detailed information about specific pools
4. Retrieve historical price data
5. Display all data in the console

## Prerequisites

- DexTools API key (obtain from [DexTools Developer Portal](https://developer.dextools.io/))
- Node.js (for JavaScript implementation)
- Python 3.7+ (for Python implementation)

## Setup

1. Clone this repository
2. Create a `.env` file in the root directory with your API key:
   ```
   DEXTOOLS_API_KEY=your_api_key_here
   ```

## JavaScript Implementation

### Installation

```bash
npm install axios dotenv
```

### Running the Demo

```bash
node dextools-demo.js
```

## Python Implementation

### Installation

```bash
pip install requests python-dotenv
```

### Running the Demo

```bash
python dextools_demo.py
```

## Expected Output

Both implementations will output:
1. A list of recently created token pools on Solana
2. Detailed information about the most recent pool
3. Price data for the most recent pool over the last 24 hours

All data will be displayed in the console as formatted JSON.

## Implementation Details

### JavaScript Version
- Uses axios for HTTP requests
- Simple promise-based async/await structure
- Basic error handling

### Python Version
- Uses requests library for HTTP requests
- Implements TypedDict for proper type hinting
- Comprehensive logging
- Structured error handling

## Next Steps

After confirming successful API connectivity, consider:
1. Implementing data storage in a database
2. Adding token evaluation logic
3. Integrating with social media APIs
4. Building a user interface

## License

MIT 