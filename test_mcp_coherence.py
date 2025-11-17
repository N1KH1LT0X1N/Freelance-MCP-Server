#!/usr/bin/env python3
"""
Comprehensive MCP Server Coherence Test
Tests all MCP features: tools, resources, prompts, and overall coherence
"""

import asyncio
import json
import sys
from pathlib import Path

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


class MCPCoherenceTest:
    """Comprehensive test suite for MCP server coherence"""

    def __init__(self):
        self.session = None
        self.transport = None
        self.results = {
            "passed": [],
            "failed": [],
            "warnings": []
        }

    def log_pass(self, test_name: str, message: str = ""):
        """Log a passed test"""
        self.results["passed"].append(test_name)
        print(f"✅ {test_name}: {message}")

    def log_fail(self, test_name: str, error: str):
        """Log a failed test"""
        self.results["failed"].append((test_name, error))
        print(f"❌ {test_name}: {error}")

    def log_warning(self, test_name: str, message: str):
        """Log a warning"""
        self.results["warnings"].append((test_name, message))
        print(f"⚠️  {test_name}: {message}")

    async def connect(self) -> bool:
        """Connect to MCP server"""
        try:
            print("\n🔌 Connecting to MCP server...")

            server_params = StdioServerParameters(
                command="python",
                args=["freelance_server.py", "stdio"],
                env={}
            )

            self.transport = await stdio_client(server_params).__aenter__()
            read, write = self.transport
            self.session = await ClientSession(read, write).__aenter__()

            # Initialize session
            init_result = await self.session.initialize()

            server_name = init_result.serverInfo.name
            server_version = init_result.serverInfo.version

            self.log_pass("Server Connection", f"{server_name} v{server_version}")
            return True

        except Exception as e:
            self.log_fail("Server Connection", str(e))
            return False

    async def disconnect(self):
        """Disconnect from MCP server"""
        try:
            if self.session:
                await self.session.__aexit__(None, None, None)
            if self.transport:
                await self.transport.__aexit__(None, None, None)
            print("\n👋 Disconnected from server")
        except Exception as e:
            print(f"⚠️  Disconnect warning: {e}")

    async def test_capabilities_discovery(self):
        """Test 1: Capability Discovery"""
        print("\n" + "="*70)
        print("TEST 1: CAPABILITY DISCOVERY")
        print("="*70)

        try:
            # Test tools listing
            tools_result = await self.session.list_tools()
            tools_count = len(tools_result.tools)

            if tools_count == 10:
                self.log_pass("Tools Discovery", f"{tools_count} tools available")
            else:
                self.log_fail("Tools Discovery", f"Expected 10 tools, got {tools_count}")

            # Verify expected tools
            expected_tools = [
                "search_gigs", "create_user_profile", "analyze_profile_fit",
                "generate_proposal", "negotiate_rate", "code_review",
                "code_debug", "optimize_profile", "track_application_status", "validate"
            ]

            tool_names = [t.name for t in tools_result.tools]
            missing_tools = set(expected_tools) - set(tool_names)

            if not missing_tools:
                self.log_pass("Tools Completeness", "All 10 expected tools present")
            else:
                self.log_fail("Tools Completeness", f"Missing tools: {missing_tools}")

            # Test resources listing
            resources_result = await self.session.list_resources()
            resources_count = len(resources_result.resources)

            if resources_count == 3:
                self.log_pass("Resources Discovery", f"{resources_count} resources available")
            else:
                self.log_fail("Resources Discovery", f"Expected 3 resources, got {resources_count}")

            # Verify resource URIs
            resource_uris = [r.uri for r in resources_result.resources]
            print(f"   Resources: {', '.join(resource_uris)}")

            # Test prompts listing
            try:
                prompts_result = await self.session.list_prompts()
                prompts_count = len(prompts_result.prompts)

                if prompts_count == 8:
                    self.log_pass("Prompts Discovery", f"{prompts_count} prompts available")
                else:
                    self.log_warning("Prompts Discovery", f"Expected 8 prompts, got {prompts_count}")

                # Verify expected prompts
                expected_prompts = [
                    "find_and_apply", "optimize_profile", "full_gig_workflow",
                    "market_research", "code_review_workflow", "proposal_generator",
                    "rate_negotiation", "skill_gap_analysis"
                ]

                prompt_names = [p.name for p in prompts_result.prompts]
                missing_prompts = set(expected_prompts) - set(prompt_names)

                if not missing_prompts:
                    self.log_pass("Prompts Completeness", "All 8 expected prompts present")
                else:
                    self.log_warning("Prompts Completeness", f"Missing prompts: {missing_prompts}")

            except Exception as e:
                self.log_warning("Prompts Discovery", f"Prompts may not be supported: {e}")

        except Exception as e:
            self.log_fail("Capability Discovery", str(e))

    async def test_core_tools(self):
        """Test 2: Core Tools Functionality"""
        print("\n" + "="*70)
        print("TEST 2: CORE TOOLS FUNCTIONALITY")
        print("="*70)

        # Test search_gigs
        try:
            result = await self.session.call_tool("search_gigs", {
                "skills": ["Python", "Django"],
                "max_budget": 2000
            })

            content = json.loads(result.content[0].text)
            matches = content.get("matches", [])

            if matches and len(matches) > 0:
                self.log_pass("search_gigs Tool", f"Found {len(matches)} matching gigs")
            else:
                self.log_warning("search_gigs Tool", "No matches found")

        except Exception as e:
            self.log_fail("search_gigs Tool", str(e))

        # Test create_user_profile
        try:
            result = await self.session.call_tool("create_user_profile", {
                "name": "Test User",
                "title": "Python Developer",
                "skills": [
                    {"name": "Python", "level": "expert", "years_experience": 5}
                ],
                "hourly_rate_min": 50,
                "hourly_rate_max": 80
            })

            content = json.loads(result.content[0].text)
            profile_id = content.get("profile_id")

            if profile_id:
                self.log_pass("create_user_profile Tool", f"Profile created: {profile_id}")
                return profile_id
            else:
                self.log_fail("create_user_profile Tool", "No profile_id returned")

        except Exception as e:
            self.log_fail("create_user_profile Tool", str(e))
            return None

    async def test_resources(self):
        """Test 3: Resource Access"""
        print("\n" + "="*70)
        print("TEST 3: RESOURCE ACCESS")
        print("="*70)

        # Test market-trends resource
        try:
            result = await self.session.read_resource("freelance://market-trends")
            content = json.loads(result.contents[0].text)

            if "hot_skills" in content and "average_rates" in content:
                hot_skills = content["hot_skills"][:3]
                self.log_pass("market-trends Resource", f"Hot skills: {', '.join(hot_skills)}")
            else:
                self.log_fail("market-trends Resource", "Missing expected data")

        except Exception as e:
            self.log_fail("market-trends Resource", str(e))

        # Test gigs resource
        try:
            result = await self.session.read_resource("freelance://gigs/upwork")
            content = json.loads(result.contents[0].text)

            if isinstance(content, list) and len(content) > 0:
                self.log_pass("gigs/upwork Resource", f"{len(content)} gigs available")
            else:
                self.log_fail("gigs/upwork Resource", "No gigs found")

        except Exception as e:
            self.log_fail("gigs/upwork Resource", str(e))

    async def test_code_tools(self):
        """Test 4: Code Review/Debug Tools"""
        print("\n" + "="*70)
        print("TEST 4: CODE TOOLS")
        print("="*70)

        sample_code = """
def calculate_total(items):
    total = 0
    for item in items:
        total += item['price']
    return total
"""

        # Test code_review
        try:
            result = await self.session.call_tool("code_review", {
                "code_snippet": sample_code,
                "language": "python",
                "review_type": "general"
            })

            content = json.loads(result.content[0].text)
            quality_score = content.get("quality_score", 0)

            if quality_score > 0:
                self.log_pass("code_review Tool", f"Quality score: {quality_score}/100")
            else:
                self.log_warning("code_review Tool", "Quality score is 0")

        except Exception as e:
            self.log_fail("code_review Tool", str(e))

        # Test code_debug
        try:
            result = await self.session.call_tool("code_debug", {
                "code_snippet": sample_code,
                "language": "python",
                "issue_description": "Add type hints",
                "fix_type": "auto"
            })

            content = json.loads(result.content[0].text)

            if "fixed_code" in content or "suggestions" in content:
                self.log_pass("code_debug Tool", "Debug suggestions provided")
            else:
                self.log_warning("code_debug Tool", "No fixes provided")

        except Exception as e:
            self.log_fail("code_debug Tool", str(e))

    async def test_ai_tools(self):
        """Test 5: AI-Powered Tools (May require API key)"""
        print("\n" + "="*70)
        print("TEST 5: AI-POWERED TOOLS")
        print("="*70)

        # Test generate_proposal
        try:
            result = await self.session.call_tool("generate_proposal", {
                "gig_id": "upwork_001",
                "user_profile": {
                    "name": "Test User",
                    "title": "Python Developer",
                    "skills": [{"name": "Python", "level": "expert", "years_experience": 5}]
                },
                "tone": "professional"
            })

            content = json.loads(result.content[0].text)

            if "proposal" in content:
                self.log_pass("generate_proposal Tool", "Proposal generated")
            elif "error" in content and "API key" in content["error"]:
                self.log_warning("generate_proposal Tool", "Requires GROQ_API_KEY (expected)")
            else:
                self.log_warning("generate_proposal Tool", str(content))

        except Exception as e:
            if "API key" in str(e):
                self.log_warning("generate_proposal Tool", "Requires GROQ_API_KEY (expected)")
            else:
                self.log_fail("generate_proposal Tool", str(e))

    async def test_prompts(self):
        """Test 6: MCP Prompts"""
        print("\n" + "="*70)
        print("TEST 6: MCP PROMPTS")
        print("="*70)

        try:
            # Test get_prompt
            result = await self.session.get_prompt("find_and_apply", {
                "skills": "Python,Django",
                "max_budget": "2000",
                "min_match_score": "0.7"
            })

            if result.messages and len(result.messages) > 0:
                message = result.messages[0].content.text
                self.log_pass("find_and_apply Prompt", "Prompt generated successfully")

                # Verify prompt contains expected workflow steps
                if "Step 1" in message and "Step 2" in message:
                    self.log_pass("Prompt Structure", "Multi-step workflow present")
                else:
                    self.log_warning("Prompt Structure", "May not have all workflow steps")
            else:
                self.log_fail("find_and_apply Prompt", "No messages returned")

        except Exception as e:
            self.log_warning("Prompts", f"Prompt functionality may not be available: {e}")

    async def test_coherence(self):
        """Test 7: Overall Coherence - Full Workflow"""
        print("\n" + "="*70)
        print("TEST 7: OVERALL COHERENCE - FULL WORKFLOW")
        print("="*70)

        try:
            # Workflow: Search → Create Profile → Analyze Fit

            # Step 1: Search
            search_result = await self.session.call_tool("search_gigs", {
                "skills": ["Python"],
                "max_budget": 5000
            })
            search_content = json.loads(search_result.content[0].text)
            gigs = search_content.get("matches", [])

            if not gigs:
                self.log_warning("Workflow Coherence", "No gigs found for workflow test")
                return

            gig_id = gigs[0]["id"]

            # Step 2: Create Profile
            profile_result = await self.session.call_tool("create_user_profile", {
                "name": "Workflow Test User",
                "title": "Python Developer",
                "skills": [{"name": "Python", "level": "expert", "years_experience": 5}],
                "hourly_rate_min": 50,
                "hourly_rate_max": 100
            })
            profile_content = json.loads(profile_result.content[0].text)
            profile_id = profile_content.get("profile_id")

            # Step 3: Analyze Fit
            fit_result = await self.session.call_tool("analyze_profile_fit", {
                "profile_id": profile_id,
                "gig_id": gig_id
            })
            fit_content = json.loads(fit_result.content[0].text)

            if "overall_score" in fit_content:
                score = fit_content["overall_score"]
                self.log_pass("Workflow Coherence", f"Complete workflow executed (fit score: {score:.2f})")
            else:
                self.log_fail("Workflow Coherence", "Workflow incomplete")

        except Exception as e:
            self.log_fail("Workflow Coherence", str(e))

    async def run_all_tests(self):
        """Run all coherence tests"""
        print("\n" + "="*70)
        print("       MCP SERVER COMPREHENSIVE COHERENCE TEST")
        print("="*70)

        # Connect
        if not await self.connect():
            print("\n❌ Cannot proceed - server connection failed")
            return

        try:
            # Run all tests
            await self.test_capabilities_discovery()
            await self.test_core_tools()
            await self.test_resources()
            await self.test_code_tools()
            await self.test_ai_tools()
            await self.test_prompts()
            await self.test_coherence()

        finally:
            await self.disconnect()

        # Print summary
        self.print_summary()

    def print_summary(self):
        """Print test summary"""
        print("\n" + "="*70)
        print("                    TEST SUMMARY")
        print("="*70)

        total_tests = len(self.results["passed"]) + len(self.results["failed"])
        passed = len(self.results["passed"])
        failed = len(self.results["failed"])
        warnings = len(self.results["warnings"])

        print(f"\n✅ Passed:   {passed}/{total_tests}")
        print(f"❌ Failed:   {failed}/{total_tests}")
        print(f"⚠️  Warnings: {warnings}")

        if self.results["failed"]:
            print("\n❌ Failed Tests:")
            for test_name, error in self.results["failed"]:
                print(f"   - {test_name}: {error}")

        if self.results["warnings"]:
            print("\n⚠️  Warnings:")
            for test_name, message in self.results["warnings"]:
                print(f"   - {test_name}: {message}")

        print("\n" + "="*70)

        if failed == 0:
            print("✅ ALL TESTS PASSED - SERVER IS COHERENT AND FUNCTIONAL!")
        elif failed <= 2:
            print("⚠️  MOSTLY FUNCTIONAL - Minor issues found")
        else:
            print("❌ MAJOR ISSUES FOUND - Needs attention")

        print("="*70 + "\n")

        return failed == 0


async def main():
    """Run MCP coherence tests"""
    tester = MCPCoherenceTest()
    success = await tester.run_all_tests()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    asyncio.run(main())
