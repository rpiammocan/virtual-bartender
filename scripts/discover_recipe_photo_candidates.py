"""Discover Wikimedia Commons image candidates for a recipe-photo batch.

Reads a planner JSON and writes a review manifest containing up to five Commons
candidates per recipe, including source URL and license metadata. Nothing is
automatically approved or downloaded into the application.
"""
from __future__ import annotations

import argparse
import json
import time
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import Request, urlopen
from urllib.error import HTTPError

API = "https://commons.wikimedia.org/w/api.php"
UA = "VirtualBartender/1.0 recipe-photo-candidate-discovery"
ALLOWED_LICENSE_HINTS = ("CC0", "Public domain", "CC BY", "CC BY-SA")


def api(params: dict) -> dict:
    params = {**params, "format": "json", "formatversion": 2}
    url = API + "?" + urlencode(params)
    delay = 4
    for attempt in range(7):
        try:
            req = Request(url, headers={"User-Agent": UA})
            with urlopen(req, timeout=60) as response:
                return json.loads(response.read().decode("utf-8"))
        except HTTPError as exc:
            if exc.code == 429 and attempt < 6:
                retry_after = exc.headers.get("Retry-After")
                try:
                    wait = int(retry_after) if retry_after else delay
                except (TypeError, ValueError):
                    wait = delay
                wait = max(wait, delay)
                print(f"Wikimedia rate limit: waiting {wait}s before retry...", flush=True)
                time.sleep(wait)
                delay = min(delay * 2, 120)
                continue
            raise


def clean_html(value: str | None) -> str:
    if not value:
        return ""
    import re
    return re.sub(r"<[^>]+>", "", value).replace("&nbsp;", " ").strip()


def ext(meta: dict, key: str) -> str:
    value = meta.get(key, {})
    if isinstance(value, dict):
        return clean_html(str(value.get("value", "")))
    return ""


def search_candidates(name: str) -> list[dict]:
    queries = [f'"{name}" cocktail', f'"{name}" drink', name]
    seen: set[str] = set()
    titles: list[str] = []
    for query in queries:
        data = api({"action": "query", "list": "search", "srsearch": query, "srnamespace": 6, "srlimit": 8})
        for row in data.get("query", {}).get("search", []):
            title = row.get("title", "")
            if title and title not in seen:
                seen.add(title)
                titles.append(title)
            if len(titles) >= 8:
                break
        if len(titles) >= 5:
            break
        time.sleep(0.6)

    candidates: list[dict] = []
    for title in titles[:8]:
        data = api({
            "action": "query",
            "titles": title,
            "prop": "imageinfo",
            "iiprop": "url|extmetadata|size|mime",
        })
        pages = data.get("query", {}).get("pages", [])
        if not pages or "imageinfo" not in pages[0]:
            continue
        info = pages[0]["imageinfo"][0]
        meta = info.get("extmetadata", {})
        license_name = ext(meta, "LicenseShortName") or ext(meta, "UsageTerms")
        acceptable = any(h.lower() in license_name.lower() for h in ALLOWED_LICENSE_HINTS)
        candidates.append({
            "file_title": title,
            "commons_page": info.get("descriptionurl", ""),
            "original_url": info.get("url", ""),
            "mime": info.get("mime", ""),
            "width": info.get("width"),
            "height": info.get("height"),
            "license": license_name,
            "license_url": ext(meta, "LicenseUrl"),
            "artist": ext(meta, "Artist"),
            "credit": ext(meta, "Credit"),
            "description": ext(meta, "ImageDescription"),
            "license_allowed": acceptable,
        })
        time.sleep(0.6)
        if len(candidates) >= 5:
            break
    return candidates


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--batch", default="docs/recipe-photo-batch-1.json")
    parser.add_argument("--output", default="docs/recipe-photo-candidates-batch-1.json")
    args = parser.parse_args()

    batch_path = Path(args.batch)
    out_path = Path(args.output)
    batch = json.loads(batch_path.read_text(encoding="utf-8"))
    rows = batch["batch"]
    out = {
        "catalog_total": batch["catalog_total"],
        "existing_image_total": batch["image_metadata_total"],
        "batch_size": len(rows),
        "policy": {
            "auto_approved": False,
            "allowed_license_families": list(ALLOWED_LICENSE_HINTS),
            "note": "Candidates require recipe-name/visual review before production use.",
        },
        "recipes": [],
    }
    for index, recipe in enumerate(rows, 1):
        print(f"[{index:03d}/{len(rows)}] {recipe['name']}", flush=True)
        candidates = search_candidates(recipe["name"])
        out["recipes"].append({**recipe, "candidates": candidates})
        time.sleep(1.0)

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(out, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Wrote {out_path}")


if __name__ == "__main__":
    main()
