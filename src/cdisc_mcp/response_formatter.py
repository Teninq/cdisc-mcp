"""Utilities for trimming and normalising CDISC API responses.

The CDISC Library API returns HAL-flavoured JSON with hypermedia link blocks
(_links) and UI ordering hints (ordinal) that are not meaningful to MCP
tool consumers. These are stripped to reduce token usage.

Long lists nested inside response dicts are truncated to DEFAULT_MAX_ITEMS
and a sentinel notice dict is appended so callers know that data was omitted.

When a top-level list is passed directly, it is wrapped in an envelope dict
with keys: items, total_returned, has_more.
"""

from __future__ import annotations

from typing import Any

# HAL hypermedia links and display ordering hints — not useful to LLM consumers.
_EXCLUDED_KEYS: frozenset[str] = frozenset({"_links", "ordinal"})

# Independent constant — not derived from config so it can be changed without
# affecting config.MAX_LIST_LENGTH (which controls nested-list truncation in
# dict responses).
DEFAULT_MAX_ITEMS: int = 100


def format_response(
    payload: dict[str, Any] | list[Any],
    max_items: int = DEFAULT_MAX_ITEMS,
) -> dict[str, Any]:
    """Normalise a raw CDISC API response for MCP tool output.

    When *payload* is a **list**:
    - Trims each item (removing _links and ordinal recursively).
    - Truncates to *max_items* elements.
    - Returns an envelope: ``{"items": [...], "total_returned": N, "has_more": bool}``.

    When *payload* is a **dict**:
    - Recursively removes _links and ordinal keys at every nesting level.
    - Truncates any list value that exceeds *max_items* elements; a sentinel
      dict is appended as the final element so consumers know data was cut.
    - Never mutates the original *payload*.

    Args:
        payload: Raw parsed JSON dict or list from the CDISC Library API.
        max_items: Maximum number of items to keep in any list value.
            Defaults to DEFAULT_MAX_ITEMS (100).

    Returns:
        New dict with excluded keys removed and long lists truncated.
    """
    if isinstance(payload, list):
        return _wrap_list(payload, max_items=max_items)
    return _trim_dict(payload, max_items=max_items)


# ---------------------------------------------------------------------------
# Private helpers
# ---------------------------------------------------------------------------

def _wrap_list(items: list[Any], max_items: int) -> dict[str, Any]:
    """Wrap a top-level list in an envelope dict.

    Args:
        items: The raw list from the API.
        max_items: Maximum number of items to include.

    Returns:
        ``{"items": [...trimmed...], "total_returned": N, "has_more": bool}``
    """
    has_more = len(items) > max_items
    kept = items[:max_items]
    trimmed_items = [_trim_value(item, max_items=max_items) for item in kept]
    return {
        "items": trimmed_items,
        "total_returned": len(trimmed_items),
        "has_more": has_more,
    }


def _trim_dict(obj: dict[str, Any], max_items: int) -> dict[str, Any]:
    """Return a new dict with excluded keys removed and nested values trimmed."""
    result: dict[str, Any] = {}
    for key, value in obj.items():
        if key in _EXCLUDED_KEYS:
            continue
        result[key] = _trim_value(value, max_items=max_items)
    return result


def _trim_value(value: Any, max_items: int) -> Any:
    """Recursively trim a single value."""
    if isinstance(value, dict):
        return _trim_dict(value, max_items=max_items)
    if isinstance(value, list):
        return _trim_list(value, max_items=max_items)
    return value


def _trim_list(items: list[Any], max_items: int) -> list[Any]:
    """Trim a list to *max_items*, appending a truncation notice when cut.

    The notice dict is appended as the (max_items)-th element so the total
    length never exceeds max_items. Real items occupy max_items - 1 slots
    when truncation occurs.

    Args:
        items: The original list.
        max_items: Maximum number of elements to keep (including any notice).

    Returns:
        A new list. If len(items) > max_items the list is truncated to
        max_items - 1 real items followed by a sentinel notice dict.
    """
    original_count = len(items)

    if original_count <= max_items:
        # No truncation needed — still recurse into dict/list items.
        return [_trim_value(item, max_items=max_items) for item in items]

    kept_items = items[: max_items - 1]
    trimmed = [_trim_value(item, max_items=max_items) for item in kept_items]
    trimmed.append(
        {
            "_truncated": True,
            "total_count": original_count,
            "message": (
                f"Results truncated: showing {max_items - 1} of {original_count} items."
            ),
        }
    )
    return trimmed
