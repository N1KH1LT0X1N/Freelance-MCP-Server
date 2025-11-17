"""
Example: Custom MCP Client Integration

Demonstrates how to build a custom client that integrates the Freelance MCP Server
with your own application logic.
"""

import asyncio
import json
from typing import Dict, List, Any
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


class CustomFreelanceIntegration:
    """Custom integration example for Freelance MCP Server"""

    def __init__(self):
        self.session = None
        self.transport = None
        self.user_profile_id = None

    async def connect(self):
        """Connect to the MCP server"""
        server_params = StdioServerParameters(
            command="python",
            args=["freelance_server.py", "stdio"],
            env={}
        )

        self.transport = await stdio_client(server_params).__aenter__()
        read, write = self.transport
        self.session = await ClientSession(read, write).__aenter__()
        await self.session.initialize()

        print("✓ Connected to Freelance MCP Server")

    async def disconnect(self):
        """Disconnect from server"""
        if self.session:
            await self.session.__aexit__(None, None, None)
        if self.transport:
            await self.transport.__aexit__(None, None, None)

    async def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Any:
        """Helper to call tools and parse results"""
        result = await self.session.call_tool(tool_name, arguments)

        if hasattr(result, 'content') and result.content:
            for content_item in result.content:
                if hasattr(content_item, 'text'):
                    try:
                        return json.loads(content_item.text)
                    except json.JSONDecodeError:
                        return content_item.text
        return result

    async def setup_user_profile(self, user_data: Dict) -> str:
        """
        Setup user profile for the application

        Args:
            user_data: Dictionary with user information

        Returns:
            Profile ID
        """
        print("\n📝 Creating user profile...")

        profile_data = {
            "name": user_data.get("name", "User"),
            "title": user_data.get("title", "Freelancer"),
            "skills": user_data.get("skills", []),
            "hourly_rate_min": user_data.get("rate_min", 50.0),
            "hourly_rate_max": user_data.get("rate_max", 100.0),
            "location": user_data.get("location", "Remote"),
            "bio": user_data.get("bio", "")
        }

        result = await self.call_tool("create_user_profile", profile_data)
        self.user_profile_id = result.get("profile_id")

        print(f"✓ Profile created: {self.user_profile_id}")
        return self.user_profile_id

    async def find_matching_gigs(self, skills: List[str], budget_max: float = None) -> List[Dict]:
        """
        Find gigs matching user skills

        Args:
            skills: List of skills to match
            budget_max: Maximum budget filter

        Returns:
            List of matching gigs
        """
        print(f"\n🔍 Searching for gigs with skills: {', '.join(skills)}")

        args = {"skills": skills}
        if budget_max:
            args["max_budget"] = budget_max

        result = await self.call_tool("search_gigs", args)

        matches = result.get("matches", [])
        print(f"✓ Found {len(matches)} matching gigs")

        return matches

    async def analyze_and_apply(self, gig: Dict) -> Dict:
        """
        Analyze fit and generate proposal for a gig

        Args:
            gig: Gig dictionary

        Returns:
            Application result
        """
        gig_id = gig.get("id")
        print(f"\n📊 Analyzing fit for: {gig.get('title')}")

        # Analyze fit
        fit_result = await self.call_tool("analyze_profile_fit", {
            "profile_id": self.user_profile_id,
            "gig_id": gig_id
        })

        score = fit_result.get("overall_score", 0)
        print(f"  Match Score: {score:.2f}")
        print(f"  Recommendation: {fit_result.get('recommendation')}")

        # Generate proposal if good match
        if score >= 0.7:
            print(f"\n✍️  Generating proposal...")

            profile_result = await self.call_tool("analyze_profile_fit", {
                "profile_id": self.user_profile_id,
                "gig_id": gig_id
            })

            proposal_result = await self.call_tool("generate_proposal", {
                "gig_id": gig_id,
                "user_profile": profile_result,
                "tone": "professional"
            })

            print(f"✓ Proposal generated")

            return {
                "gig": gig,
                "fit_score": score,
                "proposal": proposal_result.get("proposal"),
                "applied": True
            }
        else:
            print(f"⊘ Skipping (score too low)")
            return {
                "gig": gig,
                "fit_score": score,
                "applied": False
            }

    async def run_workflow(self, user_data: Dict, search_skills: List[str]):
        """
        Complete workflow: setup → search → analyze → apply

        Args:
            user_data: User profile data
            search_skills: Skills to search for
        """
        try:
            await self.connect()

            # Step 1: Setup profile
            await self.setup_user_profile(user_data)

            # Step 2: Find matching gigs
            gigs = await self.find_matching_gigs(search_skills, budget_max=2000)

            # Step 3: Analyze and apply to top matches
            applications = []
            for gig in gigs[:3]:  # Top 3 matches
                result = await self.analyze_and_apply(gig)
                applications.append(result)

            # Summary
            print("\n" + "="*60)
            print("📋 Application Summary")
            print("="*60)

            applied_count = sum(1 for app in applications if app["applied"])
            print(f"  Total Gigs Analyzed: {len(applications)}")
            print(f"  Applications Sent: {applied_count}")
            print(f"  Skipped: {len(applications) - applied_count}")

            for app in applications:
                status = "✓ Applied" if app["applied"] else "⊘ Skipped"
                print(f"\n  {app['gig']['title']}")
                print(f"    Platform: {app['gig']['platform']}")
                print(f"    Match Score: {app['fit_score']:.2f}")
                print(f"    Status: {status}")

            print("\n" + "="*60)

        finally:
            await self.disconnect()


async def main():
    """Example usage"""
    # Define user data
    user_data = {
        "name": "Jane Developer",
        "title": "Full-Stack Python Developer",
        "skills": [
            {"name": "Python", "level": "expert", "years_experience": 6},
            {"name": "JavaScript", "level": "advanced", "years_experience": 4},
            {"name": "React", "level": "advanced", "years_experience": 3},
            {"name": "Django", "level": "expert", "years_experience": 5}
        ],
        "rate_min": 60.0,
        "rate_max": 95.0,
        "location": "Remote",
        "bio": "Experienced full-stack developer specializing in Python and modern web frameworks"
    }

    # Define search criteria
    search_skills = ["Python", "JavaScript", "React"]

    # Run the workflow
    integration = CustomFreelanceIntegration()
    await integration.run_workflow(user_data, search_skills)


if __name__ == "__main__":
    print("""
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║   Custom Freelance MCP Integration Example                  ║
║                                                              ║
║   Demonstrates automated gig search and application          ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
    """)

    asyncio.run(main())
