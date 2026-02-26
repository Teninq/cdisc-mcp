"""
Unit tests for src/cdisc_mcp/tools/sdtm.py

Updated to match current async implementation where tools accept CDISCClient
as first argument. Uses AsyncMock for the async client.get() calls.

Coverage target: 90%+
"""

from unittest.mock import AsyncMock, MagicMock

import pytest

# ---------------------------------------------------------------------------
# Shared mock client setup
# ---------------------------------------------------------------------------

@pytest.fixture()
def mock_client():
    """CDISCClient mock with async get method."""
    client = MagicMock()
    client.get = AsyncMock()
    return client


# ---------------------------------------------------------------------------
# Test: get_sdtm_domains
# ---------------------------------------------------------------------------

class TestGetSdtmDomains:
    """get_sdtm_domains(client, version) fetches domain list for a version."""

    @pytest.mark.asyncio
    async def test_calls_correct_endpoint(self, mock_client):
        from cdisc_mcp.tools.sdtm import get_sdtm_domains

        mock_client.get.return_value = {"datasets": [], "_links": {}}
        await get_sdtm_domains(mock_client, version="3-4")

        mock_client.get.assert_called_once_with("/mdr/sdtm/3-4")

    @pytest.mark.asyncio
    async def test_raises_for_empty_version(self, mock_client):
        from cdisc_mcp.tools.sdtm import get_sdtm_domains

        with pytest.raises(ValueError, match="version"):
            await get_sdtm_domains(mock_client, version="")

    @pytest.mark.asyncio
    async def test_raises_for_path_traversal(self, mock_client):
        from cdisc_mcp.tools.sdtm import get_sdtm_domains

        with pytest.raises(ValueError):
            await get_sdtm_domains(mock_client, version="../../etc/passwd")

    @pytest.mark.asyncio
    async def test_returns_formatted_response(self, mock_client):
        from cdisc_mcp.tools.sdtm import get_sdtm_domains

        mock_client.get.return_value = {
            "_links": {"self": {"href": "/mdr/sdtm/3-4"}},
            "datasets": [{"name": "AE", "label": "Adverse Events"}],
        }
        result = await get_sdtm_domains(mock_client, version="3-4")

        assert "_links" not in result
        assert "datasets" in result


# ---------------------------------------------------------------------------
# Test: get_sdtm_domain_variables
# ---------------------------------------------------------------------------

class TestGetSdtmDomainVariables:
    """get_sdtm_domain_variables(client, version, domain) fetches variables."""

    @pytest.mark.asyncio
    async def test_domain_uppercased_before_call(self, mock_client):
        from cdisc_mcp.tools.sdtm import get_sdtm_domain_variables

        mock_client.get.return_value = {"variables": [], "_links": {}}
        await get_sdtm_domain_variables(mock_client, version="3-4", domain="ae")

        call_args = mock_client.get.call_args[0][0]
        assert "/AE/" in call_args

    @pytest.mark.asyncio
    async def test_version_and_domain_in_url(self, mock_client):
        from cdisc_mcp.tools.sdtm import get_sdtm_domain_variables

        mock_client.get.return_value = {"variables": [], "_links": {}}
        await get_sdtm_domain_variables(mock_client, version="3-4", domain="DM")

        mock_client.get.assert_called_once_with("/mdr/sdtm/3-4/datasets/DM/variables")

    @pytest.mark.asyncio
    async def test_returns_formatted_response(self, mock_client):
        from cdisc_mcp.tools.sdtm import get_sdtm_domain_variables

        mock_client.get.return_value = {
            "_links": {"self": {"href": "/mdr/sdtm/3-4/datasets/DM/variables"}},
            "variables": [
                {"name": "STUDYID", "label": "Study Identifier", "ordinal": 1}
            ],
        }
        result = await get_sdtm_domain_variables(mock_client, version="3-4", domain="DM")

        assert "_links" not in result


# ---------------------------------------------------------------------------
# Test: get_sdtm_variable
# ---------------------------------------------------------------------------

class TestGetSdtmVariable:
    """get_sdtm_variable(client, version, domain, variable) fetches a variable."""

    @pytest.mark.asyncio
    async def test_domain_and_variable_uppercased(self, mock_client):
        from cdisc_mcp.tools.sdtm import get_sdtm_variable

        mock_client.get.return_value = {"name": "AETERM", "_links": {}}
        await get_sdtm_variable(mock_client, version="3-4", domain="ae", variable="aeterm")

        call_args = mock_client.get.call_args[0][0]
        assert "/AE/" in call_args
        assert "/AETERM" in call_args

    @pytest.mark.asyncio
    async def test_correct_endpoint_constructed(self, mock_client):
        from cdisc_mcp.tools.sdtm import get_sdtm_variable

        mock_client.get.return_value = {"name": "AETERM", "_links": {}}
        await get_sdtm_variable(mock_client, version="3-4", domain="AE", variable="AETERM")

        mock_client.get.assert_called_once_with(
            "/mdr/sdtm/3-4/datasets/AE/variables/AETERM"
        )
