# MCP Integration Guide - Freelance Gig Aggregator

Complete guide for integrating and using this MCP server with Claude and other MCP clients.

---

## 🎯 What is MCP?

**Model Context Protocol (MCP)** is an open protocol that standardizes how applications provide context to LLMs. This server implements MCP to give Claude and other LLMs access to freelance gig data, AI-powered proposal generation, and market insights.

---

## 📋 Table of Contents

1. [Quick Start](#quick-start)
2. [MCP Capabilities](#mcp-capabilities)
3. [Tools Reference](#tools-reference)
4. [Resources Reference](#resources-reference)
5. [Prompts Reference](#prompts-reference)
6. [Integration Examples](#integration-examples)
7. [Best Practices](#best-practices)

---

## 🚀 Quick Start

### For Claude Desktop Users

1. **Install Dependencies**
   ```bash
   ./install.sh
   ```

2. **Configure Claude Desktop**

   Edit `claude_desktop_config.json`:

   **Windows:** `%APPDATA%\Claude\claude_desktop_config.json`
   **Mac:** `~/Library/Application Support/Claude/claude_desktop_config.json`
   **Linux:** `~/.config/Claude/claude_desktop_config.json`

   ```json
   {
     "mcpServers": {
       "freelance": {
         "command": "python",
         "args": ["/absolute/path/to/freelance_server.py", "stdio"],
         "env": {
           "GROQ_API_KEY": "your_groq_api_key_here"
         }
       }
     }
   }
   ```

3. **Restart Claude Desktop**

4. **Test the Connection**

   In Claude, try:
   - "Show me Python freelance gigs under $1000"
   - "Help me create a freelancer profile"
   - "Generate a proposal for gig upwork_001"

---

## 🔧 MCP Capabilities

### What This Server Provides

```json
{
  "name": "Freelance Gig Aggregator",
  "version": "2.1.0",
  "protocol_version": "2024-11-05",
  "capabilities": {
    "tools": {
      "count": 10,
      "ai_powered": 3
    },
    "resources": {
      "count": 3,
      "dynamic": true
    },
    "prompts": {
      "count": 8,
      "workflows": true
    }
  }
}
```

### Core Capabilities

✅ **10 Tools** - Search gigs, generate proposals, code review, etc.
✅ **3 Resources** - Profile data, gig listings, market trends
✅ **8 Prompts** - Pre-configured workflows for common tasks
✅ **6 Platforms** - Upwork, Fiverr, Freelancer, Toptal, Guru, PeoplePerHour
✅ **AI Integration** - ChatGroq for intelligent content generation
✅ **Persistent Storage** - Optional SQLite database
✅ **Real-time Data** - Live gig information (demo with 17 samples)

---

## 🛠️ Tools Reference

### 1. search_gigs

**Purpose:** Search for freelance gigs across platforms

**MCP Tool Call:**
```json
{
  "name": "search_gigs",
  "arguments": {
    "skills": ["Python", "Django"],
    "max_budget": 2000,
    "project_type": "fixed_price",
    "platforms": ["upwork", "freelancer"]
  }
}
```

**Returns:** List of matching gigs with scores

**Use Cases:**
- Find opportunities matching your skills
- Filter by budget and project type
- Compare across platforms

---

### 2. create_user_profile

**Purpose:** Create a freelancer profile

**MCP Tool Call:**
```json
{
  "name": "create_user_profile",
  "arguments": {
    "name": "Jane Doe",
    "title": "Full-Stack Developer",
    "skills": [
      {"name": "Python", "level": "expert", "years_experience": 5}
    ],
    "hourly_rate_min": 60,
    "hourly_rate_max": 95
  }
}
```

**Returns:** Profile ID and confirmation

---

### 3. analyze_profile_fit

**Purpose:** Analyze how well a profile matches a gig

**MCP Tool Call:**
```json
{
  "name": "analyze_profile_fit",
  "arguments": {
    "profile_id": "user_123",
    "gig_id": "upwork_001"
  }
}
```

**Returns:** Match score, skills analysis, recommendation

---

### 4. generate_proposal (AI-Powered 🤖)

**Purpose:** Generate personalized proposals using AI

**MCP Tool Call:**
```json
{
  "name": "generate_proposal",
  "arguments": {
    "gig_id": "upwork_001",
    "user_profile": {...},
    "tone": "professional",
    "include_portfolio": true
  }
}
```

**Requires:** GROQ_API_KEY environment variable

**Returns:** AI-generated proposal text

---

### 5. negotiate_rate (AI-Powered 🤖)

**Purpose:** Get AI-powered rate negotiation strategies

**MCP Tool Call:**
```json
{
  "name": "negotiate_rate",
  "arguments": {
    "current_rate": 50,
    "target_rate": 75,
    "justification_points": ["5+ years experience", "Expert certifications"],
    "project_complexity": "high"
  }
}
```

**Returns:** Negotiation strategy and talking points

---

### 6. code_review

**Purpose:** Review code quality with detailed metrics

**MCP Tool Call:**
```json
{
  "name": "code_review",
  "arguments": {
    "code_snippet": "function example() { var x = 1; }",
    "language": "javascript",
    "review_type": "general"
  }
}
```

**Returns:** Quality score, issues, suggestions

---

### 7. code_debug

**Purpose:** Debug and auto-fix code issues

**MCP Tool Call:**
```json
{
  "name": "code_debug",
  "arguments": {
    "code_snippet": "...",
    "language": "python",
    "issue_description": "Add type hints",
    "fix_type": "auto"
  }
}
```

**Returns:** Fixed code and explanation

---

### 8. optimize_profile (AI-Powered 🤖)

**Purpose:** Get AI recommendations for profile improvement

**MCP Tool Call:**
```json
{
  "name": "optimize_profile",
  "arguments": {
    "profile_data": {...},
    "target_platforms": ["upwork", "toptal"]
  }
}
```

**Returns:** Optimization recommendations

---

### 9. track_application_status

**Purpose:** Track application performance

**MCP Tool Call:**
```json
{
  "name": "track_application_status",
  "arguments": {
    "profile_id": "user_123",
    "gig_ids": ["upwork_001", "fiverr_001"]
  }
}
```

**Returns:** Application statistics and metrics

---

### 10. validate

**Purpose:** Validate server owner phone number

**MCP Tool Call:**
```json
{
  "name": "validate",
  "arguments": {
    "country_code": "1",
    "phone_number": "5551234567"
  }
}
```

**Returns:** Validation result

---

## 📚 Resources Reference

### 1. freelance://profile/{profile_id}

**Purpose:** Access user profile data

**Example:**
```
freelance://profile/user_123
```

**Returns:** Complete profile with skills, rates, history

**MCP Resource Call:**
```json
{
  "uri": "freelance://profile/user_123"
}
```

---

### 2. freelance://gigs/{platform}

**Purpose:** Get platform-specific gigs

**Example:**
```
freelance://gigs/upwork
freelance://gigs/fiverr
```

**Supported Platforms:**
- upwork
- fiverr
- freelancer
- toptal
- guru
- peopleperhour

---

### 3. freelance://market-trends

**Purpose:** Access current market insights

**Example:**
```
freelance://market-trends
```

**Returns:**
- Hot skills
- Average rates by category
- Platform competition analysis
- Success tips

---

## 🎯 Prompts Reference

MCP Prompts provide pre-configured workflows that guide the LLM through common tasks.

### 1. find_and_apply

**Purpose:** Complete workflow from search to application

**Usage in Claude:**
```
"Use the find_and_apply prompt with skills: Python, Django and max budget: 2000"
```

**What it does:**
1. Searches for matching gigs
2. Analyzes profile fit
3. Generates proposals for top matches
4. Tracks applications

---

### 2. optimize_profile

**Purpose:** Complete profile optimization workflow

**Usage:**
```
"Use the optimize_profile prompt for profile user_123 targeting upwork and toptal"
```

**What it does:**
1. Fetches current profile
2. Analyzes market trends
3. Provides optimization tips
4. Suggests rate adjustments

---

### 3. full_gig_workflow

**Purpose:** End-to-end freelancing workflow

**Usage:**
```
"Use the full_gig_workflow prompt to set me up as a Python developer at $60-90/hr"
```

**What it does:**
1. Creates profile
2. Searches for gigs
3. Analyzes fits
4. Generates proposals
5. Tracks applications

---

### 4. market_research

**Purpose:** Comprehensive market analysis

**Usage:**
```
"Use market_research prompt for React and TypeScript skills"
```

**What it does:**
1. Fetches market trends
2. Analyzes competition
3. Reviews rates
4. Identifies opportunities

---

### 5. code_review_workflow

**Purpose:** Complete code review process

**Usage:**
```
"Use code_review_workflow for my Python file with security review"
```

**What it does:**
1. Reviews code
2. Identifies issues
3. Provides fixes
4. Suggests improvements

---

### 6. proposal_generator

**Purpose:** Targeted proposal creation

**Usage:**
```
"Use proposal_generator for gig upwork_001 with professional tone"
```

**What it does:**
1. Fetches gig details
2. Analyzes requirements
3. Generates AI proposal
4. Includes portfolio

---

### 7. rate_negotiation

**Purpose:** Strategic rate negotiation

**Usage:**
```
"Use rate_negotiation to go from $50/hr to $75/hr for high complexity projects"
```

**What it does:**
1. Analyzes current vs target
2. Builds justification
3. Provides negotiation tactics
4. Suggests timing

---

### 8. skill_gap_analysis

**Purpose:** Identify missing skills

**Usage:**
```
"Use skill_gap_analysis for my current React skills wanting to do full-stack work"
```

**What it does:**
1. Analyzes current skills
2. Searches target gigs
3. Identifies gaps
4. Recommends learning path

---

## 💡 Integration Examples

### Example 1: Basic Claude Desktop Usage

```
User: "Find me Python freelance gigs under $1500"

Claude: I'll search for Python gigs within your budget.
[Uses search_gigs tool]
Found 5 matching gigs:
1. Python Automation Script - $200-400
2. Django REST API - $800-1200
...
```

### Example 2: Complete Workflow

```
User: "Help me find and apply to React gigs"

Claude: I'll guide you through the process.
[Uses full_gig_workflow prompt]

Step 1: Let's create your profile...
Step 2: Searching for React gigs...
Step 3: Found 8 matches, analyzing fit...
Step 4: Top 3 gigs have 80%+ match...
Step 5: Generating proposals...
```

### Example 3: Market Research

```
User: "What's the market like for Python developers?"

Claude: I'll research the Python market for you.
[Uses market_trends resource]
[Uses search_gigs tool]

Current Python Market:
- Average Rate: $40-100/hr
- Hot Skills: Django, FastAPI, Machine Learning
- Top Platforms: Upwork (premium), Freelancer (volume)
- Competition: Medium to High
```

---

## 🎓 Best Practices

### 1. Efficient Tool Use

❌ **Don't:**
```
"Show me gigs"
[Uses search_gigs with no filters]
[Returns too many results]
```

✅ **Do:**
```
"Show me Python gigs under $2000 on Upwork"
[Uses search_gigs with specific filters]
[Returns targeted results]
```

### 2. Leverage Prompts

❌ **Don't:**
```
[Call tools one by one manually]
```

✅ **Do:**
```
"Use the find_and_apply prompt..."
[Executes complete workflow]
```

### 3. Use Resources for Context

❌ **Don't:**
```
[Make multiple tool calls for related data]
```

✅ **Do:**
```
[Use freelance://market-trends resource]
[Get comprehensive market data in one call]
```

### 4. Combine Capabilities

```
1. Use resource to get market trends
2. Use tool to search matching gigs
3. Use AI tool to generate proposals
4. Use tracking tool to monitor results
```

---

## 🔐 Security & Privacy

- **API Keys:** Never expose in client code, use environment variables
- **Authentication:** Optional MCP_AUTH_TOKEN for production
- **Data:** In-memory by default, opt-in persistence
- **Logs:** Structured JSON logs, configurable levels

---

## 📊 Monitoring & Health

Check server health:
```python
from utils.monitoring import HealthCheck
health = HealthCheck.check_health()
```

View capabilities:
```python
from mcp_extensions.capabilities import print_capabilities
print_capabilities()
```

---

## 🆘 Troubleshooting

### Server Not Responding

1. Check Claude Desktop logs
2. Verify absolute path in config
3. Ensure Python 3.11+ installed
4. Check GROQ_API_KEY if using AI features

### Tools Not Working

1. Restart Claude Desktop
2. Check server stdout/stderr
3. Verify environment variables
4. Test server standalone: `python freelance_server.py stdio`

### AI Features Failing

1. Verify GROQ_API_KEY is set
2. Check API quota/limits
3. Review error messages
4. Test with non-AI tools first

---

## 📚 Additional Resources

- [Main README](README.md) - Project overview
- [USAGE.md](USAGE.md) - Detailed usage guide
- [DEPLOYMENT.md](DEPLOYMENT.md) - Deployment options
- [FEATURES.md](FEATURES.md) - Complete feature list

---

## 🎉 Ready to Use!

This MCP server is production-ready and fully integrated with the MCP protocol. Start using it with Claude Desktop or any MCP-compatible client!

**Server Version:** 2.1.0
**MCP Protocol:** 2024-11-05
**Status:** Production Ready ✅
