"""Shared pytest fixtures for CDISC MCP tests."""

import pytest


FAKE_API_KEY = "test-api-key-12345"
BASE_URL = "https://library.cdisc.org/api/cosmos/v2"


@pytest.fixture
def api_key() -> str:
    return FAKE_API_KEY


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
def sample_codelist() -> dict:
    """Sample codelist with 150 terms to test truncation."""
    return {
        "conceptId": "C66781",
        "name": "AGEU",
        "submissionValue": "AGEU",
        "_links": {"self": {"href": "/..."}},
        "terms": [{"conceptId": f"C{i}", "submissionValue": f"TERM{i}"} for i in range(150)],
    }
