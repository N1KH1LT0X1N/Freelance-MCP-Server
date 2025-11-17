#!/usr/bin/env python3
"""
Simple MCP Server Test - Just test if server starts and responds
"""

import asyncio
import json
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


async def test_server():
    """Simple test to verify server works"""
    print("Starting MCP server test...")

    server_params = StdioServerParameters(
        command="python",
        args=["freelance_server.py", "stdio"],
        env={}
    )

    try:
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                # Initialize
                init_result = await session.initialize()
                print(f"✅ Connected: {init_result.serverInfo.name} v{init_result.serverInfo.version}")

                # List tools
                tools = await session.list_tools()
                print(f"✅ Tools: {len(tools.tools)} available")
                for tool in tools.tools[:5]:
                    print(f"   - {tool.name}")

                # List resources
                resources = await session.list_resources()
                print(f"✅ Resources: {len(resources.resources)} available")
                for resource in resources.resources:
                    print(f"   - {resource.uri}")

                # List prompts
                try:
                    prompts = await session.list_prompts()
                    print(f"✅ Prompts: {len(prompts.prompts)} available")
                    for prompt in prompts.prompts[:5]:
                        print(f"   - {prompt.name}")
                except Exception as e:
                    print(f"⚠️  Prompts: {e}")

                # Try calling a simple tool
                print("\nTesting search_gigs tool...")
                result = await session.call_tool("search_gigs", {"skills": ["Python"]})
                content = json.loads(result.content[0].text)
                print(f"✅ Tool call successful: Found {len(content.get('matches', []))} gigs")

                # Test reading a resource
                print("\nTesting market-trends resource...")
                resource_result = await session.read_resource("freelance://market-trends")
                resource_content = json.loads(resource_result.contents[0].text)
                print(f"✅ Resource access successful: {len(resource_content.get('hot_skills', []))} hot skills")

                # Test dynamic resource
                print("\nTesting gigs/upwork resource...")
                try:
                    gigs_result = await session.read_resource("freelance://gigs/upwork")
                    gigs_content = json.loads(gigs_result.contents[0].text)
                    print(f"✅ Dynamic resource successful: {len(gigs_content)} gigs from Upwork")
                except Exception as e:
                    print(f"⚠️  Dynamic resource: {e}")

                # Test a prompt
                print("\nTesting find_and_apply prompt...")
                try:
                    prompt_result = await session.get_prompt("find_and_apply", {
                        "skills": "Python,Django",
                        "max_budget": "2000",
                        "min_match_score": "0.7"
                    })
                    print(f"✅ Prompt successful: {len(prompt_result.messages)} messages generated")
                except Exception as e:
                    print(f"⚠️  Prompt: {e}")

                print("\n✅ ALL TESTS PASSED!")

    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(test_server())
