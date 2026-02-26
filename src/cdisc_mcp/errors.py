"""Custom exception types for the CDISC MCP server."""


class CDISCClientError(Exception):
    """Base class for CDISC client errors."""


class AuthenticationError(CDISCClientError):
    """Raised when the API key is rejected (HTTP 401)."""


class RateLimitError(CDISCClientError):
    """Raised when the API rate limit is exceeded (HTTP 429) after all retries."""

    def __init__(self, retry_after: int | None = None) -> None:
        self.retry_after = retry_after
        msg = f"Rate limit exceeded. Retry after {retry_after}s." if retry_after else "Rate limit exceeded."
        super().__init__(msg)


class ResourceNotFoundError(CDISCClientError):
    """Raised when the requested resource does not exist (HTTP 404)."""
