# Freelance MCP Server - Usage Guide

Detailed usage instructions for all features and tools.

## Table of Contents

1. [Running the Server](#running-the-server)
2. [Using the Clients](#using-the-clients)
3. [Available Tools](#available-tools)
4. [Available Resources](#available-resources)
5. [Advanced Usage](#advanced-usage)
6. [Examples](#examples)

## Running the Server

### Standalone Mode

```bash
# stdio mode (default for Claude Desktop)
python freelance_server.py stdio

# SSE mode (for web clients)
python freelance_server.py sse --port 8080

# Streamable HTTP mode
python freelance_server.py streamable-http --port 8080

# With uv
uv run --with mcp --with langchain-groq freelance_server.py stdio
```

### With Environment Variables

```bash
# Set variables inline
GROQ_API_KEY=your_key python freelance_server.py stdio

# Or use .env file (recommended)
python freelance_server.py stdio
```

## Using the Clients

### Main Entry Point (Recommended for Beginners)

```bash
python main.py
```

Interactive menu with options:
1. Comprehensive demo (all features)
2. Quick demo (simplified)
3. Environment check
4. Exit

### Comprehensive Client

```bash
# Full demo mode
python freelance_client.py --mode demo

# Interactive mode
python freelance_client.py --mode interactive

# Check environment
python freelance_client.py --check-env

# Custom server path
python freelance_client.py --server-path /path/to/freelance_server.py
```

### Simplified Client

```bash
# Quick demonstration
python freelance_client2.py
```

## Available Tools

### 1. search_gigs

Search for freelance gigs based on skills and criteria.

**Parameters:**
- `skills` (List[str], required) - Skills to match
- `max_budget` (float, optional) - Maximum budget filter
- `min_budget` (float, optional) - Minimum budget filter
- `project_type` (str, optional) - fixed_price, hourly, retainer, contest
- `platforms` (List[str], optional) - upwork, fiverr, freelancer, toptal, guru, peopleperhour

**Example:**
```python
result = await session.call_tool("search_gigs", {
    "skills": ["Python", "Django", "PostgreSQL"],
    "max_budget": 2000,
    "project_type": "fixed_price",
    "platforms": ["upwork", "freelancer"]
})
```

### 2. create_user_profile

Create a new freelancer profile.

**Parameters:**
- `name` (str, required)
- `title` (str, required)
- `skills` (List[dict], required) - [{"name": "Python", "level": "expert", "years_experience": 5}]
- `hourly_rate_min` (float, required)
- `hourly_rate_max` (float, required)
- `location` (str, optional)
- `bio` (str, optional)

**Example:**
```python
result = await session.call_tool("create_user_profile", {
    "name": "Jane Developer",
    "title": "Full-Stack Engineer",
    "skills": [
        {"name": "React", "level": "expert", "years_experience": 5},
        {"name": "Node.js", "level": "advanced", "years_experience": 4}
    ],
    "hourly_rate_min": 75.0,
    "hourly_rate_max": 120.0,
    "location": "Remote",
    "bio": "Experienced full-stack engineer specializing in React and Node.js"
})
```

### 3. analyze_profile_fit

Analyze how well a profile matches a gig.

**Parameters:**
- `profile_id` (str, required)
- `gig_id` (str, required)

**Returns:**
- `overall_score` - Match score (0.0 - 1.0)
- `skill_match` - Skill compatibility score
- `rate_compatibility` - Rate match score
- `recommendation` - Suggested action

### 4. generate_proposal

Generate AI-powered personalized proposal (requires GROQ_API_KEY).

**Parameters:**
- `gig_id` (str, required)
- `user_profile` (dict, required)
- `tone` (str, optional) - professional, friendly, confident
- `include_portfolio` (bool, optional)
- `custom_message` (str, optional)

**Example:**
```python
result = await session.call_tool("generate_proposal", {
    "gig_id": "upwork_001",
    "user_profile": profile_data,
    "tone": "professional",
    "include_portfolio": True,
    "custom_message": "I've built 5+ similar e-commerce sites"
})
```

### 5. negotiate_rate

Get AI-powered rate negotiation strategies (requires GROQ_API_KEY).

**Parameters:**
- `current_rate` (float, required)
- `target_rate` (float, required)
- `justification_points` (List[str], required)
- `project_complexity` (str, optional) - low, medium, high

**Example:**
```python
result = await session.call_tool("negotiate_rate", {
    "current_rate": 60.0,
    "target_rate": 85.0,
    "justification_points": [
        "7+ years React experience",
        "Built 50+ production applications",
        "Expert in TypeScript and Redux"
    ],
    "project_complexity": "high"
})
```

### 6. code_review

Review code quality and get suggestions.

**Parameters:**
- `code_snippet` (str, optional) - Code to review
- `file_path` (str, optional) - Path to file to review
- `language` (str, optional) - python, javascript, typescript, etc.
- `review_type` (str, optional) - general, security, performance

**Example:**
```python
code = """
function processData(items) {
    var results = [];
    for (var i = 0; i < items.length; i++) {
        results.push(items[i] * 2);
    }
    return results;
}
"""

result = await session.call_tool("code_review", {
    "code_snippet": code,
    "language": "javascript",
    "review_type": "general"
})
```

### 7. code_debug

Debug and automatically fix code issues.

**Parameters:**
- `code_snippet` (str, optional)
- `file_path` (str, optional)
- `language` (str, optional)
- `issue_description` (str, required)
- `fix_type` (str, optional) - auto, suggest

**Example:**
```python
result = await session.call_tool("code_debug", {
    "code_snippet": buggy_code,
    "language": "python",
    "issue_description": "Add type hints and error handling",
    "fix_type": "auto"
})
```

### 8. optimize_profile

Get AI-powered profile optimization recommendations (requires GROQ_API_KEY).

**Parameters:**
- `profile_data` (dict, required)
- `target_platforms` (List[str], optional)

### 9. track_application_status

Track application performance and status.

**Parameters:**
- `profile_id` (str, required)
- `gig_ids` (List[str], optional)

### 10. validate

Validate server owner's phone number.

**Parameters:**
- `country_code` (str, required)
- `phone_number` (str, required)

## Available Resources

### 1. freelance://profile/{profile_id}

Access user profile information.

**Example:**
```python
profile = await session.read_resource("freelance://profile/user_123")
```

### 2. freelance://gigs/{platform}

Get platform-specific gigs.

**Platforms:** upwork, fiverr, freelancer, toptal, guru, peopleperhour

**Example:**
```python
gigs = await session.read_resource("freelance://gigs/upwork")
```

### 3. freelance://market-trends

Get current freelance market trends and insights.

**Example:**
```python
trends = await session.read_resource("freelance://market-trends")
```

## Advanced Usage

### Custom Client Implementation

```python
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
import asyncio

async def my_custom_client():
    server_params = StdioServerParameters(
        command="python",
        args=["freelance_server.py", "stdio"],
        env={"GROQ_API_KEY": "your_key"}
    )

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            # Your custom logic here
            result = await session.call_tool("search_gigs", {
                "skills": ["Python"]
            })

            print(result)

asyncio.run(my_custom_client())
```

### Integration with Claude Desktop

See [README.md](README.md) section "Integration with Claude Desktop" for detailed instructions.

### Running Tests

```bash
# Run all tests
pytest tests/ -v

# Run specific test file
pytest tests/test_server.py -v

# Run with coverage
pytest tests/ --cov=. --cov-report=html

# Skip AI tests (no GROQ_API_KEY needed)
pytest tests/ -v -k "not generate_proposal and not negotiate_rate and not optimize_profile"
```

## Examples

### Example 1: Find and Apply to Gigs

```python
# Search for React gigs
gigs = await call_tool("search_gigs", {
    "skills": ["React", "TypeScript"],
    "max_budget": 2000,
    "platforms": ["upwork"]
})

# Create profile
profile = await call_tool("create_user_profile", {
    "name": "React Expert",
    "title": "Senior React Developer",
    "skills": [{"name": "React", "level": "expert", "years_experience": 6}],
    "hourly_rate_min": 80,
    "hourly_rate_max": 120
})

# Analyze fit
fit = await call_tool("analyze_profile_fit", {
    "profile_id": profile["profile_id"],
    "gig_id": gigs["matches"][0]["id"]
})

# Generate proposal if good fit
if fit["overall_score"] > 0.7:
    proposal = await call_tool("generate_proposal", {
        "gig_id": gigs["matches"][0]["id"],
        "user_profile": profile,
        "tone": "professional"
    })
```

### Example 2: Code Review Workflow

```python
# Review code
review = await call_tool("code_review", {
    "file_path": "./src/main.py",
    "language": "python",
    "review_type": "security"
})

# If issues found, debug and fix
if review["issues"]:
    fixed = await call_tool("code_debug", {
        "file_path": "./src/main.py",
        "language": "python",
        "issue_description": "Fix security issues",
        "fix_type": "auto"
    })
```

### Example 3: Profile Optimization

```python
# Get market trends
trends = await read_resource("freelance://market-trends")

# Optimize profile based on trends
optimized = await call_tool("optimize_profile", {
    "profile_data": current_profile,
    "target_platforms": ["toptal", "upwork"]
})

# Apply suggestions and update profile
# ... update logic ...
```

## Tips & Best Practices

1. **Always check environment** - Run `--check-env` before starting
2. **Use mock data for testing** - Server includes sample gigs
3. **Start with demo mode** - Learn features before interactive mode
4. **Check GROQ API limits** - Free tier has rate limits
5. **Use appropriate tone** - Professional for enterprise, friendly for startups
6. **Review before sending** - Always review AI-generated proposals
7. **Track applications** - Use `track_application_status` regularly

## Troubleshooting

### Issue: "ChatGroq not initialized"
**Solution:** Set GROQ_API_KEY in .env file

### Issue: "Server connection timeout"
**Solution:** Check that freelance_server.py is in the same directory

### Issue: "Tool call failed"
**Solution:** Check tool parameters match the expected format

### Issue: "Resource not found"
**Solution:** Verify resource URI format (e.g., "freelance://gigs/upwork")

## Need More Help?

- Check [QUICKSTART.md](QUICKSTART.md) for setup
- See [README.md](README.md) for overview
- Review [CHANGELOG.md](CHANGELOG.md) for version info
- Open an issue on GitHub
