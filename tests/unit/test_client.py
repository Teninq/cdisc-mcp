"""
Unit tests for src/cdisc_mcp/client.py

Updated to match current async CDISCClient implementation.
Uses pytest-httpx to intercept all outbound HTTP without a live server.
"""

import pytest

# ---------------------------------------------------------------------------
# Fixtures local to this module
# ---------------------------------------------------------------------------

@pytest.fixture(autouse=True)
def _set_env(mock_env):
    """Every client test needs CDISC_API_KEY in the environment."""
    pass


@pytest.fixture()
def config():
    """Fresh Config instance per test."""
    from cdisc_mcp.config import load_config
    return load_config()


@pytest.fixture()
def client(config):
    """Fresh CDISCClient instance per test."""
    from cdisc_mcp.client import CDISCClient
    return CDISCClient(config)


BASE_URL = "https://library.cdisc.org/api"


# ---------------------------------------------------------------------------
# Test: authentication header
# ---------------------------------------------------------------------------

class TestAuthHeader:
    """Every request must carry the api-key header."""

    @pytest.mark.asyncio
    async def test_api_key_header_sent(self, client, httpx_mock, api_key):
        httpx_mock.add_response(
            url=f"{BASE_URL}/mdr/sdtm",
            json={"versions": []},
        )

        await client.get("/mdr/sdtm")

        requests = httpx_mock.get_requests()
        assert len(requests) == 1
        assert requests[0].headers["api-key"] == api_key

    @pytest.mark.asyncio
    async def test_base_url_prepended(self, client, httpx_mock):
        httpx_mock.add_response(
            url=f"{BASE_URL}/mdr/sdtm",
            json={"versions": []},
        )

        await client.get("/mdr/sdtm")

        req = httpx_mock.get_requests()[0]
        assert str(req.url).startswith(BASE_URL)


# ---------------------------------------------------------------------------
# Test: LRU cache behaviour
# ---------------------------------------------------------------------------

class TestLruCache:
    """Identical GET requests must be served from cache (single HTTP call)."""

    @pytest.mark.asyncio
    async def test_second_call_hits_cache(self, client, httpx_mock):
        httpx_mock.add_response(
            url=f"{BASE_URL}/mdr/sdtm",
            json={"versions": ["3-4"]},
        )

        result1 = await client.get("/mdr/sdtm")
        result2 = await client.get("/mdr/sdtm")

        # Only one real HTTP request should have been made
        assert len(httpx_mock.get_requests()) == 1
        assert result1 == result2

    @pytest.mark.asyncio
    async def test_different_paths_not_cached_together(self, client, httpx_mock):
        httpx_mock.add_response(
            url=f"{BASE_URL}/mdr/sdtm",
            json={"versions": ["3-4"]},
        )
        httpx_mock.add_response(
            url=f"{BASE_URL}/mdr/sdtm/3-4",
            json={"name": "SDTM 3.4"},
        )

        await client.get("/mdr/sdtm")
        await client.get("/mdr/sdtm/3-4")

        assert len(httpx_mock.get_requests()) == 2

    @pytest.mark.asyncio
    async def test_cache_returns_parsed_json(self, client, httpx_mock):
        httpx_mock.add_response(
            url=f"{BASE_URL}/mdr/sdtm",
            json={"versions": ["3-4", "3-3"]},
        )

        result = await client.get("/mdr/sdtm")

        assert isinstance(result, dict)
        assert "versions" in result


# ---------------------------------------------------------------------------
# Test: HTTP 429 rate-limit → retry with back-off
# ---------------------------------------------------------------------------

class TestRateLimitRetry:
    """On HTTP 429 the client must retry and eventually succeed."""

    @pytest.mark.asyncio
    async def test_retries_on_429_then_succeeds(self, client, httpx_mock):
        httpx_mock.add_response(
            url=f"{BASE_URL}/mdr/sdtm",
            status_code=429,
            json={"message": "rate limited"},
        )
        httpx_mock.add_response(
            url=f"{BASE_URL}/mdr/sdtm",
            json={"versions": ["3-4"]},
        )

        result = await client.get("/mdr/sdtm")

        assert result == {"versions": ["3-4"]}
        assert len(httpx_mock.get_requests()) == 2

    @pytest.mark.asyncio
    async def test_raises_after_max_retries_exceeded(self, config, httpx_mock):
        """After exhausting retries the client must raise, not silently fail."""
        from cdisc_mcp.client import CDISCClient

        # Create a fresh client to avoid cache from other tests
        fresh_client = CDISCClient(config)
        # Register exactly max_retries + 1 (= 4) responses so none are left unused
        attempts = config.max_retries + 1
        for _ in range(attempts):
            httpx_mock.add_response(
                url=f"{BASE_URL}/mdr/sdtm/exhaust-retries",
                status_code=429,
                json={"message": "rate limited"},
            )

        with pytest.raises(Exception):
            await fresh_client.get("/mdr/sdtm/exhaust-retries")

    @pytest.mark.asyncio
    async def test_non_429_error_not_retried(self, client, httpx_mock):
        """HTTP 404 is a client error — must not trigger retry logic."""
        httpx_mock.add_response(
            url=f"{BASE_URL}/mdr/sdtm/bad-version",
            status_code=404,
            json={"message": "not found"},
        )

        with pytest.raises(Exception):
            await client.get("/mdr/sdtm/bad-version")

        assert len(httpx_mock.get_requests()) == 1


# ---------------------------------------------------------------------------
# Test: HTTP 5xx server errors → retry
# ---------------------------------------------------------------------------

class TestServerErrorRetry:
    """Transient 5xx errors should also be retried."""

    @pytest.mark.asyncio
    async def test_retries_on_503(self, client, httpx_mock):
        httpx_mock.add_response(
            url=f"{BASE_URL}/mdr/sdtm",
            status_code=503,
            json={"message": "service unavailable"},
        )
        httpx_mock.add_response(
            url=f"{BASE_URL}/mdr/sdtm",
            json={"versions": ["3-4"]},
        )

        result = await client.get("/mdr/sdtm")

        assert "versions" in result
        assert len(httpx_mock.get_requests()) == 2


# ---------------------------------------------------------------------------
# Test: 401 Unauthorized — bad API key
# ---------------------------------------------------------------------------

class TestUnauthorized:
    """401 must surface as an explicit AuthenticationError."""

    @pytest.mark.asyncio
    async def test_raises_authentication_error_on_401(self, client, httpx_mock):
        httpx_mock.add_response(
            url=f"{BASE_URL}/mdr/sdtm",
            status_code=401,
            json={"message": "Unauthorized"},
        )

        from cdisc_mcp.client import AuthenticationError

        with pytest.raises(AuthenticationError):
            await client.get("/mdr/sdtm")
