#!/usr/bin/env python3
"""
Test script for DexTools API
"""

import asyncio
import json
import logging
from dextools_python import AsyncDextoolsAPIV2

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('test_dextools_api')

async def test_api():
    """Test the DexTools API"""
    logger.info("Initializing DexTools API client with trial plan")
    client = AsyncDextoolsAPIV2(api_key="", plan="trial")
    
    # Test get_blockchains
    logger.info("Testing get_blockchains")
    try:
        blockchains = await client.get_blockchains()
        logger.info(f"Response type: {type(blockchains)}")
        if blockchains:
            logger.info(f"Response keys: {blockchains.keys() if isinstance(blockchains, dict) else 'Not a dict'}")
            print(json.dumps(blockchains, indent=2)[:1000] + "...")  # Print first 1000 chars
    except Exception as e:
        logger.error(f"Error in get_blockchains: {str(e)}")
    
    # Test get_ranking_hotpools
    logger.info("Testing get_ranking_hotpools for Solana")
    try:
        hotpools = await client.get_ranking_hotpools("solana")
        logger.info(f"Response type: {type(hotpools)}")
        if hotpools:
            logger.info(f"Response keys: {hotpools.keys() if isinstance(hotpools, dict) else 'Not a dict'}")
            print(json.dumps(hotpools, indent=2)[:1000] + "...")  # Print first 1000 chars
    except Exception as e:
        logger.error(f"Error in get_ranking_hotpools: {str(e)}")
    
    # Test get_pools
    logger.info("Testing get_pools for Solana")
    try:
        # Current time in milliseconds
        import time
        current_time = int(time.time() * 1000)
        two_days_ago = current_time - (2 * 24 * 60 * 60 * 1000)
        
        pools = await client.get_pools(
            chain="solana",
            from_=two_days_ago,
            to=current_time,
            sort="creationTime",
            order="desc"
        )
        logger.info(f"Response type: {type(pools)}")
        if pools:
            logger.info(f"Response keys: {pools.keys() if isinstance(pools, dict) else 'Not a dict'}")
            print(json.dumps(pools, indent=2)[:1000] + "...")  # Print first 1000 chars
    except Exception as e:
        logger.error(f"Error in get_pools: {str(e)}")

async def main():
    """Main function"""
    await test_api()

if __name__ == "__main__":
    asyncio.run(main()) 