# Freelance Platform API Research & Documentation

## Executive Summary

This document provides comprehensive research on available APIs for freelance platforms, their capabilities, limitations, and implementation requirements.

---

## Platform-by-Platform Analysis

### 1. Upwork API ✅ **RECOMMENDED - HIGHEST PRIORITY**

#### Status: Fully Available
- **Official Documentation**: https://developers.upwork.com/
- **GraphQL Endpoint**: `https://api.upwork.com/graphql`
- **REST Endpoint**: Available but being deprecated in favor of GraphQL

#### Authentication
- **Method**: OAuth 2.0 (RFC 6749)
- **Token TTL**: Access token: 24 hours | Refresh token: 2 weeks
- **Grant Types Supported**:
  - Authorization Code Grant (recommended)
  - Implicit Grant
  - Client Credentials Grant

#### Getting API Access
1. Log into Upwork account
2. Navigate to API Center (https://www.upwork.com/services/api/keys)
3. Request OAuth 2.0 credentials
4. Select Key Type: OAuth 2.0
5. Request permission: "Read marketplace Job Postings - Public"

#### GraphQL Query for Job Search
```graphql
query SearchJobs($searchTerm: String, $sortOrder: SortOrder) {
  marketplaceJobPostings(
    marketPlaceJobFilter: {
      searchTerm_eq: { andTerms_all: $searchTerm }
    }
    searchType: USER_JOBS_SEARCH
    sortAttributes: { field: CREATE_TIME, sortOrder: $sortOrder }
  ) {
    edges {
      node {
        id
        title
        createdDateTime
        description
        content {
          ... on Project {
            budget
            duration
            skills {
              prettyName
            }
          }
        }
        contractTerms {
          ... on ProjectContractTerms {
            engagementDuration
          }
          ... on HourlyContractTerms {
            hourlyBudgetMin
            hourlyBudgetMax
            hourlyBudgetType
          }
        }
        client {
          totalReviews
          totalFeedback
        }
        proposalsTier
      }
    }
    pageInfo {
      hasNextPage
      endCursor
    }
  }
}
```

#### Available Filters
- Search term (keywords)
- Skills
- Budget range
- Job type (hourly/fixed)
- Date posted
- Client rating
- Proposals count

#### Rate Limits
- Not publicly documented
- Typical industry standard: 60-100 requests/minute
- Implement exponential backoff for rate limit errors

#### Cost
- **Free tier**: Available for individual developers
- **Enterprise**: Contact Upwork for pricing

#### Limitations
- Returns top 10 jobs by default (pagination required for more)
- Multiple skill filtering has limitations
- Some fields require additional permissions

---

### 2. Freelancer.com API ✅ **RECOMMENDED**

#### Status: Fully Available
- **Official Documentation**: https://developers.freelancer.com/
- **REST Endpoint**: `https://www.freelancer.com/api/`
- **Python SDK**: `freelancersdk` (https://github.com/freelancer/freelancer-sdk-python)

#### Authentication
- **Method**: OAuth 2.0
- **Token Management**: Session-based using SDK

#### Installation
```bash
pip install freelancersdk
```

#### Python SDK Example - Search Projects
```python
from freelancersdk.session import Session
from freelancersdk.resources.projects.projects import search_projects
from freelancersdk.resources.projects.helpers import create_search_projects_filter

# Create session with OAuth token
session = Session(oauth2_token='YOUR_OAUTH2_TOKEN')

# Create search filter
search_filter = create_search_projects_filter(
    sort_field='time_updated',
    job_details=True,
    user_details=True,
    full_description=True
)

# Search projects
projects = search_projects(
    session=session,
    query='python web development',
    search_filter=search_filter,
    limit=50,
    offset=0
)
```

#### Available Filters
- Query string (keywords)
- Budget range
- Project type (fixed/hourly)
- Skills
- Job status
- Country
- Language

#### SDK Methods
- `search_projects()` - Search for projects
- `get_projects()` - Get specific projects by ID
- `get_project_details()` - Get detailed project information
- `get_bids()` - Get bids for a project

#### Rate Limits
- Not publicly documented
- SDK handles rate limiting automatically

#### Cost
- **Free tier**: Available for developers
- API access included with account

#### Limitations
- Requires OAuth token (user must authorize)
- SDK is Python-only (REST API available for other languages)
- Some endpoints require specific permissions

---

### 3. Guru.com ❌ **NOT AVAILABLE**

#### Status: No Public API
- The search results for "Guru.com API" return results for **getguru.com** (a knowledge management platform)
- **Guru.com** (the freelance platform) does NOT have a public API
- **Alternative**: Web scraping (not recommended - violates TOS)

#### Recommendation
Skip this platform for now. Monitor for future API releases.

---

### 4. PeoplePerHour ❌ **PRIVATE API ONLY**

#### Status: Limited/Partner Access Only
- **API exists** but is not publicly documented
- **GitHub repo**: https://github.com/PeoplePerHour/pph-php-client (PHP client)
- **Access method**: Requires Application ID and Secret Key
- **Environments**: Sandbox and Live

#### Current Challenges
- No public documentation
- No clear process to request API credentials
- Developer forum shows multiple requests for API access with no clear answers

#### Recommendation
**Skip for initial implementation**. May require:
1. Direct contact with PeoplePerHour business development
2. Partnership agreement
3. Potential fees

---

### 5. Fiverr ❌ **NO OFFICIAL API**

#### Status: No Public API Available
- **Fiverr does not offer an official public API**
- Multiple developer inquiries have confirmed no official API exists

#### Unofficial Alternatives (NOT RECOMMENDED)
1. **Web Scrapers**: Various Python libraries exist (violates TOS)
2. **Apify Fiverr Scraper**: Third-party scraping service
3. **RapidAPI "Fiverr Private API"**: Reverse-engineered mobile API

#### Risks of Unofficial Methods
- Violates Fiverr Terms of Service
- Can break at any time (Cloudflare protection, site changes)
- Legal liability
- Account suspension risk

#### Recommendation
**Skip Fiverr for official integration**. Alternative: Direct user to Fiverr website.

---

## Recommended Implementation Strategy

### Phase 1: Core Platforms (MVP)
1. **Upwork** (GraphQL API) - Highest priority
2. **Freelancer.com** (Python SDK) - Good documentation

### Phase 2: Future Expansion
3. Monitor Guru.com for API availability
4. Explore partnership with PeoplePerHour
5. Consider RSS feeds or email alerts for platforms without APIs

### Phase 3: Enhancement
6. Add caching layer (Redis/Memcached)
7. Implement intelligent rate limiting
8. Add webhook support where available
9. Build aggregation algorithms for duplicate detection

---

## Implementation Requirements

### Required Python Packages
```bash
pip install requests
pip install aiohttp  # Async HTTP requests
pip install freelancersdk  # Freelancer.com official SDK
pip install gql  # GraphQL client for Upwork
pip install python-dotenv  # Environment variables
pip install tenacity  # Retry logic
pip install cachetools  # Caching
```

### Environment Variables Needed
```env
# Upwork OAuth 2.0
UPWORK_CLIENT_ID=your_client_id
UPWORK_CLIENT_SECRET=your_client_secret
UPWORK_ACCESS_TOKEN=your_access_token
UPWORK_REFRESH_TOKEN=your_refresh_token

# Freelancer.com OAuth 2.0
FREELANCER_CLIENT_ID=your_client_id
FREELANCER_CLIENT_SECRET=your_client_secret
FREELANCER_OAUTH_TOKEN=your_oauth_token

# Optional: Rate limiting
RATE_LIMIT_REQUESTS_PER_MINUTE=60
CACHE_TTL_SECONDS=300
```

---

## API Comparison Matrix

| Feature | Upwork | Freelancer.com | Guru.com | PeoplePerHour | Fiverr |
|---------|--------|----------------|----------|---------------|--------|
| **Public API** | ✅ Yes | ✅ Yes | ❌ No | ⚠️ Private | ❌ No |
| **Documentation** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | N/A | ⭐ | N/A |
| **Authentication** | OAuth 2.0 | OAuth 2.0 | N/A | OAuth (?) | N/A |
| **Python SDK** | ❌ No | ✅ Yes | N/A | ❌ No | N/A |
| **GraphQL** | ✅ Yes | ❌ No | N/A | Unknown | N/A |
| **REST API** | ⚠️ Legacy | ✅ Yes | N/A | ✅ Yes | N/A |
| **Free Tier** | ✅ Yes | ✅ Yes | N/A | Unknown | N/A |
| **Rate Limits** | Moderate | Moderate | N/A | Unknown | N/A |
| **Search Jobs** | ✅ Yes | ✅ Yes | N/A | Unknown | N/A |
| **Job Details** | ✅ Yes | ✅ Yes | N/A | Unknown | N/A |
| **Filters** | Comprehensive | Comprehensive | N/A | Unknown | N/A |
| **Pagination** | ✅ Yes | ✅ Yes | N/A | Unknown | N/A |
| **Webhooks** | ✅ Yes | ✅ Yes | N/A | Unknown | N/A |
| **Recommendation** | 🟢 **USE** | 🟢 **USE** | 🔴 Skip | 🟡 Future | 🔴 Skip |

---

## Next Steps

1. ✅ Create Upwork developer account and request API access
2. ✅ Create Freelancer.com developer account and get OAuth token
3. ✅ Design unified API client architecture
4. ✅ Implement Upwork GraphQL client
5. ✅ Implement Freelancer.com SDK wrapper
6. ✅ Build unified response normalizer
7. ✅ Add error handling and retry logic
8. ✅ Implement caching layer
9. ✅ Write comprehensive tests
10. ✅ Document setup process

---

## References

- Upwork API Documentation: https://developers.upwork.com/
- Upwork GraphQL Explorer: https://www.upwork.com/developer/documentation/graphql/api/docs/
- Freelancer.com API: https://developers.freelancer.com/
- Freelancer Python SDK: https://github.com/freelancer/freelancer-sdk-python
- OAuth 2.0 RFC: https://tools.ietf.org/html/rfc6749

---

**Document Version**: 1.0
**Last Updated**: 2025-11-18
**Author**: Freelance MCP Server Development Team
