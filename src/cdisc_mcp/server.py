"""FastMCP server entry point for the CDISC Library MCP service.

All MCP tools are registered here with dependency injection of the
CDISCClient, ensuring tools are testable without a running server.
"""

from __future__ import annotations

import asyncio
import logging
from typing import Any

from fastmcp import FastMCP

from .client import CDISCClient
from .config import load_config
from .tools import adam, cdash, sdtm, search, terminology

logger = logging.getLogger(__name__)


def create_server(client: CDISCClient) -> FastMCP:
    """Create and configure the FastMCP server with all CDISC tools.

    Args:
        client: An already-initialised CDISCClient whose lifecycle is
                managed by the caller (e.g. via ``async with``).

    Returns:
        Configured FastMCP server instance ready to run.
    """
    mcp = FastMCP("cdisc-mcp")

    @mcp.tool()
    async def list_products() -> dict[str, Any]:
        """List all available CDISC standards and their published versions.
        Use this first to discover available versions before querying specific content.
        """
        return await search.list_products(client)

    @mcp.tool()
    async def get_sdtm_domains(version: str) -> dict[str, Any]:
        """List all SDTM domains for a given version.

        Args:
            version: SDTM-IG version, e.g. "3.4", "3.3". Use list_products() first.
        """
        return await sdtm.get_sdtm_domains(client, version)

    @mcp.tool()
    async def get_sdtm_domain_variables(version: str, domain: str) -> dict[str, Any]:
        """Get all variables defined in an SDTM domain.

        Args:
            version: SDTM-IG version, e.g. "3.4"
            domain: Two-letter domain code, e.g. "DM", "AE", "LB"
        """
        return await sdtm.get_sdtm_domain_variables(client, version, domain)

    @mcp.tool()
    async def get_sdtm_variable(version: str, domain: str, variable: str) -> dict[str, Any]:
        """Get the full definition of a specific SDTM variable.

        Args:
            version: SDTM-IG version, e.g. "3.4"
            domain: Domain code, e.g. "AE"
            variable: Variable name, e.g. "AETERM", "AEDECOD"
        """
        return await sdtm.get_sdtm_variable(client, version, domain, variable)

    @mcp.tool()
    async def get_adam_datastructures(version: str) -> dict[str, Any]:
        """List all ADaM data structures for a given version.

        Args:
            version: ADaM version, e.g. "1.3", "2.1"
        """
        return await adam.get_adam_datastructures(client, version)

    @mcp.tool()
    async def get_adam_variable(version: str, data_structure: str, variable: str) -> dict[str, Any]:
        """Get the definition of a specific ADaM variable.

        Args:
            version: ADaM version, e.g. "1.3"
            data_structure: Data structure name, e.g. "ADSL", "ADAE"
            variable: Variable name, e.g. "USUBJID", "AVAL"
        """
        return await adam.get_adam_variable(client, version, data_structure, variable)

    @mcp.tool()
    async def get_cdash_domains(version: str) -> dict[str, Any]:
        """List all CDASH domains for a given version.

        Args:
            version: CDASH version, e.g. "2.0", "1.1"
        """
        return await cdash.get_cdash_domains(client, version)

    @mcp.tool()
    async def get_cdash_domain_fields(version: str, domain: str) -> dict[str, Any]:
        """Get all data collection fields for a CDASH domain.

        Args:
            version: CDASH version, e.g. "2.0"
            domain: Domain code, e.g. "DM", "AE", "VS"
        """
        return await cdash.get_cdash_domain_fields(client, version, domain)

    @mcp.tool()
    async def list_ct_packages() -> dict[str, Any]:
        """List all available CDISC Controlled Terminology packages with release dates."""
        return await terminology.list_ct_packages(client)

    @mcp.tool()
    async def get_codelist(package_id: str, codelist_id: str) -> dict[str, Any]:
        """Get a specific Controlled Terminology codelist definition.

        Args:
            package_id: CT package identifier, e.g. "sdtmct-2024-03-29"
            codelist_id: Codelist concept ID or submission value, e.g. "C66781", "AGEU"
        """
        return await terminology.get_codelist(client, package_id, codelist_id)

    @mcp.tool()
    async def get_codelist_terms(package_id: str, codelist_id: str) -> dict[str, Any]:
        """List all valid terms in a CT codelist (max 100 shown, check has_more).

        Args:
            package_id: CT package identifier
            codelist_id: Codelist concept ID or submission value
        """
        return await terminology.get_codelist_terms(client, package_id, codelist_id)

    return mcp


async def _async_main() -> None:
    """Async entry point that manages CDISCClient lifecycle via async context manager."""
    config = load_config()
    async with CDISCClient(config) as client:
        mcp = create_server(client)
        await mcp.run_async()


def main() -> None:
    """Entry point for cdisc-mcp command."""
    logging.basicConfig(level=logging.INFO)
    asyncio.run(_async_main())


if __name__ == "__main__":
    main()
