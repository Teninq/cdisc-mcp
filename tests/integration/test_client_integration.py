"""
Integration tests for CDISCClient + response_formatter pipeline.

Updated to match current async CDISCClient implementation.
Wires the real client and real formatter together, with HTTP intercepted
by pytest-httpx.
"""

import pytest

BASE_URL = "https://library.cdisc.org/api/cosmos/v2"


@pytest.fixture(autouse=True)
def _env(mock_env):
    pass


@pytest.fixture()
def config():
    from cdisc_mcp.config import load_config
    return load_config()


@pytest.fixture()
def client(config):
    from cdisc_mcp.client import CDISCClient
    return CDISCClient(config)


# ---------------------------------------------------------------------------
# Full pipeline: client.get → format_response
# ---------------------------------------------------------------------------

class TestClientFormatterPipeline:

    @pytest.mark.asyncio
    async def test_pipeline_removes_links(self, client, httpx_mock, sample_sdtm_dataset):
        from cdisc_mcp.response_formatter import format_response

        httpx_mock.add_response(
            url=f"{BASE_URL}/mdr/sdtm/3-4/datasets/AE",
            json=sample_sdtm_dataset,
        )

        raw = await client.get("/mdr/sdtm/3-4/datasets/AE")
        formatted = format_response(raw)

        assert "_links" not in formatted

    @pytest.mark.asyncio
    async def test_pipeline_truncates_variables_with_small_limit(
        self, client, httpx_mock, sample_sdtm_dataset
    ):
        from cdisc_mcp.response_formatter import format_response

        httpx_mock.add_response(
            url=f"{BASE_URL}/mdr/sdtm/3-4/datasets/AE",
            json=sample_sdtm_dataset,
        )

        raw = await client.get("/mdr/sdtm/3-4/datasets/AE")
        # Pass max_items=5 to force truncation of the 20-variable fixture
        formatted = format_response(raw, max_items=5)

        # 20 variables → truncated to 5 (4 real + 1 sentinel notice)
        assert len(formatted["variables"]) == 5

    @pytest.mark.asyncio
    async def test_pipeline_preserves_essential_fields(
        self, client, httpx_mock, sample_sdtm_dataset
    ):
        from cdisc_mcp.response_formatter import format_response

        httpx_mock.add_response(
            url=f"{BASE_URL}/mdr/sdtm/3-4/datasets/AE",
            json=sample_sdtm_dataset,
        )

        raw = await client.get("/mdr/sdtm/3-4/datasets/AE")
        formatted = format_response(raw)

        assert formatted["name"] == "AE"
        assert formatted["label"] == "Adverse Events"


# ---------------------------------------------------------------------------
# Retry integration: 429 → retry → formatter
# ---------------------------------------------------------------------------

class TestRetryThenFormat:

    @pytest.mark.asyncio
    async def test_retry_result_is_correctly_formatted(
        self, client, httpx_mock, sample_sdtm_dataset
    ):
        from cdisc_mcp.response_formatter import format_response

        httpx_mock.add_response(
            url=f"{BASE_URL}/mdr/sdtm/3-4/datasets/AE",
            status_code=429,
            json={"message": "rate limited"},
        )
        httpx_mock.add_response(
            url=f"{BASE_URL}/mdr/sdtm/3-4/datasets/AE",
            json=sample_sdtm_dataset,
        )

        raw = await client.get("/mdr/sdtm/3-4/datasets/AE")
        formatted = format_response(raw)

        assert formatted["name"] == "AE"
        assert "_links" not in formatted


# ---------------------------------------------------------------------------
# Cache integration: cached response still formats correctly
# ---------------------------------------------------------------------------

class TestCachedResponseFormatting:

    @pytest.mark.asyncio
    async def test_cached_response_formats_identically(
        self, client, httpx_mock, sample_sdtm_dataset
    ):
        from cdisc_mcp.response_formatter import format_response

        httpx_mock.add_response(
            url=f"{BASE_URL}/mdr/sdtm/3-4/datasets/AE",
            json=sample_sdtm_dataset,
        )

        raw1 = await client.get("/mdr/sdtm/3-4/datasets/AE")
        raw2 = await client.get("/mdr/sdtm/3-4/datasets/AE")  # cache hit

        formatted1 = format_response(raw1)
        formatted2 = format_response(raw2)

        assert formatted1 == formatted2
        # Only one real HTTP call
        assert len(httpx_mock.get_requests()) == 1
