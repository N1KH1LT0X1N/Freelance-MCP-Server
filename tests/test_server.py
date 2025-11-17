"""
Unit tests for Freelance MCP Server

Tests all tools, resources, and core functionality.

Usage:
    pytest tests/test_server.py
    python -m pytest tests/
"""

import asyncio
import json
import os
import sys
from pathlib import Path

import pytest

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


@pytest.fixture
async def client_session():
    """Create a client session for testing"""
    server_params = StdioServerParameters(
        command="python",
        args=["freelance_server.py", "stdio"],
        env=dict(os.environ)
    )

    transport = await stdio_client(server_params).__aenter__()
    read, write = transport

    session = await ClientSession(read, write).__aenter__()
    await session.initialize()

    yield session

    await session.__aexit__(None, None, None)
    await transport.__aexit__(None, None, None)


@pytest.mark.asyncio
async def test_server_initialization(client_session):
    """Test that server initializes correctly"""
    assert client_session is not None


@pytest.mark.asyncio
async def test_list_tools(client_session):
    """Test listing available tools"""
    result = await client_session.list_tools()
    tools = [tool.name for tool in result.tools]

    expected_tools = [
        "search_gigs",
        "validate",
        "analyze_profile_fit",
        "generate_proposal",
        "negotiate_rate",
        "create_user_profile",
        "code_review",
        "code_debug",
        "optimize_profile",
        "track_application_status"
    ]

    for tool in expected_tools:
        assert tool in tools, f"Tool {tool} not found"


@pytest.mark.asyncio
async def test_list_resources(client_session):
    """Test listing available resources"""
    result = await client_session.list_resources()
    resource_uris = [resource.uri for resource in result.resources]

    expected_resources = [
        "freelance://profile/{profile_id}",
        "freelance://gigs/{platform}",
        "freelance://market-trends"
    ]

    for resource in expected_resources:
        assert resource in resource_uris, f"Resource {resource} not found"


@pytest.mark.asyncio
async def test_search_gigs_basic(client_session):
    """Test basic gig search"""
    result = await client_session.call_tool("search_gigs", {
        "skills": ["Python"],
        "max_budget": 1000
    })

    assert result.content
    content_text = result.content[0].text
    data = json.loads(content_text)

    assert "matches" in data
    assert "total_found" in data
    assert isinstance(data["matches"], list)


@pytest.mark.asyncio
async def test_search_gigs_with_filters(client_session):
    """Test gig search with multiple filters"""
    result = await client_session.call_tool("search_gigs", {
        "skills": ["React", "TypeScript"],
        "platforms": ["upwork"],
        "project_type": "fixed_price",
        "max_budget": 2000
    })

    content_text = result.content[0].text
    data = json.loads(content_text)

    assert "matches" in data
    # Should find at least the upwork_001 React gig
    if data["total_found"] > 0:
        assert data["matches"][0]["platform"] == "upwork"


@pytest.mark.asyncio
async def test_create_user_profile(client_session):
    """Test user profile creation"""
    profile_data = {
        "name": "Test User",
        "title": "Software Engineer",
        "skills": [
            {"name": "Python", "level": "advanced", "years_experience": 3}
        ],
        "hourly_rate_min": 50.0,
        "hourly_rate_max": 80.0,
        "location": "Remote"
    }

    result = await client_session.call_tool("create_user_profile", profile_data)
    content_text = result.content[0].text
    data = json.loads(content_text)

    assert "profile_id" in data
    assert data["name"] == "Test User"


@pytest.mark.asyncio
async def test_analyze_profile_fit(client_session):
    """Test profile fit analysis"""
    # First create a profile
    profile_data = {
        "name": "Test Analyst",
        "title": "React Developer",
        "skills": [
            {"name": "React", "level": "expert", "years_experience": 5},
            {"name": "TypeScript", "level": "advanced", "years_experience": 4}
        ],
        "hourly_rate_min": 60.0,
        "hourly_rate_max": 90.0
    }

    profile_result = await client_session.call_tool("create_user_profile", profile_data)
    profile_text = profile_result.content[0].text
    profile = json.loads(profile_text)
    profile_id = profile["profile_id"]

    # Analyze fit with React gig
    result = await client_session.call_tool("analyze_profile_fit", {
        "profile_id": profile_id,
        "gig_id": "upwork_001"  # React e-commerce gig
    })

    content_text = result.content[0].text
    data = json.loads(content_text)

    assert "overall_score" in data
    assert "skill_match" in data
    assert "recommendation" in data
    assert data["overall_score"] >= 0.7  # Should be a good match


@pytest.mark.asyncio
async def test_code_review(client_session):
    """Test code review functionality"""
    code = """
def calculate_sum(numbers):
    total = 0
    for num in numbers:
        total += num
    return total
"""

    result = await client_session.call_tool("code_review", {
        "code_snippet": code,
        "language": "python",
        "review_type": "general"
    })

    content_text = result.content[0].text
    data = json.loads(content_text)

    assert "quality_score" in data
    assert "issues" in data
    assert "suggestions" in data


@pytest.mark.asyncio
async def test_code_debug(client_session):
    """Test code debugging functionality"""
    buggy_code = """
def process_items(items):
    result = []
    for item in items:
        result.append(item * 2)
    return result
"""

    result = await client_session.call_tool("code_debug", {
        "code_snippet": buggy_code,
        "language": "python",
        "issue_description": "Add type hints",
        "fix_type": "auto"
    })

    content_text = result.content[0].text
    data = json.loads(content_text)

    assert "fixed_code" in data
    assert "issues_found" in data


@pytest.mark.asyncio
async def test_validate_owner(client_session):
    """Test owner validation"""
    country_code = os.getenv("OWNER_COUNTRY_CODE", "1")
    phone = os.getenv("OWNER_PHONE_NUMBER", "5551234567")

    result = await client_session.call_tool("validate", {
        "country_code": country_code,
        "phone_number": phone
    })

    content_text = result.content[0].text
    data = json.loads(content_text)

    assert "valid" in data
    assert data["valid"] is True


@pytest.mark.asyncio
async def test_track_application_status(client_session):
    """Test application tracking"""
    result = await client_session.call_tool("track_application_status", {
        "profile_id": "test_profile",
        "gig_ids": ["upwork_001", "fiverr_001"]
    })

    content_text = result.content[0].text
    data = json.loads(content_text)

    assert "applications" in data
    assert isinstance(data["applications"], list)


@pytest.mark.asyncio
async def test_read_market_trends_resource(client_session):
    """Test reading market trends resource"""
    result = await client_session.read_resource("freelance://market-trends")

    assert result.contents
    content_text = result.contents[0].text
    data = json.loads(content_text)

    assert "hot_skills" in data
    assert "average_rates" in data
    assert "platform_competition" in data


@pytest.mark.asyncio
async def test_read_platform_gigs_resource(client_session):
    """Test reading platform-specific gigs"""
    result = await client_session.read_resource("freelance://gigs/upwork")

    assert result.contents
    content_text = result.contents[0].text
    data = json.loads(content_text)

    assert isinstance(data, list)
    # Should have upwork gigs
    if len(data) > 0:
        assert "id" in data[0]
        assert "title" in data[0]


# AI-powered tests (require GROQ_API_KEY)
@pytest.mark.skipif(
    not os.getenv("GROQ_API_KEY") or len(os.getenv("GROQ_API_KEY", "")) < 20,
    reason="GROQ_API_KEY not configured"
)
@pytest.mark.asyncio
async def test_generate_proposal(client_session):
    """Test AI proposal generation"""
    profile_data = {
        "name": "AI Test User",
        "title": "Full-Stack Developer",
        "skills": [
            {"name": "React", "level": "expert", "years_experience": 5}
        ],
        "hourly_rate_min": 70.0,
        "hourly_rate_max": 100.0
    }

    result = await client_session.call_tool("generate_proposal", {
        "gig_id": "upwork_001",
        "user_profile": profile_data,
        "tone": "professional"
    })

    content_text = result.content[0].text
    data = json.loads(content_text)

    assert "proposal" in data
    assert len(data["proposal"]) > 50  # Should be a substantial proposal


@pytest.mark.skipif(
    not os.getenv("GROQ_API_KEY") or len(os.getenv("GROQ_API_KEY", "")) < 20,
    reason="GROQ_API_KEY not configured"
)
@pytest.mark.asyncio
async def test_negotiate_rate(client_session):
    """Test AI rate negotiation"""
    result = await client_session.call_tool("negotiate_rate", {
        "current_rate": 50.0,
        "target_rate": 75.0,
        "justification_points": ["5+ years experience", "Expert in React"],
        "project_complexity": "high"
    })

    content_text = result.content[0].text
    data = json.loads(content_text)

    assert "strategy" in data
    assert "talking_points" in data


@pytest.mark.skipif(
    not os.getenv("GROQ_API_KEY") or len(os.getenv("GROQ_API_KEY", "")) < 20,
    reason="GROQ_API_KEY not configured"
)
@pytest.mark.asyncio
async def test_optimize_profile(client_session):
    """Test AI profile optimization"""
    profile_data = {
        "name": "Optimization Test",
        "title": "Developer",
        "skills": [{"name": "Python", "level": "intermediate", "years_experience": 2}],
        "hourly_rate_min": 40.0,
        "hourly_rate_max": 60.0
    }

    result = await client_session.call_tool("optimize_profile", {
        "profile_data": profile_data,
        "target_platforms": ["upwork", "toptal"]
    })

    content_text = result.content[0].text
    data = json.loads(content_text)

    assert "recommendations" in data
    assert isinstance(data["recommendations"], list)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
