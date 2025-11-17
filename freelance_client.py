"""
Freelance MCP Client - Comprehensive Implementation

A full-featured async MCP client for testing and demonstrating the Freelance MCP Server.

Features:
- Environment validation
- Demo mode (automated showcase of all features)
- Interactive mode (manual command interface)
- Comprehensive error handling
- Tool and resource access

Usage:
    python freelance_client.py --check-env        # Verify environment setup
    python freelance_client.py --mode demo        # Run automated demo
    python freelance_client.py --mode interactive # Interactive command mode
"""

import asyncio
import argparse
import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from dotenv import load_dotenv
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

# Load environment variables
load_dotenv()


class FreelanceClient:
    """MCP Client for Freelance Gig Aggregator Server"""

    def __init__(self, server_path: str = "freelance_server.py"):
        self.server_path = server_path
        self.session: Optional[ClientSession] = None

    async def connect(self) -> None:
        """Establish connection to the MCP server"""
        server_params = StdioServerParameters(
            command="python",
            args=[self.server_path, "stdio"],
            env=dict(os.environ)
        )

        self.stdio_transport = await stdio_client(server_params).__aenter__()
        read, write = self.stdio_transport
        self.session = await ClientSession(read, write).__aenter__()
        await self.session.initialize()

        print("✅ Connected to Freelance MCP Server")

    async def disconnect(self) -> None:
        """Close connection to the MCP server"""
        if self.session:
            await self.session.__aexit__(None, None, None)
        if hasattr(self, 'stdio_transport'):
            await self.stdio_transport.__aexit__(None, None, None)
        print("👋 Disconnected from server")

    async def list_tools(self) -> List[str]:
        """Get list of available tools"""
        if not self.session:
            raise RuntimeError("Not connected to server")

        tools_response = await self.session.list_tools()
        return [tool.name for tool in tools_response.tools]

    async def list_resources(self) -> List[str]:
        """Get list of available resources"""
        if not self.session:
            raise RuntimeError("Not connected to server")

        resources_response = await self.session.list_resources()
        return [resource.uri for resource in resources_response.resources]

    async def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Any:
        """Call a tool on the server"""
        if not self.session:
            raise RuntimeError("Not connected to server")

        try:
            result = await self.session.call_tool(tool_name, arguments)

            # Parse the result
            if hasattr(result, 'content') and result.content:
                for content_item in result.content:
                    if hasattr(content_item, 'text'):
                        try:
                            return json.loads(content_item.text)
                        except json.JSONDecodeError:
                            return content_item.text

            return result
        except Exception as e:
            return {"error": str(e)}

    async def read_resource(self, uri: str) -> str:
        """Read a resource from the server"""
        if not self.session:
            raise RuntimeError("Not connected to server")

        try:
            result = await self.session.read_resource(uri)
            if hasattr(result, 'contents') and result.contents:
                return result.contents[0].text
            return str(result)
        except Exception as e:
            return f"Error reading resource: {e}"


class DemoRunner:
    """Automated demo of all server features"""

    def __init__(self, client: FreelanceClient):
        self.client = client

    def print_section(self, title: str) -> None:
        """Print formatted section header"""
        print(f"\n{'='*70}")
        print(f"  {title}")
        print(f"{'='*70}\n")

    def print_json(self, data: Any, indent: int = 2) -> None:
        """Pretty print JSON data"""
        if isinstance(data, (dict, list)):
            print(json.dumps(data, indent=indent))
        else:
            print(data)

    async def run_full_demo(self) -> None:
        """Run comprehensive demo of all features"""
        print("\n🚀 Starting Freelance MCP Server Demo")
        print(f"⏰ Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

        # 1. List available tools
        self.print_section("1. Available Tools")
        tools = await self.client.list_tools()
        for i, tool in enumerate(tools, 1):
            print(f"  {i}. {tool}")

        # 2. List available resources
        self.print_section("2. Available Resources")
        resources = await self.client.list_resources()
        for i, resource in enumerate(resources, 1):
            print(f"  {i}. {resource}")

        # 3. Search for gigs
        self.print_section("3. Search Gigs - Python & JavaScript")
        result = await self.client.call_tool("search_gigs", {
            "skills": ["Python", "JavaScript"],
            "max_budget": 2000
        })
        self.print_json(result)

        # 4. Search React gigs on Upwork
        self.print_section("4. Search React Gigs on Upwork")
        result = await self.client.call_tool("search_gigs", {
            "skills": ["React", "TypeScript"],
            "platforms": ["upwork"],
            "project_type": "fixed_price"
        })
        self.print_json(result)

        # 5. Create user profile
        self.print_section("5. Create User Profile")
        profile_data = {
            "name": "Demo User",
            "title": "Full-Stack Developer",
            "skills": [
                {"name": "Python", "level": "expert", "years_experience": 5},
                {"name": "JavaScript", "level": "advanced", "years_experience": 4},
                {"name": "React", "level": "advanced", "years_experience": 3}
            ],
            "hourly_rate_min": 50.0,
            "hourly_rate_max": 85.0,
            "location": "Remote",
            "bio": "Experienced full-stack developer specializing in Python and JavaScript"
        }
        result = await self.client.call_tool("create_user_profile", profile_data)
        self.print_json(result)

        profile_id = result.get("profile_id", "demo_user_001") if isinstance(result, dict) else "demo_user_001"

        # 6. Analyze profile fit
        self.print_section("6. Analyze Profile Fit for Gig")
        result = await self.client.call_tool("analyze_profile_fit", {
            "profile_id": profile_id,
            "gig_id": "upwork_001"
        })
        self.print_json(result)

        # 7. Generate proposal
        self.print_section("7. Generate AI-Powered Proposal")
        result = await self.client.call_tool("generate_proposal", {
            "gig_id": "upwork_001",
            "user_profile": profile_data,
            "tone": "professional",
            "include_portfolio": True
        })
        self.print_json(result)

        # 8. Rate negotiation
        self.print_section("8. Rate Negotiation Strategy")
        result = await self.client.call_tool("negotiate_rate", {
            "current_rate": 50.0,
            "target_rate": 75.0,
            "justification_points": [
                "5+ years Python experience",
                "Successfully delivered 20+ projects",
                "Expert in React and TypeScript"
            ],
            "project_complexity": "high"
        })
        self.print_json(result)

        # 9. Code review
        self.print_section("9. Code Review")
        sample_code = """
function calculateTotal(items) {
    var total = 0;
    for (var i = 0; i < items.length; i++) {
        total += items[i].price;
    }
    return total;
}
"""
        result = await self.client.call_tool("code_review", {
            "code_snippet": sample_code,
            "language": "javascript",
            "review_type": "general"
        })
        self.print_json(result)

        # 10. Code debug
        self.print_section("10. Code Debug & Fix")
        buggy_code = """
def process_data(data):
    result = []
    for item in data:
        if item['value'] > 0:
            result.append(item['name'])
    return result
"""
        result = await self.client.call_tool("code_debug", {
            "code_snippet": buggy_code,
            "language": "python",
            "issue_description": "Add type hints and error handling",
            "fix_type": "auto"
        })
        self.print_json(result)

        # 11. Profile optimization
        self.print_section("11. Profile Optimization Tips")
        result = await self.client.call_tool("optimize_profile", {
            "profile_data": profile_data,
            "target_platforms": ["upwork", "toptal"]
        })
        self.print_json(result)

        # 12. Track application status
        self.print_section("12. Track Application Status")
        result = await self.client.call_tool("track_application_status", {
            "profile_id": profile_id,
            "gig_ids": ["upwork_001", "fiverr_001"]
        })
        self.print_json(result)

        # 13. Access resources
        self.print_section("13. Access Market Trends Resource")
        trends = await self.client.read_resource("freelance://market-trends")
        self.print_json(json.loads(trends))

        # 14. Validate owner phone
        self.print_section("14. Validate Server Owner Phone")
        country_code = os.getenv("OWNER_COUNTRY_CODE", "1")
        phone = os.getenv("OWNER_PHONE_NUMBER", "5551234567")
        result = await self.client.call_tool("validate", {
            "country_code": country_code,
            "phone_number": phone
        })
        self.print_json(result)

        print("\n" + "="*70)
        print("✅ Demo completed successfully!")
        print("="*70 + "\n")


class InteractiveMode:
    """Interactive command-line interface"""

    def __init__(self, client: FreelanceClient):
        self.client = client
        self.running = True

    def print_help(self) -> None:
        """Print available commands"""
        commands = """
Available Commands:
  search         - Search for matching gigs
  profile        - Create user profile
  analyze        - Analyze profile fit for gigs
  proposal       - Generate AI proposals
  negotiate      - Get rate negotiation help
  review         - Review code quality
  debug          - Debug and fix code issues
  optimize       - Get profile optimization tips
  track          - Track application status
  resources      - Access market data
  validate       - Validate owner phone number
  demo           - Run full automated demo
  help           - Show this help message
  quit           - Exit interactive mode
"""
        print(commands)

    async def handle_search(self) -> None:
        """Handle gig search command"""
        skills = input("Enter skills (comma-separated): ").split(",")
        skills = [s.strip() for s in skills if s.strip()]
        max_budget = input("Max budget (optional, press Enter to skip): ").strip()

        args = {"skills": skills}
        if max_budget:
            args["max_budget"] = float(max_budget)

        result = await self.client.call_tool("search_gigs", args)
        print(json.dumps(result, indent=2))

    async def handle_profile(self) -> None:
        """Handle profile creation"""
        name = input("Your name: ")
        title = input("Your title: ")
        rate_min = float(input("Minimum hourly rate: "))
        rate_max = float(input("Maximum hourly rate: "))

        profile_data = {
            "name": name,
            "title": title,
            "hourly_rate_min": rate_min,
            "hourly_rate_max": rate_max,
            "skills": [
                {"name": "Python", "level": "advanced", "years_experience": 3}
            ]
        }

        result = await self.client.call_tool("create_user_profile", profile_data)
        print(json.dumps(result, indent=2))

    async def run(self) -> None:
        """Run interactive mode loop"""
        print("\n🎮 Interactive Mode Started")
        print("Type 'help' for available commands\n")

        while self.running:
            try:
                command = input("freelance> ").strip().lower()

                if not command:
                    continue

                if command == "quit" or command == "exit":
                    self.running = False
                    print("Goodbye!")
                elif command == "help":
                    self.print_help()
                elif command == "search":
                    await self.handle_search()
                elif command == "profile":
                    await self.handle_profile()
                elif command == "demo":
                    demo = DemoRunner(self.client)
                    await demo.run_full_demo()
                elif command == "resources":
                    trends = await self.client.read_resource("freelance://market-trends")
                    print(json.dumps(json.loads(trends), indent=2))
                else:
                    print(f"Unknown command: {command}. Type 'help' for available commands.")

            except KeyboardInterrupt:
                print("\n\nUse 'quit' to exit")
            except Exception as e:
                print(f"Error: {e}")


def check_environment() -> bool:
    """Validate environment setup"""
    print("\n🔍 Checking Environment Setup...\n")

    issues = []
    warnings = []

    # Check Python version
    python_version = sys.version_info
    if python_version >= (3, 11):
        print(f"✅ Python {python_version.major}.{python_version.minor}.{python_version.micro}")
    else:
        issues.append(f"Python version {python_version.major}.{python_version.minor} (requires 3.11+)")

    # Check required packages
    required_packages = ["mcp", "pydantic", "dotenv"]
    for package in required_packages:
        try:
            __import__(package)
            print(f"✅ {package}")
        except ImportError:
            issues.append(f"Missing package: {package}")

    # Check optional packages
    try:
        import langchain_groq
        print(f"✅ langchain-groq")
    except ImportError:
        warnings.append("langchain-groq not installed (AI features won't work)")

    # Check files
    if Path("freelance_server.py").exists():
        print(f"✅ freelance_server.py")
    else:
        issues.append("freelance_server.py not found")

    if Path(".env").exists():
        print(f"✅ .env file")
    else:
        warnings.append(".env file not found")

    # Check environment variables
    groq_key = os.getenv("GROQ_API_KEY")
    if groq_key and len(groq_key) > 20:
        print(f"✅ GROQ_API_KEY configured")
    else:
        warnings.append("GROQ_API_KEY not set or invalid (AI features won't work)")

    # Print summary
    print("\n" + "="*60)
    if issues:
        print("❌ ISSUES FOUND:")
        for issue in issues:
            print(f"  - {issue}")

    if warnings:
        print("\n⚠️  WARNINGS:")
        for warning in warnings:
            print(f"  - {warning}")

    if not issues and not warnings:
        print("✅ All checks passed! Environment is ready.")
    elif not issues:
        print("✅ Environment is mostly ready (check warnings above)")
    else:
        print("❌ Please fix the issues above before running the client")

    print("="*60 + "\n")

    return len(issues) == 0


async def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="Freelance MCP Client")
    parser.add_argument("--mode", choices=["demo", "interactive"], default="demo",
                       help="Run mode: demo (automated) or interactive")
    parser.add_argument("--check-env", action="store_true",
                       help="Check environment setup")
    parser.add_argument("--server-path", default="freelance_server.py",
                       help="Path to server file")

    args = parser.parse_args()

    # Check environment if requested
    if args.check_env:
        check_environment()
        return

    # Create client
    client = FreelanceClient(args.server_path)

    try:
        # Connect to server
        await client.connect()

        # Run appropriate mode
        if args.mode == "demo":
            demo = DemoRunner(client)
            await demo.run_full_demo()
        else:
            interactive = InteractiveMode(client)
            await interactive.run()

    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        await client.disconnect()


if __name__ == "__main__":
    asyncio.run(main())
