"""MCP tools for SDTM standard queries."""

from __future__ import annotations

from typing import Any

from ..client import CDISCClient
from ..response_formatter import format_response
from ._helpers import hal_items
from ._validators import normalize_version_for_path, validate_version


async def get_sdtm_domains(client: CDISCClient, version: str) -> dict[str, Any]:
    """List all SDTM datasets for a given version.

    Args:
        version: SDTM-IG version, e.g. "3.4" or "3-4".
    """
    version = normalize_version_for_path(validate_version(version))
    data = await client.get(f"/mdr/sdtmig/{version}/datasets")
    return {
        "label": data.get("label"),
        "version": data.get("version"),
        "datasets": hal_items(data, "datasets"),
    }


async def get_sdtm_domain_variables(
    client: CDISCClient, version: str, domain: str
) -> dict[str, Any]:
    """Get all variables defined for an SDTM domain.

    Args:
        version: SDTM-IG version, e.g. "3.4" or "3-4".
        domain: Two-letter domain code, e.g. "DM", "AE", "LB".
    """
    version = normalize_version_for_path(validate_version(version))
    domain = domain.upper().strip()
    data = await client.get(f"/mdr/sdtmig/{version}/datasets/{domain}/variables")
    return {
        "domain": domain,
        "label": data.get("label"),
        "variables": hal_items(data, "datasetVariables"),
    }


async def get_sdtm_variable(
    client: CDISCClient, version: str, domain: str, variable: str
) -> dict[str, Any]:
    """Get the full definition of a specific SDTM variable.

    Args:
        version: SDTM-IG version, e.g. "3.4" or "3-4".
        domain: Two-letter domain code, e.g. "AE".
        variable: Variable name, e.g. "AETERM", "AEDECOD".
    """
    version = normalize_version_for_path(validate_version(version))
    domain = domain.upper().strip()
    variable = variable.upper().strip()
    data = await client.get(
        f"/mdr/sdtmig/{version}/datasets/{domain}/variables/{variable}"
    )
    return format_response(data)
