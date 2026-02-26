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
        Dict with product information.
    """
    data = await client.get("/mdr/products")
    return format_response(data)


async def search_cdisc(client: CDISCClient, query: str) -> dict[str, Any]:
    """Search across all CDISC standards by keyword.

    Searches variable names, labels, descriptions, and codelist terms across
    all CDISC standards.

    Args:
        query: Search keyword or phrase (e.g., "adverse event", "AEDECOD").

    Returns:
        Dict with matching results.
    """
    params = urlencode({"query": query})
    data = await client.get(f"/mdr/search?{params}")
    return format_response(data)
