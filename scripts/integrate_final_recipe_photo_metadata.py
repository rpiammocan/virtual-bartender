"""Integrate final recipe-photo metadata into the canonical seed.

Generated assignments intentionally appear after the base IMAGE_METADATA literal,
so corrections such as Margarita override earlier metadata safely.
"""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SEED = ROOT / "backend/app/seed.py"
METADATA = ROOT / "backend/app/recipe_photo_metadata_final.json"
START = "# BEGIN GENERATED FINAL IMAGE METADATA"
END = "# END GENERATED FINAL IMAGE METADATA"


def main() -> None:
    mapping = json.loads(METADATA.read_text(encoding="utf-8"))
    lines = [START]
    for key in sorted(mapping):
        lines.append("IMAGE_METADATA[%r] = %r" % (key, mapping[key]))
    lines.append(END)
    block = "\n".join(lines)

    text = SEED.read_text(encoding="utf-8")
    if START in text and END in text:
        before = text.split(START, 1)[0].rstrip()
        after = text.split(END, 1)[1].lstrip("\n")
        text = before + "\n\n" + block + "\n\n" + after
    else:
        marker = "\n\nBASE_RECIPES = ["
        if marker not in text:
            raise SystemExit("Could not locate BASE_RECIPES marker in seed.py")
        text = text.replace(marker, "\n\n" + block + marker, 1)

    SEED.write_text(text, encoding="utf-8")
    print(f"Integrated {len(mapping)} final image metadata entries into {SEED.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
