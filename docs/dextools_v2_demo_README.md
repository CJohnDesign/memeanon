# DexTools API Demo v2

This is a Python-based demo for interacting with the DexTools API using the [dextools-python](https://github.com/alb2001/dextools-python) library. The script demonstrates how to fetch cryptocurrency token data from the DexTools API and display it in the console.

## Features

- Fetch supported blockchains
- Get hot pairs/pools for a specific chain
- Get detailed information about specific trading pairs
- Get token information
- Get top gainers and losers
- Get recent pools
- Get price information for pairs

## Prerequisites

- Python 3.6+
- A valid DexTools API key

## Setup

1. Create a virtual environment:
   ```bash
   python -m venv venv
   ```

2. Activate the virtual environment:
   - On Windows:
     ```bash
     venv\Scripts\activate
     ```
   - On macOS/Linux:
     ```bash
     source venv/bin/activate
     ```

3. Install the required packages:
   ```bash
   pip install git+https://github.com/alb2001/dextools-python.git python-dotenv
   ```

4. Create a `.env` file in the root directory with your DexTools API key:
   ```
   DEXTOOLS_API_KEY=your_api_key_here
   ```

## Usage

Run the script:
```bash
python dextools_v2_demo.py
```

## Current Status

### API Connection Success!

We have successfully connected to the DexTools API using the "trial" plan. The API key works with several plan types, but "trial" provides the most complete responses.

### Working Endpoints

The following endpoints are working correctly:
- `get_blockchains`: Returns a list of supported blockchains
- `get_ranking_hotpools`: Returns hot pairs/pools for a specific chain
- `get_ranking_gainers`: Returns top gainers for a specific chain
- `get_ranking_losers`: Returns top losers for a specific chain

### Issues with Some Endpoints

Some endpoints still have issues:
- `get_pools`: The date parameters (from/to) need to be in a specific format that differs from what we're currently using
- Some other endpoints may require specific permissions or additional parameters

## Plan Testing Results

We tested the API key with different plans and found that several plans work:
- free
- trial
- standard
- advanced
- pro

The "partner" plan does not work with the current API key.

## Troubleshooting Tips

1. **Use the Correct Plan**: Make sure to use one of the working plans (trial is recommended):
   ```python
   self.client = AsyncDextoolsAPIV2(api_key=self.api_key, plan="trial")
   ```

2. **Date Format Issues**: When using endpoints that require date parameters, ensure they are in the correct format expected by the API.

3. **API Limits**: Be aware of rate limits that may apply to your API key and plan.

4. **Error Handling**: Implement robust error handling to gracefully handle API errors and rate limiting.

## Library Documentation

The dextools-python library provides the following classes:

- `DextoolsAPI`: Synchronous client for v1 API
- `AsyncDextoolsAPI`: Asynchronous client for v1 API
- `DextoolsAPIV2`: Synchronous client for v2 API
- `AsyncDextoolsAPIV2`: Asynchronous client for v2 API

This demo uses the `AsyncDextoolsAPIV2` class for asynchronous access to the v2 API.

## Next Steps

1. Refine the date parameters for the `get_pools` endpoint to match the expected format.
2. Expand the demo to include more API endpoints.
3. Implement error handling and retry logic for more robust API interactions.
4. Add data processing and visualization for the retrieved data.

## Resources

- [DexTools Website](https://www.dextools.io/)
- [dextools-python GitHub Repository](https://github.com/alb2001/dextools-python) 