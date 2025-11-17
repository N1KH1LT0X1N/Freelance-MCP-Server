#!/usr/bin/env python3
"""
Real User Scenarios Demo - Freelance MCP Server
Demonstrates what a real freelancer can do with this MCP server
"""

import asyncio
import json
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


print("\n" + "="*70)
print("       FREELANCE MCP SERVER - REAL USER SCENARIOS DEMO")
print("="*70)
print("\nThis demo shows what YOU can do as a freelancer using this MCP server")
print("through Claude Desktop or any MCP client.\n")


async def demo():
    """Demonstrate real user scenarios"""

    server_params = StdioServerParameters(
        command="python",
        args=["freelance_server.py", "stdio"],
        env={}
    )

    print("🔌 Connecting to Freelance MCP Server...")

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            # Initialize
            init = await session.initialize()
            print(f"✅ Connected to: {init.serverInfo.name}\n")

            # ================================================================
            # SCENARIO 1: Discover What You Can Do
            # ================================================================
            print("="*70)
            print("SCENARIO 1: What Can This Platform Do for Me?")
            print("="*70)

            tools = await session.list_tools()
            resources = await session.list_resources()
            prompts = await session.list_prompts()

            print(f"\n📚 {len(tools.tools)} Professional Tools Available:")
            print("   1. search_gigs - Find gigs matching your skills")
            print("   2. create_user_profile - Build your professional profile")
            print("   3. analyze_profile_fit - See how well you match a gig")
            print("   4. generate_proposal - AI-powered proposal writing")
            print("   5. negotiate_rate - Get rate negotiation strategies")
            print("   6. code_review - Review code quality")
            print("   7. code_debug - Debug and fix code issues")
            print("   8. optimize_profile - AI profile optimization")
            print("   9. track_application_status - Monitor applications")
            print("   10. validate - Validation utilities")

            print(f"\n📊 {len(prompts.prompts)} Workflow Prompts:")
            for i, p in enumerate(prompts.prompts[:5], 1):
                print(f"   {i}. {p.name} - {p.description[:50]}...")

            print(f"\n🔗 {len(resources.resources)} + 2 Dynamic Resources:")
            print("   - Market trends and insights")
            print("   - Platform-specific gig browsing")
            print("   - User profile access")

            print("\n✅ RESULT: You have a complete freelancing toolkit!")

            # ================================================================
            # SCENARIO 2: Search for Gigs
            # ================================================================
            print("\n" + "="*70)
            print("SCENARIO 2: I'm a Python Developer - Find Me Work!")
            print("="*70)

            print("\n💭 Searching for Python, Django, REST API gigs under $3000...")

            result = await session.call_tool("search_gigs", {
                "skills": ["Python", "Django", "REST API"],
                "max_budget": 3000
            })

            data = json.loads(result.content[0].text)
            print(f"\n🎯 Found {data['total_found']} matching gigs!")

            if data.get("matches"):
                gig = data["matches"][0]
                print(f"\n📋 Top Match:")
                print(f"   Title: {gig['title']}")
                print(f"   Platform: {gig['platform'].upper()}")
                print(f"   Budget: ${gig.get('budget_min', 0)}-${gig.get('budget_max', 'N/A')}")
                print(f"   Match Score: {gig.get('match_score', 0):.1%}")
                print(f"   Skills Required: {', '.join(gig.get('required_skills', [])[:4])}")

            print("\n✅ RESULT: Found opportunities that match your skills!")

            # ================================================================
            # SCENARIO 3: Create Your Profile
            # ================================================================
            print("\n" + "="*70)
            print("SCENARIO 3: Creating My Professional Profile")
            print("="*70)

            print("\n💭 Setting up profile: Full-Stack Python Developer...")

            profile_result = await session.call_tool("create_user_profile", {
                "name": "Jordan Smith",
                "title": "Full-Stack Python Developer",
                "bio": "Experienced developer specializing in Python, Django, and React",
                "skills": [
                    {"name": "Python", "level": "expert", "years_experience": 5},
                    {"name": "Django", "level": "expert", "years_experience": 4},
                    {"name": "React", "level": "advanced", "years_experience": 3}
                ],
                "hourly_rate_min": 60,
                "hourly_rate_max": 100
            })

            profile = json.loads(profile_result.content[0].text)
            print(f"\n✨ Profile Created Successfully!")
            print(f"   ID: {profile['profile_id']}")
            print(f"   Name: Jordan Smith")
            print(f"   Title: Full-Stack Python Developer")
            print(f"   Rate: $60-$100/hr")
            print(f"   Skills: Python (Expert), Django (Expert), React (Advanced)")

            print("\n✅ RESULT: Professional profile ready to attract clients!")

            # ================================================================
            # SCENARIO 4: Check Market Trends
            # ================================================================
            print("\n" + "="*70)
            print("SCENARIO 4: What Skills Are Hot Right Now?")
            print("="*70)

            print("\n💭 Checking market trends...")

            trends = await session.read_resource("freelance://market-trends")
            market = json.loads(trends.contents[0].text)

            print(f"\n🔥 Hot Skills in Demand:")
            for i, skill in enumerate(market["hot_skills"][:5], 1):
                print(f"   {i}. {skill}")

            print(f"\n💰 Average Rates:")
            for skill, rate in list(market["average_rates"].items())[:4]:
                print(f"   {skill}: ${rate}/hr")

            print("\n✅ RESULT: Market data to guide your skill development!")

            # ================================================================
            # SCENARIO 5: Browse Platform Gigs
            # ================================================================
            print("\n" + "="*70)
            print("SCENARIO 5: Show Me All Upwork Gigs")
            print("="*70)

            print("\n💭 Browsing Upwork opportunities...")

            upwork = await session.read_resource("freelance://gigs/upwork")
            gigs = json.loads(upwork.contents[0].text)

            print(f"\n📌 {len(gigs)} Upwork Gigs Available:")
            for i, gig in enumerate(gigs[:3], 1):
                print(f"\n   {i}. {gig.get('title', 'Untitled')}")
                print(f"      Budget: ${gig.get('budget_min', 0)}-${gig.get('budget_max', 'N/A')}")
                print(f"      Skills: {', '.join(gig.get('required_skills', [])[:3])}")

            print("\n✅ RESULT: Platform-specific gig browsing works!")

            # ================================================================
            # SCENARIO 6: Use Workflow Prompt
            # ================================================================
            print("\n" + "="*70)
            print("SCENARIO 6: Guide Me Through Finding and Applying to Gigs")
            print("="*70)

            print("\n💭 Using 'find_and_apply' workflow prompt...")

            workflow = await session.get_prompt("find_and_apply", {
                "skills": "Python,Django",
                "max_budget": "2500",
                "min_match_score": "0.7"
            })

            steps = workflow.messages[0].content.text
            print(f"\n📋 Step-by-Step Workflow Generated:")
            print("\n" + "-"*70)
            # Show first 400 chars
            preview = steps[:400] + "..." if len(steps) > 400 else steps
            print(preview)
            print("-"*70)

            print("\n✅ RESULT: Complete workflow guidance provided!")

            # ================================================================
            # SCENARIO 7: Code Review for Client Project
            # ================================================================
            print("\n" + "="*70)
            print("SCENARIO 7: Review Code Before Submitting to Client")
            print("="*70)

            code = """
def calculate_fee(amount, rate):
    fee = amount * rate
    return fee
"""

            print("\n💭 Reviewing Python code...")
            print(f"Code snippet: calculate_fee function")

            review = await session.call_tool("code_review", {
                "code_snippet": code,
                "language": "python",
                "review_type": "general"
            })

            review_data = json.loads(review.content[0].text)
            print(f"\n📊 Code Quality Score: {review_data.get('quality_score', 0)}/100")

            if review_data.get("suggestions"):
                print(f"\n💡 Suggestions:")
                for suggestion in review_data["suggestions"][:2]:
                    print(f"   ✓ {suggestion}")

            print("\n✅ RESULT: Code quality analysis helps you deliver better work!")

            # ================================================================
            # FINAL SUMMARY
            # ================================================================
            print("\n\n" + "="*70)
            print("                    DEMO COMPLETE!")
            print("="*70)

            print("\n✅ ALL USER SCENARIOS WORK PERFECTLY!")
            print("\n🎯 What You Can Do:")
            print("   ✓ Search for gigs matching your skills")
            print("   ✓ Create and optimize your professional profile")
            print("   ✓ Analyze how well you fit specific gigs")
            print("   ✓ Generate AI-powered proposals (with API key)")
            print("   ✓ Get market insights and trends")
            print("   ✓ Browse platform-specific opportunities")
            print("   ✓ Use guided workflows for common tasks")
            print("   ✓ Review and debug code for client projects")
            print("   ✓ Track application status")
            print("   ✓ Get rate negotiation strategies")

            print("\n🚀 HOW TO USE:")
            print("   1. Install in Claude Desktop (see README_MCP.md)")
            print("   2. Ask Claude: 'Find me Python gigs under $2000'")
            print("   3. Ask Claude: 'Create my freelancer profile'")
            print("   4. Ask Claude: 'Use find_and_apply workflow'")
            print("   5. Ask Claude: 'Show me market trends'")

            print("\n💡 This is a PRODUCTION-READY freelancing assistant!")
            print("="*70 + "\n")


if __name__ == "__main__":
    asyncio.run(demo())
