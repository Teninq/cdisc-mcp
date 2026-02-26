"""MCP tools for CDISC Controlled Terminology queries."""

from __future__ import annotations

from typing import Any

from ..client import CDISCClient
from ..response_formatter import format_response


async def list_ct_packages(client: CDISCClient) -> dict[str, Any]:
    """List all available CDISC Controlled Terminology packages."""
    data = await client.get("/mdr/ct/packages")
    return format_response(data)


async def get_codelist(
    client: CDISCClient, package_id: str, codelist_id: str
) -> dict[str, Any]:
    """Get the definition and metadata of a specific codelist.

    Args:
        package_id: CT package identifier, e.g. "sdtmct-2024-03-29".
        codelist_id: Codelist concept ID, e.g. "C66781" or "AGEU".
    """
    data = await client.get(
        f"/mdr/ct/packages/{package_id}/codelists/{codelist_id}"
    )
    return format_response(data)


async def get_codelist_terms(
    client: CDISCClient, package_id: str, codelist_id: str
) -> dict[str, Any]:
    """Get all valid terms within a specific codelist (max 100 shown).

    Args:
        package_id: CT package identifier.
        codelist_id: Codelist concept ID or submission value.
    """
    data = await client.get(
        f"/mdr/ct/packages/{package_id}/codelists/{codelist_id}/terms"
    )
    return format_response(data)
