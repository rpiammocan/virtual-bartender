#!/usr/bin/env python3
"""Deep structural QA for the canonical Virtual Bartender recipe catalog."""
from __future__ import annotations

import ast
import json
import re
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
APP = ROOT / "backend" / "app"
DOCS = ROOT / "docs"

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

ALLOWED_UNITS = {"oz", "ml", "tsp", "tbsp", "dash", "pc", "cup", "cups"}
NONALCOHOLIC_EXACT = {"ginger beer", "ginger ale", "root beer", "maraschino cherry", "maraschino cherries"}
ALCOHOL_TERMS = {
    "bourbon", "whiskey", "whisky", "scotch", "gin", "vodka", "rum", "tequila", "mezcal",
    "cognac", "brandy", "campari", "aperol", "amaretto", "vermouth", "chartreuse", "liqueur",
    "cointreau", "triple sec", "pisco", "cachaca", "cachaça", "prosecco", "champagne", "wine",
    "absinthe", "sherry", "port", "fernet", "galliano", "benedictine", "drambuie", "grappa",
    "aguardiente", "sambuca", "curacao", "curaçao", "creme de", "crème de",
}


def literal_assignments(text: str) -> dict[str, object]:
    tree = ast.parse(text)
    values: dict[str, object] = {}
    for node in tree.body:
        if not isinstance(node, ast.Assign) or len(node.targets) != 1:
            continue
        target = node.targets[0]
        if not isinstance(target, ast.Name):
            continue
        try:
            values[target.id] = ast.literal_eval(node.value)
        except (ValueError, TypeError):
            pass
    return values


def find_base(values: dict[str, object]) -> list[dict]:
    candidates = []
    for name, value in values.items():
        if isinstance(value, list) and value and all(isinstance(x, dict) for x in value):
            if all("key" in x and "ingredients" in x for x in value):
                candidates.append((name, value))
    if not candidates:
        raise RuntimeError("Could not locate base recipe list in seed.py")
    candidates.sort(key=lambda pair: ("recipe" not in pair[0].lower(), -len(pair[1])))
    return candidates[0][1]


def load_catalog() -> list[dict]:
    rows: list[dict] = []
    for filename, variable in SOURCES:
        values = literal_assignments((APP / filename).read_text(encoding="utf-8"))
        recipes = values[variable] if variable else find_base(values)
        rows.extend(recipes)
    return rows


def norm(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "", text.casefold())


def slug(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", text.casefold()).strip("-")


def required_formula(recipe: dict) -> tuple:
    rows = []
    for name, quantity, unit, optional in recipe.get("ingredients", []):
        if optional:
            continue
        rows.append((norm(str(name)), float(quantity), str(unit).casefold()))
    return tuple(sorted(rows))


def all_formula(recipe: dict) -> tuple:
    rows = []
    for name, quantity, unit, optional in recipe.get("ingredients", []):
        rows.append((norm(str(name)), float(quantity), str(unit).casefold(), bool(optional)))
    return tuple(sorted(rows))


def alcoholic(name: str) -> bool:
    low = name.casefold().strip()
    if low in NONALCOHOLIC_EXACT:
        return False
    words = set(re.findall(r"[a-zà-ÿ]+", low))
    if "rum" in words or "gin" in words or "vodka" in words or "tequila" in words or "mezcal" in words:
        return True
    return any(term in low for term in ALCOHOL_TERMS if " " in term or len(term) > 4)


def main() -> None:
    recipes = load_catalog()
    errors: list[dict] = []
    warnings: list[dict] = []

    key_counts = Counter(r.get("key") for r in recipes)
    for key, count in sorted(key_counts.items()):
        if count > 1:
            errors.append({"kind": "duplicate_key", "key": key, "count": count})

    name_groups: dict[str, list[dict]] = defaultdict(list)
    required_groups: dict[tuple, list[dict]] = defaultdict(list)
    full_groups: dict[tuple, list[dict]] = defaultdict(list)
    ingredient_spellings: dict[str, set[str]] = defaultdict(set)
    unit_counts = Counter()

    for recipe in recipes:
        key = str(recipe.get("key", ""))
        name = str(recipe.get("name", ""))
        rtype = recipe.get("type")
        ingredients = recipe.get("ingredients", [])

        if not key or not re.fullmatch(r"[a-z0-9][a-z0-9-]*", key):
            errors.append({"kind": "invalid_key", "key": key, "name": name})
        if not name.strip():
            errors.append({"kind": "blank_name", "key": key})
        if rtype not in {"cocktail", "mocktail"}:
            errors.append({"kind": "invalid_type", "key": key, "type": rtype})
        if not ingredients:
            errors.append({"kind": "no_ingredients", "key": key})
            continue

        name_groups[norm(name)].append(recipe)
        required_groups[required_formula(recipe)].append(recipe)
        full_groups[all_formula(recipe)].append(recipe)

        seen_ingredients = Counter(norm(str(i[0])) for i in ingredients)
        for ingredient_norm, count in seen_ingredients.items():
            if count > 1:
                warnings.append({"kind": "duplicate_ingredient_in_recipe", "key": key, "name": name, "ingredient": ingredient_norm, "count": count})

        required_count = 0
        alcohol_present = False
        for item in ingredients:
            if not isinstance(item, (list, tuple)) or len(item) != 4:
                errors.append({"kind": "malformed_ingredient_row", "key": key, "row": repr(item)})
                continue
            ingredient, quantity, unit, optional = item
            ingredient = str(ingredient).strip()
            unit = str(unit).strip().casefold()
            ingredient_spellings[norm(ingredient)].add(ingredient)
            unit_counts[unit] += 1
            if not optional:
                required_count += 1
            if alcoholic(ingredient):
                alcohol_present = True
            if not ingredient:
                errors.append({"kind": "blank_ingredient", "key": key})
            try:
                q = float(quantity)
            except (TypeError, ValueError):
                errors.append({"kind": "non_numeric_quantity", "key": key, "ingredient": ingredient, "quantity": repr(quantity)})
                continue
            if q <= 0:
                errors.append({"kind": "nonpositive_quantity", "key": key, "ingredient": ingredient, "quantity": q})
            if unit not in ALLOWED_UNITS:
                warnings.append({"kind": "unusual_unit", "key": key, "ingredient": ingredient, "unit": unit})
            if unit == "oz" and q > 12:
                warnings.append({"kind": "large_ounce_quantity", "key": key, "ingredient": ingredient, "quantity": q})
            if unit in {"tsp", "tbsp"} and q > 12:
                warnings.append({"kind": "large_spoon_quantity", "key": key, "ingredient": ingredient, "quantity": q, "unit": unit})
            if unit == "dash" and q > 20:
                warnings.append({"kind": "large_dash_quantity", "key": key, "ingredient": ingredient, "quantity": q})
            if unit == "pc" and q > 30:
                warnings.append({"kind": "large_piece_quantity", "key": key, "ingredient": ingredient, "quantity": q})

        if required_count == 0:
            errors.append({"kind": "no_required_ingredients", "key": key})
        if rtype == "mocktail" and alcohol_present:
            warnings.append({"kind": "mocktail_with_alcohol_marker", "key": key, "name": name})
        if rtype == "cocktail" and not alcohol_present:
            warnings.append({"kind": "cocktail_without_alcohol_marker", "key": key, "name": name})

        instructions = str(recipe.get("instructions", "")).strip()
        description = str(recipe.get("description", "")).strip()
        source = str(recipe.get("source", "")).strip()
        url = str(recipe.get("url", "")).strip()
        if not instructions:
            errors.append({"kind": "blank_instructions", "key": key})
        elif len(instructions) < 20:
            warnings.append({"kind": "very_short_instructions", "key": key, "instructions": instructions})
        if not description:
            warnings.append({"kind": "blank_description", "key": key})
        if not source:
            warnings.append({"kind": "blank_source", "key": key})
        if not url:
            warnings.append({"kind": "blank_source_url", "key": key})

        expected_slug = slug(name)
        if key != expected_slug and not (key in expected_slug or expected_slug in key):
            warnings.append({"kind": "key_name_mismatch", "key": key, "name": name, "name_slug": expected_slug})

    for rows in name_groups.values():
        if len(rows) > 1:
            warnings.append({"kind": "normalized_name_collision", "recipes": [{"key": r["key"], "name": r["name"]} for r in rows]})

    for rows in full_groups.values():
        if len(rows) > 1:
            warnings.append({"kind": "identical_full_formula", "recipes": [{"key": r["key"], "name": r["name"]} for r in rows]})

    for rows in required_groups.values():
        if len(rows) > 1 and len({all_formula(r) for r in rows}) > 1:
            warnings.append({"kind": "same_required_formula_optional_variation", "recipes": [{"key": r["key"], "name": r["name"]} for r in rows]})

    spelling_variants = []
    for normalized, spellings in sorted(ingredient_spellings.items()):
        if len(spellings) > 1:
            spelling_variants.append({"normalized": normalized, "spellings": sorted(spellings)})

    summary = {
        "catalog_total": len(recipes),
        "cocktails": sum(r.get("type") == "cocktail" for r in recipes),
        "mocktails": sum(r.get("type") == "mocktail" for r in recipes),
        "unique_ingredient_names": len(ingredient_spellings),
        "hard_errors": len(errors),
        "review_warnings": len(warnings),
        "ingredient_spelling_variant_groups": len(spelling_variants),
        "unit_counts": dict(sorted(unit_counts.items())),
    }
    report = {"summary": summary, "errors": errors, "warnings": warnings, "ingredient_spelling_variants": spelling_variants}
    DOCS.mkdir(parents=True, exist_ok=True)
    (DOCS / "catalog-deep-qa.json").write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    md = ["# Virtual Bartender Deep Catalog QA", "", "## Summary", ""]
    for k, v in summary.items():
        md.append(f"- **{k.replace('_', ' ')}:** `{json.dumps(v, ensure_ascii=False)}`")
    md += ["", "## Hard errors", ""]
    md += [f"- `{x['kind']}` — `{json.dumps(x, ensure_ascii=False)}`" for x in errors] or ["- None."]
    md += ["", "## Review warnings", ""]
    md += [f"- `{x['kind']}` — `{json.dumps(x, ensure_ascii=False)}`" for x in warnings] or ["- None."]
    md += ["", "## Ingredient spelling variants", ""]
    md += [f"- `{json.dumps(x, ensure_ascii=False)}`" for x in spelling_variants] or ["- None."]
    (DOCS / "catalog-deep-qa.md").write_text("\n".join(md) + "\n", encoding="utf-8")

    print(json.dumps(summary, indent=2))
    if errors:
        raise SystemExit(f"Deep catalog audit found {len(errors)} hard error(s)")


if __name__ == "__main__":
    main()
