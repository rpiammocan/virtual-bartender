"""Integrate generated Batch 1 image metadata into the canonical CasaOS seed.

The image builder writes backend/app/recipe_photo_metadata_batch_1.json. This
script turns that mapping into a generated block in seed.py so the built-in
recipe rows receive their image path, source, license, and attribution on seed.
"""
from __future__ import annotations

import json
from pathlib import Path

SEED = Path("backend/app/seed.py")
METADATA = Path("backend/app/recipe_photo_metadata_batch_1.json")
START = "# BEGIN GENERATED BATCH 1 IMAGE METADATA"
END = "# END GENERATED BATCH 1 IMAGE METADATA"


def main() -> None:
    mapping = json.loads(METADATA.read_text(encoding="utf-8"))
    lines = [START]
    for key in sorted(mapping):
        data = mapping[key]
        lines.append(
            "IMAGE_METADATA[%r] = %r" % (key, data)
        )
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
    print(f"Integrated {len(mapping)} Batch 1 image metadata entries into {SEED}")


if __name__ == "__main__":
    main()
