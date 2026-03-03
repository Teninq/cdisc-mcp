"""Unit tests for tools validators."""

import pytest

from cdisc_mcp.tools._validators import normalize_version_for_path, validate_version


def test_normalize_version_for_path_converts_dots_to_dashes() -> None:
    assert normalize_version_for_path("3.4") == "3-4"
    assert normalize_version_for_path("1.3") == "1-3"


def test_normalize_version_for_path_preserves_dashes() -> None:
    assert normalize_version_for_path("3-4") == "3-4"


def test_normalize_version_for_path_keeps_codelist_like_values() -> None:
    assert normalize_version_for_path("AGEU") == "AGEU"
    assert normalize_version_for_path("C66781") == "C66781"


def test_validate_version_strips_whitespace() -> None:
    assert validate_version(" 3.4 ") == "3.4"


def test_validate_version_blocks_path_traversal() -> None:
    with pytest.raises(ValueError, match="invalid characters"):
        validate_version("3.4/../admin")
