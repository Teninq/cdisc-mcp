"""Tests for MCP tool functions."""
from typing import Any
from unittest.mock import AsyncMock, MagicMock

import pytest

from cdisc_mcp.tools.search import list_products, search_cdisc
from cdisc_mcp.tools.sdtm import get_sdtm_domains, get_sdtm_domain_variables, get_sdtm_variable
from cdisc_mcp.tools.terminology import list_ct_packages, get_codelist, get_codelist_terms
from cdisc_mcp.tools.adam import get_adam_datastructures, get_adam_variable
from cdisc_mcp.tools.cdash import get_cdash_domains, get_cdash_domain_fields


@pytest.fixture
def mock_client() -> MagicMock:
    client = MagicMock()
    client.get = AsyncMock()
    return client


class TestListProducts:
    async def test_calls_correct_endpoint(self, mock_client: MagicMock) -> None:
        mock_client.get.return_value = {"products": []}
        await list_products(mock_client)
        mock_client.get.assert_called_once_with("/mdr/products")

    async def test_returns_formatted_response(self, mock_client: MagicMock) -> None:
        mock_client.get.return_value = {
            "_links": {"self": {}},
            "products": [{"name": "SDTM"}],
        }
        result = await list_products(mock_client)
        assert "_links" not in result


class TestSearchCdisc:
    async def test_query_included_in_url(self, mock_client: MagicMock) -> None:
        mock_client.get.return_value = {"results": []}
        await search_cdisc(mock_client, query="adverse")
        call_path = mock_client.get.call_args[0][0]
        assert "adverse" in call_path

    async def test_returns_formatted_response(self, mock_client: MagicMock) -> None:
        mock_client.get.return_value = {"results": [], "_links": {}}
        result = await search_cdisc(mock_client, query="dm")
        assert "_links" not in result

    async def test_query_url_encoded_with_spaces(self, mock_client: MagicMock) -> None:
        mock_client.get.return_value = {"results": []}
        await search_cdisc(mock_client, query="adverse event")
        call_path = mock_client.get.call_args[0][0]
        # urlencode converts space to + or %20
        assert "adverse" in call_path
        assert "event" in call_path
        assert " " not in call_path  # space must be encoded


class TestGetSdtmDomains:
    async def test_version_in_url(self, mock_client: MagicMock) -> None:
        mock_client.get.return_value = {"datasets": []}
        await get_sdtm_domains(mock_client, version="3.4")
        call_path = mock_client.get.call_args[0][0]
        assert "3.4" in call_path

    async def test_returns_formatted_response(self, mock_client: MagicMock) -> None:
        mock_client.get.return_value = {"datasets": [], "_links": {}}
        result = await get_sdtm_domains(mock_client, version="3.4")
        assert "_links" not in result

    async def test_invalid_version_raises_error(self, mock_client: MagicMock) -> None:
        with pytest.raises(ValueError, match="invalid characters"):
            await get_sdtm_domains(mock_client, version="3.4/../admin")


class TestGetSdtmDomainVariables:
    async def test_domain_uppercased(self, mock_client: MagicMock) -> None:
        mock_client.get.return_value = {"variables": []}
        await get_sdtm_domain_variables(mock_client, version="3.4", domain="ae")
        call_path = mock_client.get.call_args[0][0]
        assert "/AE/" in call_path

    async def test_version_and_domain_in_url(self, mock_client: MagicMock) -> None:
        mock_client.get.return_value = {"variables": []}
        await get_sdtm_domain_variables(mock_client, version="3.4", domain="DM")
        call_path = mock_client.get.call_args[0][0]
        assert "3.4" in call_path
        assert "DM" in call_path


class TestGetSdtmVariable:
    async def test_domain_and_variable_uppercased(self, mock_client: MagicMock) -> None:
        mock_client.get.return_value = {}
        await get_sdtm_variable(mock_client, version="3.4", domain="ae", variable="aeterm")
        call_path = mock_client.get.call_args[0][0]
        assert "AE" in call_path
        assert "AETERM" in call_path


class TestTerminology:
    async def test_list_packages_endpoint(self, mock_client: MagicMock) -> None:
        mock_client.get.return_value = {"packages": []}
        await list_ct_packages(mock_client)
        mock_client.get.assert_called_once_with("/mdr/ct/packages")

    async def test_get_codelist_strips_links(self, mock_client: MagicMock, sample_codelist: dict[str, Any]) -> None:
        mock_client.get.return_value = sample_codelist
        result = await get_codelist(mock_client, package_id="sdtmct-2024-03-29", codelist_id="C66781")
        assert "_links" not in result

    async def test_get_codelist_terms_truncates(self, mock_client: MagicMock, sample_codelist: dict[str, Any]) -> None:
        # sample_codelist["terms"] has 150 terms, DEFAULT_MAX_ITEMS=100
        mock_client.get.return_value = sample_codelist["terms"]
        result = await get_codelist_terms(mock_client, package_id="sdtmct-2024-03-29", codelist_id="C66781")
        assert result.get("has_more") is True


class TestAdam:
    async def test_version_in_url(self, mock_client: MagicMock) -> None:
        mock_client.get.return_value = {"dataStructures": []}
        await get_adam_datastructures(mock_client, version="1.3")
        call_path = mock_client.get.call_args[0][0]
        assert "1.3" in call_path

    async def test_variable_uppercased(self, mock_client: MagicMock) -> None:
        mock_client.get.return_value = {}
        await get_adam_variable(mock_client, version="1.3", data_structure="adsl", variable="usubjid")
        call_path = mock_client.get.call_args[0][0]
        assert "ADSL" in call_path
        assert "USUBJID" in call_path


class TestCdash:
    async def test_version_in_url(self, mock_client: MagicMock) -> None:
        mock_client.get.return_value = {"domains": []}
        await get_cdash_domains(mock_client, version="2.0")
        call_path = mock_client.get.call_args[0][0]
        assert "2.0" in call_path

    async def test_domain_uppercased(self, mock_client: MagicMock) -> None:
        mock_client.get.return_value = {"fields": []}
        await get_cdash_domain_fields(mock_client, version="2.0", domain="ae")
        call_path = mock_client.get.call_args[0][0]
        assert "AE" in call_path
