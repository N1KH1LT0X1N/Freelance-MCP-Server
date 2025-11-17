"""
Freelance MCP Client 2 - Simplified Implementation

A lightweight, streamlined MCP client for quick testing of the Freelance MCP Server.

Features:
- Simplified connection handling
- Quick demo mode
- Minimal dependencies
- Easy to understand code structure

Usage:
    python freelance_client2.py
"""

import asyncio
import json
import os
from typing import Any, Dict

from dotenv import load_dotenv
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

# Load environment variables
load_dotenv()


class SimpleFreelanceClient:
    """Simplified MCP Client for quick testing"""

    def __init__(self):
        self.session = None
        self.transport = None

    async def start(self) -> None:
        """Start the client and connect to server"""
        print("🚀 Starting Freelance MCP Client...")

        # Setup server connection
        server_params = StdioServerParameters(
            command="python",
            args=["freelance_server.py", "stdio"],
            env=dict(os.environ)
        )

        # Connect to server
        self.transport = await stdio_client(server_params).__aenter__()
        read, write = self.transport

        # Create session
        self.session = await ClientSession(read, write).__aenter__()
        await self.session.initialize()

        print("✅ Connected to server\n")

    async def stop(self) -> None:
        """Stop the client and disconnect"""
        if self.session:
            await self.session.__aexit__(None, None, None)
        if self.transport:
            await self.transport.__aexit__(None, None, None)
        print("\n👋 Disconnected from server")

    async def call_tool(self, tool_name: str, args: Dict[str, Any]) -> Any:
        """Call a tool and return the result"""
        result = await self.session.call_tool(tool_name, args)

        # Extract text from result
        if hasattr(result, 'content') and result.content:
            for item in result.content:
                if hasattr(item, 'text'):
                    try:
                        return json.loads(item.text)
                    except json.JSONDecodeError:
                        return item.text
        return result

    async def read_resource(self, uri: str) -> str:
        """Read a resource"""
        result = await self.session.read_resource(uri)
        if hasattr(result, 'contents') and result.contents:
            return result.contents[0].text
        return str(result)

    def print_result(self, title: str, result: Any) -> None:
        """Pretty print a result"""
        print(f"\n{'='*60}")
        print(f"  {title}")
        print(f"{'='*60}")
        if isinstance(result, (dict, list)):
            print(json.dumps(result, indent=2))
        else:
            print(result)
        print()

    async def run_quick_demo(self) -> None:
        """Run a quick demonstration of key features"""
        print("🎬 Running Quick Demo\n")

        # 1. Search for Python gigs
        print("1️⃣  Searching for Python gigs...")
        result = await self.call_tool("search_gigs", {
            "skills": ["Python"],
            "max_budget": 1500
        })
        self.print_result("Search Results", result)

        # 2. Create a profile
        print("2️⃣  Creating user profile...")
        profile = {
            "name": "Quick Demo User",
            "title": "Python Developer",
            "hourly_rate_min": 40.0,
            "hourly_rate_max": 70.0,
            "skills": [
                {"name": "Python", "level": "advanced", "years_experience": 4}
            ]
        }
        result = await self.call_tool("create_user_profile", profile)
        self.print_result("Profile Created", result)

        # 3. Analyze profile fit
        print("3️⃣  Analyzing profile fit...")
        profile_id = result.get("profile_id", "demo_user") if isinstance(result, dict) else "demo_user"
        result = await self.call_tool("analyze_profile_fit", {
            "profile_id": profile_id,
            "gig_id": "fiverr_001"
        })
        self.print_result("Profile Fit Analysis", result)

        # 4. Generate proposal (if GROQ key is available)
        if os.getenv("GROQ_API_KEY") and len(os.getenv("GROQ_API_KEY", "")) > 20:
            print("4️⃣  Generating AI proposal...")
            result = await self.call_tool("generate_proposal", {
                "gig_id": "fiverr_001",
                "user_profile": profile,
                "tone": "professional"
            })
            self.print_result("Generated Proposal", result)
        else:
            print("⚠️  Skipping proposal generation (GROQ_API_KEY not configured)")

        # 5. Access market trends
        print("5️⃣  Fetching market trends...")
        trends = await self.read_resource("freelance://market-trends")
        self.print_result("Market Trends", json.loads(trends))

        # 6. Quick code review
        print("6️⃣  Running code review...")
        code = """
def add_numbers(a, b):
    return a + b

result = add_numbers(5, 10)
print(result)
"""
        result = await self.call_tool("code_review", {
            "code_snippet": code,
            "language": "python",
            "review_type": "general"
        })
        self.print_result("Code Review", result)

        print("\n✅ Quick demo completed!")


async def main():
    """Main entry point"""
    client = SimpleFreelanceClient()

    try:
        await client.start()
        await client.run_quick_demo()
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        await client.stop()


if __name__ == "__main__":
    print("""
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║           Freelance MCP Client - Quick Demo                 ║
║                                                              ║
║  A simplified client for testing the Freelance MCP Server   ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
    """)

    asyncio.run(main())
