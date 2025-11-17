# Examples

This directory contains example code demonstrating various ways to integrate and extend the Freelance MCP Server.

## Available Examples

### 1. custom_client.py

**Purpose:** Demonstrates how to build a custom MCP client with your own workflow logic.

**Features:**
- Profile setup automation
- Gig search integration
- Automated proposal generation
- Complete application workflow

**Usage:**
```bash
python examples/custom_client.py
```

**What it does:**
1. Connects to the MCP server
2. Creates a user profile
3. Searches for matching gigs
4. Analyzes fit for each gig
5. Generates and submits proposals for good matches

### 2. batch_processor.py (Future)

Process multiple gig applications in batch mode.

### 3. webhook_integration.py (Future)

Integrate with external services using webhooks.

### 4. api_wrapper.py (Future)

REST API wrapper around the MCP server.

## Creating Your Own Integration

### Basic Pattern

```python
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

async def my_integration():
    # 1. Setup connection
    server_params = StdioServerParameters(
        command="python",
        args=["freelance_server.py", "stdio"]
    )

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            # 2. Call tools
            result = await session.call_tool("search_gigs", {
                "skills": ["Python"]
            })

            # 3. Process results
            # ... your logic here ...
```

### Common Use Cases

#### Automated Job Application

```python
# Search → Analyze → Apply workflow
gigs = await search_gigs(skills)
for gig in gigs:
    if analyze_fit(gig) > 0.7:
        proposal = generate_proposal(gig)
        submit_application(gig, proposal)
```

#### Portfolio Optimization

```python
# Get optimization recommendations
recommendations = await optimize_profile(profile)
apply_recommendations(recommendations)
retest_profile()
```

#### Market Research

```python
# Analyze market trends
trends = await get_market_trends()
analyze_competition(trends)
adjust_rates(trends)
```

## Best Practices

1. **Always close connections properly**
   ```python
   async with stdio_client(...) as transport:
       # ... use connection ...
   # Connection automatically closed
   ```

2. **Handle errors gracefully**
   ```python
   try:
       result = await call_tool(...)
   except Exception as e:
       logger.error(f"Tool call failed: {e}")
       # Implement fallback logic
   ```

3. **Parse results carefully**
   ```python
   if hasattr(result, 'content'):
       data = json.loads(result.content[0].text)
   ```

4. **Use async/await properly**
   - All MCP calls are async
   - Use `asyncio.run()` for main entry point
   - Use `await` for all tool calls

5. **Cache frequently accessed data**
   - Market trends
   - User profiles
   - Common search results

## Extending the Examples

### Add Your Own Tools

1. Modify `freelance_server.py`
2. Add new tool with `@mcp.tool()` decorator
3. Update client to use new tool

### Add Custom Workflows

1. Create new file in `examples/`
2. Import base client classes
3. Implement your workflow logic
4. Add documentation here

### Add External Integrations

```python
# Example: Slack notifications
async def notify_slack(message):
    webhook_url = "your_webhook_url"
    requests.post(webhook_url, json={"text": message})

# Use in workflow
await apply_to_gig(gig)
await notify_slack(f"Applied to {gig['title']}")
```

## Testing Your Integration

```bash
# Run with test data
python your_integration.py --test-mode

# Run with dry-run (no actual applications)
python your_integration.py --dry-run

# Run with specific profile
python your_integration.py --profile myprofile.json
```

## Need Help?

- Check [USAGE.md](../USAGE.md) for tool documentation
- See [QUICKSTART.md](../QUICKSTART.md) for setup help
- Open an issue on GitHub for questions

## Contributing Examples

Have a cool integration? Submit a PR!

1. Add your example file
2. Update this README
3. Include documentation
4. Add usage instructions
