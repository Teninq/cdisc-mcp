"""MCP tools for CDASH standard queries."""

from __future__ import annotations

from typing import Any

from ..client import CDISCClient
from ._validators import validate_version


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


async def get_cdash_domains(client: CDISCClient, version: str) -> dict[str, Any]:
    """List all CDASH domains for a given version.

    Args:
        version: CDASH IG version using dashes, e.g. "2-0", "2-1", "1-1-1".
    """
    version = validate_version(version)
    data = await client.get(f"/mdr/cdashig/{version}/domains")
    return {
        "label": data.get("label"),
        "version": data.get("version"),
        "domains": _hal_items(data, "domains"),
    }


async def get_cdash_domain_fields(
    client: CDISCClient, version: str, domain: str
) -> dict[str, Any]:
    """Get all data collection fields for a CDASH domain.

    Args:
        version: CDASH IG version using dashes, e.g. "2-0".
        domain: Domain code, e.g. "DM", "AE", "VS".
    """
    version = validate_version(version)
    domain = domain.upper().strip()
    data = await client.get(f"/mdr/cdashig/{version}/domains/{domain}/fields")
    return {
        "domain": domain,
        "label": data.get("label"),
        "fields": _hal_items(data, "fields"),
    }
