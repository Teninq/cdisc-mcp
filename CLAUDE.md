# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```bash
# Install with dev dependencies
pip install -e ".[dev]"

# Run full test suite (must reach 80% coverage)
pytest

# Run specific test files
pytest tests/test_tools.py -v

# Run a single test
pytest tests/test_tools.py::test_function_name -v

# Lint
ruff check src/ tests/

# Type check
mypy src/
```

## Architecture

The server exposes the [CDISC Library Cosmos v2 REST API](https://library.cdisc.org/api/cosmos/v2) as MCP tools using **FastMCP**.

**Request flow:** MCP tool call → `server.py` (thin wrappers) → domain tool function in `tools/` → `CDISCClient.get()` (cached, retried) → CDISC Library API

### Key design decisions

- **`CDISCClient`** (`client.py`) is a singleton async HTTP client. It is created once in `_async_main()` via `async with CDISCClient(config)` and injected into every tool function. Tests pass a mock client directly to tool functions — no monkeypatching needed.
- **Caching** is in-memory `TTLCache` (default 1 hr, 256 entries), protected by `asyncio.Lock` for concurrent access safety.
- **Retry** via `tenacity` — only 429 and 5xx are retried; 4xx raise immediately. After exhausting retries on 429, `RateLimitError` is raised.
- **Tool registration** in `server.py::create_server()` — each `@mcp.tool()` closure delegates to a pure async function in `tools/`. This separation keeps tools testable standalone.
- **`_validators.py`** contains `validate_version()` which guards against path traversal in URL path parameters.
- **`response_formatter.py`** truncates large API responses before returning them to the LLM.

### Module map

| Module | Role |
|--------|------|
| `config.py` | `Config` dataclass + `load_config()` from `CDISC_API_KEY` env var |
| `client.py` | `CDISCClient` — async HTTP with cache and retry |
| `errors.py` | `AuthenticationError`, `ResourceNotFoundError`, `RateLimitError` |
| `response_formatter.py` | Truncate/clean API responses |
| `server.py` | FastMCP tool registration + entry point |
| `tools/search.py` | `list_products`, `search_cdisc` |
| `tools/sdtm.py` | SDTM domain/variable tools |
| `tools/adam.py` | ADaM data structure/variable tools |
| `tools/cdash.py` | CDASH domain/field tools |
| `tools/terminology.py` | Controlled Terminology codelist tools |

## Environment

```bash
# Required
CDISC_API_KEY=your_api_key_here  # Obtain at https://library.cdisc.org
```

`load_config()` raises `ValueError` at startup if `CDISC_API_KEY` is missing.
