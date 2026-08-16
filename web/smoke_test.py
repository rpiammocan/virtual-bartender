#!/usr/bin/env python3
"""End-to-end smoke and persistence tests for Virtual Bartender Web."""

from __future__ import annotations

import json
import sys
import urllib.error
import urllib.request

BASE = sys.argv[1].rstrip("/") if len(sys.argv) > 1 else "http://127.0.0.1:8080"
MODE = sys.argv[2] if len(sys.argv) > 2 else "exercise"
TEST_INGREDIENT = "Web V1 Smoke Test Ingredient"
TEST_SHOPPING = "Web V1 Smoke Test Shopping Item"
TEST_HISTORY_NOTE = "Web V1 smoke test"
TEST_TONIGHT = "Web V1 Smoke Test Tonight"


def request(path: str, method: str = "GET", payload: dict | None = None):
    body = None if payload is None else json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        BASE + path,
        data=body,
        method=method,
        headers={"Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(req, timeout=20) as response:
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


def catalogs():
    health = request("/api/health")
    assert_true(health == {"status": "ok"}, "health endpoint failed")
    recipes = request("/api/recipes")
    ingredients = request("/api/ingredients")
    assert_true(isinstance(recipes, list) and recipes, "seeded recipe catalog is empty")
    assert_true(isinstance(ingredients, list) and ingredients, "seeded ingredient catalog is empty")
    return recipes, ingredients


def exercise() -> None:
    recipes, ingredients = catalogs()
    recipe_id = recipes[0]["id"]
    detail = request(f"/api/recipes/{recipe_id}")
    assert_true(isinstance(detail, dict) and detail.get("ingredients") is not None, "recipe detail failed")

    test_ingredient = request(
        "/api/ingredients",
        "POST",
        {"name": TEST_INGREDIENT, "category": "Test"},
    )
    ingredient_id = test_ingredient["id"]

    request(
        "/api/inventory",
        "POST",
        {
            "ingredient_id": ingredient_id,
            "context_type": "my_bar",
            "context_id": None,
            "quantity": 1,
            "unit_id": None,
            "have": True,
            "notes": TEST_HISTORY_NOTE,
        },
    )

    my_bar = request("/api/inventory?context_type=my_bar")
    present = {item["ingredient_id"] for item in my_bar}
    assert_true(ingredient_id in present, "My Bar write/readback failed")

    # Stock every required ingredient for one known recipe so Surprise Me has
    # at least one eligible result during this deterministic CI run.
    for item in detail["ingredients"]:
        if item.get("is_optional") or item["ingredient_id"] in present:
            continue
        request(
            "/api/inventory",
            "POST",
            {
                "ingredient_id": item["ingredient_id"],
                "context_type": "my_bar",
                "context_id": None,
                "quantity": 9999,
                "unit_id": None,
                "have": True,
                "notes": TEST_HISTORY_NOTE,
            },
        )
        present.add(item["ingredient_id"])

    matches = request("/api/matches?context_type=my_bar")
    assert_true(isinstance(matches, list) and matches, "recipe matching endpoint failed")

    surprise = request("/api/surprise?context_type=my_bar")
    assert_true(isinstance(surprise, dict) and surprise.get("recipe_id"), "Surprise Me failed")

    request(f"/api/favorites/{recipe_id}", "POST")
    favorites = request("/api/favorites")
    assert_true(any(item["recipe_id"] == recipe_id for item in favorites), "favorite write/readback failed")

    shopping_item = request(
        "/api/shopping",
        "POST",
        {
            "ingredient_id": None,
            "custom_name": TEST_SHOPPING,
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
        {"recipe_id": recipe_id, "session_id": None, "rating": 5, "notes": TEST_HISTORY_NOTE},
    )
    history = request("/api/history")
    assert_true(any(item["id"] == history_item["id"] for item in history), "history write/readback failed")

    tonight = request(
        "/api/bars/tonight",
        "POST",
        {"name": TEST_TONIGHT, "session_date": "2026-08-16", "source_type": "tonight"},
    )
    tonight_id = tonight["id"]
    request(f"/api/bars/tonight/{tonight_id}/copy-my-bar", "POST")
    tonight_inventory = request(f"/api/inventory?context_type=tonight_bar&context_id={tonight_id}")
    assert_true(len(tonight_inventory) >= 1, "Tonight's Bar copy from My Bar failed")
    tonight_matches = request(f"/api/matches?context_type=tonight_bar&context_id={tonight_id}")
    assert_true(isinstance(tonight_matches, list), "Tonight's Bar matching failed")

    backup = request("/api/backups", "POST")
    backups = request("/api/backups")
    assert_true(isinstance(backup, dict), "manual backup creation failed")
    assert_true(isinstance(backups, list) and backups, "backup listing failed")

    display = request(f"/api/display/recipe/{recipe_id}?metric=false")
    assert_true(isinstance(display, dict), "recipe display endpoint failed")

    print(
        "Web V1 functional test passed: "
        f"{len(recipes)} recipes, {len(ingredients)} seeded ingredients; "
        "My Bar, matching, Surprise Me, favorites, shopping, history, "
        "Tonight's Bar, backups, and recipe display verified."
    )


def verify_persistence() -> None:
    recipes, _ = catalogs()
    recipe_id = recipes[0]["id"]

    ingredients = request("/api/ingredients")
    test_ingredient = next((i for i in ingredients if i["name"] == TEST_INGREDIENT), None)
    assert_true(test_ingredient is not None, "custom ingredient did not persist across restart")

    my_bar = request("/api/inventory?context_type=my_bar")
    assert_true(
        any(item["ingredient_id"] == test_ingredient["id"] for item in my_bar),
        "My Bar did not persist across restart",
    )

    favorites = request("/api/favorites")
    assert_true(any(item["recipe_id"] == recipe_id for item in favorites), "favorites did not persist across restart")

    shopping = request("/api/shopping")
    assert_true(any(item.get("custom_name") == TEST_SHOPPING for item in shopping), "shopping did not persist across restart")

    history = request("/api/history")
    assert_true(any(item.get("notes") == TEST_HISTORY_NOTE for item in history), "history did not persist across restart")

    tonight = request("/api/bars/tonight")
    assert_true(any(item["name"] == TEST_TONIGHT for item in tonight), "Tonight's Bar did not persist across restart")

    backups = request("/api/backups")
    assert_true(isinstance(backups, list) and backups, "backup metadata did not persist across restart")

    print("Web V1 persistence test passed after container restart.")


def main() -> None:
    if MODE == "exercise":
        exercise()
    elif MODE == "verify-persistence":
        verify_persistence()
    else:
        raise SystemExit(f"Unknown mode: {MODE}")


if __name__ == "__main__":
    main()
