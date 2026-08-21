#!/usr/bin/env python3
"""Apply the first conservative catalog/image QA cleanup.

Removes only image mappings proven to be unrelated/duplicated and removes the
synthetic Brandy Lemon Sour duplicate while retaining Brandy Sour as canonical.
"""
from __future__ import annotations

import ast
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SEED = ROOT / "backend" / "app" / "seed.py"
CATALOG_V5 = ROOT / "backend" / "app" / "catalog_v5.py"

# These mappings were manually reviewed from the QA report and are clearly
# unrelated to the named recipe, or duplicate another recipe's exact photo.
REMOVE_IMAGE_KEYS = {
    "amaretto-cream",          # Panettone photo
    "bourbon-cola",            # Bourbon Street / Coca-Cola street scene
    "brandy-orange",           # Sangria photo
    "brandy-pineapple",        # exact Brandy Sour duplicate photo
    "cognac-cranberry",        # hot-dog photo
    "cognac-orange",           # exact Sidecar photo
    "cucumber-gimlet",         # cucumbers, not the cocktail
    "irish-creamless-coffee",  # historical diary page
    "lime-soda-mocktail",      # unrelated alcoholic cocktail photo
    "gold-rush",               # unrelated City of Downey 'Gold Rush' photo
    "brandy-sour-lemon",       # duplicate recipe removed below
}

DUPLICATE_RECIPE_KEY = "brandy-sour-lemon"


def remove_image_metadata() -> int:
    text = SEED.read_text(encoding="utf-8")
    kept = []
    removed = 0
    for line in text.splitlines():
        stripped = line.strip()
        matched = False
        for key in REMOVE_IMAGE_KEYS:
            if stripped.startswith(f"IMAGE_METADATA[{key!r}]") or stripped.startswith(f'IMAGE_METADATA["{key}"]'):
                removed += 1
                matched = True
                break
        if not matched:
            kept.append(line)
    SEED.write_text("\n".join(kept) + "\n", encoding="utf-8")
    return removed


def remove_duplicate_recipe() -> int:
    source = CATALOG_V5.read_text(encoding="utf-8")
    tree = ast.parse(source)
    recipes = None
    for node in tree.body:
        if not isinstance(node, ast.Assign) or len(node.targets) != 1:
            continue
        target = node.targets[0]
        if isinstance(target, ast.Name) and target.id == "RECIPES_V5":
            recipes = ast.literal_eval(node.value)
            break
    if recipes is None:
        raise SystemExit("Could not find RECIPES_V5")
    filtered = [r for r in recipes if r.get("key") != DUPLICATE_RECIPE_KEY]
    removed = len(recipes) - len(filtered)
    if removed != 1:
        raise SystemExit(f"Expected to remove exactly one {DUPLICATE_RECIPE_KEY!r}; removed {removed}")
    # Reformatting this generated catalog file is intentional and keeps it valid,
    # deterministic Python without hand-editing a one-line list literal.
    CATALOG_V5.write_text("RECIPES_V5 = " + repr(filtered) + "\n", encoding="utf-8")
    return removed


def main() -> None:
    metadata_removed = remove_image_metadata()
    recipe_removed = remove_duplicate_recipe()
    print(f"Removed {metadata_removed} bad/obsolete image mappings")
    print(f"Removed {recipe_removed} duplicate recipe")


if __name__ == "__main__":
    main()
