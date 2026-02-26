"""
Unit tests for src/cdisc_mcp/config.py

TDD cycle: these tests are written BEFORE the implementation.
Run them first — they MUST all fail (RED).
After implementing config.py they MUST all pass (GREEN).

Coverage target: 95%+ (pure logic, no I/O, trivial to cover completely)
"""

import pytest

# ---------------------------------------------------------------------------
# Test: get_api_key() - happy path
# ---------------------------------------------------------------------------

class TestGetApiKeySuccess:
    """CDISC_API_KEY is present and non-empty → return it as-is."""

    def test_returns_key_when_env_is_set(self, mock_env, api_key):
        from cdisc_mcp.config import get_api_key

        result = get_api_key()

        assert result == api_key

    def test_returns_string_type(self, mock_env):
        from cdisc_mcp.config import get_api_key

        assert isinstance(get_api_key(), str)

    def test_preserves_key_with_special_characters(self, monkeypatch):
        """Keys sometimes contain hyphens and mixed case — preserve exactly."""
        raw = "Ab1-Cd2_Ef3.Gh4"
        monkeypatch.setenv("CDISC_API_KEY", raw)

        from cdisc_mcp.config import get_api_key

        assert get_api_key() == raw


# ---------------------------------------------------------------------------
# Test: get_api_key() - missing / empty key → raise
# ---------------------------------------------------------------------------

class TestGetApiKeyFailure:
    """Misconfigured environment must raise a clear error at startup."""

    def test_raises_when_env_var_missing(self, missing_env):
        from cdisc_mcp.config import get_api_key

        with pytest.raises(EnvironmentError, match="CDISC_API_KEY"):
            get_api_key()

    def test_raises_when_env_var_is_empty_string(self, monkeypatch):
        monkeypatch.setenv("CDISC_API_KEY", "")

        from cdisc_mcp.config import get_api_key

        with pytest.raises(EnvironmentError, match="CDISC_API_KEY"):
            get_api_key()

    def test_raises_when_env_var_is_whitespace_only(self, monkeypatch):
        """Whitespace-only keys are as unusable as empty strings."""
        monkeypatch.setenv("CDISC_API_KEY", "   ")

        from cdisc_mcp.config import get_api_key

        with pytest.raises(EnvironmentError, match="CDISC_API_KEY"):
            get_api_key()

    def test_error_message_is_actionable(self, missing_env):
        """Error text must tell the operator what to do."""
        from cdisc_mcp.config import get_api_key

        with pytest.raises(EnvironmentError) as exc_info:
            get_api_key()

        # Message should hint at how to fix the problem
        msg = str(exc_info.value)
        assert "CDISC_API_KEY" in msg


# ---------------------------------------------------------------------------
# Test: settings object / module-level constants
# ---------------------------------------------------------------------------

class TestSettings:
    """Config module must expose a base URL constant and optional timeout."""

    def test_base_url_is_https(self, mock_env):
        from cdisc_mcp import config

        assert config.BASE_URL.startswith("https://")

    def test_base_url_points_to_cdisc(self, mock_env):
        from cdisc_mcp import config

        assert "cdisc.org" in config.BASE_URL

    def test_request_timeout_is_positive_number(self, mock_env):
        from cdisc_mcp import config

        assert config.REQUEST_TIMEOUT > 0

    def test_max_list_length_is_reasonable(self, mock_env):
        """Formatter uses this to truncate large arrays — must be > 0."""
        from cdisc_mcp import config

        assert 1 <= config.MAX_LIST_LENGTH <= 100
