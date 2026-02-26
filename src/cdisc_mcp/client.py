# -*- coding: utf-8 -*-
"""Async HTTP client for the CDISC Library REST API.

Handles connection pooling, response caching with asyncio.Lock protection,
and retry logic that only retries 429 and 5xx responses.
"""

from __future__ import annotations

import asyncio
import logging
from typing import Any

import httpx
from cachetools import TTLCache
from tenacity import retry, retry_if_exception, stop_after_attempt, wait_exponential

from .config import Config
from .errors import AuthenticationError, RateLimitError, ResourceNotFoundError

logger = logging.getLogger(__name__)


def _should_retry(exc: BaseException) -> bool:
    """Only retry 429 Too Many Requests and 5xx server errors.

    4xx errors other than 429 are client mistakes and must NOT be retried.
    """
    if isinstance(exc, httpx.HTTPStatusError):
        return exc.response.status_code == 429 or exc.response.status_code >= 500
    if isinstance(exc, (httpx.TimeoutException, httpx.NetworkError)):
        return True
    return False


class CDISCClient:
    """Reusable async HTTP client with connection pooling, caching, and retry.

    Create one instance at application startup and reuse it for all requests.
    Use as an async context manager to ensure the connection pool is closed.

    Example:
        async with CDISCClient(config) as client:
            data = await client.get("/mdr/products")
    """

    def __init__(self, config: Config) -> None:
        self._config = config
        self._cache: TTLCache[str, Any] = TTLCache(
            maxsize=config.cache_maxsize,
            ttl=config.cache_ttl,
        )
        self._lock = asyncio.Lock()
        self._http = httpx.AsyncClient(
            base_url=config.base_url,
            headers={"api-key": config.api_key},
            timeout=httpx.Timeout(config.request_timeout),
        )

    async def get(self, path: str) -> Any:
        """Fetch a resource from the CDISC Library API.

        Responses are cached using the TTL from Config. Only 429 and 5xx
        responses are retried; 4xx errors (except 429) raise immediately.

        Args:
            path: URL path relative to base_url.

        Returns:
            Parsed JSON as dict or list.

        Raises:
            AuthenticationError: If the API key is invalid (HTTP 401).
            ResourceNotFoundError: If the resource does not exist (HTTP 404).
            RateLimitError: If the rate limit is exceeded after all retries (HTTP 429).
            httpx.HTTPStatusError: For other non-retriable HTTP errors.
        """
        async with self._lock:
            if path in self._cache:
                logger.debug("cache hit: %s", path)
                return self._cache[path]

        data = await self._fetch_with_retry(path)

        async with self._lock:
            self._cache[path] = data

        return data

    async def _fetch_with_retry(self, path: str) -> Any:
        max_retries = self._config.max_retries

        @retry(
            stop=stop_after_attempt(max_retries + 1),
            wait=wait_exponential(multiplier=0.1, min=0.1, max=1.0),
            retry=retry_if_exception(_should_retry),
            reraise=True,
        )
        async def _do() -> Any:
            logger.debug("GET %s", path)
            resp = await self._http.get(path)
            if resp.status_code == 401:
                raise AuthenticationError("Invalid CDISC API key (HTTP 401)")
            if resp.status_code == 404:
                raise ResourceNotFoundError(f"Resource not found: {path}")
            resp.raise_for_status()
            return resp.json()

        try:
            return await _do()
        except httpx.HTTPStatusError as exc:
            if exc.response.status_code == 429:
                retry_after_header = exc.response.headers.get("Retry-After")
                raise RateLimitError(
                    retry_after=int(retry_after_header) if retry_after_header else None
                ) from exc
            raise

    async def close(self) -> None:
        """Close the underlying HTTP connection pool."""
        await self._http.aclose()

    async def __aenter__(self) -> CDISCClient:
        return self

    async def __aexit__(self, *_: object) -> None:
        await self.close()
