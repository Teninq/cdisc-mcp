"""
Unit tests for src/cdisc_mcp/response_formatter.py

All tests are pure Python — no HTTP, no environment variables required.

Coverage target: 95%+ (pure transformation logic)
"""



# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def make_nested(depth: int) -> dict:
    """Build a deeply nested dict: {"_links": {...}, "data": {...recursive...}}."""
    node: dict = {"value": "leaf"}
    for _ in range(depth):
        node = {"_links": {"self": {"href": "/x"}}, "data": node}
    return node


# ---------------------------------------------------------------------------
# Test: _links removal
# ---------------------------------------------------------------------------

class TestLinksRemoval:
    """_links keys must be stripped at every nesting level."""

    def test_removes_top_level_links(self):
        from cdisc_mcp.response_formatter import format_response

        payload = {"_links": {"self": {"href": "/mdr/sdtm"}}, "name": "SDTM"}
        result = format_response(payload)

        assert "_links" not in result

    def test_preserves_other_top_level_keys(self):
        from cdisc_mcp.response_formatter import format_response

        payload = {"_links": {}, "name": "AE", "label": "Adverse Events"}
        result = format_response(payload)

        assert result["name"] == "AE"
        assert result["label"] == "Adverse Events"

    def test_removes_nested_links(self, sample_sdtm_dataset):
        """Variables inside a dataset response each have their own _links."""
        from cdisc_mcp.response_formatter import format_response

        result = format_response(sample_sdtm_dataset)

        for var in result.get("variables", []):
            assert "_links" not in var

    def test_removes_links_in_list_items(self):
        from cdisc_mcp.response_formatter import format_response

        payload = {
            "items": [
                {"_links": {"self": {"href": "/a"}}, "id": 1},
                {"_links": {"self": {"href": "/b"}}, "id": 2},
            ]
        }
        result = format_response(payload)

        for item in result["items"]:
            assert "_links" not in item

    def test_handles_deeply_nested_links(self):
        from cdisc_mcp.response_formatter import format_response

        payload = make_nested(depth=5)
        result = format_response(payload)

        # Walk the result and assert no _links anywhere
        def has_links(obj) -> bool:
            if isinstance(obj, dict):
                if "_links" in obj:
                    return True
                return any(has_links(v) for v in obj.values())
            if isinstance(obj, list):
                return any(has_links(item) for item in obj)
            return False

        assert not has_links(result)


# ---------------------------------------------------------------------------
# Test: list truncation
# ---------------------------------------------------------------------------

class TestListTruncation:
    """Large arrays are truncated to MAX_LIST_LENGTH with a truncation notice."""

    def test_short_list_is_not_truncated(self):
        from cdisc_mcp import config
        from cdisc_mcp.response_formatter import format_response

        short = [{"id": i} for i in range(config.MAX_LIST_LENGTH - 1)]
        payload = {"items": short}
        result = format_response(payload)

        assert len(result["items"]) == len(short)

    def test_exact_boundary_list_is_not_truncated(self):
        from cdisc_mcp import config
        from cdisc_mcp.response_formatter import format_response

        exact = [{"id": i} for i in range(config.MAX_LIST_LENGTH)]
        payload = {"items": exact}
        result = format_response(payload)

        assert len(result["items"]) == config.MAX_LIST_LENGTH

    def test_long_list_is_truncated(self, sample_sdtm_dataset):
        """Truncation triggers when max_items is set below the variable count."""
        from cdisc_mcp.response_formatter import format_response

        # sample_sdtm_dataset has 20 variables; use max_items=5 to force truncation.
        result = format_response(sample_sdtm_dataset, max_items=5)

        assert len(result["variables"]) <= 5

    def test_truncation_notice_appended(self, sample_sdtm_dataset):
        """A sentinel dict is appended so consumers know data was cut."""
        from cdisc_mcp.response_formatter import format_response

        # Force truncation by using a max_items smaller than variable count.
        result = format_response(sample_sdtm_dataset, max_items=5)
        variables = result["variables"]

        # The last element must be the truncation notice
        last = variables[-1]
        assert "_truncated" in last or "truncated" in last

    def test_truncation_notice_includes_total_count(self, sample_sdtm_dataset):
        from cdisc_mcp.response_formatter import format_response

        original_count = len(sample_sdtm_dataset["variables"])
        # Force truncation by using a max_items smaller than variable count.
        result = format_response(sample_sdtm_dataset, max_items=5)
        last = result["variables"][-1]

        # The notice must embed the original count so the caller can report it
        notice_str = str(last)
        assert str(original_count) in notice_str

    def test_codelist_terms_truncated(self, sample_codelist):
        """sample_codelist has 150 terms — must be truncated to DEFAULT_MAX_ITEMS."""
        from cdisc_mcp.response_formatter import DEFAULT_MAX_ITEMS, format_response

        result = format_response(sample_codelist)

        # DEFAULT_MAX_ITEMS is 100; list has 150 items, so truncation fires.
        # Truncated list length = (DEFAULT_MAX_ITEMS - 1) real items + 1 notice.
        assert len(result["terms"]) <= DEFAULT_MAX_ITEMS


# ---------------------------------------------------------------------------
# Test: redundant field removal
# ---------------------------------------------------------------------------

class TestRedundantFieldRemoval:
    """Fields like 'ordinal' that add no LLM value should be stripped."""

    def test_ordinal_field_removed(self, sample_sdtm_dataset):
        from cdisc_mcp.response_formatter import format_response

        result = format_response(sample_sdtm_dataset)

        assert "ordinal" not in result

    def test_ordinal_removed_from_nested_variables(self, sample_sdtm_dataset):
        from cdisc_mcp.response_formatter import format_response

        result = format_response(sample_sdtm_dataset)

        for var in result.get("variables", []):
            assert "ordinal" not in var


# ---------------------------------------------------------------------------
# Test: edge cases / defensive behaviour
# ---------------------------------------------------------------------------

class TestEdgeCases:
    """format_response must never raise on unusual but valid inputs."""

    def test_empty_dict(self):
        from cdisc_mcp.response_formatter import format_response

        assert format_response({}) == {}

    def test_dict_with_no_links(self):
        from cdisc_mcp.response_formatter import format_response

        payload = {"name": "X", "value": 42}
        result = format_response(payload)

        assert result == {"name": "X", "value": 42}

    def test_empty_list_value_unchanged(self):
        from cdisc_mcp.response_formatter import format_response

        payload = {"items": []}
        result = format_response(payload)

        assert result["items"] == []

    def test_none_values_preserved(self):
        from cdisc_mcp.response_formatter import format_response

        payload = {"name": None, "label": "X"}
        result = format_response(payload)

        assert result["name"] is None

    def test_does_not_mutate_original(self, sample_sdtm_dataset):
        """format_response must return a new object — immutability rule."""
        from cdisc_mcp.response_formatter import format_response

        original_var_count = len(sample_sdtm_dataset["variables"])
        format_response(sample_sdtm_dataset)

        # Original must be unchanged
        assert len(sample_sdtm_dataset["variables"]) == original_var_count
        assert "_links" in sample_sdtm_dataset

    def test_non_dict_list_items_handled(self):
        """Lists of scalars (strings, ints) must not cause errors."""
        from cdisc_mcp.response_formatter import format_response

        payload = {"versions": ["3-4", "3-3", "3-2"]}
        result = format_response(payload)

        assert result["versions"] == ["3-4", "3-3", "3-2"]
