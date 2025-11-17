"""
MCP Extensions - Enhanced MCP-specific functionality

This module provides additional MCP features like prompts, resource templates,
and server capabilities that make the Freelance MCP Server more powerful.
"""

from .prompts import get_all_prompts, register_prompt
from .capabilities import ServerCapabilities
from .resource_templates import ResourceTemplateManager

__all__ = [
    'get_all_prompts',
    'register_prompt',
    'ServerCapabilities',
    'ResourceTemplateManager'
]
