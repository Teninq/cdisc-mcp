"""MCP tools for ADaM standard queries."""

from __future__ import annotations

from typing import Any

from ..client import CDISCClient
from ..response_formatter import format_response
from ._validators import validate_version


async def get_adam_datastructures(client: CDISCClient, version: str) -> dict[str, Any]:
    """List all ADaM data structures for a given version.

    Args:
        version: ADaM version, e.g. "1.3", "2.1".
    """
    version = validate_version(version)
    data = await client.get(f"/mdr/adam/{version}")
    return format_response(data)


async def get_adam_variable(
    client: CDISCClient, version: str, data_structure: str, variable: str
) -> dict[str, Any]:
    """Get the definition of a specific ADaM variable.

    Args:
        version: ADaM version, e.g. "1.3".
        data_structure: Data structure name, e.g. "ADSL", "ADAE".
        variable: Variable name, e.g. "USUBJID", "AVAL".
    """
    version = validate_version(version)
    data_structure = data_structure.upper().strip()
    variable = variable.upper().strip()
    data = await client.get(
        f"/mdr/adam/{version}/{data_structure}/variables/{variable}"
    )
    return format_response(data)
