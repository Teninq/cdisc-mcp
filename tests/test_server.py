# -*- coding: utf-8 -*-
"""Unit tests for src/cdisc_mcp/server.py

Tests the server factory function create_server() and verifies that all
12 MCP tools are properly registered. Uses AsyncMock for CDISCClient.
"""

from unittest.mock import AsyncMock, MagicMock
import pytest


@pytest.fixture()
def mock_client():
    """CDISCClient mock with async get method."""
    client = MagicMock()
    client.get = AsyncMock()
    return client


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

    def test_all_12_tools_registered(self, mock_client):
        from cdisc_mcp.server import create_server

        server = create_server(mock_client)

        expected_tools = {
            "list_products",
            "search_cdisc",
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

        # FastMCP stores tools in a dict keyed by tool name
        registered = set(server._tool_manager._tools.keys())
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

        tools = server._tool_manager._tools
        result = await tools["list_products"].fn()

        mock_client.get.assert_called_once_with("/mdr/products")

    @pytest.mark.asyncio
    async def test_search_cdisc_passes_query(self, mock_client):
        from cdisc_mcp.server import create_server

        mock_client.get.return_value = {"_links": {}, "results": []}
        server = create_server(mock_client)

        tools = server._tool_manager._tools
        await tools["search_cdisc"].fn(query="adverse event")

        call_url = mock_client.get.call_args[0][0]
        assert "adverse+event" in call_url or "adverse%20event" in call_url

    @pytest.mark.asyncio
    async def test_get_sdtm_domains_passes_version(self, mock_client):
        from cdisc_mcp.server import create_server

        mock_client.get.return_value = {"_links": {}, "datasets": []}
        server = create_server(mock_client)

        tools = server._tool_manager._tools
        await tools["get_sdtm_domains"].fn(version="3-4")

        mock_client.get.assert_called_once_with("/mdr/sdtm/3-4")

    @pytest.mark.asyncio
    async def test_list_ct_packages_delegates_to_terminology(self, mock_client):
        from cdisc_mcp.server import create_server

        mock_client.get.return_value = {"_links": {}, "packages": []}
        server = create_server(mock_client)

        tools = server._tool_manager._tools
        await tools["list_ct_packages"].fn()

        mock_client.get.assert_called_once_with("/mdr/ct/packages")
