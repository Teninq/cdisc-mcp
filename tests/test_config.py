"""Tests for configuration loading."""
import pytest

from cdisc_mcp.config import load_config


class TestLoadConfig:
    def test_returns_config_when_key_set(self, mock_env: None, api_key: str) -> None:
        cfg = load_config()
        assert cfg.api_key == api_key

    def test_config_is_frozen(self, mock_env: None) -> None:
        cfg = load_config()
        with pytest.raises((AttributeError, TypeError)):
            cfg.api_key = "new-key"  # type: ignore[misc]

    def test_raises_when_env_missing(self, missing_env: None) -> None:
        with pytest.raises(ValueError, match="CDISC_API_KEY"):
            load_config()

    def test_raises_when_env_is_empty(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("CDISC_API_KEY", "")
        with pytest.raises(ValueError, match="CDISC_API_KEY"):
            load_config()

    def test_raises_when_env_is_whitespace(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("CDISC_API_KEY", "   ")
        with pytest.raises(ValueError, match="CDISC_API_KEY"):
            load_config()

    def test_default_base_url_is_https(self, mock_env: None) -> None:
        cfg = load_config()
        assert cfg.base_url.startswith("https://")
        assert "cdisc.org" in cfg.base_url

    def test_default_cache_ttl_is_positive(self, mock_env: None) -> None:
        cfg = load_config()
        assert cfg.cache_ttl > 0

    def test_default_max_retries_is_reasonable(self, mock_env: None) -> None:
        cfg = load_config()
        assert 1 <= cfg.max_retries <= 5
