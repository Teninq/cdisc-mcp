"""MCP tools for SDTM standard queries."""

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


async def get_sdtm_domains(client: CDISCClient, version: str) -> dict[str, Any]:
    """List all SDTM datasets for a given version.

    Args:
        version: SDTM-IG version using dashes, e.g. "3-4", "3-3".
    """
    version = validate_version(version)
    data = await client.get(f"/mdr/sdtmig/{version}/datasets")
    return {
        "label": data.get("label"),
        "version": data.get("version"),
        "datasets": _hal_items(data, "datasets"),
    }


async def get_sdtm_domain_variables(
    client: CDISCClient, version: str, domain: str
) -> dict[str, Any]:
    """Get all variables defined for an SDTM domain.

    Args:
        version: SDTM-IG version using dashes, e.g. "3-4".
        domain: Two-letter domain code, e.g. "DM", "AE", "LB".
    """
    version = validate_version(version)
    domain = domain.upper().strip()
    data = await client.get(f"/mdr/sdtmig/{version}/datasets/{domain}/variables")
    return {
        "domain": domain,
        "label": data.get("label"),
        "variables": _hal_items(data, "datasetVariables"),
    }


async def get_sdtm_variable(
    client: CDISCClient, version: str, domain: str, variable: str
) -> dict[str, Any]:
    """Get the full definition of a specific SDTM variable.

    Args:
        version: SDTM-IG version using dashes, e.g. "3-4".
        domain: Two-letter domain code, e.g. "AE".
        variable: Variable name, e.g. "AETERM", "AEDECOD".
    """
    version = validate_version(version)
    domain = domain.upper().strip()
    variable = variable.upper().strip()
    data = await client.get(
        f"/mdr/sdtmig/{version}/datasets/{domain}/variables/{variable}"
    )
    return format_response(data)
