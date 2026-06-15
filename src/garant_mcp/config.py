"""Configuration for Garant MCP Server."""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
env_path = Path(__file__).parent.parent.parent / ".env"
if env_path.exists():
    load_dotenv(env_path)


class Config:
    """Application configuration."""

    # API Configuration
    GARANT_TOKEN = os.getenv("GARANT_TOKEN", "").strip()
    GARANT_BASE_URL = os.getenv("GARANT_BASE_URL", "https://api.garant.ru/v2").strip()

    # Logging
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    LOG_FILE = os.getenv("LOG_FILE", "logs/garant-mcp.log")

    # Cache TTL (in seconds)
    CACHE_TTL_TOPIC = int(os.getenv("CACHE_TTL_TOPIC", "7200"))  # 2 hours
    CACHE_TTL_LIMITS = int(os.getenv("CACHE_TTL_LIMITS", "300"))  # 5 minutes
    CACHE_TTL_PRIME = int(os.getenv("CACHE_TTL_PRIME", "3600"))  # 1 hour
    CACHE_TTL_SNIPPETS = int(os.getenv("CACHE_TTL_SNIPPETS", "1800"))  # 30 minutes
    CACHE_TTL_SEARCH = int(os.getenv("CACHE_TTL_SEARCH", "900"))  # 15 minutes

    # Cache directory
    CACHE_DIR = os.getenv("CACHE_DIR", ".cache")

    # Export directory for downloaded files
    EXPORT_DIR = os.getenv("EXPORT_DIR", "exports")

    @classmethod
    def validate(cls) -> list[str]:
        """Validate configuration and return list of errors."""
        errors = []
        if not cls.GARANT_TOKEN:
            errors.append("GARANT_TOKEN is not set. Please check your .env file.")
        return errors
