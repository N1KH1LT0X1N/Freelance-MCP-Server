"""
Example: Complete MCP Integration with Claude

Demonstrates proper MCP protocol usage with all server capabilities:
- Tools, Resources, and Prompts
- Error handling
- Resource discovery
- Capability negotiation
"""

import asyncio
import json
from typing import Dict, Any, List
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


class MCPFreelanceClient:
    """
    Complete MCP client demonstrating protocol best practices

    This client shows how to properly use all MCP features:
    - Server capability discovery
    - Tool invocation
    - Resource access
    - Prompt workflows
    - Error handling
    """

    def __init__(self):
        self.session: ClientSession = None
        self.transport = None
        self.capabilities = None

    async def connect(self) -> None:
        """Connect and perform MCP initialization"""
        print("🔌 Connecting to MCP server...")

        server_params = StdioServerParameters(
            command="python",
            args=["freelance_server.py", "stdio"],
            env={}
        )

        self.transport = await stdio_client(server_params).__aenter__()
        read, write = self.transport
        self.session = await ClientSession(read, write).__aenter__()

        # Initialize session (MCP handshake)
        init_result = await self.session.initialize()
        print(f"✅ Connected! Server: {init_result.serverInfo.name} v{init_result.serverInfo.version}")

        # Discover capabilities
        await self.discover_capabilities()

    async def disconnect(self) -> None:
        """Proper MCP disconnect"""
        if self.session:
            await self.session.__aexit__(None, None, None)
        if self.transport:
            await self.transport.__aexit__(None, None, None)
        print("👋 Disconnected")

    async def discover_capabilities(self) -> None:
        """
        MCP Best Practice: Discover server capabilities

        Before using tools/resources, check what's available
        """
        print("\n📋 Discovering Server Capabilities...")

        # List available tools
        tools_result = await self.session.list_tools()
        print(f"  ✓ Tools: {len(tools_result.tools)} available")
        for tool in tools_result.tools[:3]:
            print(f"    - {tool.name}")
        if len(tools_result.tools) > 3:
            print(f"    ... and {len(tools_result.tools) - 3} more")

        # List available resources
        resources_result = await self.session.list_resources()
        print(f"  ✓ Resources: {len(resources_result.resources)} available")
        for resource in resources_result.resources:
            print(f"    - {resource.uri}")

        # List available prompts (if supported)
        try:
            prompts_result = await self.session.list_prompts()
            print(f"  ✓ Prompts: {len(prompts_result.prompts)} available")
            for prompt in prompts_result.prompts[:3]:
                print(f"    - {prompt.name}")
        except Exception:
            print(f"  ⚠ Prompts: Not available (server may not support them yet)")

    async def call_tool_safe(self, tool_name: str, arguments: Dict[str, Any]) -> Any:
        """
        MCP Best Practice: Safe tool invocation with error handling
        """
        try:
            result = await self.session.call_tool(tool_name, arguments)

            if hasattr(result, 'content') and result.content:
                for content_item in result.content:
                    if hasattr(content_item, 'text'):
                        try:
                            return json.loads(content_item.text)
                        except json.JSONDecodeError:
                            return content_item.text
            return result

        except Exception as e:
            print(f"❌ Tool call failed: {e}")
            return {"error": str(e)}

    async def read_resource_safe(self, uri: str) -> Any:
        """
        MCP Best Practice: Safe resource access
        """
        try:
            result = await self.session.read_resource(uri)
            if hasattr(result, 'contents') and result.contents:
                text = result.contents[0].text
                try:
                    return json.loads(text)
                except json.JSONDecodeError:
                    return text
            return result
        except Exception as e:
            print(f"❌ Resource access failed: {e}")
            return {"error": str(e)}

    async def demo_workflow_1_search_and_analyze(self) -> None:
        """
        Demo Workflow 1: Search gigs and analyze fit

        MCP Pattern: Tool → Tool → Resource
        """
        print("\n" + "="*70)
        print("DEMO 1: Search & Analyze Workflow")
        print("="*70)

        # Step 1: Search for gigs (Tool)
        print("\n🔍 Step 1: Searching for Python gigs...")
        gigs = await self.call_tool_safe("search_gigs", {
            "skills": ["Python", "Django"],
            "max_budget": 2000
        })

        matches = gigs.get("matches", [])
        print(f"✓ Found {len(matches)} matching gigs")

        if matches:
            top_gig = matches[0]
            print(f"  Top match: {top_gig['title']}")
            print(f"  Platform: {top_gig['platform']}")
            print(f"  Score: {top_gig['match_score']:.2f}")

            # Step 2: Create profile (Tool)
            print("\n👤 Step 2: Creating user profile...")
            profile = await self.call_tool_safe("create_user_profile", {
                "name": "Demo User",
                "title": "Python Developer",
                "skills": [
                    {"name": "Python", "level": "expert", "years_experience": 5},
                    {"name": "Django", "level": "advanced", "years_experience": 3}
                ],
                "hourly_rate_min": 50,
                "hourly_rate_max": 80
            })

            profile_id = profile.get("profile_id")
            print(f"✓ Profile created: {profile_id}")

            # Step 3: Analyze fit (Tool)
            print("\n📊 Step 3: Analyzing profile fit...")
            fit = await self.call_tool_safe("analyze_profile_fit", {
                "profile_id": profile_id,
                "gig_id": top_gig["id"]
            })

            print(f"✓ Overall Score: {fit.get('overall_score', 0):.2f}")
            print(f"  Skill Match: {fit.get('skill_match', 0):.2f}")
            print(f"  Rate Compatible: {fit.get('rate_compatibility', 0):.2f}")
            print(f"  Recommendation: {fit.get('recommendation', 'N/A')}")

            # Step 4: Access market trends (Resource)
            print("\n📈 Step 4: Checking market trends...")
            trends = await self.read_resource_safe("freelance://market-trends")

            if "hot_skills" in trends:
                print(f"✓ Hot Skills: {', '.join(trends['hot_skills'][:5])}")
                print(f"  Your rate range fits: {trends['average_rates'].get('Web Development', 'N/A')}")

    async def demo_workflow_2_ai_proposal(self) -> None:
        """
        Demo Workflow 2: AI-powered proposal generation

        MCP Pattern: Resource → Tool (AI) → Result
        """
        print("\n" + "="*70)
        print("DEMO 2: AI Proposal Generation Workflow")
        print("="*70)

        # Step 1: Get gig details (Resource)
        print("\n📋 Step 1: Fetching gig from Upwork...")
        gigs_data = await self.read_resource_safe("freelance://gigs/upwork")

        if gigs_data and len(gigs_data) > 0:
            gig = gigs_data[0]
            print(f"✓ Selected: {gig['title']}")

            # Step 2: Generate AI proposal (AI Tool)
            print("\n🤖 Step 2: Generating AI-powered proposal...")
            print("   (Requires GROQ_API_KEY)")

            profile_data = {
                "name": "AI Demo User",
                "title": "Senior React Developer",
                "skills": [
                    {"name": "React", "level": "expert", "years_experience": 6}
                ],
                "hourly_rate_min": 70,
                "hourly_rate_max": 110
            }

            proposal = await self.call_tool_safe("generate_proposal", {
                "gig_id": gig["id"],
                "user_profile": profile_data,
                "tone": "professional",
                "include_portfolio": True
            })

            if "proposal" in proposal:
                print("✓ Proposal generated!")
                print("\n📝 Preview:")
                print(proposal["proposal"][:300] + "...")
            elif "error" in proposal:
                print(f"⚠ Could not generate (AI features require GROQ_API_KEY)")
            else:
                print("✓ Proposal generated (AI features may not be configured)")

    async def demo_workflow_3_code_review(self) -> None:
        """
        Demo Workflow 3: Code review and debugging

        MCP Pattern: Tool → Tool (with file/code)
        """
        print("\n" + "="*70)
        print("DEMO 3: Code Review & Debug Workflow")
        print("="*70)

        sample_code = """
def calculate_total(items):
    total = 0
    for item in items:
        if item['price'] > 0:
            total = total + item['price']
    return total

# Usage
products = [{'name': 'A', 'price': 10}, {'name': 'B', 'price': 20}]
result = calculate_total(products)
print(result)
"""

        # Step 1: Code review (Tool)
        print("\n🔍 Step 1: Reviewing Python code...")
        review = await self.call_tool_safe("code_review", {
            "code_snippet": sample_code,
            "language": "python",
            "review_type": "general"
        })

        print(f"✓ Quality Score: {review.get('quality_score', 0)}/100")
        print(f"  Issues Found: {len(review.get('issues', []))}")

        if review.get("issues"):
            print("\n  Issues:")
            for issue in review.get("issues", [])[:3]:
                print(f"    - {issue}")

        # Step 2: Auto-fix (Tool)
        print("\n🔧 Step 2: Auto-fixing issues...")
        fixed = await self.call_tool_safe("code_debug", {
            "code_snippet": sample_code,
            "language": "python",
            "issue_description": "Add type hints and improve style",
            "fix_type": "auto"
        })

        if fixed.get("fixed_code"):
            print("✓ Code fixed!")
            print("\n💾 Fixed Code Preview:")
            print(fixed["fixed_code"][:200] + "...")

    async def demo_workflow_4_complete_pipeline(self) -> None:
        """
        Demo Workflow 4: Complete freelancing pipeline

        MCP Pattern: Multi-step with Resources, Tools, and AI
        """
        print("\n" + "="*70)
        print("DEMO 4: Complete Pipeline (Search → Fit → Propose → Track)")
        print("="*70)

        # Pipeline: Search → Create Profile → Analyze → Generate → Track

        print("\n1️⃣ Market Research...")
        trends = await self.read_resource_safe("freelance://market-trends")
        hot_skills = trends.get("hot_skills", [])[:3] if trends else ["Python", "JavaScript"]
        print(f"   Hot skills: {', '.join(hot_skills)}")

        print("\n2️⃣ Searching for relevant gigs...")
        gigs = await self.call_tool_safe("search_gigs", {
            "skills": hot_skills,
            "max_budget": 3000
        })
        matches = gigs.get("matches", [])[:3]
        print(f"   Found {len(matches)} top matches")

        print("\n3️⃣ Creating optimized profile...")
        profile = await self.call_tool_safe("create_user_profile", {
            "name": "Pipeline Demo User",
            "title": "Full-Stack Developer",
            "skills": [
                {"name": skill, "level": "advanced", "years_experience": 4}
                for skill in hot_skills
            ],
            "hourly_rate_min": 60,
            "hourly_rate_max": 95
        })
        profile_id = profile.get("profile_id")

        print("\n4️⃣ Analyzing fit and applying...")
        applied_count = 0
        for gig in matches:
            fit = await self.call_tool_safe("analyze_profile_fit", {
                "profile_id": profile_id,
                "gig_id": gig["id"]
            })

            if fit.get("overall_score", 0) >= 0.7:
                print(f"   ✓ {gig['title'][:40]}... (Score: {fit['overall_score']:.2f})")
                applied_count += 1

        print(f"\n5️⃣ Tracking {applied_count} applications...")
        tracking = await self.call_tool_safe("track_application_status", {
            "profile_id": profile_id,
            "gig_ids": [g["id"] for g in matches]
        })

        print(f"   ✓ Applications tracked")
        print(f"   Summary: {tracking.get('summary', 'Complete')}")

    async def run_complete_demo(self) -> None:
        """Run all MCP demo workflows"""
        print("""
╔══════════════════════════════════════════════════════════════════╗
║                                                                  ║
║         MCP FREELANCE SERVER - COMPLETE DEMO                     ║
║                                                                  ║
║    Demonstrating proper MCP protocol usage                      ║
║                                                                  ║
╚══════════════════════════════════════════════════════════════════╝
        """)

        try:
            await self.connect()

            # Run all workflow demos
            await self.demo_workflow_1_search_and_analyze()
            await self.demo_workflow_2_ai_proposal()
            await self.demo_workflow_3_code_review()
            await self.demo_workflow_4_complete_pipeline()

            print("\n" + "="*70)
            print("✅ All MCP Workflows Completed Successfully!")
            print("="*70)
            print("\nThis demo showed:")
            print("  ✓ MCP server capability discovery")
            print("  ✓ Tool invocation patterns")
            print("  ✓ Resource access patterns")
            print("  ✓ AI integration (with GROQ)")
            print("  ✓ Complete workflows")
            print("  ✓ Error handling")
            print("\n" + "="*70)

        finally:
            await self.disconnect()


async def main():
    """Run the complete MCP demo"""
    client = MCPFreelanceClient()
    await client.run_complete_demo()


if __name__ == "__main__":
    asyncio.run(main())
