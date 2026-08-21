#!/usr/bin/env python3
"""Remove two redundant coffee recipes found by deep catalog QA."""
from __future__ import annotations

import ast
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
APP = ROOT / "backend" / "app"
SEED = APP / "seed.py"
SOURCES = [
    ("seed.py", None),
    ("catalog_v2.py", "RECIPES_V2"),
    ("catalog_v3.py", "RECIPES_V3"),
    ("catalog_v4.py", "RECIPES_V4"),
    ("catalog_v5.py", "RECIPES_V5"),
    ("catalog_v6.py", "RECIPES_V6"),
    ("catalog_v7.py", "RECIPES_V7"),
    ("catalog_v8.py", "RECIPES_V8"),
]
REMOVE_KEYS = {"coffee-cognac", "coffee-rum"}


def assignments(text: str):
    tree = ast.parse(text)
    out = {}
    for node in tree.body:
        if isinstance(node, ast.Assign) and len(node.targets) == 1 and isinstance(node.targets[0], ast.Name):
            try:
                out[node.targets[0].id] = ast.literal_eval(node.value)
            except (ValueError, TypeError):
                pass
    return out


def find_base_name(values):
    candidates = []
    for name, value in values.items():
        if isinstance(value, list) and value and all(isinstance(x, dict) for x in value):
            if all("key" in x and "ingredients" in x for x in value):
                candidates.append((name, value))
    candidates.sort(key=lambda pair: ("recipe" not in pair[0].lower(), -len(pair[1])))
    return candidates[0][0] if candidates else None


def rewrite_recipe_list(path: Path, variable: str, recipes: list[dict]) -> None:
    if path.name == "seed.py":
        text = path.read_text(encoding="utf-8")
        tree = ast.parse(text)
        target_node = None
        for node in tree.body:
            if isinstance(node, ast.Assign) and len(node.targets) == 1 and isinstance(node.targets[0], ast.Name) and node.targets[0].id == variable:
                target_node = node
                break
        if target_node is None or not hasattr(target_node, "end_lineno"):
            raise RuntimeError(f"Could not locate {variable} in seed.py")
        lines = text.splitlines()
        replacement = f"{variable} = {repr(recipes)}"
        lines[target_node.lineno - 1:target_node.end_lineno] = [replacement]
        path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    else:
        path.write_text(f"{variable} = {repr(recipes)}\n", encoding="utf-8")


def remove_recipes() -> int:
    removed = 0
    for filename, variable in SOURCES:
        path = APP / filename
        values = assignments(path.read_text(encoding="utf-8"))
        var = variable or find_base_name(values)
        if not var:
            continue
        recipes = values[var]
        keys = {r.get("key") for r in recipes}
        if not (keys & REMOVE_KEYS):
            continue
        filtered = [r for r in recipes if r.get("key") not in REMOVE_KEYS]
        removed += len(recipes) - len(filtered)
        rewrite_recipe_list(path, var, filtered)
    return removed


def remove_image_metadata() -> int:
    text = SEED.read_text(encoding="utf-8")
    kept = []
    removed = 0
    for line in text.splitlines():
        stripped = line.strip()
        if any(stripped.startswith(f"IMAGE_METADATA['{key}']") or stripped.startswith(f'IMAGE_METADATA["{key}"]') for key in REMOVE_KEYS):
            removed += 1
            continue
        kept.append(line)
    SEED.write_text("\n".join(kept) + "\n", encoding="utf-8")
    return removed


def main():
    recipe_count = remove_recipes()
    image_count = remove_image_metadata()
    if recipe_count != 2:
        raise SystemExit(f"Expected to remove 2 recipes; removed {recipe_count}")
    print(f"Removed {recipe_count} redundant recipes")
    print(f"Removed {image_count} obsolete image metadata rows")


if __name__ == "__main__":
    main()
