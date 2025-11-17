"""
MCP Server Capabilities - Declares what this server can do

Following MCP protocol specifications for server capabilities.
"""

from typing import Dict, List, Any
from dataclasses import dataclass, field


@dataclass
class ServerCapabilities:
    """
    MCP Server Capabilities Declaration

    Tells clients what features this server supports.
    """

    # Server metadata
    name: str = "Freelance Gig Aggregator"
    version: str = "2.1.0"
    protocol_version: str = "2024-11-05"

    # Core capabilities
    supports_tools: bool = True
    supports_resources: bool = True
    supports_prompts: bool = True
    supports_sampling: bool = False  # For future LLM sampling

    # Tool capabilities
    total_tools: int = 10
    tool_names: List[str] = field(default_factory=lambda: [
        "search_gigs",
        "create_user_profile",
        "analyze_profile_fit",
        "generate_proposal",
        "negotiate_rate",
        "code_review",
        "code_debug",
        "optimize_profile",
        "track_application_status",
        "validate"
    ])

    # Resource capabilities
    total_resources: int = 3
    resource_patterns: List[str] = field(default_factory=lambda: [
        "freelance://profile/{profile_id}",
        "freelance://gigs/{platform}",
        "freelance://market-trends"
    ])

    # Prompt capabilities
    total_prompts: int = 8
    prompt_names: List[str] = field(default_factory=lambda: [
        "find_and_apply",
        "optimize_profile",
        "full_gig_workflow",
        "market_research",
        "code_review_workflow",
        "proposal_generator",
        "rate_negotiation",
        "skill_gap_analysis"
    ])

    # Platform support
    supported_platforms: List[str] = field(default_factory=lambda: [
        "upwork", "fiverr", "freelancer",
        "toptal", "guru", "peopleperhour"
    ])

    # AI capabilities
    ai_powered_tools: List[str] = field(default_factory=lambda: [
        "generate_proposal",
        "negotiate_rate",
        "optimize_profile"
    ])

    # Data capabilities
    sample_gigs_count: int = 17
    supports_persistence: bool = True
    supports_caching: bool = True

    # Transport support
    supported_transports: List[str] = field(default_factory=lambda: [
        "stdio",
        "sse",
        "streamable-http"
    ])

    # Feature flags
    features: Dict[str, bool] = field(default_factory=lambda: {
        "multi_platform_search": True,
        "ai_proposals": True,
        "rate_negotiation": True,
        "code_review": True,
        "profile_optimization": True,
        "market_analysis": True,
        "application_tracking": True,
        "database_persistence": True,
        "structured_logging": True,
        "health_monitoring": True
    })

    def to_dict(self) -> Dict[str, Any]:
        """Convert capabilities to dictionary"""
        return {
            "name": self.name,
            "version": self.version,
            "protocol_version": self.protocol_version,
            "capabilities": {
                "tools": {
                    "supported": self.supports_tools,
                    "count": self.total_tools,
                    "names": self.tool_names
                },
                "resources": {
                    "supported": self.supports_resources,
                    "count": self.total_resources,
                    "patterns": self.resource_patterns
                },
                "prompts": {
                    "supported": self.supports_prompts,
                    "count": self.total_prompts,
                    "names": self.prompt_names
                },
                "sampling": {
                    "supported": self.supports_sampling
                }
            },
            "platforms": self.supported_platforms,
            "ai_tools": self.ai_powered_tools,
            "data": {
                "sample_gigs": self.sample_gigs_count,
                "persistence": self.supports_persistence,
                "caching": self.supports_caching
            },
            "transports": self.supported_transports,
            "features": self.features
        }

    def supports_feature(self, feature: str) -> bool:
        """Check if a feature is supported"""
        return self.features.get(feature, False)

    def get_tool_info(self) -> Dict[str, Any]:
        """Get detailed tool information"""
        return {
            "total": self.total_tools,
            "names": self.tool_names,
            "ai_powered": self.ai_powered_tools
        }

    def get_resource_info(self) -> Dict[str, Any]:
        """Get detailed resource information"""
        return {
            "total": self.total_resources,
            "patterns": self.resource_patterns
        }

    def get_prompt_info(self) -> Dict[str, Any]:
        """Get detailed prompt information"""
        return {
            "total": self.total_prompts,
            "names": self.prompt_names
        }


# Global capabilities instance
SERVER_CAPABILITIES = ServerCapabilities()


def get_capabilities() -> ServerCapabilities:
    """Get server capabilities"""
    return SERVER_CAPABILITIES


def print_capabilities() -> None:
    """Print server capabilities in a readable format"""
    caps = SERVER_CAPABILITIES

    print("\n" + "="*70)
    print(f"  {caps.name} v{caps.version}")
    print(f"  MCP Protocol: {caps.protocol_version}")
    print("="*70)

    print(f"\n📦 Capabilities:")
    print(f"  Tools:     {caps.total_tools} available")
    print(f"  Resources: {caps.total_resources} endpoints")
    print(f"  Prompts:   {caps.total_prompts} workflows")

    print(f"\n🌐 Platforms:")
    for platform in caps.supported_platforms:
        print(f"  • {platform.title()}")

    print(f"\n🤖 AI-Powered Tools:")
    for tool in caps.ai_powered_tools:
        print(f"  • {tool}")

    print(f"\n🚀 Transports:")
    for transport in caps.supported_transports:
        print(f"  • {transport}")

    print(f"\n✨ Features:")
    for feature, enabled in caps.features.items():
        status = "✓" if enabled else "✗"
        print(f"  {status} {feature.replace('_', ' ').title()}")

    print("\n" + "="*70 + "\n")
