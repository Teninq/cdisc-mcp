"""MCP tools for CDASH standard queries."""

from __future__ import annotations

from typing import Any

from ..client import CDISCClient
from ._helpers import hal_items
from ._validators import normalize_version_for_path, validate_version


async def get_cdash_domains(client: CDISCClient, version: str) -> dict[str, Any]:
    """List all CDASH domains for a given version.

    Args:
        version: CDASH IG version, e.g. "2.0" or "2-0", "2.1" or "2-1".
    """
    version = normalize_version_for_path(validate_version(version))
    data = await client.get(f"/mdr/cdashig/{version}/domains")
    return {
        "label": data.get("label"),
        "version": data.get("version"),
        "domains": hal_items(data, "domains"),
    }


async def get_cdash_domain_fields(
    client: CDISCClient, version: str, domain: str
) -> dict[str, Any]:
    """Get all data collection fields for a CDASH domain.

    Args:
        version: CDASH IG version, e.g. "2.0" or "2-0".
        domain: Domain code, e.g. "DM", "AE", "VS".
    """
    version = normalize_version_for_path(validate_version(version))
    domain = domain.upper().strip()
    data = await client.get(f"/mdr/cdashig/{version}/domains/{domain}/fields")
    return {
        "domain": domain,
        "label": data.get("label"),
        "fields": hal_items(data, "fields"),
    }
