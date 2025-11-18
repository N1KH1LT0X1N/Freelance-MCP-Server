# Freelance MCP Server - Real API Integration Setup Guide

This guide will walk you through setting up real API integrations for Upwork and Freelancer.com to fetch live gig data instead of using mock data.

---

## Table of Contents

1. [Quick Start](#quick-start)
2. [Prerequisites](#prerequisites)
3. [Installation](#installation)
4. [API Setup - Upwork](#api-setup---upwork)
5. [API Setup - Freelancer.com](#api-setup---freelancercom)
6. [Configuration](#configuration)
7. [Testing](#testing)
8. [Troubleshooting](#troubleshooting)
9. [API Limitations](#api-limitations)

---

## Quick Start

**TL;DR** - If you want to use mock data (no API setup required):

```bash
# Install dependencies
pip install -r requirements.txt

# Run with mock data (no API keys needed)
python freelance_server.py
```

The server will automatically fall back to demo data if no API keys are configured.

---

## Prerequisites

Before you begin, ensure you have:

- Python 3.8 or higher
- Active accounts on platforms you want to integrate:
  - **Upwork** account (for Upwork API)
  - **Freelancer.com** account (for Freelancer API)
- A **Groq API key** (for AI-powered features)

---

## Installation

### 1. Clone the Repository

```bash
git clone <your-repo-url>
cd Freelance-MCP-Server
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

This will install:
- `mcp` - MCP server framework
- `aiohttp` - Async HTTP client
- `tenacity` - Retry logic
- `cachetools` - Response caching
- `freelancersdk` - Freelancer.com Python SDK
- `langchain-groq` - AI/LLM integration
- And other required dependencies

### 3. Create Environment File

```bash
cp .env.example .env
```

Now edit `.env` with your actual API credentials (see sections below).

---

## API Setup - Upwork

### Why Upwork?

Upwork is the **highest priority** platform with:
- ✅ Full GraphQL API
- ✅ Comprehensive job search
- ✅ Free tier available
- ✅ Excellent documentation

### Step-by-Step Setup

#### 1. Create Upwork Account

If you don't have one already, sign up at [upwork.com](https://www.upwork.com).

#### 2. Request API Access

1. Log into your Upwork account
2. Navigate to: **Settings → API Access**
   - Or visit directly: https://www.upwork.com/services/api/keys
3. Click **"Create a Key"**
4. Fill in the application details:
   - **Application Name**: `Freelance MCP Server` (or your preferred name)
   - **Key Type**: Select **OAuth 2.0**
   - **Application Description**: Brief description of your use case
   - **Callback URL**: `http://localhost:8080/callback` (for local testing)

#### 3. Request Permissions

**IMPORTANT**: You must request the following permission:

- ✅ **"Read marketplace Job Postings - Public"**

Without this permission, you won't be able to search for jobs.

#### 4. Get Your Credentials

Once approved (usually instant for basic access), you'll receive:

- **Client ID** (also called API Key)
- **Client Secret**

#### 5. Get Access Token

**Option A: Using OAuth 2.0 Flow (Recommended)**

Run this Python script to get your access token:

```python
import requests
from urllib.parse import urlencode

# Your credentials
CLIENT_ID = "your_client_id_here"
CLIENT_SECRET = "your_client_secret_here"
REDIRECT_URI = "http://localhost:8080/callback"

# Step 1: Get authorization code
auth_url = "https://www.upwork.com/ab/account-security/oauth2/authorize"
params = {
    "client_id": CLIENT_ID,
    "redirect_uri": REDIRECT_URI,
    "response_type": "code"
}

print(f"Visit this URL and authorize:\n{auth_url}?{urlencode(params)}\n")
auth_code = input("Enter the authorization code from the callback URL: ")

# Step 2: Exchange code for access token
token_url = "https://www.upwork.com/api/v3/oauth2/token"
data = {
    "grant_type": "authorization_code",
    "code": auth_code,
    "client_id": CLIENT_ID,
    "client_secret": CLIENT_SECRET,
    "redirect_uri": REDIRECT_URI
}

response = requests.post(token_url, data=data)
tokens = response.json()

print("\n=== Your Tokens ===")
print(f"Access Token: {tokens['access_token']}")
print(f"Refresh Token: {tokens['refresh_token']}")
print(f"Expires in: {tokens['expires_in']} seconds")
```

**Option B: Manual OAuth Flow**

1. Visit: `https://www.upwork.com/ab/account-security/oauth2/authorize?client_id=YOUR_CLIENT_ID&redirect_uri=http://localhost:8080/callback&response_type=code`
2. Authorize the application
3. Copy the `code` from the redirect URL
4. Exchange it for an access token using curl:

```bash
curl -X POST "https://www.upwork.com/api/v3/oauth2/token" \
  -d "grant_type=authorization_code" \
  -d "code=YOUR_AUTH_CODE" \
  -d "client_id=YOUR_CLIENT_ID" \
  -d "client_secret=YOUR_CLIENT_SECRET" \
  -d "redirect_uri=http://localhost:8080/callback"
```

#### 6. Add to .env File

Open your `.env` file and add:

```env
UPWORK_CLIENT_ID=your_actual_client_id
UPWORK_CLIENT_SECRET=your_actual_client_secret
UPWORK_ACCESS_TOKEN=your_actual_access_token
UPWORK_REFRESH_TOKEN=your_actual_refresh_token
```

### Token Expiration

- **Access Token**: Expires in 24 hours
- **Refresh Token**: Valid for 2 weeks (refreshes automatically)

The server will automatically refresh your access token using the refresh token.

---

## API Setup - Freelancer.com

### Why Freelancer.com?

Freelancer.com provides:
- ✅ Official Python SDK
- ✅ REST API
- ✅ Good documentation
- ✅ Free tier available

### Step-by-Step Setup

#### 1. Create Freelancer.com Account

Sign up at [freelancer.com](https://www.freelancer.com) if you don't have an account.

#### 2. Register Your Application

1. Visit: https://developers.freelancer.com/
2. Click **"Register Application"** or **"Get API Access"**
3. Fill in application details:
   - **Application Name**: `Freelance MCP Server`
   - **Description**: Brief description
   - **Callback URL**: `http://localhost:8080/callback`

#### 3. Get OAuth Token

**Option A: Using the Python SDK**

```python
from freelancersdk.session import Session
from freelancersdk.resources.auth import get_oauth2_token

# Your app credentials
CLIENT_ID = "your_client_id"
CLIENT_SECRET = "your_client_secret"
REDIRECT_URI = "http://localhost:8080/callback"

# Step 1: Get authorization URL
auth_url = f"https://accounts.freelancer.com/oauth/authorize?client_id={CLIENT_ID}&response_type=code&redirect_uri={REDIRECT_URI}"

print(f"Visit: {auth_url}")
code = input("Enter authorization code: ")

# Step 2: Exchange for token
token = get_oauth2_token(
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET,
    code=code,
    redirect_uri=REDIRECT_URI
)

print(f"OAuth Token: {token}")
```

**Option B: Manual Process**

1. Visit: `https://accounts.freelancer.com/oauth/authorize?client_id=YOUR_CLIENT_ID&response_type=code&redirect_uri=http://localhost:8080/callback`
2. Authorize the app
3. Get the code from the redirect
4. Exchange for token:

```bash
curl -X POST "https://accounts.freelancer.com/oauth/token" \
  -d "grant_type=authorization_code" \
  -d "code=YOUR_CODE" \
  -d "client_id=YOUR_CLIENT_ID" \
  -d "client_secret=YOUR_CLIENT_SECRET" \
  -d "redirect_uri=http://localhost:8080/callback"
```

#### 4. Add to .env File

```env
FREELANCER_CLIENT_ID=your_actual_client_id
FREELANCER_CLIENT_SECRET=your_actual_client_secret
FREELANCER_OAUTH_TOKEN=your_actual_oauth_token
```

---

## Configuration

### Full .env File Example

```env
# AI/LLM
GROQ_API_KEY=gsk_your_groq_key_here

# Owner Phone
OWNER_COUNTRY_CODE=1
OWNER_PHONE_NUMBER=5551234567

# Upwork API
UPWORK_CLIENT_ID=your_upwork_client_id
UPWORK_CLIENT_SECRET=your_upwork_client_secret
UPWORK_ACCESS_TOKEN=your_upwork_access_token
UPWORK_REFRESH_TOKEN=your_upwork_refresh_token

# Freelancer.com API
FREELANCER_CLIENT_ID=your_freelancer_client_id
FREELANCER_CLIENT_SECRET=your_freelancer_client_secret
FREELANCER_OAUTH_TOKEN=your_freelancer_oauth_token

# Optional settings
RATE_LIMIT_REQUESTS_PER_MINUTE=60
CACHE_TTL_SECONDS=300
ENABLED_PLATFORMS=upwork,freelancer
```

### Configuration Options

| Variable | Required | Description | Default |
|----------|----------|-------------|---------|
| `GROQ_API_KEY` | Yes | Groq API key for AI features | - |
| `UPWORK_ACCESS_TOKEN` | No* | Upwork API access token | - |
| `FREELANCER_OAUTH_TOKEN` | No* | Freelancer OAuth token | - |
| `RATE_LIMIT_REQUESTS_PER_MINUTE` | No | API rate limit | 60 |
| `CACHE_TTL_SECONDS` | No | Cache duration | 300 |
| `ENABLED_PLATFORMS` | No | Active platforms | All |

*At least one platform API key is recommended for real data

---

## Testing

### 1. Verify Installation

```bash
python -c "import freelance_api_clients; print('✅ API clients module loaded')"
```

### 2. Test API Clients

Run the built-in test:

```bash
python freelance_api_clients.py
```

Expected output:
```
Testing Freelance API Clients

✅ Upwork: API client initialized
✅ Freelancer.com: API client initialized
🔍 Searching real APIs for gigs with skills: ['Python', 'Django', 'React']
✅ Upwork: Found 5 gigs
✅ Freelancer.com: Found 4 gigs

Total gigs found: 9
Platforms searched: ['upwork', 'freelancer']

Top 3 matches:
1. Build a Django REST API with React Frontend
   Platform: upwork
   Budget: $1000-$2000
   Match: 100.0%
   URL: https://www.upwork.com/jobs/~123456
...
```

### 3. Test MCP Server

```bash
python freelance_server.py
```

### 4. Test Search Function

Using the MCP client or direct call:

```python
import asyncio
from freelance_server import search_gigs

async def test_search():
    results = await search_gigs(
        skills=["Python", "React", "AWS"],
        max_budget=5000,
        project_type="fixed_price",
        use_real_api=True
    )

    print(f"Data source: {results['data_source']}")
    print(f"Total found: {results['total_found']}")

    for gig in results['gigs'][:3]:
        print(f"\n{gig['title']}")
        print(f"  Platform: {gig['platform']}")
        print(f"  Budget: {gig['budget']}")
        print(f"  Match: {gig['match_score']}%")

asyncio.run(test_search())
```

### 5. Test with Mock Data

To test without API keys:

```python
results = await search_gigs(
    skills=["Python"],
    use_real_api=False  # Force mock data
)
```

---

## Troubleshooting

### Common Issues

#### 1. "No API clients available"

**Problem**: No platforms are initialized.

**Solution**:
- Verify `.env` file exists and has correct API keys
- Check that at least one set of credentials is valid
- Run with `DEBUG=true` in `.env` for more info

#### 2. "Upwork authentication failed (401)"

**Possible causes**:
- Access token expired (they last 24 hours)
- Invalid credentials
- Missing permissions

**Solution**:
```python
# Check if token needs refresh
# The server should auto-refresh, but you can manually refresh:
# 1. Use the refresh token to get a new access token
# 2. Update .env with new access token
```

#### 3. "Rate limit exceeded (429)"

**Problem**: Too many API requests.

**Solution**:
- The client has built-in rate limiting and caching
- Increase `CACHE_TTL_SECONDS` in .env
- Reduce `RATE_LIMIT_REQUESTS_PER_MINUTE`
- Wait a few minutes before retrying

#### 4. "Freelancer.com: No OAuth token configured"

**Problem**: Missing Freelancer API credentials.

**Solution**:
- Complete the Freelancer.com API setup
- Add `FREELANCER_OAUTH_TOKEN` to `.env`
- Or disable Freelancer: `ENABLED_PLATFORMS=upwork`

#### 5. "Module not found: freelance_api_clients"

**Problem**: API client module not in Python path.

**Solution**:
```bash
# Ensure you're in the correct directory
cd /path/to/Freelance-MCP-Server

# Or install in development mode
pip install -e .
```

### Debug Mode

Enable verbose logging:

```env
DEBUG=true
```

Then check console output for detailed error messages.

---

## API Limitations

### Upwork

| Limit | Value |
|-------|-------|
| **Rate Limit** | ~60-100 requests/minute |
| **Results per Query** | 10 (default), max varies |
| **Access Token TTL** | 24 hours |
| **Refresh Token TTL** | 2 weeks |
| **Cost** | Free tier available |

**Notes**:
- GraphQL API is newer and preferred
- Some fields require additional permissions
- Rate limits are per user/app combination

### Freelancer.com

| Limit | Value |
|-------|-------|
| **Rate Limit** | ~60 requests/minute |
| **Results per Query** | Configurable (default: 10) |
| **Token TTL** | Varies by implementation |
| **Cost** | Free tier available |

**Notes**:
- Python SDK handles rate limiting
- OAuth token doesn't expire frequently
- Full description requires special flag

---

## Advanced Usage

### Caching Strategy

The API clients implement a TTL cache (default: 5 minutes):

```python
# Adjust cache TTL
from freelance_api_clients import UpworkAPIClient

client = UpworkAPIClient(cache_ttl=600)  # 10 minutes
```

### Custom Platform Selection

Enable only specific platforms:

```python
from freelance_api_clients import FreelanceAPIAggregator

aggregator = FreelanceAPIAggregator(
    enabled_platforms=["upwork"]  # Only use Upwork
)
```

### Retry Logic

Built-in retry with exponential backoff:

```python
# Automatically retries up to 3 times
# Waits: 2s, 4s, 8s between retries
# Only on rate limit errors
```

---

## Performance Tips

1. **Use Caching**: Default 5-minute cache prevents redundant API calls
2. **Rate Limiting**: Built-in delays prevent 429 errors
3. **Concurrent Searches**: Platforms are searched in parallel
4. **Pagination**: Implement pagination for large result sets
5. **Filter Early**: Use min/max budget filters to reduce results

---

## Security Best Practices

1. **Never commit .env file** to git
2. **Rotate tokens regularly** (especially after testing)
3. **Use environment variables** in production
4. **Limit API permissions** to only what's needed
5. **Monitor API usage** to detect anomalies

---

## Getting Help

### Resources

- **Upwork API Docs**: https://developers.upwork.com/
- **Freelancer API Docs**: https://developers.freelancer.com/
- **MCP Documentation**: https://docs.mcp.io/
- **GitHub Issues**: [Your repo issues page]

### Support Channels

1. Check this guide first
2. Review API documentation
3. Enable DEBUG mode for detailed logs
4. Open a GitHub issue with:
   - Error message
   - Steps to reproduce
   - Debug logs (redact sensitive info)

---

## Next Steps

Once you have real API integration working:

1. ✅ Test different search queries
2. ✅ Monitor API usage and costs
3. ✅ Customize match scoring algorithm
4. ✅ Add more platforms (if APIs become available)
5. ✅ Implement webhook notifications
6. ✅ Build a frontend dashboard

---

## Appendix: Platform API Status

| Platform | API Available | SDK Available | Recommended |
|----------|--------------|---------------|-------------|
| **Upwork** | ✅ Yes (GraphQL) | ❌ No official | ✅ **Yes** |
| **Freelancer.com** | ✅ Yes (REST) | ✅ Python SDK | ✅ **Yes** |
| **Guru.com** | ❌ No | ❌ No | ❌ No |
| **Fiverr** | ❌ No official | ❌ No | ❌ No |
| **PeoplePerHour** | ⚠️ Private only | ❌ No | ⚠️ Future |
| **Toptal** | ❌ No | ❌ No | ❌ No |

*Status as of November 2025*

---

**Happy Freelancing! 🚀**

For questions or issues, please open a GitHub issue or check the documentation.
