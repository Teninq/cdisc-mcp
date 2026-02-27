"""MCP tools for CDISC Controlled Terminology queries."""

from __future__ import annotations

from typing import Any

from ..client import CDISCClient
from ..response_formatter import format_response


def _hal_items(data: dict[str, Any], key: str) -> list[dict[str, Any]]:
    """Extract a named list from HAL _links and return clean items."""
    items = data.get("_links", {}).get(key, [])
    return [
        {
            "name": item["href"].rstrip("/").split("/")[-1],
            "title": item.get("title"),
            "type": item.get("type"),
        }
        for item in items
        if isinstance(item, dict)
    ]


async def list_ct_packages(client: CDISCClient) -> dict[str, Any]:
    """List all available CDISC Controlled Terminology packages."""
    data = await client.get("/mdr/ct/packages")
    packages = _hal_items(data, "packages")
    return {"packages": packages, "count": len(packages)}


async def get_codelist(
    client: CDISCClient, package_id: str, codelist_id: str
) -> dict[str, Any]:
    """Get the definition and metadata of a specific codelist.

    Args:
        package_id: CT package identifier, e.g. "sdtmct-2024-09-27".
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
    terms = _hal_items(data, "terms")
    return {
        "codelist": codelist_id,
        "package": package_id,
        "terms": terms,
        "count": len(terms),
    }
