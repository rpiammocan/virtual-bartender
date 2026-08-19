"""Create the production manifest for recipe-photo Batch 1.

This converts the Wikimedia candidate-review manifest into a conservative
production manifest. Only actual image files with an allowed license are
eligible. A candidate must also match the recipe name strongly enough to avoid
silently attaching unrelated images to a drink.
"""
from __future__ import annotations

import json
import re
import unicodedata
from pathlib import Path

CANDIDATE_PATH = Path("docs/recipe-photo-candidates-batch-1.json")
OUT_PATH = Path("docs/recipe-photo-production-batch-1.json")

STOPWORDS = {
    "and", "the", "a", "an", "of", "with", "style", "cocktail", "drink",
    "mocktail", "virgin", "classic", "hot",
}


def normalize(value: str) -> str:
    value = unicodedata.normalize("NFKD", value or "")
    value = "".join(ch for ch in value if not unicodedata.combining(ch))
    value = value.lower()
    value = re.sub(r"[^a-z0-9]+", " ", value)
    return " ".join(value.split())


def significant_tokens(name: str) -> list[str]:
    return [t for t in normalize(name).split() if t not in STOPWORDS and len(t) > 1]


def score_candidate(recipe_name: str, candidate: dict) -> int:
    if not candidate.get("license_allowed"):
        return -1
    if not str(candidate.get("mime", "")).startswith("image/"):
        return -1

    title = normalize(candidate.get("file_title", ""))
    description = normalize(candidate.get("description", ""))
    combined = f"{title} {description}".strip()
    recipe = normalize(recipe_name)
    tokens = significant_tokens(recipe_name)

    if recipe and recipe in title:
        return 100
    if recipe and recipe in combined:
        return 95
    if not tokens:
        return -1

    title_hits = sum(1 for token in tokens if token in title.split())
    combined_hits = sum(1 for token in tokens if token in combined.split())
    title_ratio = title_hits / len(tokens)
    combined_ratio = combined_hits / len(tokens)

    # Single-word names are risky (Casino, Aviation, etc.). Require an obvious
    # drink/cocktail context unless the full normalized recipe name appears.
    if len(tokens) == 1:
        drink_context = any(word in combined.split() for word in ("cocktail", "drink", "mocktail"))
        if title_hits == 1 and drink_context:
            return 85
        return -1

    if title_ratio == 1.0:
        return 90
    if combined_ratio == 1.0:
        return 85
    if title_ratio >= 0.75:
        return 80
    if combined_ratio >= 0.75:
        return 75
    return -1


def main() -> None:
    source = json.loads(CANDIDATE_PATH.read_text(encoding="utf-8"))
    recipes = []
    approved = 0

    for recipe in source["recipes"]:
        ranked = []
        for candidate in recipe.get("candidates", []):
            score = score_candidate(recipe["name"], candidate)
            if score >= 75:
                ranked.append((score, candidate))
        ranked.sort(key=lambda item: item[0], reverse=True)

        selected = None
        if ranked:
            score, candidate = ranked[0]
            selected = {
                "score": score,
                "file_title": candidate.get("file_title", ""),
                "commons_page": candidate.get("commons_page", ""),
                "download_url": candidate.get("original_url", ""),
                "mime": candidate.get("mime", ""),
                "license": candidate.get("license", ""),
                "license_url": candidate.get("license_url", ""),
                "artist": candidate.get("artist", ""),
                "credit": candidate.get("credit", ""),
            }
            approved += 1

        recipes.append({
            "key": recipe["key"],
            "name": recipe["name"],
            "recipe_type": recipe["recipe_type"],
            "source": recipe["source"],
            "output_file": f"{recipe['key']}.webp",
            "status": "approved_commons" if selected else "needs_original_or_manual_match",
            "selected": selected,
        })

    out = {
        "catalog_total": source["catalog_total"],
        "existing_image_total": source["existing_image_total"],
        "batch_size": source["batch_size"],
        "approved_commons_total": approved,
        "needs_original_or_manual_match_total": source["batch_size"] - approved,
        "policy": {
            "max_dimensions": [800, 800],
            "format": "WebP",
            "quality": 80,
            "crop": False,
            "allowed_license_families": source["policy"]["allowed_license_families"],
            "selection_note": "Only strongly name-matched image files are auto-approved; ambiguous results remain unresolved.",
        },
        "recipes": recipes,
    }
    OUT_PATH.write_text(json.dumps(out, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Approved Commons matches: {approved}/{source['batch_size']}")
    print(f"Wrote {OUT_PATH}")


if __name__ == "__main__":
    main()
