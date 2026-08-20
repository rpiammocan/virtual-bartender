"""Integrate approved AI recipe image metadata into the canonical CasaOS seed."""
from __future__ import annotations

import json
from pathlib import Path

SEED = Path("backend/app/seed.py")
METADATA = Path("backend/app/recipe_photo_metadata_ai_approved.json")
START = "# BEGIN APPROVED AI IMAGE METADATA"
END = "# END APPROVED AI IMAGE METADATA"


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
        marker = "# END GENERATED FINAL IMAGE METADATA"
        if marker not in text:
            raise SystemExit("Could not locate final image metadata marker in seed.py")
        text = text.replace(marker, marker + "\n\n" + block, 1)

    SEED.write_text(text, encoding="utf-8")
    print(f"Integrated {len(mapping)} approved AI image entries into {SEED}")


if __name__ == "__main__":
    main()
