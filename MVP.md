# DexTools API Integration MVP

This document outlines a minimal viable product (MVP) for integrating with the DexTools API to fetch cryptocurrency token data and display it in the console.

## Overview

The MVP demonstrates basic API connectivity with DexTools to retrieve token data from the Solana blockchain. This serves as a proof of concept for the Crypto Discovery Bot's token discovery capabilities.

## Implementation

### 1. Setup

```bash
# Install required dependencies
npm install axios dotenv
```

Create a `.env` file to store your API key:
```
DEXTOOLS_API_KEY=your_api_key_here
```

### 2. API Integration Script

Create a file named `dextools-demo.js`:

```javascript
require('dotenv').config();
const axios = require('axios');

// DexTools API configuration
const API_KEY = process.env.DEXTOOLS_API_KEY;
const BASE_URL = 'https://api.dextools.io/v1';

// Headers for authentication
const headers = {
  'X-API-Key': API_KEY,
  'Accept': 'application/json'
};

// Function to fetch recently created pools on Solana
async function getRecentSolanaPools() {
  try {
    const response = await axios.get(`${BASE_URL}/pool/solana/created`, {
      headers,
      params: {
        limit: 10,  // Fetch 10 most recent pools
        sort: 'created'  // Sort by creation date
      }
    });
    
    console.log('Recent Solana Pools:');
    console.log(JSON.stringify(response.data, null, 2));
    
    return response.data;
  } catch (error) {
    console.error('Error fetching recent Solana pools:', error.message);
    if (error.response) {
      console.error('Response data:', error.response.data);
      console.error('Response status:', error.response.status);
    }
    throw error;
  }
}

// Function to get detailed information about a specific pool
async function getPoolInfo(poolAddress) {
  try {
    const response = await axios.get(`${BASE_URL}/pool/solana/${poolAddress}/info`, {
      headers
    });
    
    console.log(`Pool Info for ${poolAddress}:`);
    console.log(JSON.stringify(response.data, null, 2));
    
    return response.data;
  } catch (error) {
    console.error(`Error fetching pool info for ${poolAddress}:`, error.message);
    throw error;
  }
}

// Function to get price data for a specific pool
async function getPoolPriceData(poolAddress) {
  try {
    const response = await axios.get(`${BASE_URL}/pool/solana/${poolAddress}/prices`, {
      headers,
      params: {
        from: Math.floor(Date.now() / 1000) - 86400,  // Last 24 hours
        to: Math.floor(Date.now() / 1000)
      }
    });
    
    console.log(`Price Data for ${poolAddress}:`);
    console.log(JSON.stringify(response.data, null, 2));
    
    return response.data;
  } catch (error) {
    console.error(`Error fetching price data for ${poolAddress}:`, error.message);
    throw error;
  }
}

// Main function to run the demo
async function runDemo() {
  console.log('Starting DexTools API Demo...');
  
  try {
    // Step 1: Get recent pools
    const recentPools = await getRecentSolanaPools();
    
    // Step 2: If we have pools, get details for the first one
    if (recentPools && recentPools.data && recentPools.data.length > 0) {
      const firstPoolAddress = recentPools.data[0].id;
      
      // Step 3: Get detailed info for this pool
      await getPoolInfo(firstPoolAddress);
      
      // Step 4: Get price data for this pool
      await getPoolPriceData(firstPoolAddress);
    }
    
    console.log('Demo completed successfully!');
  } catch (error) {
    console.error('Demo failed:', error.message);
  }
}

// Run the demo
runDemo();
```

### 3. Running the Demo

Execute the script to see the API in action:

```bash
node dextools-demo.js
```

## Expected Output

The script will output:
1. A list of recently created token pools on Solana
2. Detailed information about the most recent pool
3. Price data for the most recent pool over the last 24 hours

All data will be displayed in the console as JSON.

## Next Steps

After confirming successful API connectivity, the next steps would be:

1. Implement proper data parsing and storage in a database
2. Add evaluation logic based on the metrics defined in the PRD
3. Integrate with Twitter API for social validation
4. Develop the tweet composition and posting functionality

This MVP serves as proof that we can successfully retrieve the necessary data from DexTools to power the Crypto Discovery Bot. 