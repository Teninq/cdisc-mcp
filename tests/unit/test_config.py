"""
Unit tests for src/cdisc_mcp/config.py

TDD cycle: these tests are written BEFORE the implementation.
Run them first — they MUST all fail (RED).
After implementing config.py they MUST all pass (GREEN).

Coverage target: 95%+ (pure logic, no I/O, trivial to cover completely)
"""

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
