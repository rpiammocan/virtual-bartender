#!/usr/bin/env python3
"""End-to-end smoke test for the browser-hosted Virtual Bartender edition."""

from __future__ import annotations

import json
import sys
import urllib.error
import urllib.request

BASE = sys.argv[1].rstrip("/") if len(sys.argv) > 1 else "http://127.0.0.1:8080"


def request(path: str, method: str = "GET", payload: dict | None = None):
    body = None if payload is None else json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        BASE + path,
        data=body,
        method=method,
        headers={"Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(req, timeout=15) as response:
            raw = response.read()
            if not raw:
                return None
            content_type = response.headers.get("Content-Type", "")
            if "json" in content_type:
                return json.loads(raw)
            return raw.decode("utf-8", errors="replace")
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"{method} {path} failed: HTTP {exc.code}: {detail}") from exc


def assert_true(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def main() -> None:
    health = request("/api/health")
    assert_true(health == {"status": "ok"}, "health endpoint failed")

    recipes = request("/api/recipes")
    assert_true(isinstance(recipes, list) and recipes, "seeded recipe catalog is empty")
    recipe_id = recipes[0]["id"]

    ingredients = request("/api/ingredients")
    assert_true(isinstance(ingredients, list) and ingredients, "seeded ingredient catalog is empty")

    test_ingredient = request(
        "/api/ingredients",
        "POST",
        {"name": "Web V1 Smoke Test Ingredient", "category": "Test"},
    )
    ingredient_id = test_ingredient["id"]

    inventory_item = request(
        "/api/inventory",
        "POST",
        {
            "ingredient_id": ingredient_id,
            "context_type": "my_bar",
            "context_id": None,
            "quantity": 1,
            "unit_id": None,
            "have": True,
            "notes": "Web V1 automated smoke test",
        },
    )
    assert_true(inventory_item["ingredient_id"] == ingredient_id, "My Bar write failed")

    my_bar = request("/api/inventory?context_type=my_bar")
    assert_true(any(item["ingredient_id"] == ingredient_id for item in my_bar), "My Bar readback failed")

    matches = request("/api/matches?context_type=my_bar")
    assert_true(isinstance(matches, list), "recipe matching endpoint failed")

    request(f"/api/favorites/{recipe_id}", "POST")
    favorites = request("/api/favorites")
    assert_true(any(item["recipe_id"] == recipe_id for item in favorites), "favorite write/readback failed")

    shopping_item = request(
        "/api/shopping",
        "POST",
        {
            "ingredient_id": None,
            "custom_name": "Web V1 Smoke Test Shopping Item",
            "quantity": None,
            "unit_id": None,
            "category": "Test",
        },
    )
    shopping = request("/api/shopping")
    assert_true(any(item["id"] == shopping_item["id"] for item in shopping), "shopping write/readback failed")

    history_item = request(
        "/api/history",
        "POST",
        {"recipe_id": recipe_id, "session_id": None, "rating": 5, "notes": "Web V1 smoke test"},
    )
    history = request("/api/history")
    assert_true(any(item["id"] == history_item["id"] for item in history), "history write/readback failed")

    display = request(f"/api/display/recipe/{recipe_id}?metric=false")
    assert_true(isinstance(display, dict), "recipe display endpoint failed")

    print(
        "Web V1 smoke test passed: "
        f"{len(recipes)} recipes, {len(ingredients)} seeded ingredients, "
        "My Bar, matching, favorites, shopping, history, and recipe display verified."
    )


if __name__ == "__main__":
    main()
