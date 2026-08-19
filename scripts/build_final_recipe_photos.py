"""Build approved final Commons photos plus a corrected Margarita image."""
from __future__ import annotations

import hashlib
import json
import time
from io import BytesIO
from pathlib import Path
from urllib.error import HTTPError
from urllib.request import Request, urlopen

from PIL import Image, ImageOps

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "docs/recipe-photo-final-production.json"
REPORT = ROOT / "docs/recipe-photo-final-build-report.json"
METADATA = ROOT / "backend/app/recipe_photo_metadata_final.json"
OUT = ROOT / "frontend/public/media"
OUT.mkdir(parents=True, exist_ok=True)

USER_AGENT = "VirtualBartender/1.0 (final-recipe-photo-builder; GitHub Actions)"
MAX_ATTEMPTS = 6
BASE_BACKOFF_SECONDS = 15
BETWEEN_IMAGES_SECONDS = 5

MARGARITA = {
    "key": "margarita",
    "name": "Margarita",
    "output_file": "margarita.webp",
    "download_url": "https://commons.wikimedia.org/wiki/Special:Redirect/file/MargaritaReal.jpg",
    "commons_page": "https://commons.wikimedia.org/wiki/File:MargaritaReal.jpg",
    "license": "CC BY-SA 3.0",
    "artist": "Akke Monasso",
}


def download(url: str, slug: str) -> bytes:
    for attempt in range(1, MAX_ATTEMPTS + 1):
        try:
            req = Request(url, headers={"User-Agent": USER_AGENT})
            with urlopen(req, timeout=90) as response:
                return response.read()
        except HTTPError as exc:
            if exc.code != 429 or attempt == MAX_ATTEMPTS:
                raise
            retry_after = exc.headers.get("Retry-After")
            try:
                wait = int(retry_after) if retry_after else BASE_BACKOFF_SECONDS * attempt
            except (TypeError, ValueError):
                wait = BASE_BACKOFF_SECONDS * attempt
            wait = max(wait, BASE_BACKOFF_SECONDS * attempt)
            print(f"Wikimedia rate limit for {slug}: waiting {wait}s before retry {attempt + 1}/{MAX_ATTEMPTS}...", flush=True)
            time.sleep(wait)
    raise RuntimeError(f"Unable to download {slug}")


def build_one(row: dict, selected: dict) -> tuple[dict, dict, str]:
    key = row["key"]
    raw = download(selected["download_url"], key)
    with Image.open(BytesIO(raw)) as source:
        image = ImageOps.exif_transpose(source).convert("RGB")
        image.thumbnail((800, 800), Image.Resampling.LANCZOS)
        dest = OUT / row["output_file"]
        image.save(dest, "WEBP", quality=80, method=6)
    digest = hashlib.sha256(dest.read_bytes()).hexdigest()
    built = {
        "key": key,
        "name": row["name"],
        "file": str(dest.relative_to(ROOT)),
        "width": image.width,
        "height": image.height,
        "bytes": dest.stat().st_size,
        "sha256": digest,
    }
    meta = {
        "image_path": f"/media/{row['output_file']}",
        "image_source_url": selected["commons_page"],
        "image_license": selected["license"],
        "image_attribution": selected.get("artist") or selected.get("credit") or selected.get("file_title") or row["name"],
        "image_ai_generated": False,
    }
    return built, meta, digest


def main() -> None:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    built = []
    metadata = {}
    hashes: dict[str, str] = {}
    duplicate_hashes = []

    queue = list(manifest["selected"])
    for index, row in enumerate(queue, 1):
        if index > 1:
            time.sleep(BETWEEN_IMAGES_SECONDS)
        print(f"[{index:03d}/{len(queue)}] {row['name']}", flush=True)
        built_row, meta, digest = build_one(row, row["selected"])
        if digest in hashes:
            duplicate_hashes.append({"key": row["key"], "duplicate_of": hashes[digest], "sha256": digest})
            Path(built_row["file"]).unlink(missing_ok=True) if Path(built_row["file"]).is_absolute() else (ROOT / built_row["file"]).unlink(missing_ok=True)
            print(f"  rejected duplicate output of {hashes[digest]}", flush=True)
            continue
        hashes[digest] = row["key"]
        built.append(built_row)
        metadata[row["key"]] = meta
        print(f"  {built_row['width']}x{built_row['height']}, {built_row['bytes']} bytes", flush=True)

    # Required correction: replace the old Margarita asset/source with an
    # unambiguous photograph explicitly identified by Commons as a Margarita.
    print("Building corrected Margarita image...", flush=True)
    margarita_selected = {
        "download_url": MARGARITA["download_url"],
        "commons_page": MARGARITA["commons_page"],
        "license": MARGARITA["license"],
        "artist": MARGARITA["artist"],
    }
    margarita_built, margarita_meta, margarita_digest = build_one(MARGARITA, margarita_selected)
    metadata["margarita"] = margarita_meta
    built.append(margarita_built)

    report = {
        "catalog_total": manifest["catalog_total"],
        "starting_image_total": manifest["starting_image_total"],
        "approved_unique_commons_total": manifest["approved_unique_commons_total"],
        "built_new_recipe_images_total": len([r for r in built if r["key"] != "margarita"]),
        "margarita_corrected": True,
        "duplicate_output_hashes_rejected_total": len(duplicate_hashes),
        "duplicate_output_hashes_rejected": duplicate_hashes,
        "needs_original_image_total_before_hash_rejections": manifest["needs_original_image_total"],
        "expected_image_total_after_build": manifest["starting_image_total"] + len([r for r in built if r["key"] != "margarita"]),
        "built": built,
    }
    METADATA.write_text(json.dumps(metadata, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    REPORT.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Built new final recipe images: {report['built_new_recipe_images_total']}")
    print(f"Duplicate output hashes rejected: {len(duplicate_hashes)}")
    print(f"Margarita corrected: yes")
    print(f"Expected coverage: {report['expected_image_total_after_build']}/{manifest['catalog_total']}")


if __name__ == "__main__":
    main()
