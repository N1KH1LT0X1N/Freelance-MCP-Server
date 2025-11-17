"""
Configuration management for Freelance MCP Server

Centralized configuration with environment variables, validation, and defaults.
"""

import os
from dataclasses import dataclass, field
from typing import Optional, List
from pathlib import Path
from dotenv import load_dotenv


@dataclass
class Config:
    """Application configuration"""

    # API Keys
    groq_api_key: str = ""
    mcp_auth_token: Optional[str] = None

    # Owner validation
    owner_country_code: str = "1"
    owner_phone_number: str = "5551234567"

    # Server settings
    server_mode: str = "stdio"  # stdio, sse, streamable-http
    server_port: int = 8080
    server_host: str = "0.0.0.0"

    # Database settings
    use_database: bool = False
    database_url: str = "sqlite:///data/freelance.db"
    database_pool_size: int = 5

    # Logging settings
    log_level: str = "INFO"
    log_file: str = "logs/freelance_mcp.log"
    log_format: str = "json"  # json or text

    # Performance settings
    enable_caching: bool = False
    cache_ttl: int = 300  # seconds
    max_concurrent_requests: int = 100

    # Security settings
    enable_rate_limiting: bool = False
    rate_limit_requests: int = 100
    rate_limit_period: int = 60  # seconds
    allowed_origins: List[str] = field(default_factory=lambda: ["*"])

    # LLM settings
    llm_model: str = "mixtral-8x7b-32768"
    llm_temperature: float = 0.7
    llm_max_tokens: int = 2048
    llm_timeout: int = 30  # seconds

    # Feature flags
    enable_ai_features: bool = True
    enable_code_review: bool = True
    enable_code_debug: bool = True

    # Data settings
    sample_data_enabled: bool = True
    max_search_results: int = 10

    @property
    def is_production(self) -> bool:
        """Check if running in production mode"""
        return os.getenv('ENVIRONMENT', 'development').lower() == 'production'

    @property
    def is_development(self) -> bool:
        """Check if running in development mode"""
        return not self.is_production

    def validate(self) -> List[str]:
        """
        Validate configuration and return list of issues

        Returns:
            List of validation error messages
        """
        issues = []

        # Check required fields for AI features
        if self.enable_ai_features:
            if not self.groq_api_key or len(self.groq_api_key) < 20:
                issues.append(
                    "GROQ_API_KEY is not set or invalid. AI features will not work. "
                    "Get a free key from https://console.groq.com/"
                )

        # Check database URL format
        if self.use_database:
            if not self.database_url:
                issues.append("DATABASE_URL is required when use_database is True")

        # Check port range
        if not (1024 <= self.server_port <= 65535):
            issues.append(f"Server port {self.server_port} is outside valid range (1024-65535)")

        # Check log level
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if self.log_level.upper() not in valid_levels:
            issues.append(f"Log level '{self.log_level}' is invalid. Valid: {valid_levels}")

        return issues

    def to_dict(self) -> dict:
        """Convert configuration to dictionary"""
        return {
            'groq_api_key': '***' if self.groq_api_key else None,
            'mcp_auth_token': '***' if self.mcp_auth_token else None,
            'server_mode': self.server_mode,
            'server_port': self.server_port,
            'use_database': self.use_database,
            'database_url': self.database_url.split('://')[-1] if '://' in self.database_url else self.database_url,
            'log_level': self.log_level,
            'enable_ai_features': self.enable_ai_features,
            'enable_caching': self.enable_caching,
            'environment': 'production' if self.is_production else 'development'
        }


def load_config(env_file: str = ".env") -> Config:
    """
    Load configuration from environment variables

    Args:
        env_file: Path to .env file

    Returns:
        Config instance
    """
    # Load .env file if it exists
    env_path = Path(env_file)
    if env_path.exists():
        load_dotenv(env_path)

    # Create config from environment variables
    config = Config(
        # API Keys
        groq_api_key=os.getenv('GROQ_API_KEY', ''),
        mcp_auth_token=os.getenv('MCP_AUTH_TOKEN'),

        # Owner validation
        owner_country_code=os.getenv('OWNER_COUNTRY_CODE', '1'),
        owner_phone_number=os.getenv('OWNER_PHONE_NUMBER', '5551234567'),

        # Server settings
        server_mode=os.getenv('SERVER_MODE', 'stdio'),
        server_port=int(os.getenv('SERVER_PORT', '8080')),
        server_host=os.getenv('SERVER_HOST', '0.0.0.0'),

        # Database settings
        use_database=os.getenv('USE_DATABASE', 'false').lower() == 'true',
        database_url=os.getenv('DATABASE_URL', 'sqlite:///data/freelance.db'),

        # Logging settings
        log_level=os.getenv('LOG_LEVEL', 'INFO'),
        log_file=os.getenv('LOG_FILE', 'logs/freelance_mcp.log'),
        log_format=os.getenv('LOG_FORMAT', 'json'),

        # Performance settings
        enable_caching=os.getenv('ENABLE_CACHING', 'false').lower() == 'true',
        cache_ttl=int(os.getenv('CACHE_TTL', '300')),

        # Security settings
        enable_rate_limiting=os.getenv('ENABLE_RATE_LIMITING', 'false').lower() == 'true',
        rate_limit_requests=int(os.getenv('RATE_LIMIT_REQUESTS', '100')),

        # LLM settings
        llm_model=os.getenv('LLM_MODEL', 'mixtral-8x7b-32768'),
        llm_temperature=float(os.getenv('LLM_TEMPERATURE', '0.7')),

        # Feature flags
        enable_ai_features=os.getenv('ENABLE_AI_FEATURES', 'true').lower() == 'true',
        enable_code_review=os.getenv('ENABLE_CODE_REVIEW', 'true').lower() == 'true',
        enable_code_debug=os.getenv('ENABLE_CODE_DEBUG', 'true').lower() == 'true',

        # Data settings
        sample_data_enabled=os.getenv('SAMPLE_DATA_ENABLED', 'true').lower() == 'true',
        max_search_results=int(os.getenv('MAX_SEARCH_RESULTS', '10'))
    )

    return config


def print_config_summary(config: Config) -> None:
    """Print configuration summary"""
    print("\n" + "="*60)
    print("Freelance MCP Server - Configuration Summary")
    print("="*60)

    for key, value in config.to_dict().items():
        print(f"  {key:30} : {value}")

    print("="*60)

    # Print validation issues if any
    issues = config.validate()
    if issues:
        print("\n⚠️  Configuration Issues:")
        for issue in issues:
            print(f"  - {issue}")
        print()


# Example usage
if __name__ == "__main__":
    config = load_config()
    print_config_summary(config)

    issues = config.validate()
    if issues:
        print("Configuration has issues:")
        for issue in issues:
            print(f"  - {issue}")
    else:
        print("✅ Configuration is valid")
