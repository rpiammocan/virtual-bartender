"""Create a deterministic recipe-photo production batch from the canonical catalog.

The CasaOS catalog is the source of truth. This script reports the exact catalog
size, existing image coverage, and selects the next N recipes without image
metadata in case-insensitive alphabetical order.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))

from app.seed import (  # noqa: E402
    BASE_RECIPES,
    IMAGE_METADATA,
)
from app.catalog_v2 import RECIPES_V2  # noqa: E402
from app.catalog_v3 import RECIPES_V3  # noqa: E402
from app.catalog_v4 import RECIPES_V4  # noqa: E402
from app.catalog_v5 import RECIPES_V5  # noqa: E402
from app.catalog_v6 import RECIPES_V6  # noqa: E402
from app.catalog_v7 import RECIPES_V7  # noqa: E402
from app.catalog_v8 import RECIPES_V8  # noqa: E402

ALL_RECIPES = (
    BASE_RECIPES
    + RECIPES_V2
    + RECIPES_V3
    + RECIPES_V4
    + RECIPES_V5
    + RECIPES_V6
    + RECIPES_V7
    + RECIPES_V8
)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--size", type=int, default=100)
    parser.add_argument("--output", default="docs/recipe-photo-batch-1.json")
    args = parser.parse_args()

    seen: set[str] = set()
    unique = []
    duplicates = []
    for recipe in ALL_RECIPES:
        key = recipe["key"]
        if key in seen:
            duplicates.append(key)
            continue
        seen.add(key)
        unique.append(recipe)

    existing = sorted(key for key in IMAGE_METADATA if key in seen)
    missing = sorted(
        (r for r in unique if r["key"] not in IMAGE_METADATA),
        key=lambda r: (r["name"].casefold(), r["key"]),
    )
    batch = missing[: args.size]

    report = {
        "catalog_total": len(unique),
        "image_metadata_total": len(existing),
        "missing_image_total": len(missing),
        "batch_size_requested": args.size,
        "batch_size_selected": len(batch),
        "duplicate_catalog_keys_ignored": duplicates,
        "existing_image_keys": existing,
        "batch": [
            {
                "key": r["key"],
                "name": r["name"],
                "recipe_type": r["type"],
                "source": r.get("source"),
            }
            for r in batch
        ],
    }

    output = ROOT / args.output
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    print(f"Catalog recipes: {report['catalog_total']}")
    print(f"Recipes with image metadata: {report['image_metadata_total']}")
    print(f"Recipes still needing images: {report['missing_image_total']}")
    print(f"Batch selected: {report['batch_size_selected']}")
    print(f"Wrote {output.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
