#!/usr/bin/env python3
"""
DexTools API Demo v2 - Plan Testing
This script tests different plan types with the DexTools API to see which one works with the provided API key.
"""

import os
import json
import asyncio
import logging
from typing import Dict, Any, List
from dotenv import load_dotenv
from dextools_python import AsyncDextoolsAPIV2

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('dextools_v2_plan_test')

# Load environment variables
load_dotenv()

def pretty_print_json(data: Dict[str, Any]) -> None:
    """Print JSON data in a readable format"""
    print(json.dumps(data, indent=2))

async def test_plan(plan: str) -> Dict[str, Any]:
    """
    Test a specific plan type with the DexTools API
    
    Args:
        plan: Plan type to test (free, trial, standard, advanced, pro, partner)
        
    Returns:
        Dict containing test results
    """
    logger.info(f"Testing plan: {plan}")
    
    api_key = os.getenv('DEXTOOLS_API_KEY')
    if not api_key:
        logger.error("API key not found. Please set DEXTOOLS_API_KEY in .env file")
        raise ValueError("API key not found")
    
    client = None
    results = {
        "plan": plan,
        "endpoints_tested": [],
        "successful_endpoints": [],
        "failed_endpoints": []
    }
    
    try:
        # Initialize client with the specified plan
        client = AsyncDextoolsAPIV2(api_key=api_key, plan=plan)
        logger.info(f"Client initialized with plan: {plan}")
        
        # Test endpoints
        endpoints_to_test = [
            {
                "name": "get_blockchains",
                "function": lambda: client.get_blockchains()
            },
            {
                "name": "get_ranking_hotpools (ether)",
                "function": lambda: client.get_ranking_hotpools('ether')
            },
            {
                "name": "get_ranking_gainers (ether)",
                "function": lambda: client.get_ranking_gainers('ether')
            },
            {
                "name": "get_ranking_losers (ether)",
                "function": lambda: client.get_ranking_losers('ether')
            }
        ]
        
        for endpoint in endpoints_to_test:
            endpoint_name = endpoint["name"]
            results["endpoints_tested"].append(endpoint_name)
            
            try:
                logger.info(f"Testing endpoint: {endpoint_name}")
                response = await endpoint["function"]()
                
                # Check if response indicates success
                if isinstance(response, dict) and response.get("statusCode") == 401:
                    logger.warning(f"Endpoint {endpoint_name} failed with unauthorized error")
                    results["failed_endpoints"].append({
                        "name": endpoint_name,
                        "error": "Unauthorized resource",
                        "response": response
                    })
                else:
                    logger.info(f"Endpoint {endpoint_name} succeeded")
                    results["successful_endpoints"].append({
                        "name": endpoint_name,
                        "response": response
                    })
            except Exception as e:
                logger.error(f"Endpoint {endpoint_name} failed with error: {str(e)}")
                results["failed_endpoints"].append({
                    "name": endpoint_name,
                    "error": str(e)
                })
        
        return results
    except Exception as e:
        logger.error(f"Failed to initialize client with plan {plan}: {str(e)}")
        results["error"] = str(e)
        return results
    finally:
        if client:
            await client.close()

async def run_plan_tests() -> None:
    """Run tests for all available plans"""
    logger.info("Starting DexTools API plan tests...")
    
    plans = ["free", "trial", "standard", "advanced", "pro", "partner"]
    all_results = []
    
    for plan in plans:
        try:
            results = await test_plan(plan)
            all_results.append(results)
            
            # Print summary for this plan
            print(f"\n=== Results for plan: {plan} ===")
            print(f"Endpoints tested: {len(results['endpoints_tested'])}")
            print(f"Successful endpoints: {len(results['successful_endpoints'])}")
            print(f"Failed endpoints: {len(results['failed_endpoints'])}")
            
            if results["successful_endpoints"]:
                print("\nSuccessful endpoints:")
                for endpoint in results["successful_endpoints"]:
                    print(f"- {endpoint['name']}")
                    # Print first successful response
                    if endpoint == results["successful_endpoints"][0]:
                        print("Sample response:")
                        pretty_print_json(endpoint["response"])
            
            # Add a delay between plans to avoid rate limiting
            await asyncio.sleep(1)
        except Exception as e:
            logger.error(f"Failed to test plan {plan}: {str(e)}")
    
    # Print overall summary
    print("\n=== Overall Summary ===")
    working_plans = [r["plan"] for r in all_results if r["successful_endpoints"]]
    
    if working_plans:
        print(f"Working plans: {', '.join(working_plans)}")
        print("Recommendation: Use one of the working plans in your application.")
    else:
        print("No working plans found.")
        print("Recommendation: Verify your API key and contact DexTools support.")
    
    logger.info("Plan tests completed.")

if __name__ == "__main__":
    asyncio.run(run_plan_tests()) 