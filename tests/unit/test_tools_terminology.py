"""
Unit tests for src/cdisc_mcp/tools/terminology.py

Updated to match current async implementation where tools accept CDISCClient
as first argument. Uses AsyncMock for the async client.get() calls.

Coverage target: 90%+
"""

from unittest.mock import AsyncMock, MagicMock

import pytest


@pytest.fixture()
def mock_client():
    """CDISCClient mock with async get method."""
    client = MagicMock()
    client.get = AsyncMock()
    return client


# ---------------------------------------------------------------------------
# Test: list_ct_packages
# ---------------------------------------------------------------------------

class TestListCtPackages:

    @pytest.mark.asyncio
    async def test_returns_formatted_response(self, mock_client, sample_ct_package_list):
        from cdisc_mcp.tools.terminology import list_ct_packages

        mock_client.get.return_value = sample_ct_package_list
        result = await list_ct_packages(mock_client)

        assert isinstance(result, dict)

    @pytest.mark.asyncio
    async def test_calls_correct_endpoint(self, mock_client, sample_ct_package_list):
        from cdisc_mcp.tools.terminology import list_ct_packages

        mock_client.get.return_value = sample_ct_package_list
        await list_ct_packages(mock_client)

        mock_client.get.assert_called_once_with("/mdr/ct/packages")

    @pytest.mark.asyncio
    async def test_links_stripped(self, mock_client, sample_ct_package_list):
        from cdisc_mcp.tools.terminology import list_ct_packages

        mock_client.get.return_value = sample_ct_package_list
        result = await list_ct_packages(mock_client)

        assert "_links" not in result


# ---------------------------------------------------------------------------
# Test: get_codelist
# ---------------------------------------------------------------------------

class TestGetCodelist:

    @pytest.mark.asyncio
    async def test_calls_correct_endpoint(self, mock_client, sample_codelist):
        from cdisc_mcp.tools.terminology import get_codelist

        mock_client.get.return_value = sample_codelist
        await get_codelist(mock_client, package_id="sdtmct-2024-03-29", codelist_id="C66741")

        mock_client.get.assert_called_once_with(
            "/mdr/ct/packages/sdtmct-2024-03-29/codelists/C66741"
        )

    @pytest.mark.asyncio
    async def test_returns_formatted_response(self, mock_client, sample_codelist):
        from cdisc_mcp.tools.terminology import get_codelist

        mock_client.get.return_value = sample_codelist
        result = await get_codelist(mock_client, package_id="sdtmct-2024-03-29", codelist_id="C66741")

        # _links should be stripped
        assert "_links" not in result
        # conceptId should be present
        assert result["conceptId"] == "C66741"

    @pytest.mark.asyncio
    async def test_terms_list_present(self, mock_client, sample_codelist):
        from cdisc_mcp.tools.terminology import get_codelist

        mock_client.get.return_value = sample_codelist
        result = await get_codelist(mock_client, package_id="sdtmct-2024-03-29", codelist_id="C66741")

        assert "terms" in result


# ---------------------------------------------------------------------------
# Test: get_codelist_terms
# ---------------------------------------------------------------------------

class TestGetCodelistTerms:

    @pytest.mark.asyncio
    async def test_calls_correct_endpoint(self, mock_client, sample_codelist):
        from cdisc_mcp.tools.terminology import get_codelist_terms

        mock_client.get.return_value = sample_codelist
        await get_codelist_terms(mock_client, package_id="sdtmct-2024-03-29", codelist_id="C66741")

        mock_client.get.assert_called_once_with(
            "/mdr/ct/packages/sdtmct-2024-03-29/codelists/C66741/terms"
        )

    @pytest.mark.asyncio
    async def test_returns_formatted_response(self, mock_client, sample_codelist):
        from cdisc_mcp.tools.terminology import get_codelist_terms

        mock_client.get.return_value = {"terms": [{"conceptId": "C1", "submissionValue": "VAL1"}]}
        result = await get_codelist_terms(mock_client, package_id="pkg", codelist_id="C1")

        assert isinstance(result, dict)
