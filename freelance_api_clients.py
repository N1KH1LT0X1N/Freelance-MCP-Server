"""
Freelance Platform API Clients

Unified API clients for multiple freelance platforms including Upwork and Freelancer.com.
Provides standardized interfaces for searching gigs, handling authentication, and managing API responses.

Supported Platforms:
- Upwork (GraphQL API)
- Freelancer.com (REST API with Python SDK)

Features:
- Async/await support for concurrent requests
- Automatic retry logic with exponential backoff
- Rate limiting and caching
- Normalized response format across all platforms
- Error handling and fallback strategies
"""

import asyncio
import os
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional, Union
from urllib.parse import urlencode

import aiohttp
from cachetools import TTLCache
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type
)


# ============================================================================
# DATA MODELS
# ============================================================================

@dataclass
class NormalizedGig:
    """Standardized gig format across all platforms"""
    id: str
    platform: str
    title: str
    description: str
    budget: str
    skills_required: List[str]
    match_score: float
    proposals_count: int
    client_rating: Optional[float]
    posted_date: str
    url: str
    project_type: str  # "hourly", "fixed", "contest"
    budget_min: Optional[float] = None
    budget_max: Optional[float] = None
    hourly_rate: Optional[float] = None
    deadline: Optional[str] = None
    client_reviews: Optional[int] = None
    remote_ok: bool = True
    location: str = ""

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary format"""
        return {
            "id": self.id,
            "platform": self.platform,
            "title": self.title,
            "description": self.description,
            "budget": self.budget,
            "skills_required": self.skills_required,
            "match_score": self.match_score,
            "proposals_count": self.proposals_count,
            "client_rating": self.client_rating,
            "posted_date": self.posted_date,
            "url": self.url
        }


@dataclass
class SearchCriteria:
    """Search parameters for gig queries"""
    skills: List[str]
    max_budget: Optional[float] = None
    min_budget: Optional[float] = None
    project_type: Optional[str] = None  # "hourly", "fixed_price", "contest"
    min_match_score: float = 0.0
    limit: int = 10
    offset: int = 0


class APIError(Exception):
    """Base exception for API errors"""
    pass


class RateLimitError(APIError):
    """Rate limit exceeded"""
    pass


class AuthenticationError(APIError):
    """Authentication failed"""
    pass


# ============================================================================
# BASE API CLIENT
# ============================================================================

class BaseAPIClient(ABC):
    """Abstract base class for freelance platform API clients"""

    def __init__(self, cache_ttl: int = 300):
        """
        Initialize API client

        Args:
            cache_ttl: Cache time-to-live in seconds (default: 5 minutes)
        """
        self.cache = TTLCache(maxsize=100, ttl=cache_ttl)
        self.rate_limit_delay = 1.0  # seconds between requests
        self.last_request_time = 0

    @abstractmethod
    async def search_gigs(self, criteria: SearchCriteria) -> List[NormalizedGig]:
        """
        Search for gigs based on criteria

        Args:
            criteria: Search criteria

        Returns:
            List of normalized gigs
        """
        pass

    @abstractmethod
    def authenticate(self) -> bool:
        """
        Authenticate with the API

        Returns:
            True if authentication successful
        """
        pass

    def _calculate_match_score(self, user_skills: List[str], required_skills: List[str]) -> float:
        """Calculate skill match score"""
        if not required_skills:
            return 0.5

        user_skills_lower = [skill.lower() for skill in user_skills]
        required_skills_lower = [skill.lower() for skill in required_skills]

        matches = sum(1 for skill in required_skills_lower if skill in user_skills_lower)
        return matches / len(required_skills_lower)

    async def _rate_limit(self):
        """Implement rate limiting"""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time

        if time_since_last < self.rate_limit_delay:
            await asyncio.sleep(self.rate_limit_delay - time_since_last)

        self.last_request_time = time.time()

    def _get_cache_key(self, criteria: SearchCriteria) -> str:
        """Generate cache key from search criteria"""
        return f"{self.__class__.__name__}:{criteria.skills}:{criteria.min_budget}:{criteria.max_budget}:{criteria.project_type}"


# ============================================================================
# UPWORK API CLIENT (GraphQL)
# ============================================================================

class UpworkAPIClient(BaseAPIClient):
    """Upwork API client using GraphQL"""

    GRAPHQL_ENDPOINT = "https://api.upwork.com/graphql"

    def __init__(self, client_id: str = None, client_secret: str = None,
                 access_token: str = None, cache_ttl: int = 300):
        """
        Initialize Upwork API client

        Args:
            client_id: OAuth client ID
            client_secret: OAuth client secret
            access_token: OAuth access token
            cache_ttl: Cache TTL in seconds
        """
        super().__init__(cache_ttl)
        self.client_id = client_id or os.getenv("UPWORK_CLIENT_ID", "")
        self.client_secret = client_secret or os.getenv("UPWORK_CLIENT_SECRET", "")
        self.access_token = access_token or os.getenv("UPWORK_ACCESS_TOKEN", "")
        self.refresh_token = os.getenv("UPWORK_REFRESH_TOKEN", "")
        self.rate_limit_delay = 1.0

    def authenticate(self) -> bool:
        """Check if we have valid credentials"""
        if not self.access_token:
            print("⚠️ Upwork: No access token configured. Set UPWORK_ACCESS_TOKEN environment variable.")
            return False
        return True

    async def _refresh_access_token(self) -> bool:
        """Refresh the access token using refresh token"""
        if not self.refresh_token:
            return False

        # OAuth 2.0 token refresh endpoint
        token_url = "https://www.upwork.com/api/v3/oauth2/token"

        data = {
            "grant_type": "refresh_token",
            "refresh_token": self.refresh_token,
            "client_id": self.client_id,
            "client_secret": self.client_secret
        }

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(token_url, data=data) as response:
                    if response.status == 200:
                        token_data = await response.json()
                        self.access_token = token_data.get("access_token", "")
                        self.refresh_token = token_data.get("refresh_token", self.refresh_token)
                        print("✅ Upwork: Access token refreshed successfully")
                        return True
        except Exception as e:
            print(f"❌ Upwork: Token refresh failed: {e}")

        return False

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type(RateLimitError)
    )
    async def search_gigs(self, criteria: SearchCriteria) -> List[NormalizedGig]:
        """
        Search Upwork jobs using GraphQL API

        Args:
            criteria: Search criteria

        Returns:
            List of normalized gigs from Upwork
        """
        if not self.authenticate():
            print("⚠️ Upwork: Skipping search (no authentication)")
            return []

        # Check cache
        cache_key = self._get_cache_key(criteria)
        if cache_key in self.cache:
            print("✅ Upwork: Returning cached results")
            return self.cache[cache_key]

        # Rate limiting
        await self._rate_limit()

        # Build GraphQL query
        query = self._build_graphql_query(criteria)

        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    self.GRAPHQL_ENDPOINT,
                    json={"query": query},
                    headers=headers
                ) as response:

                    if response.status == 401:
                        # Try to refresh token
                        if await self._refresh_access_token():
                            # Retry with new token
                            headers["Authorization"] = f"Bearer {self.access_token}"
                            async with session.post(
                                self.GRAPHQL_ENDPOINT,
                                json={"query": query},
                                headers=headers
                            ) as retry_response:
                                if retry_response.status == 200:
                                    data = await retry_response.json()
                                    gigs = self._parse_graphql_response(data, criteria)
                                    self.cache[cache_key] = gigs
                                    return gigs
                        raise AuthenticationError("Upwork authentication failed")

                    elif response.status == 429:
                        raise RateLimitError("Upwork rate limit exceeded")

                    elif response.status == 200:
                        data = await response.json()
                        gigs = self._parse_graphql_response(data, criteria)
                        self.cache[cache_key] = gigs
                        print(f"✅ Upwork: Found {len(gigs)} gigs")
                        return gigs
                    else:
                        error_text = await response.text()
                        raise APIError(f"Upwork API error {response.status}: {error_text}")

        except aiohttp.ClientError as e:
            print(f"❌ Upwork: Network error: {e}")
            return []
        except Exception as e:
            print(f"❌ Upwork: Error: {e}")
            return []

    def _build_graphql_query(self, criteria: SearchCriteria) -> str:
        """Build GraphQL query from search criteria"""

        # Build search term from skills
        search_term = " ".join(criteria.skills) if criteria.skills else ""

        query = f'''
        query {{
          marketplaceJobPostings(
            marketPlaceJobFilter: {{
              searchTerm_eq: {{ andTerms_all: "{search_term}" }}
            }}
            searchType: USER_JOBS_SEARCH
            sortAttributes: {{ field: RECENCY, sortOrder: DESC }}
            pagination: {{ limit: {criteria.limit}, offset: {criteria.offset} }}
          ) {{
            edges {{
              node {{
                id
                title
                createdDateTime
                description
                content {{
                  ... on Project {{
                    budget
                    duration
                    skills {{
                      prettyName
                    }}
                  }}
                }}
                contractTerms {{
                  ... on ProjectContractTerms {{
                    engagementDuration
                  }}
                  ... on HourlyContractTerms {{
                    hourlyBudgetMin
                    hourlyBudgetMax
                    hourlyBudgetType
                  }}
                }}
                client {{
                  totalReviews
                  totalFeedback
                }}
                proposalsTier
              }}
            }}
            pageInfo {{
              hasNextPage
              endCursor
            }}
          }}
        }}
        '''

        return query

    def _parse_graphql_response(self, data: Dict, criteria: SearchCriteria) -> List[NormalizedGig]:
        """Parse GraphQL response into normalized gigs"""
        gigs = []

        try:
            edges = data.get("data", {}).get("marketplaceJobPostings", {}).get("edges", [])

            for edge in edges:
                node = edge.get("node", {})

                # Extract job details
                job_id = node.get("id", "")
                title = node.get("title", "")
                description = node.get("description", "")
                created = node.get("createdDateTime", "")

                # Extract skills
                content = node.get("content", {})
                skills_data = content.get("skills", [])
                skills = [s.get("prettyName", "") for s in skills_data]

                # Extract budget/rate information
                contract_terms = node.get("contractTerms", {})
                budget_min = contract_terms.get("hourlyBudgetMin")
                budget_max = contract_terms.get("hourlyBudgetMax")
                budget = content.get("budget")

                # Determine project type and budget string
                if budget_min and budget_max:
                    project_type = "hourly"
                    budget_str = f"${budget_min}-${budget_max}/hr"
                    hourly_rate = (budget_min + budget_max) / 2 if budget_max else budget_min
                elif budget:
                    project_type = "fixed"
                    budget_str = f"${budget}"
                    budget_min = budget
                    budget_max = budget
                    hourly_rate = None
                else:
                    project_type = "unknown"
                    budget_str = "Not specified"
                    hourly_rate = None

                # Filter by budget if specified
                if criteria.max_budget:
                    if budget_max and budget_max > criteria.max_budget:
                        continue
                    if hourly_rate and hourly_rate > criteria.max_budget:
                        continue

                if criteria.min_budget:
                    if budget_min and budget_min < criteria.min_budget:
                        continue
                    if hourly_rate and hourly_rate < criteria.min_budget:
                        continue

                # Extract client info
                client = node.get("client", {})
                client_reviews = client.get("totalReviews", 0)
                client_rating = client.get("totalFeedback")

                # Proposals count (Upwork uses tier system)
                proposals_tier = node.get("proposalsTier", "")
                proposals_count = self._parse_proposals_tier(proposals_tier)

                # Calculate match score
                match_score = self._calculate_match_score(criteria.skills, skills)

                # Filter by match score
                if match_score < criteria.min_match_score:
                    continue

                # Create URL
                url = f"https://www.upwork.com/jobs/~{job_id}" if job_id else ""

                # Create normalized gig
                gig = NormalizedGig(
                    id=f"upwork_{job_id}",
                    platform="upwork",
                    title=title,
                    description=description[:500],  # Truncate long descriptions
                    budget=budget_str,
                    skills_required=skills,
                    match_score=round(match_score, 2),
                    proposals_count=proposals_count,
                    client_rating=client_rating,
                    posted_date=created,
                    url=url,
                    project_type=project_type,
                    budget_min=budget_min,
                    budget_max=budget_max,
                    hourly_rate=hourly_rate,
                    client_reviews=client_reviews,
                    remote_ok=True
                )

                gigs.append(gig)

        except Exception as e:
            print(f"❌ Upwork: Error parsing response: {e}")

        return gigs

    def _parse_proposals_tier(self, tier: str) -> int:
        """Convert Upwork proposal tier to approximate count"""
        tier_map = {
            "0 to 4": 2,
            "5 to 9": 7,
            "10 to 14": 12,
            "15 to 19": 17,
            "20 to 49": 30,
            "50+": 50
        }
        return tier_map.get(tier, 0)


# ============================================================================
# FREELANCER.COM API CLIENT
# ============================================================================

class FreelancerAPIClient(BaseAPIClient):
    """Freelancer.com API client using REST API"""

    API_BASE_URL = "https://www.freelancer.com/api"

    def __init__(self, oauth_token: str = None, cache_ttl: int = 300):
        """
        Initialize Freelancer.com API client

        Args:
            oauth_token: OAuth token for API access
            cache_ttl: Cache TTL in seconds
        """
        super().__init__(cache_ttl)
        self.oauth_token = oauth_token or os.getenv("FREELANCER_OAUTH_TOKEN", "")
        self.rate_limit_delay = 1.0

    def authenticate(self) -> bool:
        """Check if we have valid credentials"""
        if not self.oauth_token:
            print("⚠️ Freelancer.com: No OAuth token configured. Set FREELANCER_OAUTH_TOKEN environment variable.")
            return False
        return True

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type(RateLimitError)
    )
    async def search_gigs(self, criteria: SearchCriteria) -> List[NormalizedGig]:
        """
        Search Freelancer.com projects using REST API

        Args:
            criteria: Search criteria

        Returns:
            List of normalized gigs from Freelancer.com
        """
        if not self.authenticate():
            print("⚠️ Freelancer.com: Skipping search (no authentication)")
            return []

        # Check cache
        cache_key = self._get_cache_key(criteria)
        if cache_key in self.cache:
            print("✅ Freelancer.com: Returning cached results")
            return self.cache[cache_key]

        # Rate limiting
        await self._rate_limit()

        # Build API request
        endpoint = f"{self.API_BASE_URL}/projects/0.1/projects/active"

        # Build query parameters
        params = {
            "query": " ".join(criteria.skills) if criteria.skills else "",
            "limit": criteria.limit,
            "offset": criteria.offset,
            "job_details": "true",
            "user_details": "true",
            "full_description": "true"
        }

        # Add budget filters
        if criteria.min_budget:
            params["min_avg_price"] = criteria.min_budget
        if criteria.max_budget:
            params["max_avg_price"] = criteria.max_budget

        # Add project type filter
        if criteria.project_type:
            if criteria.project_type.lower() == "fixed_price":
                params["project_types[]"] = "fixed"
            elif criteria.project_type.lower() == "hourly":
                params["project_types[]"] = "hourly"

        headers = {
            "Freelancer-OAuth-V1": self.oauth_token,
            "Content-Type": "application/json"
        }

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    endpoint,
                    params=params,
                    headers=headers
                ) as response:

                    if response.status == 401:
                        raise AuthenticationError("Freelancer.com authentication failed")

                    elif response.status == 429:
                        raise RateLimitError("Freelancer.com rate limit exceeded")

                    elif response.status == 200:
                        data = await response.json()
                        gigs = self._parse_api_response(data, criteria)
                        self.cache[cache_key] = gigs
                        print(f"✅ Freelancer.com: Found {len(gigs)} gigs")
                        return gigs
                    else:
                        error_text = await response.text()
                        raise APIError(f"Freelancer.com API error {response.status}: {error_text}")

        except aiohttp.ClientError as e:
            print(f"❌ Freelancer.com: Network error: {e}")
            return []
        except Exception as e:
            print(f"❌ Freelancer.com: Error: {e}")
            return []

    def _parse_api_response(self, data: Dict, criteria: SearchCriteria) -> List[NormalizedGig]:
        """Parse Freelancer.com API response into normalized gigs"""
        gigs = []

        try:
            projects = data.get("result", {}).get("projects", [])

            for project in projects:
                # Extract project details
                project_id = project.get("id", "")
                title = project.get("title", "")
                description = project.get("description", "")

                # Extract budget
                budget_data = project.get("budget", {})
                budget_min = budget_data.get("minimum")
                budget_max = budget_data.get("maximum")
                currency = budget_data.get("currency", {}).get("code", "USD")

                # Determine project type
                project_type_id = project.get("type", "")
                if project_type_id == "fixed":
                    project_type = "fixed"
                    budget_str = f"{currency} {budget_min}-{budget_max}" if budget_max else f"{currency} {budget_min}"
                    hourly_rate = None
                elif project_type_id == "hourly":
                    project_type = "hourly"
                    budget_str = f"{currency} {budget_min}-{budget_max}/hr" if budget_max else f"{currency} {budget_min}/hr"
                    hourly_rate = (budget_min + budget_max) / 2 if budget_max else budget_min
                else:
                    project_type = "unknown"
                    budget_str = "Not specified"
                    hourly_rate = None

                # Extract skills (jobs in Freelancer.com API)
                jobs = project.get("jobs", [])
                skills = [job.get("name", "") for job in jobs]

                # Calculate match score
                match_score = self._calculate_match_score(criteria.skills, skills)

                # Filter by match score
                if match_score < criteria.min_match_score:
                    continue

                # Extract client info
                owner = project.get("owner", {})
                client_rating = owner.get("reputation", {}).get("entire_history", {}).get("overall")
                client_reviews = owner.get("reputation", {}).get("entire_history", {}).get("reviews", 0)

                # Proposals/bids count
                bid_stats = project.get("bid_stats", {})
                proposals_count = bid_stats.get("bid_count", 0)

                # Posted date
                time_submitted = project.get("time_submitted", 0)
                posted_date = datetime.fromtimestamp(time_submitted).isoformat() if time_submitted else ""

                # Create URL
                seo_url = project.get("seo_url", "")
                url = f"https://www.freelancer.com/projects/{seo_url}" if seo_url else f"https://www.freelancer.com/projects/{project_id}"

                # Create normalized gig
                gig = NormalizedGig(
                    id=f"freelancer_{project_id}",
                    platform="freelancer",
                    title=title,
                    description=description[:500],
                    budget=budget_str,
                    skills_required=skills,
                    match_score=round(match_score, 2),
                    proposals_count=proposals_count,
                    client_rating=client_rating,
                    posted_date=posted_date,
                    url=url,
                    project_type=project_type,
                    budget_min=budget_min,
                    budget_max=budget_max,
                    hourly_rate=hourly_rate,
                    client_reviews=client_reviews,
                    remote_ok=True
                )

                gigs.append(gig)

        except Exception as e:
            print(f"❌ Freelancer.com: Error parsing response: {e}")

        return gigs


# ============================================================================
# UNIFIED API AGGREGATOR
# ============================================================================

class FreelanceAPIAggregator:
    """Aggregates results from multiple freelance platform APIs"""

    def __init__(self, enabled_platforms: Optional[List[str]] = None):
        """
        Initialize API aggregator

        Args:
            enabled_platforms: List of platforms to enable (None = all available)
        """
        self.clients: Dict[str, BaseAPIClient] = {}

        # Initialize clients for enabled platforms
        all_platforms = {
            "upwork": UpworkAPIClient,
            "freelancer": FreelancerAPIClient
        }

        if enabled_platforms:
            platforms_to_init = {k: v for k, v in all_platforms.items() if k in enabled_platforms}
        else:
            platforms_to_init = all_platforms

        for platform, client_class in platforms_to_init.items():
            try:
                client = client_class()
                if client.authenticate():
                    self.clients[platform] = client
                    print(f"✅ {platform.title()}: API client initialized")
            except Exception as e:
                print(f"⚠️ {platform.title()}: Failed to initialize client: {e}")

    async def search_all_platforms(self, criteria: SearchCriteria) -> Dict[str, Any]:
        """
        Search all enabled platforms concurrently

        Args:
            criteria: Search criteria

        Returns:
            Aggregated results from all platforms
        """
        if not self.clients:
            print("⚠️ No API clients available. Using fallback data.")
            return {
                "total_found": 0,
                "gigs": [],
                "platforms_searched": [],
                "search_criteria": {
                    "skills": criteria.skills,
                    "max_budget": criteria.max_budget,
                    "min_budget": criteria.min_budget,
                    "project_type": criteria.project_type
                },
                "error": "No API clients configured. Please set API credentials in environment variables."
            }

        # Search all platforms concurrently
        tasks = []
        platform_names = []

        for platform_name, client in self.clients.items():
            tasks.append(client.search_gigs(criteria))
            platform_names.append(platform_name)

        # Wait for all searches to complete
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Aggregate results
        all_gigs = []
        platforms_searched = []

        for platform_name, result in zip(platform_names, results):
            if isinstance(result, Exception):
                print(f"❌ {platform_name}: Search failed: {result}")
            elif isinstance(result, list):
                all_gigs.extend(result)
                platforms_searched.append(platform_name)

        # Sort by match score
        all_gigs.sort(key=lambda x: x.match_score, reverse=True)

        return {
            "total_found": len(all_gigs),
            "gigs": [gig.to_dict() for gig in all_gigs],
            "platforms_searched": platforms_searched,
            "search_criteria": {
                "skills": criteria.skills,
                "max_budget": criteria.max_budget,
                "min_budget": criteria.min_budget,
                "project_type": criteria.project_type
            }
        }


# ============================================================================
# CONVENIENCE FUNCTIONS
# ============================================================================

async def search_freelance_gigs(
    skills: List[str],
    max_budget: Optional[float] = None,
    min_budget: Optional[float] = None,
    project_type: Optional[str] = None,
    platforms: Optional[List[str]] = None,
    limit: int = 10
) -> Dict[str, Any]:
    """
    Search for freelance gigs across multiple platforms

    Args:
        skills: List of skills to search for
        max_budget: Maximum budget filter
        min_budget: Minimum budget filter
        project_type: Project type filter
        platforms: List of platforms to search (None = all)
        limit: Max results per platform

    Returns:
        Aggregated search results
    """
    criteria = SearchCriteria(
        skills=skills,
        max_budget=max_budget,
        min_budget=min_budget,
        project_type=project_type,
        limit=limit
    )

    aggregator = FreelanceAPIAggregator(enabled_platforms=platforms)
    results = await aggregator.search_all_platforms(criteria)

    return results


# For testing
if __name__ == "__main__":
    async def test():
        """Test the API clients"""
        print("Testing Freelance API Clients\n")

        # Test search
        results = await search_freelance_gigs(
            skills=["Python", "Django", "React"],
            max_budget=5000,
            project_type="fixed_price",
            limit=5
        )

        print(f"\nTotal gigs found: {results['total_found']}")
        print(f"Platforms searched: {results['platforms_searched']}")
        print(f"\nTop 3 matches:")

        for i, gig in enumerate(results['gigs'][:3], 1):
            print(f"\n{i}. {gig['title']}")
            print(f"   Platform: {gig['platform']}")
            print(f"   Budget: {gig['budget']}")
            print(f"   Match: {gig['match_score']*100:.1f}%")
            print(f"   URL: {gig['url']}")

    asyncio.run(test())
