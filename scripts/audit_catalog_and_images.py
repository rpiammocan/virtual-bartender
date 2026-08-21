#!/usr/bin/env python3
"""Audit the canonical Virtual Bartender catalog and recipe-image metadata.

This is intentionally conservative: hard structural problems are separated from
review warnings so a heuristic photo/name mismatch never breaks a build.
"""
from __future__ import annotations

import ast
import hashlib
import json
import re
from collections import Counter, defaultdict
from pathlib import Path
from urllib.parse import unquote, urlparse

ROOT = Path(__file__).resolve().parents[1]
APP = ROOT / "backend" / "app"
MEDIA = ROOT / "frontend" / "public" / "media"
LEGACY_MEDIA = ROOT / "data" / "images"
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

STOP_WORDS = {
    "a", "an", "and", "at", "cocktail", "cocktails", "drink", "drinks", "glass",
    "image", "in", "of", "on", "the", "with", "recipe", "mocktail", "mocktails",
}

ALCOHOL_MARKERS = (
    "bourbon", "whiskey", "whisky", "rye whiskey", "scotch", "gin", "vodka",
    "white rum", "dark rum", "gold rum", "aged rum", "tequila", "mezcal", "cognac",
    "brandy", "campari", "aperol", "amaretto", "vermouth", "chartreuse", "liqueur",
    "cointreau", "triple sec", "pisco", "cacha", "prosecco", "champagne", "wine",
    "absinthe", "sherry", "port", "fernet", "galliano", "maraschino", "benedictine",
    "drambuie", "irish cream", "coffee liqueur", "creme de", "crème de", "aguardiente",
    "grappa",
)

NONALCOHOLIC_EXCEPTIONS = {
    "ginger beer", "root beer", "maraschino cherry", "maraschino cherries",
}


def assignments(source: str) -> dict[str, object]:
    tree = ast.parse(source)
    out: dict[str, object] = {}
    for node in tree.body:
        if not isinstance(node, ast.Assign) or len(node.targets) != 1:
            continue
        target = node.targets[0]
        if not isinstance(target, ast.Name):
            continue
        try:
            out[target.id] = ast.literal_eval(node.value)
        except (ValueError, TypeError):
            pass
    return out


def find_base_recipes(values: dict[str, object]) -> list[dict]:
    candidates = []
    for name, value in values.items():
        if isinstance(value, list) and value and all(isinstance(x, dict) for x in value):
            if all("key" in x and "ingredients" in x for x in value):
                candidates.append((name, value))
    if not candidates:
        raise RuntimeError("Could not locate base recipe list in seed.py")
    candidates.sort(key=lambda pair: ("recipe" not in pair[0].lower(), -len(pair[1])))
    return candidates[0][1]


def image_metadata(source: str) -> dict[str, dict]:
    tree = ast.parse(source)
    out: dict[str, dict] = {}
    for node in tree.body:
        if not isinstance(node, ast.Assign) or len(node.targets) != 1:
            continue
        target = node.targets[0]
        if isinstance(target, ast.Name) and target.id == "IMAGE_METADATA":
            try:
                value = ast.literal_eval(node.value)
            except (ValueError, TypeError):
                continue
            if isinstance(value, dict):
                out.update(value)
            continue
        if isinstance(target, ast.Subscript) and isinstance(target.value, ast.Name) and target.value.id == "IMAGE_METADATA":
            try:
                key = ast.literal_eval(target.slice)
                value = ast.literal_eval(node.value)
            except (ValueError, TypeError):
                continue
            if isinstance(key, str) and isinstance(value, dict):
                out[key] = value
    return out


def load_recipes() -> list[dict]:
    recipes: list[dict] = []
    for filename, variable in SOURCES:
        values = assignments((APP / filename).read_text(encoding="utf-8"))
        rows = values[variable] if variable else find_base_recipes(values)
        recipes.extend(rows)
    return recipes


def norm(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "", text.casefold())


def tokens(text: str) -> set[str]:
    words = re.findall(r"[a-z0-9]+", unquote(text).casefold())
    return {word for word in words if len(word) > 2 and word not in STOP_WORDS}


def source_filename(url: str | None) -> str:
    if not url:
        return ""
    parsed = urlparse(url)
    return Path(unquote(parsed.path)).name


def formula(recipe: dict) -> tuple:
    rows = []
    for ingredient, quantity, unit, optional in recipe.get("ingredients", []):
        rows.append((norm(str(ingredient)), str(quantity), str(unit).casefold(), bool(optional)))
    return tuple(sorted(rows))


def is_alcoholic_ingredient(name: str) -> bool:
    lower = name.casefold().strip()
    if lower in NONALCOHOLIC_EXCEPTIONS:
        return False
    return any(marker in lower for marker in ALCOHOL_MARKERS)


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def locate_image(filename: str) -> Path | None:
    for directory in (MEDIA, LEGACY_MEDIA):
        candidate = directory / filename
        if candidate.exists():
            return candidate
    return None


def main() -> None:
    recipes = load_recipes()
    seed_text = (APP / "seed.py").read_text(encoding="utf-8")
    images = image_metadata(seed_text)
    by_key = {row["key"]: row for row in recipes}

    errors: list[dict] = []
    warnings: list[dict] = []

    key_counts = Counter(row["key"] for row in recipes)
    for key, count in sorted(key_counts.items()):
        if count > 1:
            errors.append({"kind": "duplicate_key", "key": key, "count": count})

    normalized_names: dict[str, list[dict]] = defaultdict(list)
    for row in recipes:
        normalized_names[norm(row["name"])].append(row)
    for _, rows in sorted(normalized_names.items()):
        if len(rows) > 1:
            warnings.append({"kind": "normalized_name_collision", "recipes": [{"key": r["key"], "name": r["name"]} for r in rows]})

    formulas: dict[tuple, list[dict]] = defaultdict(list)
    for row in recipes:
        formulas[formula(row)].append(row)
    for rows in formulas.values():
        if len(rows) > 1:
            warnings.append({"kind": "identical_formula", "recipes": [{"key": r["key"], "name": r["name"]} for r in rows]})

    recipe_keys = set(by_key)
    for row in recipes:
        parent = row.get("parent")
        if parent and parent not in recipe_keys:
            errors.append({"kind": "missing_parent", "key": row["key"], "parent": parent})
        if row.get("type") not in {"cocktail", "mocktail"}:
            errors.append({"kind": "invalid_type", "key": row["key"], "type": row.get("type")})
        has_alcohol = any(is_alcoholic_ingredient(str(i[0])) for i in row.get("ingredients", []))
        if row.get("type") == "mocktail" and has_alcohol:
            warnings.append({"kind": "mocktail_contains_alcohol_marker", "key": row["key"], "name": row["name"]})
        if row.get("type") == "cocktail" and not has_alcohol:
            warnings.append({"kind": "cocktail_without_alcohol_marker", "key": row["key"], "name": row["name"]})

    existing_image_files: dict[str, Path] = {}
    image_hashes: dict[str, list[str]] = defaultdict(list)
    source_urls: dict[str, list[str]] = defaultdict(list)
    ai_count = 0
    real_count = 0

    for key, meta in sorted(images.items()):
        if key not in by_key:
            warnings.append({"kind": "image_metadata_without_recipe", "key": key})
        path_value = str(meta.get("image_path") or "")
        if not path_value:
            errors.append({"kind": "image_metadata_missing_path", "key": key})
            continue
        filename = Path(path_value).name
        file_path = locate_image(filename)
        if file_path is None:
            errors.append({"kind": "image_file_missing", "key": key, "path": path_value})
        else:
            existing_image_files[key] = file_path
            image_hashes[sha256(file_path)].append(key)

        ai = bool(meta.get("image_ai_generated"))
        if ai:
            ai_count += 1
            if not meta.get("image_license") or not meta.get("image_attribution"):
                warnings.append({"kind": "ai_image_missing_label_metadata", "key": key})
        else:
            real_count += 1
            for field in ("image_source_url", "image_license", "image_attribution"):
                if not meta.get(field):
                    errors.append({"kind": "real_image_missing_attribution", "key": key, "field": field})
            source_url = str(meta.get("image_source_url") or "")
            if source_url:
                source_urls[source_url].append(key)
                recipe = by_key.get(key)
                if recipe:
                    name_tokens = tokens(recipe["name"])
                    source_tokens = tokens(source_filename(source_url))
                    if name_tokens and source_tokens and not (name_tokens & source_tokens):
                        warnings.append({
                            "kind": "suspicious_image_name_match",
                            "key": key,
                            "name": recipe["name"],
                            "source_file": source_filename(source_url),
                        })

    for digest, keys in image_hashes.items():
        if len(keys) > 1:
            warnings.append({"kind": "duplicate_image_bytes", "keys": sorted(keys), "sha256": digest})
    for url, keys in source_urls.items():
        if len(keys) > 1:
            warnings.append({"kind": "duplicate_image_source", "keys": sorted(keys), "source_url": url})

    recipes_with_images = len(set(images) & recipe_keys)
    recipes_without_images = len(recipes) - recipes_with_images

    summary = {
        "catalog_total": len(recipes),
        "cocktails": sum(row.get("type") == "cocktail" for row in recipes),
        "mocktails": sum(row.get("type") == "mocktail" for row in recipes),
        "image_metadata_total": len(images),
        "recipes_with_images": recipes_with_images,
        "recipes_without_images": recipes_without_images,
        "real_source_images": real_count,
        "ai_generated_images": ai_count,
        "existing_image_files": len(existing_image_files),
        "hard_errors": len(errors),
        "review_warnings": len(warnings),
    }

    report = {"summary": summary, "errors": errors, "warnings": warnings}
    DOCS.mkdir(parents=True, exist_ok=True)
    (DOCS / "catalog-image-qa.json").write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    lines = [
        "# Virtual Bartender Catalog + Image QA",
        "",
        "Generated by `scripts/audit_catalog_and_images.py`.",
        "",
        "## Summary",
        "",
    ]
    for key, value in summary.items():
        lines.append(f"- **{key.replace('_', ' ')}:** {value}")
    lines.extend(["", "## Hard errors", ""])
    if errors:
        lines.extend(f"- `{item['kind']}` — `{json.dumps(item, ensure_ascii=False)}`" for item in errors)
    else:
        lines.append("- None.")
    lines.extend(["", "## Review warnings", ""])
    if warnings:
        lines.extend(f"- `{item['kind']}` — `{json.dumps(item, ensure_ascii=False)}`" for item in warnings)
    else:
        lines.append("- None.")
    (DOCS / "catalog-image-qa.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(json.dumps(summary, indent=2))
    if errors:
        raise SystemExit(f"Audit found {len(errors)} hard error(s); see docs/catalog-image-qa.md")


if __name__ == "__main__":
    main()
