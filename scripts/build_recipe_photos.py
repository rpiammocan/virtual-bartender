"""Build locally hosted Virtual Bartender recipe photos from Batch 1 manifest.

The production manifest is created from the successful Wikimedia candidate scan.
Only approved image candidates are downloaded. Images are resized proportionally
so the longest side is at most 800 px and saved as WebP quality 80. No cropping
or zooming is performed.
"""
from __future__ import annotations

import json
import time
from io import BytesIO
from pathlib import Path
from urllib.error import HTTPError
from urllib.request import Request, urlopen

from PIL import Image, ImageOps

MANIFEST = Path("docs/recipe-photo-production-batch-1.json")
REPORT = Path("docs/recipe-photo-build-report-batch-1.json")
METADATA = Path("backend/app/recipe_photo_metadata_batch_1.json")
OUT = Path("frontend/public/media")
OUT.mkdir(parents=True, exist_ok=True)

USER_AGENT = "VirtualBartender/1.0 (recipe-photo-builder; GitHub Actions)"
MAX_ATTEMPTS = 6
BASE_BACKOFF_SECONDS = 15
BETWEEN_IMAGES_SECONDS = 5


def download_with_retry(url: str, slug: str) -> bytes:
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
                wait_seconds = int(retry_after) if retry_after else BASE_BACKOFF_SECONDS * attempt
            except (TypeError, ValueError):
                wait_seconds = BASE_BACKOFF_SECONDS * attempt
            wait_seconds = max(wait_seconds, BASE_BACKOFF_SECONDS * attempt)
            print(
                f"Wikimedia rate-limited {slug} (HTTP 429). Waiting {wait_seconds}s "
                f"before retry {attempt + 1}/{MAX_ATTEMPTS}...",
                flush=True,
            )
            time.sleep(wait_seconds)
    raise RuntimeError(f"Unable to download {slug}")


def main() -> None:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    approved = [row for row in manifest["recipes"] if row.get("selected")]
    built_rows = []
    metadata = {}

    for index, row in enumerate(approved, 1):
        if index > 1:
            time.sleep(BETWEEN_IMAGES_SECONDS)
        key = row["key"]
        selected = row["selected"]
        print(f"[{index:03d}/{len(approved)}] Downloading {row['name']}...", flush=True)
        raw = download_with_retry(selected["download_url"], key)

        with Image.open(BytesIO(raw)) as source:
            image = ImageOps.exif_transpose(source).convert("RGB")
            image.thumbnail((800, 800), Image.Resampling.LANCZOS)
            dest = OUT / row["output_file"]
            image.save(dest, "WEBP", quality=80, method=6)
            size = dest.stat().st_size
            built_rows.append({
                "key": key,
                "name": row["name"],
                "file": str(dest),
                "width": image.width,
                "height": image.height,
                "bytes": size,
                "status": "built",
            })
            metadata[key] = {
                "image_path": f"/media/{row['output_file']}",
                "image_source_url": selected["commons_page"],
                "image_license": selected["license"],
                "image_attribution": selected["artist"] or selected["credit"] or selected["file_title"],
                "image_ai_generated": False,
            }
            print(f"  {dest}: {image.width}x{image.height}, {size} bytes", flush=True)

    unresolved = [
        {"key": row["key"], "name": row["name"], "status": row["status"]}
        for row in manifest["recipes"] if not row.get("selected")
    ]
    report = {
        "catalog_total": manifest["catalog_total"],
        "existing_image_total_before_batch": manifest["existing_image_total"],
        "batch_size": manifest["batch_size"],
        "approved_for_build": len(approved),
        "built_total": len(built_rows),
        "unresolved_total": len(unresolved),
        "expected_integrated_total_after_build": manifest["existing_image_total"] + len(built_rows),
        "built": built_rows,
        "unresolved": unresolved,
    }
    REPORT.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    METADATA.write_text(json.dumps(metadata, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Built {len(built_rows)} images; {len(unresolved)} remain unresolved.")
    print(f"Wrote {REPORT}")
    print(f"Wrote {METADATA}")


if __name__ == "__main__":
    main()
