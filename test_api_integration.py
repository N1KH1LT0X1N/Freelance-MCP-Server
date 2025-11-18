#!/usr/bin/env python3
"""
Test script for Freelance MCP Server Real API Integration

This script tests the real API clients for Upwork and Freelancer.com
to ensure they are properly configured and working.

Usage:
    python test_api_integration.py
"""

import asyncio
import os
import sys
from datetime import datetime

from dotenv import load_dotenv

# Load environment variables
load_dotenv()

print("=" * 80)
print("Freelance MCP Server - API Integration Test")
print("=" * 80)
print()


def check_env_var(var_name: str, required: bool = False) -> bool:
    """Check if environment variable is set"""
    value = os.getenv(var_name)
    status = "✅" if value else ("❌" if required else "⚠️")
    display_value = "***" if value and "TOKEN" in var_name or "SECRET" in var_name else (value or "Not set")

    print(f"{status} {var_name}: {display_value}")
    return bool(value)


print("1. Checking Environment Variables")
print("-" * 80)

# Check Groq API (required for AI features)
groq_ok = check_env_var("GROQ_API_KEY", required=True)

# Check Upwork API
print("\nUpwork API:")
upwork_client_id = check_env_var("UPWORK_CLIENT_ID")
upwork_client_secret = check_env_var("UPWORK_CLIENT_SECRET")
upwork_access_token = check_env_var("UPWORK_ACCESS_TOKEN")
upwork_refresh_token = check_env_var("UPWORK_REFRESH_TOKEN")
upwork_ok = upwork_access_token  # At minimum need access token

# Check Freelancer.com API
print("\nFreelancer.com API:")
freelancer_client_id = check_env_var("FREELANCER_CLIENT_ID")
freelancer_client_secret = check_env_var("FREELANCER_CLIENT_SECRET")
freelancer_oauth_token = check_env_var("FREELANCER_OAUTH_TOKEN")
freelancer_ok = freelancer_oauth_token  # At minimum need OAuth token

print()
print("=" * 80)
print()

# Summary
if upwork_ok or freelancer_ok:
    print("✅ At least one platform API is configured")
else:
    print("⚠️ No platform APIs configured - will use mock data")
    print("   To use real data, configure at least one platform's API keys in .env")
    print()

# Test API clients if available
print("2. Testing API Client Modules")
print("-" * 80)

try:
    from freelance_api_clients import (
        FreelanceAPIAggregator,
        SearchCriteria,
        UpworkAPIClient,
        FreelancerAPIClient,
        search_freelance_gigs
    )
    print("✅ API client modules imported successfully")
    api_clients_available = True
except ImportError as e:
    print(f"❌ Failed to import API clients: {e}")
    print("   Run: pip install -r requirements.txt")
    api_clients_available = False
    sys.exit(1)

print()
print("=" * 80)
print()


async def test_platform_clients():
    """Test individual platform clients"""
    print("3. Testing Platform Clients")
    print("-" * 80)

    results = {
        "upwork": False,
        "freelancer": False
    }

    # Test Upwork
    if upwork_ok:
        print("\nTesting Upwork API Client...")
        try:
            upwork_client = UpworkAPIClient()
            if upwork_client.authenticate():
                print("✅ Upwork: Authentication successful")

                # Test search
                criteria = SearchCriteria(
                    skills=["Python", "API"],
                    limit=3
                )
                gigs = await upwork_client.search_gigs(criteria)

                if gigs:
                    print(f"✅ Upwork: Found {len(gigs)} gigs")
                    results["upwork"] = True

                    # Show sample gig
                    if gigs:
                        sample = gigs[0]
                        print(f"\n   Sample Gig:")
                        print(f"   Title: {sample.title}")
                        print(f"   Budget: {sample.budget}")
                        print(f"   Platform: {sample.platform}")
                else:
                    print("⚠️ Upwork: No gigs found (this might be normal)")
                    results["upwork"] = True  # Still counts as success
            else:
                print("❌ Upwork: Authentication failed")
        except Exception as e:
            print(f"❌ Upwork: Error - {e}")
    else:
        print("\n⚠️ Upwork: Skipped (no credentials configured)")

    # Test Freelancer.com
    if freelancer_ok:
        print("\nTesting Freelancer.com API Client...")
        try:
            freelancer_client = FreelancerAPIClient()
            if freelancer_client.authenticate():
                print("✅ Freelancer.com: Authentication successful")

                # Test search
                criteria = SearchCriteria(
                    skills=["Python", "Web Development"],
                    limit=3
                )
                gigs = await freelancer_client.search_gigs(criteria)

                if gigs:
                    print(f"✅ Freelancer.com: Found {len(gigs)} gigs")
                    results["freelancer"] = True

                    # Show sample gig
                    if gigs:
                        sample = gigs[0]
                        print(f"\n   Sample Gig:")
                        print(f"   Title: {sample.title}")
                        print(f"   Budget: {sample.budget}")
                        print(f"   Platform: {sample.platform}")
                else:
                    print("⚠️ Freelancer.com: No gigs found (this might be normal)")
                    results["freelancer"] = True  # Still counts as success
            else:
                print("❌ Freelancer.com: Authentication failed")
        except Exception as e:
            print(f"❌ Freelancer.com: Error - {e}")
    else:
        print("\n⚠️ Freelancer.com: Skipped (no credentials configured)")

    print()
    print("=" * 80)
    print()

    return results


async def test_aggregator():
    """Test the aggregator that searches all platforms"""
    print("4. Testing API Aggregator")
    print("-" * 80)

    try:
        print("\nSearching all available platforms for Python gigs...")

        results = await search_freelance_gigs(
            skills=["Python", "Django", "REST API"],
            max_budget=5000,
            project_type="fixed_price",
            limit=5
        )

        print(f"\n✅ Aggregator search completed")
        print(f"   Total gigs found: {results['total_found']}")
        print(f"   Platforms searched: {results['platforms_searched']}")

        if results['gigs']:
            print(f"\n   Top 3 Results:")
            for i, gig in enumerate(results['gigs'][:3], 1):
                print(f"\n   {i}. {gig['title']}")
                print(f"      Platform: {gig['platform']}")
                print(f"      Budget: {gig['budget']}")
                print(f"      Match Score: {gig['match_score']*100:.1f}%")
                print(f"      URL: {gig['url']}")

        return True

    except Exception as e:
        print(f"❌ Aggregator test failed: {e}")
        return False


async def test_mcp_server():
    """Test the MCP server search_gigs function"""
    print()
    print("=" * 80)
    print()
    print("5. Testing MCP Server Integration")
    print("-" * 80)

    try:
        # Import the search_gigs function from the server
        from freelance_server import search_gigs

        print("\nTesting search_gigs() with real API...")

        result = await search_gigs(
            skills=["React", "TypeScript"],
            max_budget=3000,
            use_real_api=True
        )

        print(f"\n✅ MCP search_gigs() completed")
        print(f"   Data source: {result.get('data_source', 'unknown')}")
        print(f"   Total found: {result['total_found']}")

        if result.get('data_source') == 'real_api':
            print("\n   🎉 SUCCESS! Real API integration is working!")
        else:
            print("\n   ⚠️ Using mock data (configure API keys for real data)")

        return True

    except Exception as e:
        print(f"❌ MCP server test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """Run all tests"""

    if not api_clients_available:
        print("❌ Cannot proceed - API client modules not available")
        return

    # Test platform clients
    platform_results = await test_platform_clients()

    # Test aggregator
    aggregator_ok = await test_aggregator()

    # Test MCP server
    mcp_ok = await test_mcp_server()

    # Final summary
    print()
    print("=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)
    print()

    upwork_status = "✅ Working" if platform_results.get("upwork") else ("⚠️ Not configured" if not upwork_ok else "❌ Failed")
    freelancer_status = "✅ Working" if platform_results.get("freelancer") else ("⚠️ Not configured" if not freelancer_ok else "❌ Failed")
    aggregator_status = "✅ Working" if aggregator_ok else "❌ Failed"
    mcp_status = "✅ Working" if mcp_ok else "❌ Failed"

    print(f"Upwork API:        {upwork_status}")
    print(f"Freelancer.com:    {freelancer_status}")
    print(f"API Aggregator:    {aggregator_status}")
    print(f"MCP Server:        {mcp_status}")

    print()

    # Overall status
    if any(platform_results.values()) and aggregator_ok and mcp_ok:
        print("🎉 Overall Status: ALL TESTS PASSED!")
        print()
        print("Your Freelance MCP Server is configured correctly and ready to use!")
        print()
        print("Next steps:")
        print("  1. Run the server: python freelance_server.py")
        print("  2. Test search queries with your MCP client")
        print("  3. Monitor API usage in the console")
        return 0
    elif mcp_ok:
        print("✅ Overall Status: BASIC FUNCTIONALITY WORKING")
        print()
        print("The server works but is using mock data.")
        print()
        print("To enable real API data:")
        print("  1. Configure API keys in .env file")
        print("  2. See SETUP_GUIDE.md for detailed instructions")
        print("  3. Re-run this test script")
        return 0
    else:
        print("❌ Overall Status: SOME TESTS FAILED")
        print()
        print("Please review the errors above and:")
        print("  1. Check your .env configuration")
        print("  2. Verify API credentials are valid")
        print("  3. See SETUP_GUIDE.md for troubleshooting")
        print("  4. Enable DEBUG=true in .env for detailed logs")
        return 1


if __name__ == "__main__":
    try:
        exit_code = asyncio.run(main())
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n\n❌ Test interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
