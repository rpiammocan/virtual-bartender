"""Create the final duplicate-safe Commons production manifest.

Reads the 242-recipe discovery result. Only licensed image files with a strong
recipe-name match are selected. A Commons source/file may be assigned to only
one recipe, and sources already used by the canonical seed are excluded.
Ambiguous recipes remain unresolved for an original Virtual Bartender image.
"""
from __future__ import annotations

import ast
import json
import re
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CANDIDATES = ROOT / "docs/recipe-photo-final-candidates.json"
SEED = ROOT / "backend/app/seed.py"
OUT = ROOT / "docs/recipe-photo-final-production.json"

STOPWORDS = {"a", "an", "and", "the", "of", "with", "style", "cocktail", "drink", "mocktail", "virgin"}
DRINK_WORDS = {"cocktail", "drink", "mocktail", "highball", "sour", "spritz", "fizz", "punch", "mule", "martini", "daiquiri"}


def norm(value: str) -> str:
    value = unicodedata.normalize("NFKD", value or "")
    value = "".join(c for c in value if not unicodedata.combining(c)).lower()
    return " ".join(re.sub(r"[^a-z0-9]+", " ", value).split())


def tokens(value: str) -> list[str]:
    return [t for t in norm(value).split() if len(t) > 1 and t not in STOPWORDS]


def existing_sources_from_seed() -> set[str]:
    """Read literal IMAGE_METADATA declarations without importing the backend."""
    tree = ast.parse(SEED.read_text(encoding="utf-8"))
    sources: set[str] = set()
    for node in ast.walk(tree):
        value = None
        if isinstance(node, ast.Assign):
            # IMAGE_METADATA = {...}
            if any(isinstance(t, ast.Name) and t.id == "IMAGE_METADATA" for t in node.targets):
                try:
                    mapping = ast.literal_eval(node.value)
                except Exception:
                    mapping = None
                if isinstance(mapping, dict):
                    for meta in mapping.values():
                        if isinstance(meta, dict) and meta.get("image_source_url"):
                            sources.add(str(meta["image_source_url"]))
            # IMAGE_METADATA['key'] = {...}
            for target in node.targets:
                if isinstance(target, ast.Subscript) and isinstance(target.value, ast.Name) and target.value.id == "IMAGE_METADATA":
                    try:
                        value = ast.literal_eval(node.value)
                    except Exception:
                        value = None
                    if isinstance(value, dict) and value.get("image_source_url"):
                        sources.add(str(value["image_source_url"]))
    return sources


def candidate_score(recipe_name: str, c: dict) -> int:
    if not c.get("license_allowed") or not str(c.get("mime", "")).startswith("image/"):
        return -1
    title = norm(c.get("file_title", ""))
    desc = norm(c.get("description", ""))
    combined = f"{title} {desc}"
    recipe = norm(recipe_name)
    rtokens = tokens(recipe_name)
    if not rtokens:
        return -1

    # Strongest evidence: exact normalized recipe phrase appears in filename.
    if recipe and recipe in title:
        return 100
    if recipe and recipe in desc:
        return 96

    words = set(combined.split())
    hit_all = all(t in words for t in rtokens)
    drink_context = bool(words & DRINK_WORDS)

    # Multi-token formulas may omit connectors such as "and", but every
    # meaningful recipe token plus explicit drink context is required.
    if len(rtokens) >= 2 and hit_all and drink_context:
        return 88

    # Single-word names are especially collision-prone (Casino, Aviation...).
    # Require that word in the filename and explicit beverage context.
    if len(rtokens) == 1 and rtokens[0] in set(title.split()) and drink_context:
        return 82
    return -1


def main() -> None:
    data = json.loads(CANDIDATES.read_text(encoding="utf-8"))
    used_pages = existing_sources_from_seed()
    used_titles: set[str] = set()
    selected_rows = []
    unresolved_rows = []
    duplicate_rejections = []

    for recipe in data["recipes"]:
        ranked = []
        for c in recipe.get("candidates", []):
            score = candidate_score(recipe["name"], c)
            if score >= 82:
                ranked.append((score, c))
        ranked.sort(key=lambda x: x[0], reverse=True)

        chosen = None
        for score, c in ranked:
            page = str(c.get("commons_page", ""))
            title = str(c.get("file_title", ""))
            title_key = norm(title)
            if page in used_pages or title_key in used_titles:
                duplicate_rejections.append({"recipe": recipe["name"], "file_title": title, "commons_page": page})
                continue
            chosen = (score, c)
            used_pages.add(page)
            used_titles.add(title_key)
            break

        base = {"key": recipe["key"], "name": recipe["name"], "recipe_type": recipe["recipe_type"], "output_file": f"{recipe['key']}.webp"}
        if chosen:
            score, c = chosen
            selected_rows.append({**base, "status": "approved_commons", "selected": {
                "score": score,
                "file_title": c.get("file_title", ""),
                "commons_page": c.get("commons_page", ""),
                "download_url": c.get("original_url", ""),
                "mime": c.get("mime", ""),
                "license": c.get("license", ""),
                "license_url": c.get("license_url", ""),
                "artist": c.get("artist", ""),
                "credit": c.get("credit", ""),
            }})
        else:
            unresolved_rows.append({**base, "status": "needs_original_image"})

    out = {
        "catalog_total": data["catalog_total"],
        "starting_image_total": data.get("existing_image_total", 68),
        "final_batch_size": data["batch_size"],
        "approved_unique_commons_total": len(selected_rows),
        "needs_original_image_total": len(unresolved_rows),
        "duplicate_candidate_rejections_total": len(duplicate_rejections),
        "policy": {
            "image_files_only": True,
            "strong_name_match_required": True,
            "unique_commons_source_required": True,
            "max_dimensions": [800, 800],
            "format": "WebP",
            "quality": 80,
            "crop": False,
        },
        "selected": selected_rows,
        "unresolved": unresolved_rows,
        "duplicate_rejections": duplicate_rejections,
    }
    OUT.write_text(json.dumps(out, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Unique Commons approvals: {len(selected_rows)}/{data['batch_size']}")
    print(f"Needs original image: {len(unresolved_rows)}")
    print(f"Duplicate candidates rejected: {len(duplicate_rejections)}")
    print(f"Wrote {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
