"""Tests for CDISCClient HTTP client."""
from typing import AsyncGenerator
import pytest
import httpx
from pytest_httpx import HTTPXMock
from cdisc_mcp.client import CDISCClient
from cdisc_mcp.config import Config
from cdisc_mcp.errors import AuthenticationError, RateLimitError, ResourceNotFoundError


@pytest.fixture
def config(api_key: str) -> Config:
    return Config(api_key=api_key, cache_ttl=60, max_retries=3)


@pytest.fixture
async def client(config: Config) -> AsyncGenerator[CDISCClient, None]:
    async with CDISCClient(config) as c:
        yield c


class TestAuthentication:
    async def test_api_key_header_sent(
        self, client: CDISCClient, httpx_mock: HTTPXMock
    ) -> None:
        httpx_mock.add_response(json={"products": []})
        await client.get("/mdr/products")
        requests = httpx_mock.get_requests()
        assert requests[0].headers.get("api-key") == "test-api-key-12345"

    async def test_raises_auth_error_on_401(
        self, client: CDISCClient, httpx_mock: HTTPXMock
    ) -> None:
        httpx_mock.add_response(status_code=401)
        with pytest.raises(AuthenticationError):
            await client.get("/mdr/products")

    async def test_401_not_retried(
        self, client: CDISCClient, httpx_mock: HTTPXMock
    ) -> None:
        httpx_mock.add_response(status_code=401)
        with pytest.raises(AuthenticationError):
            await client.get("/mdr/products")
        assert len(httpx_mock.get_requests()) == 1


class TestCaching:
    async def test_second_call_uses_cache(
        self, client: CDISCClient, httpx_mock: HTTPXMock
    ) -> None:
        httpx_mock.add_response(json={"products": ["SDTM"]})
        await client.get("/mdr/products")
        await client.get("/mdr/products")
        assert len(httpx_mock.get_requests()) == 1

    async def test_different_paths_not_shared(
        self, client: CDISCClient, httpx_mock: HTTPXMock
    ) -> None:
        httpx_mock.add_response(json={"a": 1})
        httpx_mock.add_response(json={"b": 2})
        r1 = await client.get("/mdr/sdtm")
        r2 = await client.get("/mdr/adam")
        assert r1 != r2
        assert len(httpx_mock.get_requests()) == 2

    async def test_cache_returns_same_data(
        self, client: CDISCClient, httpx_mock: HTTPXMock
    ) -> None:
        httpx_mock.add_response(json={"name": "SDTM", "version": "3.4"})
        r1 = await client.get("/mdr/sdtm")
        r2 = await client.get("/mdr/sdtm")
        assert r1 == r2


class TestRetry:
    async def test_retries_on_429_then_succeeds(
        self, config: Config, httpx_mock: HTTPXMock
    ) -> None:
        # Use config with max_retries=3
        async with CDISCClient(config) as client:
            httpx_mock.add_response(status_code=429, headers={"Retry-After": "0"})
            httpx_mock.add_response(json={"products": []})
            result = await client.get("/mdr/products")
            assert result == {"products": []}
            assert len(httpx_mock.get_requests()) == 2

    async def test_does_not_retry_404(
        self, client: CDISCClient, httpx_mock: HTTPXMock
    ) -> None:
        httpx_mock.add_response(status_code=404)
        with pytest.raises(ResourceNotFoundError):
            await client.get("/mdr/sdtm/99.9")
        assert len(httpx_mock.get_requests()) == 1

    async def test_retries_on_500(
        self, httpx_mock: HTTPXMock
    ) -> None:
        cfg = Config(api_key="test-api-key-12345", max_retries=2, cache_ttl=60)
        async with CDISCClient(cfg) as client:
            httpx_mock.add_response(status_code=500)
            httpx_mock.add_response(status_code=500)
            httpx_mock.add_response(json={"ok": True})
            result = await client.get("/mdr/products")
            assert result == {"ok": True}

    async def test_raises_rate_limit_after_all_retries(
        self, httpx_mock: HTTPXMock
    ) -> None:
        cfg = Config(api_key="test-api-key-12345", max_retries=1, cache_ttl=60)
        async with CDISCClient(cfg) as client:
            httpx_mock.add_response(status_code=429, headers={"Retry-After": "30"})
            httpx_mock.add_response(status_code=429, headers={"Retry-After": "30"})
            with pytest.raises(RateLimitError) as exc_info:
                await client.get("/mdr/products")
            assert exc_info.value.retry_after == 30


class TestErrorMapping:
    async def test_raises_resource_not_found_on_404(
        self, client: CDISCClient, httpx_mock: HTTPXMock
    ) -> None:
        httpx_mock.add_response(status_code=404)
        with pytest.raises(ResourceNotFoundError, match="Resource not found"):
            await client.get("/mdr/sdtm/99.9")

    async def test_404_not_retried(
        self, client: CDISCClient, httpx_mock: HTTPXMock
    ) -> None:
        httpx_mock.add_response(status_code=404)
        with pytest.raises(ResourceNotFoundError):
            await client.get("/mdr/sdtm/99.9")
        assert len(httpx_mock.get_requests()) == 1
