"""
MCP Prompts - Pre-defined prompts for common freelancing tasks

MCP prompts provide pre-configured templates that LLMs can use
to interact with the server more effectively.
"""

from typing import Dict, List, Optional
from dataclasses import dataclass


@dataclass
class MCPPrompt:
    """MCP Prompt definition"""
    name: str
    description: str
    arguments: List[Dict[str, str]]
    template: str


# Pre-defined prompts for the Freelance MCP Server
FREELANCE_PROMPTS = {
    "find_and_apply": MCPPrompt(
        name="find_and_apply",
        description="Search for gigs matching skills and automatically generate proposals for top matches",
        arguments=[
            {"name": "skills", "description": "Comma-separated list of skills", "required": "true"},
            {"name": "max_budget", "description": "Maximum budget per project", "required": "false"},
            {"name": "min_match_score", "description": "Minimum match score (0-1) to apply", "required": "false"}
        ],
        template="""I'll help you find and apply to freelance gigs.

Step 1: Searching for gigs with skills: {skills}
Step 2: Filtering by max budget: {max_budget}
Step 3: Analyzing matches with minimum score: {min_match_score}
Step 4: Generating proposals for qualified gigs
Step 5: Tracking applications

Use search_gigs with skills={skills}, max_budget={max_budget}
Then for each match with score >= {min_match_score}:
  - Use analyze_profile_fit
  - Use generate_proposal
  - Use track_application_status"""
    ),

    "optimize_profile": MCPPrompt(
        name="optimize_profile",
        description="Analyze and optimize a freelancer profile for better visibility and match rates",
        arguments=[
            {"name": "profile_id", "description": "User profile ID to optimize", "required": "true"},
            {"name": "target_platforms", "description": "Comma-separated platforms to target", "required": "false"},
            {"name": "target_rate", "description": "Desired hourly rate", "required": "false"}
        ],
        template="""I'll optimize your freelance profile for better results.

Step 1: Fetching current profile (profile_id={profile_id})
Step 2: Analyzing market trends for platforms: {target_platforms}
Step 3: Getting AI-powered optimization recommendations
Step 4: Suggesting rate adjustments toward {target_rate}/hr
Step 5: Providing action items

Use freelance://profile/{profile_id} resource
Use freelance://market-trends resource
Use optimize_profile tool
Use negotiate_rate tool for rate suggestions"""
    ),

    "full_gig_workflow": MCPPrompt(
        name="full_gig_workflow",
        description="Complete workflow from profile creation to proposal submission",
        arguments=[
            {"name": "user_name", "description": "Freelancer name", "required": "true"},
            {"name": "title", "description": "Professional title", "required": "true"},
            {"name": "skills", "description": "Comma-separated skills", "required": "true"},
            {"name": "rate_min", "description": "Minimum hourly rate", "required": "true"},
            {"name": "rate_max", "description": "Maximum hourly rate", "required": "true"}
        ],
        template="""I'll guide you through the complete freelancing workflow.

Step 1: Create Your Profile
  - Name: {user_name}
  - Title: {title}
  - Skills: {skills}
  - Rate: ${rate_min}-${rate_max}/hr

Step 2: Search for Matching Gigs
Step 3: Analyze Profile Fit
Step 4: Generate Custom Proposals
Step 5: Track Applications

Use create_user_profile first
Then search_gigs with your skills
Then generate_proposal for good matches
Finally track_application_status"""
    ),

    "market_research": MCPPrompt(
        name="market_research",
        description="Analyze market trends and competition for specific skills",
        arguments=[
            {"name": "skills", "description": "Skills to research", "required": "true"},
            {"name": "platforms", "description": "Platforms to analyze", "required": "false"}
        ],
        template="""I'll help you research the freelance market.

Step 1: Fetching current market trends
Step 2: Analyzing gigs for skills: {skills}
Step 3: Reviewing platform competition: {platforms}
Step 4: Calculating average rates
Step 5: Identifying opportunities

Use freelance://market-trends resource
Use search_gigs to sample current opportunities
Use freelance://gigs/{platform} for platform-specific data"""
    ),

    "code_review_workflow": MCPPrompt(
        name="code_review_workflow",
        description="Review code, identify issues, and provide fixes",
        arguments=[
            {"name": "file_path", "description": "Path to code file", "required": "false"},
            {"name": "code_snippet", "description": "Code to review", "required": "false"},
            {"name": "language", "description": "Programming language", "required": "true"},
            {"name": "review_type", "description": "Type of review (general, security, performance)", "required": "false"}
        ],
        template="""I'll perform a comprehensive code review.

Step 1: Analyzing {language} code
Step 2: Running {review_type} review
Step 3: Identifying issues and anti-patterns
Step 4: Providing fix suggestions
Step 5: Optionally auto-fixing issues

Use code_review tool first
Then use code_debug if fixes are needed"""
    ),

    "proposal_generator": MCPPrompt(
        name="proposal_generator",
        description="Generate a customized proposal for a specific gig",
        arguments=[
            {"name": "gig_id", "description": "ID of the gig", "required": "true"},
            {"name": "tone", "description": "Proposal tone (professional, friendly, confident)", "required": "false"},
            {"name": "highlight_skills", "description": "Skills to emphasize", "required": "false"}
        ],
        template="""I'll create a winning proposal for this gig.

Step 1: Fetching gig details (gig_id={gig_id})
Step 2: Analyzing requirements
Step 3: Matching your skills: {highlight_skills}
Step 4: Generating {tone} proposal with AI
Step 5: Including portfolio and experience

Use analyze_profile_fit first to check compatibility
Then generate_proposal with tone={tone}
Optionally use negotiate_rate for pricing strategy"""
    ),

    "rate_negotiation": MCPPrompt(
        name="rate_negotiation",
        description="Get strategic advice for negotiating higher rates",
        arguments=[
            {"name": "current_rate", "description": "Your current rate", "required": "true"},
            {"name": "target_rate", "description": "Desired rate", "required": "true"},
            {"name": "experience", "description": "Years of experience", "required": "false"},
            {"name": "complexity", "description": "Project complexity (low, medium, high)", "required": "false"}
        ],
        template="""I'll help you negotiate better rates.

Step 1: Analyzing current rate: ${current_rate}/hr
Step 2: Target rate: ${target_rate}/hr
Step 3: Justification based on {experience} years experience
Step 4: Adjusting for {complexity} complexity projects
Step 5: Providing negotiation scripts and tactics

Use negotiate_rate tool with your parameters
Use freelance://market-trends to support your ask"""
    ),

    "skill_gap_analysis": MCPPrompt(
        name="skill_gap_analysis",
        description="Identify missing skills for desired gigs and get learning recommendations",
        arguments=[
            {"name": "current_skills", "description": "Your current skills", "required": "true"},
            {"name": "target_gigs", "description": "Types of gigs you want", "required": "true"}
        ],
        template="""I'll analyze your skill gaps and provide recommendations.

Step 1: Analyzing your skills: {current_skills}
Step 2: Searching for gigs: {target_gigs}
Step 3: Identifying required vs. current skills
Step 4: Calculating match scores
Step 5: Recommending skills to learn

Use search_gigs for target opportunities
Use analyze_profile_fit to see gaps
Use optimize_profile for improvement plan"""
    ),
}


def get_all_prompts() -> Dict[str, MCPPrompt]:
    """Get all available prompts"""
    return FREELANCE_PROMPTS.copy()


def get_prompt(name: str) -> Optional[MCPPrompt]:
    """Get a specific prompt by name"""
    return FREELANCE_PROMPTS.get(name)


def register_prompt(name: str, prompt: MCPPrompt) -> None:
    """Register a new custom prompt"""
    FREELANCE_PROMPTS[name] = prompt


def format_prompt(prompt: MCPPrompt, **kwargs) -> str:
    """Format a prompt with arguments"""
    return prompt.template.format(**kwargs)
