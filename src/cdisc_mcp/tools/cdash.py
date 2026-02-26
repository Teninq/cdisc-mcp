"""MCP tools for CDASH standard queries."""

from __future__ import annotations

from typing import Any

from ..client import CDISCClient
from ..response_formatter import format_response


async def get_cdash_domains(client: CDISCClient, version: str) -> dict[str, Any]:
    """List all CDASH domains for a given version.

    Args:
        version: CDASH version, e.g. "2.0", "1.1".
    """
    data = await client.get(f"/mdr/cdash/{version}")
    return format_response(data)


async def get_cdash_domain_fields(
    client: CDISCClient, version: str, domain: str
) -> dict[str, Any]:
    """Get all data collection fields for a CDASH domain.

    Args:
        version: CDASH version.
        domain: Domain code, e.g. "DM", "AE", "VS".
    """
    domain = domain.upper().strip()
    data = await client.get(f"/mdr/cdash/{version}/domains/{domain}/fields")
    return format_response(data)
