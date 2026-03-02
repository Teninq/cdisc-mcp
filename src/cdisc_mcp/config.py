"""Application configuration loaded from environment variables."""

import os
from dataclasses import dataclass

# ---------------------------------------------------------------------------
# Module-level constants (used directly by client and tools)
# ---------------------------------------------------------------------------

BASE_URL: str = "https://library.cdisc.org/api"
REQUEST_TIMEOUT: float = 30.0
MAX_LIST_LENGTH: int = 10


# ---------------------------------------------------------------------------
# Config dataclass
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class Config:
    """Immutable runtime configuration for the CDISC MCP server.

    Attributes:
        api_key: CDISC Library API key (required).
        base_url: Base URL for the CDISC Cosmos v2 REST API.
        cache_ttl: Time-to-live for cached responses, in seconds.
        cache_maxsize: Maximum number of entries in the in-memory cache.
        max_retries: Maximum retry attempts for transient errors.
        request_timeout: HTTP request timeout in seconds.
    """

    api_key: str
    base_url: str = "https://library.cdisc.org/api"
    cache_ttl: int = 3600
    cache_maxsize: int = 256
    max_retries: int = 3
    request_timeout: float = 30.0


# ---------------------------------------------------------------------------
# Public functions
# ---------------------------------------------------------------------------

def load_config() -> Config:
    """Load and validate configuration from environment variables.

    Returns:
        A fully populated, validated Config instance.

    Raises:
        ValueError: If CDISC_API_KEY is not set or is empty/whitespace.
    """
    api_key = os.getenv("CDISC_API_KEY", "").strip()
    if not api_key:
        raise ValueError(
            "CDISC_API_KEY environment variable is required. "
            "Set it to your CDISC Library personal API key."
        )
    return Config(api_key=api_key)


