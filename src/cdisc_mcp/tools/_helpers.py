"""Shared helpers for MCP tool modules."""

from __future__ import annotations

from typing import Any


def hal_items(data: dict[str, Any], key: str) -> list[dict[str, Any]]:
    """Extract a named list from HAL _links and return clean items.

    Strips HAL metadata (``_links``, ``self``, etc.) and returns a flat
    list of dicts with ``name``, ``title``, ``type``, and optionally
    ``href`` extracted from each link entry.

    Args:
        data: Raw HAL+JSON response dict.
        key: Key inside ``_links`` to extract (e.g. ``"datasets"``).

    Returns:
        List of cleaned item dicts.
    """
    items = data.get("_links", {}).get(key, [])
    return [
        {
            "name": item["href"].rstrip("/").split("/")[-1],
            "title": item.get("title"),
            "type": item.get("type"),
        }
        for item in items
        if isinstance(item, dict)
    ]
