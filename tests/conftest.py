"""Shared pytest fixtures for CDISC MCP tests."""

import pytest


FAKE_API_KEY = "test-api-key-12345"
BASE_URL = "https://library.cdisc.org/api/cosmos/v2"


@pytest.fixture
def api_key() -> str:
    return FAKE_API_KEY


@pytest.fixture
def base_url() -> str:
    return BASE_URL


@pytest.fixture
def mock_env(monkeypatch: pytest.MonkeyPatch, api_key: str) -> None:
    monkeypatch.setenv("CDISC_API_KEY", api_key)


@pytest.fixture
def missing_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("CDISC_API_KEY", raising=False)


@pytest.fixture
def sample_sdtm_datasets() -> dict:
    """Sample SDTM dataset list response."""
    return {
        "datasets": [
            {"name": "DM", "label": "Demographics", "_links": {"self": {"href": "/..."}}},
            {"name": "AE", "label": "Adverse Events", "_links": {"self": {"href": "/..."}}},
            {"name": "LB", "label": "Laboratory", "_links": {"self": {"href": "/..."}}},
        ]
    }


@pytest.fixture
def sample_sdtm_dataset() -> dict:
    """Sample SDTM dataset response with 20 variables, _links, and ordinal."""
    return {
        "_links": {"self": {"href": "/mdr/sdtm/3-4/datasets/AE"}},
        "name": "AE",
        "label": "Adverse Events",
        "ordinal": 1,
        "variables": [
            {
                "_links": {"self": {"href": f"/mdr/sdtm/3-4/datasets/AE/variables/VAR{i:02d}"}},
                "name": f"VAR{i:02d}",
                "label": f"Variable {i}",
                "ordinal": i,
            }
            for i in range(20)
        ],
    }


@pytest.fixture
def sample_sdtm_version_list() -> dict:
    """Sample SDTM version list response."""
    return {
        "_links": {"self": {"href": "/mdr/sdtm"}},
        "versions": [
            {"href": "/mdr/sdtm/3-4", "title": "3-4"},
            {"href": "/mdr/sdtm/3-3", "title": "3-3"},
        ],
    }


@pytest.fixture
def sample_codelist() -> dict:
    """Sample codelist with terms to test truncation."""
    return {
        "conceptId": "C66741",
        "name": "EPOCH",
        "submissionValue": "EPOCH",
        "_links": {"self": {"href": "/mdr/ct/packages/sdtmct-2024-03-29/codelists/C66741"}},
        "terms": [
            {"conceptId": f"C{i}", "submissionValue": f"VAL{i:03d}", "preferredTerm": f"Term {i}"}
            for i in range(150)
        ],
    }


@pytest.fixture
def sample_ct_package_list() -> dict:
    """Sample CT package list response."""
    return {
        "_links": {"self": {"href": "/mdr/ct/packages"}},
        "packages": [
            {
                "href": "/mdr/ct/packages/sdtmct-2024-03-29",
                "title": "sdtmct-2024-03-29",
                "label": "SDTM CT 2024-03-29",
            },
            {
                "href": "/mdr/ct/packages/adamct-2024-03-29",
                "title": "adamct-2024-03-29",
                "label": "ADaM CT 2024-03-29",
            },
        ],
    }
