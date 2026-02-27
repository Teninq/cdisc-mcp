"""Tests for MCP tool functions."""
from typing import Any
from unittest.mock import AsyncMock, MagicMock

import pytest

from cdisc_mcp.tools.adam import get_adam_datastructures, get_adam_variable
from cdisc_mcp.tools.cdash import get_cdash_domain_fields, get_cdash_domains
from cdisc_mcp.tools.sdtm import (
    get_sdtm_domain_variables,
    get_sdtm_domains,
    get_sdtm_variable,
)
from cdisc_mcp.tools.search import list_products
from cdisc_mcp.tools.terminology import (
    get_codelist,
    get_codelist_terms,
    list_ct_packages,
)


@pytest.fixture
def mock_client() -> MagicMock:
    client = MagicMock()
    client.get = AsyncMock()
    return client


class TestListProducts:
    async def test_calls_correct_endpoint(self, mock_client: MagicMock) -> None:
        mock_client.get.return_value = {"_links": {}}
        await list_products(mock_client)
        mock_client.get.assert_called_once_with("/mdr/products")

    async def test_returns_dict(self, mock_client: MagicMock) -> None:
        mock_client.get.return_value = {"_links": {}}
        result = await list_products(mock_client)
        assert isinstance(result, dict)

    async def test_links_not_in_result(self, mock_client: MagicMock) -> None:
        mock_client.get.return_value = {"_links": {"self": {"href": "/mdr/products"}}}
        result = await list_products(mock_client)
        assert "_links" not in result


class TestGetSdtmDomains:
    async def test_version_in_url(self, mock_client: MagicMock) -> None:
        mock_client.get.return_value = {"_links": {"datasets": []}}
        await get_sdtm_domains(mock_client, version="3-4")
        call_path = mock_client.get.call_args[0][0]
        assert "3-4" in call_path

    async def test_uses_sdtmig_endpoint(self, mock_client: MagicMock) -> None:
        mock_client.get.return_value = {"_links": {"datasets": []}}
        await get_sdtm_domains(mock_client, version="3-4")
        call_path = mock_client.get.call_args[0][0]
        assert "sdtmig" in call_path

    async def test_returns_dict_with_datasets_key(self, mock_client: MagicMock) -> None:
        mock_client.get.return_value = {
            "_links": {"datasets": [{"href": "/mdr/sdtmig/3-4/datasets/AE", "title": "Adverse Events", "type": "SDTM Dataset"}]},
            "label": "SDTMIG 3.4",
            "version": "3-4",
        }
        result = await get_sdtm_domains(mock_client, version="3-4")
        assert "datasets" in result

    async def test_invalid_version_raises_error(self, mock_client: MagicMock) -> None:
        with pytest.raises(ValueError, match="invalid characters"):
            await get_sdtm_domains(mock_client, version="3.4/../admin")


class TestGetSdtmDomainVariables:
    async def test_domain_uppercased(self, mock_client: MagicMock) -> None:
        mock_client.get.return_value = {"_links": {"datasetVariables": []}}
        await get_sdtm_domain_variables(mock_client, version="3-4", domain="ae")
        call_path = mock_client.get.call_args[0][0]
        assert "/AE/" in call_path

    async def test_version_and_domain_in_url(self, mock_client: MagicMock) -> None:
        mock_client.get.return_value = {"_links": {"datasetVariables": []}}
        await get_sdtm_domain_variables(mock_client, version="3-4", domain="DM")
        call_path = mock_client.get.call_args[0][0]
        assert "3-4" in call_path
        assert "DM" in call_path

    async def test_uses_sdtmig_and_datasets_path(self, mock_client: MagicMock) -> None:
        mock_client.get.return_value = {"_links": {"datasetVariables": []}}
        await get_sdtm_domain_variables(mock_client, version="3-4", domain="AE")
        call_path = mock_client.get.call_args[0][0]
        assert "/mdr/sdtmig/3-4/datasets/AE/variables" == call_path


class TestGetSdtmVariable:
    async def test_domain_and_variable_uppercased(self, mock_client: MagicMock) -> None:
        mock_client.get.return_value = {"name": "AETERM"}
        await get_sdtm_variable(mock_client, version="3-4", domain="ae", variable="aeterm")
        call_path = mock_client.get.call_args[0][0]
        assert "AE" in call_path
        assert "AETERM" in call_path

    async def test_correct_endpoint_constructed(self, mock_client: MagicMock) -> None:
        mock_client.get.return_value = {"name": "AETERM"}
        await get_sdtm_variable(mock_client, version="3-4", domain="AE", variable="AETERM")
        mock_client.get.assert_called_once_with(
            "/mdr/sdtmig/3-4/datasets/AE/variables/AETERM"
        )


class TestTerminology:
    async def test_list_packages_endpoint(self, mock_client: MagicMock) -> None:
        mock_client.get.return_value = {"_links": {"packages": []}}
        await list_ct_packages(mock_client)
        mock_client.get.assert_called_once_with("/mdr/ct/packages")

    async def test_list_packages_returns_count(self, mock_client: MagicMock) -> None:
        mock_client.get.return_value = {
            "_links": {
                "packages": [
                    {"href": "/mdr/ct/packages/sdtmct-2024-09-27", "title": "SDTM CT", "type": "Terminology"}
                ]
            }
        }
        result = await list_ct_packages(mock_client)
        assert result["count"] == 1

    async def test_get_codelist_strips_links(self, mock_client: MagicMock, sample_codelist: dict[str, Any]) -> None:
        mock_client.get.return_value = sample_codelist
        result = await get_codelist(mock_client, package_id="sdtmct-2024-03-29", codelist_id="C66781")
        assert "_links" not in result

    async def test_get_codelist_terms_returns_terms_key(self, mock_client: MagicMock) -> None:
        mock_client.get.return_value = {
            "_links": {
                "terms": [
                    {"href": "/mdr/ct/packages/sdtmct-2024-09-27/codelists/C66781/terms/C25301", "title": "Day", "type": "Code List Value"}
                ]
            }
        }
        result = await get_codelist_terms(mock_client, package_id="sdtmct-2024-09-27", codelist_id="C66781")
        assert "terms" in result
        assert result["count"] == 1


class TestAdam:
    async def test_version_in_url(self, mock_client: MagicMock) -> None:
        mock_client.get.return_value = {"_links": {"dataStructures": []}}
        await get_adam_datastructures(mock_client, version="1-3")
        call_path = mock_client.get.call_args[0][0]
        assert "1-3" in call_path

    async def test_uses_adamig_endpoint(self, mock_client: MagicMock) -> None:
        mock_client.get.return_value = {"_links": {"dataStructures": []}}
        await get_adam_datastructures(mock_client, version="1-3")
        call_path = mock_client.get.call_args[0][0]
        assert "adamig-1-3" in call_path

    async def test_variable_uppercased(self, mock_client: MagicMock) -> None:
        mock_client.get.return_value = {"name": "USUBJID"}
        await get_adam_variable(mock_client, version="1-3", data_structure="adsl", variable="usubjid")
        call_path = mock_client.get.call_args[0][0]
        assert "ADSL" in call_path
        assert "USUBJID" in call_path

    async def test_correct_endpoint_constructed(self, mock_client: MagicMock) -> None:
        mock_client.get.return_value = {"name": "USUBJID"}
        await get_adam_variable(mock_client, version="1-3", data_structure="ADSL", variable="USUBJID")
        mock_client.get.assert_called_once_with(
            "/mdr/adam/adamig-1-3/datastructures/ADSL/variables/USUBJID"
        )


class TestCdash:
    async def test_version_in_url(self, mock_client: MagicMock) -> None:
        mock_client.get.return_value = {"_links": {"domains": []}}
        await get_cdash_domains(mock_client, version="2-0")
        call_path = mock_client.get.call_args[0][0]
        assert "2-0" in call_path

    async def test_uses_cdashig_endpoint(self, mock_client: MagicMock) -> None:
        mock_client.get.return_value = {"_links": {"domains": []}}
        await get_cdash_domains(mock_client, version="2-0")
        call_path = mock_client.get.call_args[0][0]
        assert "cdashig" in call_path

    async def test_domain_uppercased(self, mock_client: MagicMock) -> None:
        mock_client.get.return_value = {"_links": {"fields": []}}
        await get_cdash_domain_fields(mock_client, version="2-0", domain="ae")
        call_path = mock_client.get.call_args[0][0]
        assert "AE" in call_path

    async def test_correct_fields_endpoint(self, mock_client: MagicMock) -> None:
        mock_client.get.return_value = {"_links": {"fields": []}}
        await get_cdash_domain_fields(mock_client, version="2-0", domain="AE")
        mock_client.get.assert_called_once_with(
            "/mdr/cdashig/2-0/domains/AE/fields"
        )
