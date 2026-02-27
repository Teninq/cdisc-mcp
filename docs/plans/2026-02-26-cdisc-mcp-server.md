# CDISC MCP Server Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** 构建一个供 AI 自动调用的 CDISC Library API MCP 服务器，覆盖 SDTM/ADaM/CDASH/Terminology 标准，具备生产级缓存、重试和响应裁剪能力。

**Architecture:** Python 3.11+，基于 FastMCP 框架，分层架构（config → client → formatter → tools），依赖注入解耦。client 使用类封装实现连接复用、TTL 缓存（asyncio.Lock 保护）和 tenacity 重试（仅 429/5xx），response_formatter 负责裁剪 _links 等噪音字段并截断过长列表。

**Tech Stack:** Python 3.11, FastMCP ≥2.0, httpx ≥0.27, cachetools ≥5.3, tenacity ≥8.3, pytest + pytest-asyncio + pytest-httpx, ruff, mypy

---

## 项目结构目标

```
cdisc-mcp/
├── pyproject.toml
├── src/cdisc_mcp/
│   ├── __init__.py
│   ├── config.py              # 配置与鉴权
│   ├── client.py              # CDISCClient（连接池+缓存+重试）
│   ├── errors.py              # 统一错误类型
│   ├── response_formatter.py  # 响应裁剪与截断
│   ├── server.py              # FastMCP 服务器入口（依赖注入）
│   └── tools/
│       ├── __init__.py
│       ├── search.py          # search_cdisc, list_products
│       ├── sdtm.py            # get_sdtm_domains, get_sdtm_variable
│       ├── adam.py            # get_adam_datastructures, get_adam_variable
│       ├── cdash.py           # get_cdash_classes, get_cdash_field
│       └── terminology.py    # list_ct_packages, get_codelist, get_codelist_terms
└── tests/
    ├── conftest.py
    ├── test_config.py
    ├── test_client.py
    ├── test_response_formatter.py
    └── test_tools.py
```

---

## Task 1: 项目基础结构

**Files:**
- Create: `pyproject.toml`
- Create: `src/cdisc_mcp/__init__.py`
- Create: `src/cdisc_mcp/errors.py`
- Create: `tests/__init__.py`
- Create: `tests/conftest.py`

**Step 1: 创建 pyproject.toml**

```toml
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[project]
name = "cdisc-mcp"
version = "0.1.0"
description = "MCP server exposing CDISC Library metadata as AI-callable tools"
readme = "README.md"
license = { text = "MIT" }
requires-python = ">=3.11"
dependencies = [
    "fastmcp>=2.0",
    "httpx>=0.27",
    "cachetools>=5.3",
    "tenacity>=8.3",
]

[project.scripts]
cdisc-mcp = "cdisc_mcp.server:main"

[dependency-groups]
dev = [
    "pytest>=8.0",
    "pytest-asyncio>=0.23",
    "pytest-httpx>=0.30",
    "pytest-cov>=5.0",
    "ruff>=0.4",
    "mypy>=1.10",
    "types-cachetools",
]

[tool.pytest.ini_options]
asyncio_mode = "auto"
testpaths = ["tests"]
addopts = [
    "--cov=src/cdisc_mcp",
    "--cov-report=term-missing",
    "--cov-fail-under=80",
]

[tool.coverage.run]
branch = true
source = ["src/cdisc_mcp"]

[tool.ruff]
target-version = "py311"
line-length = 88

[tool.ruff.lint]
select = ["E", "W", "F", "I", "B", "UP"]

[tool.ruff.lint.per-file-ignores]
"tests/**/*.py" = ["S101"]

[tool.mypy]
python_version = "3.11"
strict = true
```

**Step 2: 安装依赖**

```bash
pip install -e ".[dev]"
# 或者用 uv:
# uv sync --dev
```

Expected: 安装成功，无错误

**Step 3: 创建 src/cdisc_mcp/__init__.py**

```python
"""CDISC Library MCP Server."""

__version__ = "0.1.0"
```

**Step 4: 创建 src/cdisc_mcp/errors.py**

```python
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
```

**Step 5: 创建 tests/conftest.py**

```python
"""Shared pytest fixtures for CDISC MCP tests."""

import pytest


FAKE_API_KEY = "test-api-key-12345"
BASE_URL = "https://library.cdisc.org/api/cosmos/v2"


@pytest.fixture
def api_key() -> str:
    return FAKE_API_KEY


@pytest.fixture
def mock_env(monkeypatch: pytest.MonkeyPatch, api_key: str) -> None:
    monkeypatch.setenv("CDISC_API_KEY", api_key)


@pytest.fixture
def missing_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("CDISC_API_KEY", raising=False)


@pytest.fixture
def sample_sdtm_datasets() -> dict:
    """Sample SDTM dataset list response (> 100 items would test truncation)."""
    return {
        "datasets": [
            {"name": "DM", "label": "Demographics", "_links": {"self": {"href": "/..."}}},
            {"name": "AE", "label": "Adverse Events", "_links": {"self": {"href": "/..."}}},
            {"name": "LB", "label": "Laboratory", "_links": {"self": {"href": "/..."}}},
        ]
    }


@pytest.fixture
def sample_codelist() -> dict:
    """Sample codelist with terms (> 100 items would test truncation)."""
    return {
        "conceptId": "C66781",
        "name": "AGEU",
        "submissionValue": "AGEU",
        "_links": {"self": {"href": "/..."}},
        "terms": [{"conceptId": f"C{i}", "submissionValue": f"TERM{i}"} for i in range(150)],
    }
```

**Step 6: 验证结构**

```bash
python -c "import cdisc_mcp; print(cdisc_mcp.__version__)"
```

Expected: `0.1.0`

**Step 7: Commit**

```bash
git add pyproject.toml src/ tests/
git commit -m "chore: initialize project structure with pyproject.toml and error types"
```

---

## Task 2: config.py（TDD）

**Files:**
- Create: `src/cdisc_mcp/config.py`
- Create: `tests/test_config.py`

**Step 1: 写失败测试**

```python
# tests/test_config.py
import pytest
from cdisc_mcp.config import load_config, Config


class TestLoadConfig:
    def test_returns_config_when_key_set(self, mock_env: None, api_key: str) -> None:
        cfg = load_config()
        assert cfg.api_key == api_key

    def test_config_is_frozen(self, mock_env: None) -> None:
        cfg = load_config()
        with pytest.raises(Exception):
            cfg.api_key = "new-key"  # type: ignore[misc]

    def test_raises_when_env_missing(self, missing_env: None) -> None:
        with pytest.raises(ValueError, match="CDISC_API_KEY"):
            load_config()

    def test_raises_when_env_is_empty(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("CDISC_API_KEY", "")
        with pytest.raises(ValueError, match="CDISC_API_KEY"):
            load_config()

    def test_default_base_url_is_https(self, mock_env: None) -> None:
        cfg = load_config()
        assert cfg.base_url.startswith("https://")
        assert "cdisc.org" in cfg.base_url

    def test_default_cache_ttl_is_positive(self, mock_env: None) -> None:
        cfg = load_config()
        assert cfg.cache_ttl > 0

    def test_default_max_retries_is_reasonable(self, mock_env: None) -> None:
        cfg = load_config()
        assert 1 <= cfg.max_retries <= 5
```

**Step 2: 运行验证失败**

```bash
python -m pytest tests/test_config.py -v
```

Expected: 7 failed (ImportError)

**Step 3: 实现 config.py**

```python
"""Application configuration loaded from environment variables."""

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Config:
    """Immutable runtime configuration for the CDISC MCP server."""

    api_key: str
    base_url: str = "https://library.cdisc.org/api/cosmos/v2"
    cache_ttl: int = 3600
    cache_maxsize: int = 256
    max_retries: int = 3
    request_timeout: float = 30.0


def load_config() -> Config:
    """Load and validate configuration from environment variables.

    Returns:
        A fully populated, validated Config instance.

    Raises:
        ValueError: If CDISC_API_KEY is not set or is empty.
    """
    api_key = os.getenv("CDISC_API_KEY", "").strip()
    if not api_key:
        raise ValueError(
            "CDISC_API_KEY environment variable is required. "
            "Set it to your CDISC Library personal API key."
        )
    return Config(api_key=api_key)
```

**Step 4: 运行验证通过**

```bash
python -m pytest tests/test_config.py -v
```

Expected: 7 passed

**Step 5: Commit**

```bash
git add src/cdisc_mcp/config.py tests/test_config.py
git commit -m "feat: add Config dataclass and load_config with env validation"
```

---

## Task 3: response_formatter.py（TDD）

**Files:**
- Create: `src/cdisc_mcp/response_formatter.py`
- Create: `tests/test_response_formatter.py`

**Step 1: 写失败测试**

```python
# tests/test_response_formatter.py
import pytest
from cdisc_mcp.response_formatter import format_response, DEFAULT_MAX_ITEMS


class TestFormatResponse:
    def test_removes_links_from_dict(self) -> None:
        data = {"name": "DM", "_links": {"self": {"href": "/mdr/sdtm/3.4/DM"}}}
        result = format_response(data)
        assert "_links" not in result
        assert result["name"] == "DM"

    def test_removes_ordinal_from_dict(self) -> None:
        data = {"name": "DM", "ordinal": 1, "label": "Demographics"}
        result = format_response(data)
        assert "ordinal" not in result
        assert result["label"] == "Demographics"

    def test_does_not_mutate_input_dict(self) -> None:
        data = {"name": "DM", "_links": {}}
        original = dict(data)
        format_response(data)
        assert data == original

    def test_list_wrapped_in_envelope(self) -> None:
        items = [{"name": f"ITEM{i}"} for i in range(3)]
        result = format_response(items)
        assert "items" in result
        assert "total_returned" in result
        assert "has_more" in result

    def test_list_truncated_at_max_items(self) -> None:
        items = [{"name": f"ITEM{i}"} for i in range(DEFAULT_MAX_ITEMS + 10)]
        result = format_response(items)
        assert result["total_returned"] == DEFAULT_MAX_ITEMS
        assert result["has_more"] is True

    def test_list_not_truncated_when_under_limit(self) -> None:
        items = [{"name": f"ITEM{i}"} for i in range(5)]
        result = format_response(items)
        assert result["total_returned"] == 5
        assert result["has_more"] is False

    def test_list_items_have_links_removed(self) -> None:
        items = [{"name": "DM", "_links": {"self": {}}}]
        result = format_response(items)
        assert "_links" not in result["items"][0]

    def test_custom_max_items(self) -> None:
        items = [{"name": f"ITEM{i}"} for i in range(20)]
        result = format_response(items, max_items=5)
        assert result["total_returned"] == 5
        assert result["has_more"] is True

    def test_empty_list(self) -> None:
        result = format_response([])
        assert result["items"] == []
        assert result["total_returned"] == 0
        assert result["has_more"] is False
```

**Step 2: 运行验证失败**

```bash
python -m pytest tests/test_response_formatter.py -v
```

Expected: 9 failed (ImportError)

**Step 3: 实现 response_formatter.py**

```python
"""Utilities for trimming and normalising CDISC API responses.

The CDISC Library API returns HAL-flavoured JSON with hypermedia link blocks
(_links) and UI ordering hints (ordinal) that are not meaningful to MCP
tool consumers. These are stripped to reduce token usage.
"""

from __future__ import annotations

from typing import Any

# HAL hypermedia links and display ordering hints — not useful to LLM consumers.
_EXCLUDED_KEYS: frozenset[str] = frozenset({"_links", "ordinal"})

DEFAULT_MAX_ITEMS: int = 100


def format_response(
    data: dict[str, Any] | list[Any],
    max_items: int = DEFAULT_MAX_ITEMS,
) -> dict[str, Any]:
    """Normalise a raw CDISC API response for MCP tool output.

    Args:
        data: Raw parsed JSON from the CDISC Library API.
        max_items: Maximum list items to include. Excess items are dropped;
            has_more will be True.

    Returns:
        For list input: {"items": [...], "total_returned": int, "has_more": bool}
        For dict input: dict with excluded keys removed.
    """
    if isinstance(data, list):
        trimmed = data[:max_items]
        return {
            "items": [_trim_item(item) if isinstance(item, dict) else item for item in trimmed],
            "total_returned": len(trimmed),
            "has_more": len(data) > max_items,
        }
    return _trim_item(data)


def _trim_item(item: dict[str, Any]) -> dict[str, Any]:
    """Remove noise keys from a single API response object.

    Args:
        item: A single dict from the CDISC Library API.

    Returns:
        New dict with _EXCLUDED_KEYS removed. Original is not mutated.
    """
    return {k: v for k, v in item.items() if k not in _EXCLUDED_KEYS}
```

**Step 4: 运行验证通过**

```bash
python -m pytest tests/test_response_formatter.py -v
```

Expected: 9 passed

**Step 5: Commit**

```bash
git add src/cdisc_mcp/response_formatter.py tests/test_response_formatter.py
git commit -m "feat: add response_formatter with _links stripping and list truncation"
```

---

## Task 4: client.py（TDD）

**Files:**
- Create: `src/cdisc_mcp/client.py`
- Create: `tests/test_client.py`

**Step 1: 写失败测试**

```python
# tests/test_client.py
import pytest
import httpx
from pytest_httpx import HTTPXMock
from cdisc_mcp.client import CDISCClient
from cdisc_mcp.config import Config
from cdisc_mcp.errors import AuthenticationError, RateLimitError


@pytest.fixture
def config(api_key: str) -> Config:
    return Config(api_key=api_key, cache_ttl=60, max_retries=3)


@pytest.fixture
async def client(config: Config):
    async with CDISCClient(config) as c:
        yield c


class TestAuthentication:
    async def test_api_key_header_sent(
        self, client: CDISCClient, httpx_mock: HTTPXMock
    ) -> None:
        httpx_mock.add_response(json={"products": []})
        await client.get("/mdr/products")
        requests = httpx_mock.get_requests()
        assert requests[0].headers.get("api-key") == client._config.api_key

    async def test_raises_auth_error_on_401(
        self, client: CDISCClient, httpx_mock: HTTPXMock
    ) -> None:
        httpx_mock.add_response(status_code=401)
        with pytest.raises(AuthenticationError):
            await client.get("/mdr/products")


class TestCaching:
    async def test_second_call_uses_cache(
        self, client: CDISCClient, httpx_mock: HTTPXMock
    ) -> None:
        httpx_mock.add_response(json={"products": ["SDTM"]})
        await client.get("/mdr/products")
        await client.get("/mdr/products")
        # Only 1 HTTP request should have been made
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


class TestRetry:
    async def test_retries_on_429_then_succeeds(
        self, client: CDISCClient, httpx_mock: HTTPXMock
    ) -> None:
        httpx_mock.add_response(status_code=429, headers={"Retry-After": "0"})
        httpx_mock.add_response(json={"products": []})
        result = await client.get("/mdr/products")
        assert result == {"products": []}
        assert len(httpx_mock.get_requests()) == 2

    async def test_does_not_retry_404(
        self, client: CDISCClient, httpx_mock: HTTPXMock
    ) -> None:
        httpx_mock.add_response(status_code=404)
        with pytest.raises(httpx.HTTPStatusError):
            await client.get("/mdr/sdtm/99.9")
        assert len(httpx_mock.get_requests()) == 1

    async def test_raises_after_max_retries(
        self, config: Config, httpx_mock: HTTPXMock
    ) -> None:
        cfg = Config(api_key=config.api_key, max_retries=2, cache_ttl=60)
        async with CDISCClient(cfg) as client:
            httpx_mock.add_response(status_code=500)
            httpx_mock.add_response(status_code=500)
            httpx_mock.add_response(status_code=500)
            with pytest.raises(Exception):
                await client.get("/mdr/products")
```

**Step 2: 运行验证失败**

```bash
python -m pytest tests/test_client.py -v
```

Expected: failed (ImportError)

**Step 3: 实现 client.py**

```python
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
from .errors import AuthenticationError

logger = logging.getLogger(__name__)


def _should_retry(exc: BaseException) -> bool:
    """Only retry 429 Too Many Requests and 5xx server errors."""
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
            stop=stop_after_attempt(max_retries),
            wait=wait_exponential(multiplier=1, min=1, max=30),
            retry=retry_if_exception(_should_retry),
            reraise=True,
        )
        async def _do() -> Any:
            logger.debug("GET %s", path)
            resp = await self._http.get(path)
            if resp.status_code == 401:
                raise AuthenticationError("Invalid CDISC API key (HTTP 401)")
            resp.raise_for_status()
            return resp.json()

        return await _do()

    async def close(self) -> None:
        """Close the underlying HTTP connection pool."""
        await self._http.aclose()

    async def __aenter__(self) -> CDISCClient:
        return self

    async def __aexit__(self, *_: object) -> None:
        await self.close()
```

**Step 4: 运行验证通过**

```bash
python -m pytest tests/test_client.py -v
```

Expected: 9 passed

**Step 5: Commit**

```bash
git add src/cdisc_mcp/client.py tests/test_client.py
git commit -m "feat: add CDISCClient with connection pooling, TTL cache and retry"
```

---

## Task 5: tools/search.py（TDD）

**Files:**
- Create: `src/cdisc_mcp/tools/__init__.py`
- Create: `src/cdisc_mcp/tools/search.py`
- Modify: `tests/test_tools.py`

**Step 1: 写失败测试**

```python
# tests/test_tools.py（search 部分）
import pytest
from unittest.mock import AsyncMock, MagicMock
from cdisc_mcp.tools.search import list_products, search_cdisc


@pytest.fixture
def mock_client():
    client = MagicMock()
    client.get = AsyncMock()
    return client


class TestListProducts:
    async def test_returns_formatted_products(self, mock_client) -> None:
        mock_client.get.return_value = {
            "_links": {"self": {}},
            "products": [
                {"name": "SDTM", "version": "3.4"},
                {"name": "ADaM", "version": "1.3"},
            ],
        }
        result = await list_products(mock_client)
        assert "_links" not in result
        assert "products" in result

    async def test_calls_correct_endpoint(self, mock_client) -> None:
        mock_client.get.return_value = {"products": []}
        await list_products(mock_client)
        mock_client.get.assert_called_once_with("/mdr/products")


class TestSearchCdisc:
    async def test_returns_search_results(self, mock_client) -> None:
        mock_client.get.return_value = {
            "results": [{"type": "Domain", "name": "DM"}],
            "_links": {},
        }
        result = await search_cdisc(mock_client, query="demographics")
        assert "_links" not in result

    async def test_query_passed_as_param(self, mock_client) -> None:
        mock_client.get.return_value = {"results": []}
        await search_cdisc(mock_client, query="adverse")
        call_args = mock_client.get.call_args[0][0]
        assert "adverse" in call_args
```

**Step 2: 运行验证失败**

```bash
python -m pytest tests/test_tools.py -v
```

Expected: failed (ImportError)

**Step 3: 实现 tools/search.py**

```python
"""MCP tools for CDISC Library product discovery and global search."""

from __future__ import annotations

from typing import Any
from urllib.parse import urlencode

from ..client import CDISCClient
from ..response_formatter import format_response


async def list_products(client: CDISCClient) -> dict[str, Any]:
    """List all available CDISC standards and their published versions.

    Returns a summary of available products (SDTM, ADaM, CDASH, SEND, etc.)
    with version numbers. Use this as a first step to discover what versions
    are available before querying specific content.

    Returns:
        Dict with 'products' key listing available standards and versions.
    """
    data = await client.get("/mdr/products")
    return format_response(data)


async def search_cdisc(client: CDISCClient, query: str) -> dict[str, Any]:
    """Search across all CDISC standards by keyword.

    Searches variable names, labels, descriptions, and codelist terms across
    all CDISC standards. Use this for broad discovery when you don't know
    which specific standard contains the information you need.

    Args:
        query: Search keyword or phrase (e.g., "adverse event", "AEDECOD").

    Returns:
        Dict with 'items' list of matching results with type and location info.
    """
    params = urlencode({"query": query})
    data = await client.get(f"/mdr/search?{params}")
    return format_response(data)
```

**Step 4: 运行验证通过**

```bash
python -m pytest tests/test_tools.py -v -k "search"
```

Expected: 4 passed

**Step 5: Commit**

```bash
git add src/cdisc_mcp/tools/ tests/test_tools.py
git commit -m "feat: add list_products and search_cdisc tools"
```

---

## Task 6: tools/sdtm.py（TDD）

**Files:**
- Create: `src/cdisc_mcp/tools/sdtm.py`
- Modify: `tests/test_tools.py`

**Step 1: 写失败测试（追加到 test_tools.py）**

```python
from cdisc_mcp.tools.sdtm import get_sdtm_domains, get_sdtm_variable


class TestGetSdtmDomains:
    async def test_returns_domain_list(self, mock_client) -> None:
        mock_client.get.return_value = {
            "datasets": [
                {"name": "DM", "label": "Demographics", "_links": {}},
                {"name": "AE", "label": "Adverse Events", "_links": {}},
            ]
        }
        result = await get_sdtm_domains(mock_client, version="3.4")
        assert "items" in result or "datasets" in result

    async def test_version_in_url(self, mock_client) -> None:
        mock_client.get.return_value = {"datasets": []}
        await get_sdtm_domains(mock_client, version="3.4")
        call_path = mock_client.get.call_args[0][0]
        assert "3.4" in call_path

    async def test_domain_uppercased(self, mock_client) -> None:
        mock_client.get.return_value = {"variables": []}
        await get_sdtm_variable(mock_client, version="3.4", domain="ae", variable="AETERM")
        call_path = mock_client.get.call_args[0][0]
        assert "AE" in call_path
```

**Step 2: 运行验证失败**

```bash
python -m pytest tests/test_tools.py::TestGetSdtmDomains -v
```

Expected: failed (ImportError)

**Step 3: 实现 tools/sdtm.py**

```python
"""MCP tools for SDTM (Study Data Tabulation Model) standard queries."""

from __future__ import annotations

from typing import Any

from ..client import CDISCClient
from ..response_formatter import format_response


async def get_sdtm_domains(client: CDISCClient, version: str) -> dict[str, Any]:
    """List all SDTM domains for a given version.

    Returns all domain codes, labels, and descriptions for the specified
    SDTM Implementation Guide version.

    Args:
        version: SDTM-IG version number, e.g. "3.4", "3.3".
            Use list_products() to see available versions.

    Example queries that should use this tool:
        - "What domains are in SDTM 3.4?"
        - "List all SDTM datasets"
    """
    data = await client.get(f"/mdr/sdtm/{version}")
    return format_response(data)


async def get_sdtm_domain_variables(
    client: CDISCClient, version: str, domain: str
) -> dict[str, Any]:
    """Get all variables defined for an SDTM domain.

    Args:
        version: SDTM-IG version, e.g. "3.4".
        domain: Two-letter domain code, e.g. "DM", "AE", "LB".

    Example queries:
        - "What variables are in the AE domain?"
        - "List all DM domain variables in SDTM 3.4"
    """
    domain = domain.upper().strip()
    data = await client.get(f"/mdr/sdtm/{version}/datasets/{domain}/variables")
    return format_response(data)


async def get_sdtm_variable(
    client: CDISCClient, version: str, domain: str, variable: str
) -> dict[str, Any]:
    """Get the full definition of a specific SDTM variable.

    Args:
        version: SDTM-IG version, e.g. "3.4".
        domain: Two-letter domain code, e.g. "AE".
        variable: Variable name, e.g. "AETERM", "AEDECOD".

    Example queries:
        - "What is the definition of AEDECOD?"
        - "Is AETERM required in SDTM?"
    """
    domain = domain.upper().strip()
    variable = variable.upper().strip()
    data = await client.get(f"/mdr/sdtm/{version}/datasets/{domain}/variables/{variable}")
    return format_response(data)
```

**Step 4: 运行验证通过**

```bash
python -m pytest tests/test_tools.py -v -k "sdtm or Sdtm"
```

Expected: 3 passed

**Step 5: Commit**

```bash
git add src/cdisc_mcp/tools/sdtm.py tests/test_tools.py
git commit -m "feat: add SDTM tools (get_sdtm_domains, get_sdtm_domain_variables, get_sdtm_variable)"
```

---

## Task 7: tools/terminology.py（TDD）

**Files:**
- Create: `src/cdisc_mcp/tools/terminology.py`
- Modify: `tests/test_tools.py`

**Step 1: 写失败测试**

```python
from cdisc_mcp.tools.terminology import list_ct_packages, get_codelist, get_codelist_terms


class TestTerminology:
    async def test_list_packages_calls_correct_endpoint(self, mock_client) -> None:
        mock_client.get.return_value = {"packages": []}
        await list_ct_packages(mock_client)
        mock_client.get.assert_called_once_with("/mdr/ct/packages")

    async def test_get_codelist_strips_links(self, mock_client, sample_codelist) -> None:
        mock_client.get.return_value = sample_codelist
        result = await get_codelist(mock_client, package_id="sdtmct-2024-03-29", codelist_id="C66781")
        assert "_links" not in result

    async def test_get_codelist_terms_truncates(self, mock_client, sample_codelist) -> None:
        mock_client.get.return_value = sample_codelist["terms"]
        result = await get_codelist_terms(mock_client, package_id="sdtmct-2024-03-29", codelist_id="C66781")
        # 150 terms > DEFAULT_MAX_ITEMS(100), should be truncated
        assert result.get("has_more") is True
```

**Step 2: 运行验证失败**

```bash
python -m pytest tests/test_tools.py::TestTerminology -v
```

Expected: failed

**Step 3: 实现 tools/terminology.py**

```python
"""MCP tools for CDISC Controlled Terminology (CT) queries."""

from __future__ import annotations

from typing import Any

from ..client import CDISCClient
from ..response_formatter import format_response


async def list_ct_packages(client: CDISCClient) -> dict[str, Any]:
    """List all available CDISC Controlled Terminology packages.

    Returns available CT packages (SDTM CT, ADaM CT, etc.) with their
    release dates and identifiers. Use the package ID from here as input
    to get_codelist() and get_codelist_terms().

    Example queries:
        - "What CT packages are available?"
        - "List controlled terminology versions"
    """
    data = await client.get("/mdr/ct/packages")
    return format_response(data)


async def get_codelist(
    client: CDISCClient, package_id: str, codelist_id: str
) -> dict[str, Any]:
    """Get the definition and metadata of a specific codelist.

    Args:
        package_id: CT package identifier, e.g. "sdtmct-2024-03-29".
        codelist_id: Codelist concept ID, e.g. "C66781" (AGEU) or
            submission value like "AGEU".

    Example queries:
        - "What is the AGEU codelist?"
        - "Describe the SEX codelist"
    """
    data = await client.get(f"/mdr/ct/packages/{package_id}/codelists/{codelist_id}")
    return format_response(data)


async def get_codelist_terms(
    client: CDISCClient, package_id: str, codelist_id: str
) -> dict[str, Any]:
    """Get all valid terms within a specific codelist.

    Returns up to 100 terms. If has_more is True, additional terms exist
    but are not shown (use a more specific query to narrow results).

    Args:
        package_id: CT package identifier.
        codelist_id: Codelist concept ID or submission value.

    Example queries:
        - "What are the valid values for AGEU?"
        - "List all terms in the COUNTRY codelist"
    """
    data = await client.get(
        f"/mdr/ct/packages/{package_id}/codelists/{codelist_id}/terms"
    )
    return format_response(data)
```

**Step 4: 运行验证通过**

```bash
python -m pytest tests/test_tools.py::TestTerminology -v
```

Expected: 3 passed

**Step 5: Commit**

```bash
git add src/cdisc_mcp/tools/terminology.py tests/test_tools.py
git commit -m "feat: add Controlled Terminology tools (list_ct_packages, get_codelist, get_codelist_terms)"
```

---

## Task 8: tools/adam.py 和 tools/cdash.py

**Files:**
- Create: `src/cdisc_mcp/tools/adam.py`
- Create: `src/cdisc_mcp/tools/cdash.py`

**Step 1: 实现 adam.py**

```python
"""MCP tools for ADaM (Analysis Data Model) standard queries."""

from __future__ import annotations

from typing import Any

from ..client import CDISCClient
from ..response_formatter import format_response


async def get_adam_datastructures(client: CDISCClient, version: str) -> dict[str, Any]:
    """List all ADaM data structures for a given version.

    Args:
        version: ADaM version, e.g. "1.3", "2.1".

    Example queries:
        - "What data structures are in ADaM?"
        - "List ADaM datasets in version 1.3"
    """
    data = await client.get(f"/mdr/adam/{version}")
    return format_response(data)


async def get_adam_variable(
    client: CDISCClient, version: str, data_structure: str, variable: str
) -> dict[str, Any]:
    """Get the definition of a specific ADaM variable.

    Args:
        version: ADaM version, e.g. "1.3".
        data_structure: Data structure name, e.g. "ADSL", "ADAE".
        variable: Variable name, e.g. "USUBJID", "AVAL".
    """
    data_structure = data_structure.upper().strip()
    variable = variable.upper().strip()
    data = await client.get(
        f"/mdr/adam/{version}/{data_structure}/variables/{variable}"
    )
    return format_response(data)
```

**Step 2: 实现 cdash.py**

```python
"""MCP tools for CDASH (Clinical Data Acquisition Standards Harmonization) queries."""

from __future__ import annotations

from typing import Any

from ..client import CDISCClient
from ..response_formatter import format_response


async def get_cdash_domains(client: CDISCClient, version: str) -> dict[str, Any]:
    """List all CDASH domains for a given version.

    Args:
        version: CDASH version, e.g. "2.0", "1.1".

    Example queries:
        - "What domains are in CDASH?"
        - "List CDASH data collection domains"
    """
    data = await client.get(f"/mdr/cdash/{version}")
    return format_response(data)


async def get_cdash_domain_fields(
    client: CDISCClient, version: str, domain: str
) -> dict[str, Any]:
    """Get all data collection fields for a CDASH domain.

    Args:
        version: CDASH version.
        domain: Domain code, e.g. "DM", "AE", "VS".

    Example queries:
        - "What fields does CDASH collect for adverse events?"
        - "List all VS domain fields in CDASH 2.0"
    """
    domain = domain.upper().strip()
    data = await client.get(f"/mdr/cdash/{version}/domains/{domain}/fields")
    return format_response(data)
```

**Step 3: 写测试并验证**

```python
# test_tools.py 中追加
from cdisc_mcp.tools.adam import get_adam_datastructures
from cdisc_mcp.tools.cdash import get_cdash_domains


class TestAdam:
    async def test_version_in_url(self, mock_client) -> None:
        mock_client.get.return_value = {"dataStructures": []}
        await get_adam_datastructures(mock_client, version="1.3")
        call_path = mock_client.get.call_args[0][0]
        assert "1.3" in call_path


class TestCdash:
    async def test_domain_uppercased(self, mock_client) -> None:
        mock_client.get.return_value = {"fields": []}
        from cdisc_mcp.tools.cdash import get_cdash_domain_fields
        await get_cdash_domain_fields(mock_client, version="2.0", domain="ae")
        call_path = mock_client.get.call_args[0][0]
        assert "AE" in call_path
```

```bash
python -m pytest tests/test_tools.py -v -k "adam or cdash or Adam or Cdash"
```

Expected: 2 passed

**Step 4: Commit**

```bash
git add src/cdisc_mcp/tools/adam.py src/cdisc_mcp/tools/cdash.py tests/test_tools.py
git commit -m "feat: add ADaM and CDASH tools"
```

---

## Task 9: server.py（MCP 服务器入口）

**Files:**
- Create: `src/cdisc_mcp/server.py`

**Step 1: 实现 server.py**

```python
"""FastMCP server entry point for the CDISC Library MCP service.

All MCP tools are registered here with dependency injection of the
CDISCClient, ensuring tools are testable without a running server.
"""

from __future__ import annotations

import logging

from fastmcp import FastMCP

from .client import CDISCClient
from .config import load_config
from .tools import adam, cdash, search, sdtm, terminology

logger = logging.getLogger(__name__)


def create_server() -> FastMCP:
    """Create and configure the FastMCP server with all CDISC tools.

    Returns:
        Configured FastMCP server instance ready to run.
    """
    config = load_config()
    client = CDISCClient(config)
    mcp = FastMCP("cdisc-mcp")

    # Register all tools with injected client
    @mcp.tool()
    async def list_products() -> dict:
        """List all available CDISC standards and their published versions."""
        return await search.list_products(client)

    @mcp.tool()
    async def search_cdisc(query: str) -> dict:
        """Search across all CDISC standards by keyword.

        Args:
            query: Search keyword, e.g. "adverse event", "AEDECOD"
        """
        return await search.search_cdisc(client, query)

    @mcp.tool()
    async def get_sdtm_domains(version: str) -> dict:
        """List all SDTM domains for a given version (e.g. "3.4")."""
        return await sdtm.get_sdtm_domains(client, version)

    @mcp.tool()
    async def get_sdtm_domain_variables(version: str, domain: str) -> dict:
        """Get all variables in an SDTM domain (e.g. version="3.4", domain="AE")."""
        return await sdtm.get_sdtm_domain_variables(client, version, domain)

    @mcp.tool()
    async def get_sdtm_variable(version: str, domain: str, variable: str) -> dict:
        """Get the full definition of a specific SDTM variable."""
        return await sdtm.get_sdtm_variable(client, version, domain, variable)

    @mcp.tool()
    async def get_adam_datastructures(version: str) -> dict:
        """List all ADaM data structures for a given version (e.g. "1.3")."""
        return await adam.get_adam_datastructures(client, version)

    @mcp.tool()
    async def get_adam_variable(version: str, data_structure: str, variable: str) -> dict:
        """Get the definition of a specific ADaM variable."""
        return await adam.get_adam_variable(client, version, data_structure, variable)

    @mcp.tool()
    async def get_cdash_domains(version: str) -> dict:
        """List all CDASH domains for a given version (e.g. "2.0")."""
        return await cdash.get_cdash_domains(client, version)

    @mcp.tool()
    async def get_cdash_domain_fields(version: str, domain: str) -> dict:
        """Get all data collection fields for a CDASH domain."""
        return await cdash.get_cdash_domain_fields(client, version, domain)

    @mcp.tool()
    async def list_ct_packages() -> dict:
        """List all available CDISC Controlled Terminology packages."""
        return await terminology.list_ct_packages(client)

    @mcp.tool()
    async def get_codelist(package_id: str, codelist_id: str) -> dict:
        """Get a specific CT codelist by package and codelist ID."""
        return await terminology.get_codelist(client, package_id, codelist_id)

    @mcp.tool()
    async def get_codelist_terms(package_id: str, codelist_id: str) -> dict:
        """List all valid terms in a CT codelist (max 100 shown)."""
        return await terminology.get_codelist_terms(client, package_id, codelist_id)

    return mcp


def main() -> None:
    """Entry point for cdisc-mcp command."""
    logging.basicConfig(level=logging.INFO)
    mcp = create_server()
    mcp.run()


if __name__ == "__main__":
    main()
```

**Step 2: 验证服务器可以启动（dry run）**

```bash
python -c "from cdisc_mcp.server import create_server; print('server OK')"
```

Note: 需要设置 CDISC_API_KEY 环境变量

**Step 3: Commit**

```bash
git add src/cdisc_mcp/server.py
git commit -m "feat: add FastMCP server with all 11 CDISC tools registered"
```

---

## Task 10: 整体验证与覆盖率检查

**Step 1: 运行全部测试**

```bash
python -m pytest tests/ -v
```

Expected: 全部 pass

**Step 2: 检查覆盖率**

```bash
python -m pytest tests/ --cov=src/cdisc_mcp --cov-report=term-missing
```

Expected: 整体覆盖率 ≥ 80%

**Step 3: 若覆盖率不足，补充测试**

重点补充：
- `client.py` 的 `_should_retry` 函数各分支
- `response_formatter.py` 的空列表和非 dict 元素
- `errors.py` 的 `RateLimitError` with/without retry_after

**Step 4: 更新 README**

```bash
# 更新 README.md 加入安装和使用说明
```

**Step 5: 最终 commit**

```bash
git add -A
git commit -m "docs: update README with installation and usage instructions"
```

---

## 附录：CDISC Library API 端点参考

```
GET /mdr/products                                    # 所有产品
GET /mdr/search?query={q}                            # 全局搜索

# SDTM
GET /mdr/sdtm/{version}                              # 域列表
GET /mdr/sdtm/{version}/datasets/{domain}/variables  # 域变量列表
GET /mdr/sdtm/{version}/datasets/{domain}/variables/{variable}  # 单变量

# ADaM
GET /mdr/adam/{version}                              # 数据结构列表
GET /mdr/adam/{version}/{dataStructure}/variables/{variable}

# CDASH
GET /mdr/cdash/{version}                             # 域列表
GET /mdr/cdash/{version}/domains/{domain}/fields

# Controlled Terminology
GET /mdr/ct/packages                                 # CT 包列表
GET /mdr/ct/packages/{packageId}/codelists/{codelistId}
GET /mdr/ct/packages/{packageId}/codelists/{codelistId}/terms
```

---

## 决策记录（来自智能体团队评审）

| 决策 | 选择 | 原因 |
|------|------|------|
| HTTP mock 库 | pytest-httpx | 队列式 add_response 天然支持重试序列测试 |
| 缓存实现 | asyncio.Lock + TTLCache | 防止异步场景下的 cache stampede |
| 重试粒度 | 仅 429 + 5xx | 4xx（除429）是客户端错误，重试无意义 |
| 工具粒度 | 11 个工具 | 避免 AI 工具选择时的认知负担 |
| Python 版本 | ≥3.11 | union type `X | Y` 语法 + tomllib stdlib |
| 截断通知 | has_more + total_returned | AI 需要知道数据被截断才能正确推理 |
