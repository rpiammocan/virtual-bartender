#!/usr/bin/env python3
"""Final conservative recipe-image QA cleanup.

Removes only mappings whose Wikimedia source definitively depicts a different
recipe than the Virtual Bartender recipe using it.
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SEED = ROOT / "backend" / "app" / "seed.py"

REMOVE_IMAGE_KEYS = {
    "campari-tonic",  # source is gin & tonic with a Campari ice cube
    "rum-lemonade",   # source is a multi-spirit cocktail called Dirty Ash Tray
}


def main() -> None:
    text = SEED.read_text(encoding="utf-8")
    kept = []
    removed = 0
    for line in text.splitlines():
        stripped = line.strip()
        matched = any(
            stripped.startswith(f"IMAGE_METADATA[{key!r}]")
            or stripped.startswith(f'IMAGE_METADATA["{key}"]')
            for key in REMOVE_IMAGE_KEYS
        )
        if matched:
            removed += 1
        else:
            kept.append(line)

    if removed != len(REMOVE_IMAGE_KEYS):
        raise SystemExit(f"Expected to remove {len(REMOVE_IMAGE_KEYS)} mappings; removed {removed}")

    SEED.write_text("\n".join(kept) + "\n", encoding="utf-8")
    print(f"Removed {removed} final bad image mappings")


if __name__ == "__main__":
    main()
