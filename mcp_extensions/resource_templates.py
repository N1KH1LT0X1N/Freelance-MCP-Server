"""
Resource Templates - Standardized resource URI patterns

Makes it easy to construct and parse resource URIs following MCP conventions.
"""

from typing import Dict, List, Optional
from dataclasses import dataclass
import re


@dataclass
class ResourceTemplate:
    """Template for an MCP resource"""
    pattern: str
    description: str
    parameters: List[str]
    example: str


class ResourceTemplateManager:
    """Manages resource templates and URI construction"""

    TEMPLATES = {
        "profile": ResourceTemplate(
            pattern="freelance://profile/{profile_id}",
            description="Access user profile data with detailed skills, rates, and history",
            parameters=["profile_id"],
            example="freelance://profile/user_12345"
        ),
        "platform_gigs": ResourceTemplate(
            pattern="freelance://gigs/{platform}",
            description="Get all available gigs from a specific platform",
            parameters=["platform"],
            example="freelance://gigs/upwork"
        ),
        "market_trends": ResourceTemplate(
            pattern="freelance://market-trends",
            description="Access current market trends, rates, and insights",
            parameters=[],
            example="freelance://market-trends"
        ),
        "skill_trends": ResourceTemplate(
            pattern="freelance://trends/skill/{skill_name}",
            description="Get market trends for a specific skill",
            parameters=["skill_name"],
            example="freelance://trends/skill/python"
        ),
        "platform_comparison": ResourceTemplate(
            pattern="freelance://compare/platforms",
            description="Compare metrics across all platforms",
            parameters=[],
            example="freelance://compare/platforms"
        )
    }

    @classmethod
    def get_template(cls, name: str) -> Optional[ResourceTemplate]:
        """Get a template by name"""
        return cls.TEMPLATES.get(name)

    @classmethod
    def build_uri(cls, template_name: str, **params) -> Optional[str]:
        """
        Build a resource URI from a template

        Args:
            template_name: Name of the template
            **params: Parameters to fill in the template

        Returns:
            Complete resource URI or None if invalid
        """
        template = cls.get_template(template_name)
        if not template:
            return None

        try:
            uri = template.pattern
            for param in template.parameters:
                if param not in params:
                    raise ValueError(f"Missing required parameter: {param}")
                uri = uri.replace(f"{{{param}}}", str(params[param]))
            return uri
        except Exception:
            return None

    @classmethod
    def parse_uri(cls, uri: str) -> Optional[Dict[str, str]]:
        """
        Parse a resource URI and extract parameters

        Args:
            uri: Resource URI to parse

        Returns:
            Dictionary of parameters or None if invalid
        """
        for name, template in cls.TEMPLATES.items():
            # Convert template pattern to regex
            pattern = template.pattern
            for param in template.parameters:
                pattern = pattern.replace(f"{{{param}}}", f"(?P<{param}>[^/]+)")
            pattern = "^" + pattern + "$"

            match = re.match(pattern, uri)
            if match:
                return {
                    "template": name,
                    **match.groupdict()
                }

        return None

    @classmethod
    def get_all_templates(cls) -> Dict[str, ResourceTemplate]:
        """Get all available templates"""
        return cls.TEMPLATES.copy()

    @classmethod
    def list_templates(cls) -> List[str]:
        """List all template names"""
        return list(cls.TEMPLATES.keys())

    @classmethod
    def validate_uri(cls, uri: str) -> bool:
        """Check if a URI matches any template"""
        return cls.parse_uri(uri) is not None

    @classmethod
    def get_examples(cls) -> List[str]:
        """Get example URIs for all templates"""
        return [template.example for template in cls.TEMPLATES.values()]


# Example usage
if __name__ == "__main__":
    manager = ResourceTemplateManager()

    # Build URIs
    profile_uri = manager.build_uri("profile", profile_id="user_123")
    print(f"Profile URI: {profile_uri}")

    platform_uri = manager.build_uri("platform_gigs", platform="upwork")
    print(f"Platform URI: {platform_uri}")

    # Parse URIs
    parsed = manager.parse_uri("freelance://profile/user_456")
    print(f"Parsed: {parsed}")

    # List examples
    print("\nAll examples:")
    for example in manager.get_examples():
        print(f"  {example}")
