# DexTools API Demo

This repository contains a demonstration of integrating with the DexTools API to fetch cryptocurrency token data from the Solana blockchain.

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

## Current Status and Known Issues

During our testing, we encountered several issues with the DexTools API:

1. **API Connectivity Issues**: All API endpoints we tried returned 404 errors, suggesting that either:
   - The API endpoints have changed since the documentation was written
   - The API requires additional authentication or setup
   - The API may have usage restrictions based on IP address or other factors

2. **Documentation Access Issues**: We were unable to access the API documentation at https://developer.dextools.io/docs/start due to Cloudflare security restrictions.

3. **Website Access Issues**: Direct access to the DexTools website was also blocked by Cloudflare security measures.

### Troubleshooting Steps Taken

1. Verified the API key format and inclusion in request headers
2. Tried multiple different API endpoints based on common API patterns
3. Attempted direct curl requests to the API
4. Checked for documentation access to verify endpoints

### Next Steps for API Integration

To successfully integrate with the DexTools API, the following steps are recommended:

1. Contact DexTools support to verify API access and correct endpoints
2. Request updated API documentation or examples
3. Verify if there are any IP restrictions or additional authentication requirements
4. Consider using a browser-based approach to understand the API by inspecting network requests on the DexTools website

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

After resolving API connectivity issues, consider:
1. Implementing data storage in a database
2. Adding token evaluation logic
3. Integrating with social media APIs
4. Building a user interface

## License

MIT 