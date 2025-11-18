# Project Structure

## Overview
This repository contains a Freelance MCP Server - an AI-powered gig aggregator for Claude Desktop.

## Directory Structure

```
mcp-server-1/
├── freelance_server.py          # Main MCP server implementation
├── requirements.txt              # Python dependencies
├── pyproject.toml               # Project configuration
├── setup.py                     # Package setup
├── .env.example                 # Environment variables template
├── README.md                    # Main documentation
├── CHANGELOG.md                 # Version history
├── LICENSE                      # MIT License
│
├── core/                        # Core functionality modules
│   ├── __init__.py
│   ├── chat.py                  # Chat functionality
│   ├── claude.py                # Claude integration
│   ├── cli.py                   # Command-line interface
│   ├── cli_chat.py              # CLI chat features
│   └── tools.py                 # Core tools
│
├── database/                    # Database management
│   ├── __init__.py
│   ├── db_manager.py            # Database operations
│   └── models.py                # Data models
│
├── mcp_extensions/              # MCP protocol extensions
│   ├── __init__.py
│   ├── capabilities.py          # MCP capabilities
│   ├── prompts.py               # Prompt templates
│   └── resource_templates.py    # Resource templates
│
├── utils/                       # Utility functions
│   ├── __init__.py
│   ├── config.py                # Configuration management
│   ├── logger.py                # Logging utilities
│   └── monitoring.py            # Monitoring tools
│
├── tests/                       # Test files
│   ├── __init__.py
│   ├── test_server.py           # Server tests
│   └── integration/             # Integration tests
│       └── test_setup.py        # Setup tests
│
├── examples/                    # Example implementations
│   ├── README.md
│   ├── custom_client.py         # Custom client example
│   └── mcp_claude_integration.py # Claude integration example
│
├── docs/                        # Documentation
│   ├── readme.md                # Docs index
│   ├── FEATURES.md              # Feature documentation
│   ├── DEPLOYMENT.md            # Deployment guide
│   ├── MCP_GUIDE.md             # MCP protocol guide
│   ├── QUICKSTART.md            # Quick start guide
│   ├── USAGE.md                 # Usage instructions
│   └── guides/                  # Additional guides
│
├── .github/                     # GitHub specific files
│   ├── CONTRIBUTING.md          # Contribution guidelines
│   ├── DESCRIPTION.md           # Project description
│   ├── PULL_REQUEST_TEMPLATE.md # PR template
│   ├── ISSUE_TEMPLATE/          # Issue templates
│   │   ├── bug_report.md
│   │   └── feature_request.md
│   └── workflows/               # GitHub Actions
│       ├── test.yml
│       └── security.yml
│
├── archive/                     # Archived/deprecated files
│   └── (old test and demo files)
│
└── Docker files
    ├── Dockerfile               # Docker container definition
    ├── docker-compose.yml       # Docker compose configuration
    ├── .dockerignore            # Docker ignore patterns
    └── install.sh               # Installation script
```

## Key Files

### Production Files
- **freelance_server.py** - Main MCP server, run this with Claude Desktop
- **requirements.txt** - Install dependencies with `pip install -r requirements.txt`
- **.env.example** - Copy to `.env` and add your API keys

### Documentation
- **README.md** - Start here for setup instructions
- **docs/** - Detailed documentation and guides

### Development
- **tests/** - Unit and integration tests
- **examples/** - Example implementations
- **core/** - Core modules used by the server

## Getting Started

1. Copy `.env.example` to `.env` and add your GROQ API key
2. Install dependencies: `pip install -r requirements.txt`
3. Run server: `python freelance_server.py stdio`
4. Or integrate with Claude Desktop (see README.md)

## Archive Folder

The `archive/` folder contains deprecated test files and old implementations:
- demo_user_scenarios.py
- simple_mcp_test.py
- test_mcp_coherence.py
- user_experience_test.py
- freelance_client.py
- freelance_client2.py
- main.py

These are kept for reference but are not part of the active codebase.
