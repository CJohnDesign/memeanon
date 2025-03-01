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
    console.log('Fetching recent Solana pools...');
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
    console.log(`Fetching info for pool: ${poolAddress}...`);
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
    console.log(`Fetching price data for pool: ${poolAddress}...`);
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
      console.log(`\nSelected pool for detailed analysis: ${firstPoolAddress}`);
      
      // Step 3: Get detailed info for this pool
      await getPoolInfo(firstPoolAddress);
      
      // Step 4: Get price data for this pool
      await getPoolPriceData(firstPoolAddress);
    } else {
      console.warn('No pools found or API returned an error');
    }
    
    console.log('\nDemo completed successfully!');
  } catch (error) {
    console.error('Demo failed:', error.message);
  }
}

// Run the demo
runDemo(); 