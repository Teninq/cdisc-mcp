# -*- coding: utf-8 -*-
"""Tests for response formatter - spec compliance tests."""
from typing import Any
import pytest
from cdisc_mcp.response_formatter import format_response, DEFAULT_MAX_ITEMS


def test_default_max_items_is_100() -> None:
    assert DEFAULT_MAX_ITEMS == 100


class TestFormatResponseDict:
    def test_removes_links_from_dict(self) -> None:
        data: dict[str, Any] = {"name": "DM", "_links": {"self": {"href": "/..."}}}
        result = format_response(data)
        assert "_links" not in result
        assert result["name"] == "DM"

    def test_removes_ordinal_from_dict(self) -> None:
        data: dict[str, Any] = {"name": "DM", "ordinal": 1, "label": "Demographics"}
        result = format_response(data)
        assert "ordinal" not in result
        assert result["label"] == "Demographics"

    def test_does_not_mutate_input_dict(self) -> None:
        data: dict[str, Any] = {"name": "DM", "_links": {}}
        original = dict(data)
        format_response(data)
        assert data == original


class TestFormatResponseList:
    def test_list_wrapped_in_envelope(self) -> None:
        items: list[Any] = [{"name": f"ITEM{i}"} for i in range(3)]
        result = format_response(items)
        assert "items" in result
        assert "total_returned" in result
        assert "has_more" in result

    def test_list_truncated_at_max_items(self) -> None:
        items: list[Any] = [{"name": f"ITEM{i}"} for i in range(DEFAULT_MAX_ITEMS + 10)]
        result = format_response(items)
        assert result["total_returned"] == DEFAULT_MAX_ITEMS
        assert result["has_more"] is True

    def test_list_not_truncated_when_under_limit(self) -> None:
        items: list[Any] = [{"name": f"ITEM{i}"} for i in range(5)]
        result = format_response(items)
        assert result["total_returned"] == 5
        assert result["has_more"] is False

    def test_list_items_have_links_removed(self) -> None:
        items: list[Any] = [{"name": "DM", "_links": {"self": {}}}]
        result = format_response(items)
        assert "_links" not in result["items"][0]

    def test_custom_max_items(self) -> None:
        items: list[Any] = [{"name": f"ITEM{i}"} for i in range(20)]
        result = format_response(items, max_items=5)
        assert result["total_returned"] == 5
        assert result["has_more"] is True

    def test_empty_list(self) -> None:
        result = format_response([])
        assert result["items"] == []
        assert result["total_returned"] == 0
        assert result["has_more"] is False
