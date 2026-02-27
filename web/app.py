"""FastAPI bridge server — exposes CDISC MCP tools as REST endpoints.

Run with:
    python web/app.py

Or directly with uvicorn:
    uvicorn web.app:app --port 8080 --reload
"""

from __future__ import annotations

import os
import sys
import time
from pathlib import Path
from typing import Any

# Allow importing from src/ when running as a script
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

from cdisc_mcp.client import CDISCClient
from cdisc_mcp.config import load_config
from cdisc_mcp.errors import AuthenticationError, RateLimitError, ResourceNotFoundError
from cdisc_mcp.tools.adam import get_adam_datastructures, get_adam_variable
from cdisc_mcp.tools.cdash import get_cdash_domain_fields, get_cdash_domains
from cdisc_mcp.tools.sdtm import (
    get_sdtm_domain_variables,
    get_sdtm_domains,
    get_sdtm_variable,
)
from cdisc_mcp.tools.search import list_products
from cdisc_mcp.tools.terminology import get_codelist, get_codelist_terms, list_ct_packages

# ---------------------------------------------------------------------------
# Static tool metadata — drives the UI form generation
# ---------------------------------------------------------------------------

TOOLS_METADATA: list[dict[str, Any]] = [
    # Search
    {
        "name": "list_products",
        "category": "Search",
        "description": "List all available CDISC standards and their published versions.",
        "parameters": [],
    },
    # SDTM
    {
        "name": "get_sdtm_domains",
        "category": "SDTM",
        "description": "List all SDTM datasets for a given SDTM-IG version.",
        "parameters": [
            {
                "name": "version",
                "type": "select",
                "required": True,
                "options": ["3-4", "3-3", "3-2", "3-1-3"],
                "hint": "SDTM-IG version (use dashes)",
            }
        ],
    },
    {
        "name": "get_sdtm_domain_variables",
        "category": "SDTM",
        "description": "Get all variables defined for an SDTM domain.",
        "parameters": [
            {
                "name": "version",
                "type": "select",
                "required": True,
                "options": ["3-4", "3-3", "3-2", "3-1-3"],
                "hint": "SDTM-IG version (use dashes)",
            },
            {
                "name": "domain",
                "type": "select",
                "required": True,
                "options": ["AE", "CM", "DM", "DS", "EG", "EX", "LB", "MH", "VS", "DV", "PE", "PR", "SU", "TU"],
                "hint": "Two-letter domain code",
            },
        ],
    },
    {
        "name": "get_sdtm_variable",
        "category": "SDTM",
        "description": "Get the full definition of a specific SDTM variable.",
        "parameters": [
            {
                "name": "version",
                "type": "select",
                "required": True,
                "options": ["3-4", "3-3", "3-2", "3-1-3"],
                "hint": "SDTM-IG version (use dashes)",
            },
            {
                "name": "domain",
                "type": "select",
                "required": True,
                "options": ["AE", "CM", "DM", "DS", "EG", "EX", "LB", "MH", "VS", "DV", "PE", "PR", "SU", "TU"],
                "hint": "Two-letter domain code",
            },
            {
                "name": "variable",
                "type": "string",
                "required": True,
                "hint": "e.g. 'AETERM', 'AEDECOD', 'USUBJID'",
            },
        ],
    },
    # ADaM
    {
        "name": "get_adam_datastructures",
        "category": "ADaM",
        "description": "List all ADaM data structures for a given ADaM IG version.",
        "parameters": [
            {
                "name": "version",
                "type": "select",
                "required": True,
                "options": ["1-3", "1-2", "1-1", "1-0"],
                "hint": "ADaM IG version (use dashes)",
            }
        ],
    },
    {
        "name": "get_adam_variable",
        "category": "ADaM",
        "description": "Get the definition of a specific ADaM variable.",
        "parameters": [
            {
                "name": "version",
                "type": "select",
                "required": True,
                "options": ["1-3", "1-2", "1-1", "1-0"],
                "hint": "ADaM IG version (use dashes)",
            },
            {
                "name": "data_structure",
                "type": "select",
                "required": True,
                "options": ["ADSL", "BDS", "TTE"],
                "hint": "Data structure name (ADSL, BDS, TTE)",
            },
            {
                "name": "variable",
                "type": "string",
                "required": True,
                "hint": "e.g. 'USUBJID', 'AVAL', 'TRTP'",
            },
        ],
    },
    # CDASH
    {
        "name": "get_cdash_domains",
        "category": "CDASH",
        "description": "List all CDASH domains for a given CDASH IG version.",
        "parameters": [
            {
                "name": "version",
                "type": "select",
                "required": True,
                "options": ["2-1", "2-0", "1-1-1"],
                "hint": "CDASH IG version (use dashes)",
            }
        ],
    },
    {
        "name": "get_cdash_domain_fields",
        "category": "CDASH",
        "description": "Get all data collection fields for a CDASH domain.",
        "parameters": [
            {
                "name": "version",
                "type": "select",
                "required": True,
                "options": ["2-1", "2-0", "1-1-1"],
                "hint": "CDASH IG version (use dashes)",
            },
            {
                "name": "domain",
                "type": "select",
                "required": True,
                "options": ["AE", "CM", "DM", "EG", "EX", "LB", "MH", "VS", "DS", "PE", "PR", "SU"],
                "hint": "Domain code",
            },
        ],
    },
    # Controlled Terminology
    {
        "name": "list_ct_packages",
        "category": "Terminology",
        "description": "List all available CDISC Controlled Terminology packages.",
        "parameters": [],
    },
    {
        "name": "get_codelist",
        "category": "Terminology",
        "description": "Get the definition and metadata of a specific codelist.",
        "parameters": [
            {
                "name": "package_id",
                "type": "string",
                "required": True,
                "hint": "e.g. 'sdtmct-2024-03-29'",
            },
            {
                "name": "codelist_id",
                "type": "string",
                "required": True,
                "hint": "e.g. 'C66781' or 'AGEU'",
            },
        ],
    },
    {
        "name": "get_codelist_terms",
        "category": "Terminology",
        "description": "Get all valid terms within a specific codelist (max 100 shown).",
        "parameters": [
            {
                "name": "package_id",
                "type": "string",
                "required": True,
                "hint": "e.g. 'sdtmct-2024-03-29'",
            },
            {
                "name": "codelist_id",
                "type": "string",
                "required": True,
                "hint": "e.g. 'C66781' or 'AGEU'",
            },
        ],
    },
]

# Map tool names to their handler functions
_TOOL_HANDLERS: dict[str, Any] = {
    "list_products": list_products,
    "get_sdtm_domains": get_sdtm_domains,
    "get_sdtm_domain_variables": get_sdtm_domain_variables,
    "get_sdtm_variable": get_sdtm_variable,
    "get_adam_datastructures": get_adam_datastructures,
    "get_adam_variable": get_adam_variable,
    "get_cdash_domains": get_cdash_domains,
    "get_cdash_domain_fields": get_cdash_domain_fields,
    "list_ct_packages": list_ct_packages,
    "get_codelist": get_codelist,
    "get_codelist_terms": get_codelist_terms,
}

# ---------------------------------------------------------------------------
# FastAPI app setup
# ---------------------------------------------------------------------------

_client: CDISCClient | None = None


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    global _client
    config = load_config()
    _client = CDISCClient(config)
    yield
    if _client is not None:
        await _client.close()


app = FastAPI(title="CDISC MCP Explorer", version="0.1.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------------------------
# Request/response models
# ---------------------------------------------------------------------------


class ToolRequest(BaseModel):
    params: dict[str, Any] = {}


class ToolResponse(BaseModel):
    result: Any
    elapsed_ms: float


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------


@app.get("/", response_class=HTMLResponse)
async def root() -> HTMLResponse:
    index_path = Path(__file__).parent / "index.html"
    return HTMLResponse(content=index_path.read_text(encoding="utf-8"))


@app.get("/api/tools")
async def get_tools() -> list[dict[str, Any]]:
    return TOOLS_METADATA


@app.post("/api/tools/{tool_name}")
async def call_tool(tool_name: str, request: ToolRequest) -> ToolResponse:
    handler = _TOOL_HANDLERS.get(tool_name)
    if handler is None:
        raise HTTPException(status_code=404, detail=f"Tool '{tool_name}' not found")

    if _client is None:
        raise HTTPException(status_code=503, detail="Client not initialized")

    start = time.perf_counter()
    try:
        result = await handler(_client, **request.params)
    except AuthenticationError as exc:
        raise HTTPException(status_code=401, detail=str(exc)) from exc
    except ResourceNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except RateLimitError as exc:
        raise HTTPException(status_code=429, detail=str(exc)) from exc
    except TypeError as exc:
        raise HTTPException(status_code=422, detail=f"Invalid parameters: {exc}") from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    elapsed_ms = (time.perf_counter() - start) * 1000
    return ToolResponse(result=result, elapsed_ms=round(elapsed_ms, 1))


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import uvicorn

    port = int(os.environ.get("PORT", 8080))
    try:
        uvicorn.run(app, host="0.0.0.0", port=port)
    except OSError as e:
        if "10048" in str(e) or "address already in use" in str(e).lower():
            print(
                f"\nPort {port} is already in use. Kill the previous process first:\n\n"
                f"  PowerShell:  Get-Process -Id (Get-NetTCPConnection -LocalPort {port}"
                f" -ErrorAction SilentlyContinue).OwningProcess | Stop-Process -Force\n"
                f"  CMD:         for /f \"tokens=5\" %a in ('netstat -ano ^| findstr :{port}') do taskkill /PID %a /F\n\n"
                f"Or start on a different port:  set PORT=8081 && python web/app.py\n"
            )
        else:
            raise
