"""MCP tools for SDTM standard queries."""

from __future__ import annotations

from typing import Any

from ..client import CDISCClient
from ..response_formatter import format_response
from ._validators import validate_version


async def get_sdtm_domains(client: CDISCClient, version: str) -> dict[str, Any]:
    """List all SDTM domains for a given version.

    Args:
        version: SDTM-IG version number, e.g. "3.4", "3.3".
    """
    version = validate_version(version)
    data = await client.get(f"/mdr/sdtm/{version}")
    return format_response(data)


async def get_sdtm_domain_variables(
    client: CDISCClient, version: str, domain: str
) -> dict[str, Any]:
    """Get all variables defined for an SDTM domain.

    Args:
        version: SDTM-IG version, e.g. "3.4".
        domain: Two-letter domain code, e.g. "DM", "AE", "LB".
    """
    version = validate_version(version)
    domain = domain.upper().strip()
    data = await client.get(f"/mdr/sdtm/{version}/datasets/{domain}/variables")
    return format_response(data)


async def get_sdtm_variable(
    client: CDISCClient, version: str, domain: str, variable: str
) -> dict[str, Any]:
    """Get the full definition of a specific SDTM variable.

    Args:
        version: SDTM-IG version, e.g. "3.4".
        domain: Two-letter domain code, e.g. "AE".
        variable: Variable name, e.g. "AETERM", "AEDECOD".
    """
    version = validate_version(version)
    domain = domain.upper().strip()
    variable = variable.upper().strip()
    data = await client.get(
        f"/mdr/sdtm/{version}/datasets/{domain}/variables/{variable}"
    )
    return format_response(data)
