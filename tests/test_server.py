"""Unit tests for src/cdisc_mcp/server.py

Tests the server factory function create_server() and verifies that all
11 MCP tools are properly registered. Uses AsyncMock for CDISCClient.
"""

from unittest.mock import AsyncMock, MagicMock

import pytest


@pytest.fixture()
def mock_client():
    """CDISCClient mock with async get method."""
    client = MagicMock()
    client.get = AsyncMock()
    return client


async def _get_registered_tool_names(server) -> set[str]:
    if hasattr(server, "get_tools"):
        tools = await server.get_tools()
        return set(tools.keys())

    if hasattr(server, "_mcp_list_tools"):
        tools = await server._mcp_list_tools()
        return {tool.name for tool in tools}

    if hasattr(server, "_list_tools"):
        tools = await server._list_tools()
        return {tool.name for tool in tools}

    raise AttributeError("FastMCP tool-list API not found")


async def _invoke_tool(server, tool_name: str, **kwargs):
    if hasattr(server, "_mcp_call_tool"):
        _, result = await server._mcp_call_tool(tool_name, kwargs)
        return result

    if hasattr(server, "get_tools"):
        tools = await server.get_tools()
        return await tools[tool_name].fn(**kwargs)

    if hasattr(server, "_tool_manager"):
        tools = server._tool_manager._tools
        return await tools[tool_name].fn(**kwargs)

    if hasattr(server, "_list_tools"):
        tools = {tool.name: tool for tool in await server._list_tools()}
        return await tools[tool_name].fn(**kwargs)

    raise AttributeError("FastMCP tool-call API not found")


class TestCreateServer:
    """create_server() returns a configured FastMCP instance."""

    def test_returns_fastmcp_instance(self, mock_client):
        from fastmcp import FastMCP

        from cdisc_mcp.server import create_server

        server = create_server(mock_client)

        assert isinstance(server, FastMCP)

    def test_server_name_is_cdisc_mcp(self, mock_client):
        from cdisc_mcp.server import create_server

        server = create_server(mock_client)

        assert server.name == "cdisc-mcp"

    @pytest.mark.asyncio
    async def test_all_11_tools_registered(self, mock_client):
        from cdisc_mcp.server import create_server

        server = create_server(mock_client)

        expected_tools = {
            "list_products",
            "get_sdtm_domains",
            "get_sdtm_domain_variables",
            "get_sdtm_variable",
            "get_adam_datastructures",
            "get_adam_variable",
            "get_cdash_domains",
            "get_cdash_domain_fields",
            "list_ct_packages",
            "get_codelist",
            "get_codelist_terms",
        }

        registered = await _get_registered_tool_names(server)
        assert expected_tools == registered

    def test_create_server_twice_gives_independent_instances(self, mock_client):
        from cdisc_mcp.server import create_server

        server1 = create_server(mock_client)
        server2 = create_server(mock_client)

        assert server1 is not server2


class TestServerToolCallsClient:
    """Registered tools delegate to the correct client calls."""

    @pytest.mark.asyncio
    async def test_list_products_delegates_to_search(self, mock_client):
        from cdisc_mcp.server import create_server

        mock_client.get.return_value = {"_links": {}, "products": []}
        server = create_server(mock_client)

        await _invoke_tool(server, "list_products")

        mock_client.get.assert_called_once_with("/mdr/products")

    @pytest.mark.asyncio
    async def test_get_sdtm_domains_passes_version(self, mock_client):
        from cdisc_mcp.server import create_server

        mock_client.get.return_value = {"_links": {}, "datasets": []}
        server = create_server(mock_client)

        await _invoke_tool(server, "get_sdtm_domains", version="3-4")

        mock_client.get.assert_called_once_with("/mdr/sdtmig/3-4/datasets")

    @pytest.mark.asyncio
    async def test_list_ct_packages_delegates_to_terminology(self, mock_client):
        from cdisc_mcp.server import create_server

        mock_client.get.return_value = {"_links": {}, "packages": []}
        server = create_server(mock_client)

        await _invoke_tool(server, "list_ct_packages")

        mock_client.get.assert_called_once_with("/mdr/ct/packages")

    @pytest.mark.asyncio
    async def test_get_sdtm_domain_variables_passes_version_and_domain(self, mock_client):
        from cdisc_mcp.server import create_server

        mock_client.get.return_value = {"_links": {}, "variables": []}
        server = create_server(mock_client)

        await _invoke_tool(server, "get_sdtm_domain_variables", version="3-4", domain="AE")

        mock_client.get.assert_called_once_with(
            "/mdr/sdtmig/3-4/datasets/AE/variables"
        )

    @pytest.mark.asyncio
    async def test_get_sdtm_variable_passes_all_args(self, mock_client):
        from cdisc_mcp.server import create_server

        mock_client.get.return_value = {"_links": {}, "name": "AETERM"}
        server = create_server(mock_client)

        await _invoke_tool(server, "get_sdtm_variable", version="3-4", domain="AE", variable="AETERM")

        mock_client.get.assert_called_once_with(
            "/mdr/sdtmig/3-4/datasets/AE/variables/AETERM"
        )

    @pytest.mark.asyncio
    async def test_get_adam_datastructures_passes_version(self, mock_client):
        from cdisc_mcp.server import create_server

        mock_client.get.return_value = {"_links": {}, "dataStructures": []}
        server = create_server(mock_client)

        await _invoke_tool(server, "get_adam_datastructures", version="1-3")

        mock_client.get.assert_called_once_with("/mdr/adam/adamig-1-3/datastructures")

    @pytest.mark.asyncio
    async def test_get_adam_variable_passes_all_args(self, mock_client):
        from cdisc_mcp.server import create_server

        mock_client.get.return_value = {"_links": {}, "name": "USUBJID"}
        server = create_server(mock_client)

        await _invoke_tool(
            server,
            "get_adam_variable",
            version="1-3",
            data_structure="ADSL",
            variable="USUBJID",
        )

        mock_client.get.assert_called_once_with(
            "/mdr/adam/adamig-1-3/datastructures/ADSL/variables/USUBJID"
        )

    @pytest.mark.asyncio
    async def test_get_cdash_domains_passes_version(self, mock_client):
        from cdisc_mcp.server import create_server

        mock_client.get.return_value = {"_links": {}, "domains": []}
        server = create_server(mock_client)

        await _invoke_tool(server, "get_cdash_domains", version="2-0")

        mock_client.get.assert_called_once_with("/mdr/cdashig/2-0/domains")

    @pytest.mark.asyncio
    async def test_get_cdash_domain_fields_passes_version_and_domain(self, mock_client):
        from cdisc_mcp.server import create_server

        mock_client.get.return_value = {"_links": {}, "fields": []}
        server = create_server(mock_client)

        await _invoke_tool(server, "get_cdash_domain_fields", version="2-0", domain="DM")

        mock_client.get.assert_called_once_with(
            "/mdr/cdashig/2-0/domains/DM/fields"
        )

    @pytest.mark.asyncio
    async def test_get_codelist_passes_package_and_codelist_id(self, mock_client):
        from cdisc_mcp.server import create_server

        mock_client.get.return_value = {"_links": {}, "conceptId": "C66781"}
        server = create_server(mock_client)

        await _invoke_tool(
            server,
            "get_codelist",
            package_id="sdtmct-2024-03-29",
            codelist_id="C66781",
        )

        mock_client.get.assert_called_once_with(
            "/mdr/ct/packages/sdtmct-2024-03-29/codelists/C66781"
        )

    @pytest.mark.asyncio
    async def test_get_codelist_terms_passes_package_and_codelist_id(self, mock_client):
        from cdisc_mcp.server import create_server

        mock_client.get.return_value = {"_links": {}, "terms": []}
        server = create_server(mock_client)

        await _invoke_tool(
            server,
            "get_codelist_terms",
            package_id="sdtmct-2024-03-29",
            codelist_id="C66781",
        )

        mock_client.get.assert_called_once_with(
            "/mdr/ct/packages/sdtmct-2024-03-29/codelists/C66781/terms"
        )


class TestAsyncMain:
    """_async_main and main() entry-point functions."""

    @pytest.mark.asyncio
    async def test_async_main_creates_server_and_runs(self):
        from unittest.mock import AsyncMock, MagicMock, patch

        mock_config = MagicMock()
        mock_client = MagicMock()
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)
        mock_client.get = AsyncMock()

        mock_mcp = MagicMock()
        mock_mcp.run_async = AsyncMock(return_value=None)

        with (
            patch("cdisc_mcp.server.load_config", return_value=mock_config),
            patch("cdisc_mcp.server.CDISCClient", return_value=mock_client),
            patch("cdisc_mcp.server.create_server", return_value=mock_mcp),
        ):
            from cdisc_mcp.server import _async_main

            await _async_main()

        mock_mcp.run_async.assert_called_once()

    def test_main_calls_asyncio_run(self):
        from unittest.mock import patch

        with patch("cdisc_mcp.server.asyncio.run") as mock_run:
            from cdisc_mcp.server import main

            main()

        mock_run.assert_called_once()
