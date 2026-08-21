#!/usr/bin/env python3
"""Second conservative recipe-image QA cleanup.

Remove only mappings whose source filename makes it clear that the retained
asset depicts a different named cocktail, a non-drink object/document, or an
unrelated beverage. Recipes themselves remain untouched.
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SEED = ROOT / "backend" / "app" / "seed.py"

REMOVE_IMAGE_KEYS = {
    "aperol-spritz",              # source is explicitly a different cocktail: Mitch
    "basil-lime-soda",            # Alinea course photo, not a matching drink
    "brandy-cola",                # Kirk-a-kola asset, not a Brandy and Cola photo
    "club-pineapple-mocktail",    # scanned historical recipe-book page
    "dark-rum-pineapple",         # source is explicitly a Zombie cocktail
    "dark-rum-sour",              # source is Davy Jones's Locker punch
    "pineapple-ginger-mocktail",  # source is Nigerian sobo juice
    "tequila-orange",             # source is Mardi Gras/Mexican Melon, different drinks
    "vodka-pineapple",            # source is explicitly a Catwalk cocktail
}


def main() -> None:
    text = SEED.read_text(encoding="utf-8")
    kept = []
    removed = []
    for line in text.splitlines():
        stripped = line.strip()
        matched = None
        for key in REMOVE_IMAGE_KEYS:
            if stripped.startswith(f"IMAGE_METADATA[{key!r}]") or stripped.startswith(f'IMAGE_METADATA["{key}"]'):
                matched = key
                break
        if matched:
            removed.append(matched)
        else:
            kept.append(line)

    missing = sorted(REMOVE_IMAGE_KEYS - set(removed))
    if missing:
        raise SystemExit(f"Expected image mappings were not found: {', '.join(missing)}")

    SEED.write_text("\n".join(kept) + "\n", encoding="utf-8")
    print(f"Removed {len(removed)} clearly mismatched image mappings:")
    for key in sorted(removed):
        print(f"- {key}")


if __name__ == "__main__":
    main()
