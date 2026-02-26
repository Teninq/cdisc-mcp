# cdisc-mcp

CDISC Library MCP Server — exposes CDISC standards data (SDTM, ADaM, CDASH, Controlled Terminology) as MCP tools that AI assistants can call directly.

For a full guide covering installation, API key setup, connecting to Claude Desktop or VS Code, tool reference, and troubleshooting, see the **[User Manual](docs/user-manual.md)**.

## Installation

```bash
# Install with development dependencies (recommended)
pip install -e ".[dev]"

# Install runtime only
pip install -e .
```

## Configuration

A CDISC Library personal API key is required. Obtain one at https://library.cdisc.org.

**Linux / macOS**
```bash
export CDISC_API_KEY=your_api_key_here
```

**Windows (Command Prompt)**
```cmd
set CDISC_API_KEY=your_api_key_here
```

**Windows (PowerShell)**
```powershell
$env:CDISC_API_KEY = "your_api_key_here"
```

## Running the Server

```bash
# Via installed entry point
cdisc-mcp

# Via Python module
python -m cdisc_mcp.server
```

## Available Tools (12)

| Tool | Description |
|------|-------------|
| `list_products` | List all available CDISC standards and their published versions |
| `search_cdisc` | Search across all CDISC standards by keyword |
| `get_sdtm_domains` | List all SDTM domains for a given version |
| `get_sdtm_domain_variables` | Get all variables defined in an SDTM domain |
| `get_sdtm_variable` | Get the full definition of a specific SDTM variable |
| `get_adam_datastructures` | List all ADaM data structures for a given version |
| `get_adam_variable` | Get the definition of a specific ADaM variable |
| `get_cdash_domains` | List all CDASH domains for a given version |
| `get_cdash_domain_fields` | Get all data collection fields for a CDASH domain |
| `list_ct_packages` | List all available Controlled Terminology packages |
| `get_codelist` | Get a specific CT codelist definition and metadata |
| `get_codelist_terms` | List all valid terms in a CT codelist (max 100) |

## Web Explorer (Optional)

A lightweight browser UI for interactively testing tools without an AI client.

```bash
# Install web dependencies
pip install -e ".[web]"

# Set API key and start the bridge server
set CDISC_API_KEY=your_api_key_here   # Windows CMD
python web/app.py
```

Open **http://localhost:8080** in your browser. The explorer lets you select any of the 12 tools, fill in parameters, run them, and inspect syntax-highlighted JSON responses.

## Development

### Running Tests

```bash
# Run full test suite with coverage (must reach 80%)
pytest

# Run specific test files
pytest tests/test_config.py tests/test_client.py tests/test_response_formatter.py tests/test_tools.py -v
```

### Project Structure

```
src/cdisc_mcp/
    __init__.py          # Package version
    client.py            # Async HTTP client with caching and retry
    config.py            # Configuration from environment variables
    errors.py            # Custom exception types
    response_formatter.py # Response cleaning and truncation
    server.py            # FastMCP server entry point
    tools/
        search.py        # list_products, search_cdisc
        sdtm.py          # SDTM domain and variable tools
        adam.py          # ADaM data structure and variable tools
        cdash.py         # CDASH domain and field tools
        terminology.py   # Controlled Terminology tools
        _validators.py   # Input validation helpers
web/
    app.py               # FastAPI bridge server (HTTP → tool functions)
    index.html           # Single-file browser explorer UI
tests/
    test_config.py
    test_client.py
    test_response_formatter.py
    test_tools.py
    test_errors.py
    test_server.py
    unit/                # Additional unit tests
    integration/         # Integration tests
```

### Code Quality

```bash
# Linting
ruff check src/ tests/

# Type checking
mypy src/
```
