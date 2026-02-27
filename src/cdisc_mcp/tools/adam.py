"""MCP tools for ADaM standard queries."""

from __future__ import annotations

from typing import Any

from ..client import CDISCClient
from ..response_formatter import format_response
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


async def get_adam_datastructures(client: CDISCClient, version: str) -> dict[str, Any]:
    """List all ADaM data structures for a given ADaM IG version.

    Args:
        version: ADaM IG version using dashes, e.g. "1-3", "1-2".
    """
    version = validate_version(version)
    data = await client.get(f"/mdr/adam/adamig-{version}/datastructures")
    return {
        "label": data.get("label"),
        "version": data.get("version"),
        "dataStructures": _hal_items(data, "dataStructures"),
    }


async def get_adam_variable(
    client: CDISCClient, version: str, data_structure: str, variable: str
) -> dict[str, Any]:
    """Get the definition of a specific ADaM variable.

    Args:
        version: ADaM IG version using dashes, e.g. "1-3".
        data_structure: Data structure name, e.g. "ADSL", "BDS", "TTE".
        variable: Variable name, e.g. "USUBJID", "AVAL".
    """
    version = validate_version(version)
    data_structure = data_structure.upper().strip()
    variable = variable.upper().strip()
    data = await client.get(
        f"/mdr/adam/adamig-{version}/datastructures/{data_structure}/variables/{variable}"
    )
    return format_response(data)
