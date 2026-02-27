"""MCP tools for CDISC Library product discovery."""

from __future__ import annotations

from typing import Any

from ..client import CDISCClient


def _hal_items(data: dict[str, Any], key: str) -> list[dict[str, Any]]:
    """Extract a named list from HAL _links and return clean items."""
    items = data.get("_links", {}).get(key, [])
    return [
        {
            "name": item["href"].rstrip("/").split("/")[-1],
            "title": item.get("title"),
            "type": item.get("type"),
            "href": item["href"],
        }
        for item in items
        if isinstance(item, dict)
    ]


async def list_products(client: CDISCClient) -> dict[str, Any]:
    """List all available CDISC standards and their published versions.

    Returns a summary of available products (SDTM, ADaM, CDASH, SEND, etc.)
    with version numbers. Use this as a first step to discover what versions
    are available before querying specific content.

    Returns:
        Dict with product information grouped by standard area.
    """
    data = await client.get("/mdr/products")
    links = data.get("_links", {})

    result: dict[str, Any] = {}
    for group_key, group_val in links.items():
        if group_key in ("self",):
            continue
        if isinstance(group_val, dict):
            group_links = group_val.get("_links", {})
            group_items: dict[str, list[str]] = {}
            for product_key, product_list in group_links.items():
                if product_key in ("self",) or not isinstance(product_list, list):
                    continue
                group_items[product_key] = [
                    item.get("title") or item.get("href", "").split("/")[-1]
                    for item in product_list
                    if isinstance(item, dict) and "href" in item
                ]
            if group_items:
                result[group_key] = group_items
        elif isinstance(group_val, list):
            result[group_key] = [
                item.get("title") or item.get("href", "").split("/")[-1]
                for item in group_val
                if isinstance(item, dict) and "href" in item
            ]

    return result
