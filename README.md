<div align="center">

<br/>

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="docs/header-dark.svg">
  <img src="docs/cdisc-mcp.png" alt="CDISC MCP" width="728">
</picture>

<br/>

**CDISC Library MCP Server** — Query clinical data standards (SDTM, ADaM, CDASH, CT) directly from AI assistants.

<br/>

[![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?style=flat-square&logo=python&logoColor=white)](https://python.org)
[![FastMCP](https://img.shields.io/badge/FastMCP-latest-FF6B35?style=flat-square)](https://github.com/jlowin/fastmcp)
![License: MIT](https://img.shields.io/badge/License-MIT-22C55E?style=flat-square)
[![Tests](https://img.shields.io/badge/Coverage-80%25%2B-22C55E?style=flat-square)](tests/)
[![API](https://img.shields.io/badge/CDISC_Library-v2_API-0EA5E9?style=flat-square)](https://library.cdisc.org)

<br/>

**🌐 Translations:** [中文 README](docs/README.zh.md) · [日本語 README](docs/README.ja.md)

<br/>

</div>

---

## What is This?

The **CDISC MCP Server** connects AI assistants (Claude, VS Code Copilot, Cursor, etc.) to the [CDISC Library REST API](https://library.cdisc.org), exposing 11 structured tools for querying clinical trial data standards. Ask your AI assistant questions like:

> *"What variables are in the SDTM AE domain?"*/m
> *"Show me the ADSL variables in ADaM IG 1.3"*
> *"List all available Controlled Terminology packages"*

For full setup instructions, see the **[User Manual →](docs/user-manual.md)**. See **[Examples →](docs/examples.md)** for real conversation samples.

---

## Quick Start

### 1 · Get a CDISC Library API Key

Register at **https://library.cdisc.org** and obtain a personal API key.

### 2 · Install

```bash
# Runtime only
pip install -e .

# With dev dependencies
pip install -e ".[dev]"

# With web explorer
pip install -e ".[web]"
```

### 3 · Set API Key

```bash
# Linux / macOS
export CDISC_API_KEY=your_key_here

# Windows — Command Prompt
set CDISC_API_KEY=your_key_here

# Windows — PowerShell
$env:CDISC_API_KEY = "your_key_here"
```

### 4 · Run

```bash
# Start MCP server (for AI assistant integration)
cdisc-mcp

# OR: Start Web Explorer (quick interactive testing)
python web/app.py
```

---

## Web Explorer — Quick Interactive Testing

The fastest way to verify your setup and explore tools **without any AI client**.

```bash
# 1. Install web dependencies
pip install -e ".[web]"

# 2. Set your API key
export CDISC_API_KEY=your_key_here   # Linux/macOS
set CDISC_API_KEY=your_key_here      # Windows CMD
$env:CDISC_API_KEY = "your_key_here" # Windows PowerShell

# 3. Start the bridge server
python web/app.py

# 4. Open in browser
#    → http://localhost:8080
```

The explorer provides:
- **Sidebar navigation** — all 11 tools organized by standard (SDTM / ADaM / CDASH / Terminology)
- **Auto-generated forms** — dropdowns for versions and domains, text inputs for variables
- **Live JSON responses** — syntax-highlighted, copyable output with response time
- **Bridge status indicator** — confirms your API key and connectivity

> **Tip:** Use version strings with dashes — `3-4` not `3.4`, `1-3` not `1.3`.
> Example: SDTM-IG `3-4`, ADaM-IG `1-3`, CDASH-IG `2-0`

---

## Available Tools

| # | Tool | Standard | Description |
|---|------|----------|-------------|
| 1 | `list_products` | — | List all available CDISC standards and published versions |
| 2 | `get_sdtm_domains` | SDTM | List all datasets in a SDTM-IG version |
| 3 | `get_sdtm_domain_variables` | SDTM | List all variables in an SDTM domain/dataset |
| 4 | `get_sdtm_variable` | SDTM | Get full definition of a specific SDTM variable |
| 5 | `get_adam_datastructures` | ADaM | List all data structures in an ADaM-IG version |
| 6 | `get_adam_variable` | ADaM | Get definition of a specific ADaM variable |
| 7 | `get_cdash_domains` | CDASH | List all domains in a CDASH-IG version |
| 8 | `get_cdash_domain_fields` | CDASH | Get all data collection fields for a CDASH domain |
| 9 | `list_ct_packages` | CT | List all available Controlled Terminology packages |
| 10 | `get_codelist` | CT | Get definition and metadata of a CT codelist |
| 11 | `get_codelist_terms` | CT | List all valid terms in a CT codelist |

### Version Reference

| Standard | Available Versions (use dashes) |
|----------|--------------------------------|
| SDTM-IG | `3-4` · `3-3` · `3-2` · `3-1-3` |
| ADaM-IG | `1-3` · `1-2` · `1-1` · `1-0` |
| CDASH-IG | `2-1` · `2-0` · `1-1-1` |

---

## Connect to an AI Assistant

### Claude Desktop

Add to `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "cdisc": {
      "command": "cdisc-mcp",
      "env": {
        "CDISC_API_KEY": "your_key_here"
      }
    }
  }
}
```

### VS Code / Cursor

Add to `.vscode/mcp.json` or equivalent MCP config:

```json
{
  "servers": {
    "cdisc": {
      "command": "cdisc-mcp",
      "env": {
        "CDISC_API_KEY": "your_key_here"
      }
    }
  }
}
```

### Claude Code (CLI)

Claude Code supports MCP servers at two scopes: **user** (global, all projects) and **project** (local, current project only).

**Option A — CLI command (recommended)**

```bash
# Add globally (available in all projects)
claude mcp add cdisc-mcp -e CDISC_API_KEY=your_key_here -- python -m cdisc_mcp.server

# Add for the current project only
claude mcp add cdisc-mcp --scope project -e CDISC_API_KEY=your_key_here -- python -m cdisc_mcp.server

# Verify the server was registered
claude mcp list
```

**Option B — Edit `~/.claude.json` directly**

```json
{
  "mcpServers": {
    "cdisc-mcp": {
      "command": "python",
      "args": ["-m", "cdisc_mcp.server"],
      "env": {
        "CDISC_API_KEY": "your_key_here"
      }
    }
  }
}
```

> **Tip:** If `CDISC_API_KEY` is already in your system environment, omit the `env` block entirely — Claude Code inherits it automatically.

Once registered, confirm with `/mcp` in any Claude Code session, then use the tools conversationally:

```
User: What SDTM domains are defined in version 3.4?
Claude: [calls get_sdtm_domains with version="3-4"] ...
```

---

## Using in Your Own Python Tools

You can call CDISC MCP tools programmatically from any Python script using the official MCP client SDK.

### Install the client

```bash
pip install mcp
```

### Minimal example

```python
import asyncio
import os
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

SERVER = StdioServerParameters(
    command="python",
    args=["-m", "cdisc_mcp.server"],
    env={"CDISC_API_KEY": os.environ["CDISC_API_KEY"]},
)

async def main():
    async with stdio_client(SERVER) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            # List all available tools
            tools = await session.list_tools()
            print([t.name for t in tools.tools])

            # Call a tool
            result = await session.call_tool(
                "get_sdtm_domains",
                arguments={"version": "3-4"},
            )
            print(result.content[0].text)

asyncio.run(main())
```

### Reusable helper

```python
import asyncio, os, json
from contextlib import asynccontextmanager
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

_SERVER = StdioServerParameters(
    command="python",
    args=["-m", "cdisc_mcp.server"],
    env={"CDISC_API_KEY": os.environ["CDISC_API_KEY"]},
)

@asynccontextmanager
async def cdisc_session():
    """Async context manager that yields an initialised MCP session."""
    async with stdio_client(_SERVER) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            yield session

async def call(tool: str, **kwargs) -> dict:
    async with cdisc_session() as s:
        result = await s.call_tool(tool, arguments=kwargs)
        return json.loads(result.content[0].text)

# --- Usage examples ---
async def demo():
    # Fetch SDTM domains
    domains = await call("get_sdtm_domains", version="3-4")

    # Fetch all variables in the AE domain
    variables = await call("get_sdtm_domain_variables", version="3-4", domain="AE")

    # Look up a single variable
    aeterm = await call("get_sdtm_variable", version="3-4", domain="AE", variable="AETERM")

    print(aeterm)

asyncio.run(demo())
```

### Available tool signatures (quick reference)

```python
# Products / versions
await session.call_tool("list_products", {})

# SDTM
await session.call_tool("get_sdtm_domains",          {"version": "3-4"})
await session.call_tool("get_sdtm_domain_variables", {"version": "3-4", "domain": "AE"})
await session.call_tool("get_sdtm_variable",         {"version": "3-4", "domain": "AE", "variable": "AETERM"})

# ADaM
await session.call_tool("get_adam_datastructures",   {"version": "1-3"})
await session.call_tool("get_adam_variable",         {"version": "1-3", "data_structure": "ADSL", "variable": "USUBJID"})

# CDASH
await session.call_tool("get_cdash_domains",         {"version": "2-0"})
await session.call_tool("get_cdash_domain_fields",   {"version": "2-0", "domain": "AE"})

# Controlled Terminology
await session.call_tool("list_ct_packages",          {})
await session.call_tool("get_codelist",              {"package_id": "sdtmct-2024-03-29", "codelist_id": "C66781"})
await session.call_tool("get_codelist_terms",        {"package_id": "sdtmct-2024-03-29", "codelist_id": "AGEU"})
```

> **Version format:** Always use dashes, not dots — `"3-4"` not `"3.4"`.

---

## Architecture

```
MCP Client (Claude / VS Code / Cursor)
        │
        │  MCP protocol (stdio)
        ▼
   server.py  ──── FastMCP tool registration
        │
        ▼
   tools/  ──────── domain functions (sdtm, adam, cdash, terminology, search)
        │
        ▼
   client.py  ───── CDISCClient (async HTTP · TTL cache · retry)
        │
        │  HTTPS
        ▼
   library.cdisc.org/api  ──── CDISC Library REST API
```

**Key design decisions:**
- `CDISCClient` is a singleton async HTTP client with 1-hour TTL in-memory cache
- Only `429` and `5xx` responses are retried; `4xx` raise immediately
- Tool functions are pure async — independently testable without patching
- `format_response()` strips HAL `_links` metadata, extracts structured data for LLM consumption

---

## Development

**Development workflow (devel-first, branch & merge SOP):** See [Contributing Guide](docs/CONTRIBUTING.md).

### Running Tests

```bash
# Full suite with coverage (≥80% required)
pytest

# Specific modules
pytest tests/test_tools.py tests/test_client.py -v

# Single test
pytest tests/test_tools.py::test_list_products -v
```

### Code Quality

```bash
ruff check src/ tests/    # Linting
mypy src/                 # Type checking
```

### GitHub Branch Protection (Required Checks)

Configure `main` branch protection to require:
- `CI Tests / tests`
- `CI Lint / lint`
- `CI Types / types`

### Project Structure

```
src/cdisc_mcp/
├── server.py              # FastMCP server + tool registration
├── client.py              # Async HTTP client (cache, retry)
├── config.py              # Config dataclass + env loader
├── errors.py              # AuthenticationError, ResourceNotFoundError, RateLimitError
├── response_formatter.py  # HAL response normalization
└── tools/
    ├── search.py          # list_products (product catalog)
    ├── sdtm.py            # SDTM domain/variable tools
    ├── adam.py            # ADaM datastructure/variable tools
    ├── cdash.py           # CDASH domain/field tools
    ├── terminology.py     # CT package/codelist tools
    └── _validators.py     # Path traversal guards
web/
├── app.py                 # FastAPI bridge server
└── index.html             # Single-file browser explorer
tests/
├── test_config.py
├── test_client.py
├── test_response_formatter.py
├── test_tools.py
├── test_errors.py
└── test_server.py
```

---

## License

MIT license.

---

<div align="center">

Built for clinical data professionals working with CDISC standards.

**[User Manual](docs/user-manual.md)** · **[Examples](docs/examples.md)** · **[CDISC Library](https://library.cdisc.org)** · **[API Docs](https://www.cdisc.org/cdisc-library/api-documentation)**

</div>
