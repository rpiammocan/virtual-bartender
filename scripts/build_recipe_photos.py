"""Build locally hosted Virtual Bartender recipe photos from licensed sources.

Each source image is downloaded from Wikimedia Commons, resized proportionally so
its longest side is at most 800 px, and saved as WebP at quality 80. No cropping
or zooming is performed.
"""
from pathlib import Path
from urllib.request import Request, urlopen
from urllib.error import HTTPError
from io import BytesIO
import time
from PIL import Image, ImageOps

OUT = Path("frontend/public/media")
OUT.mkdir(parents=True, exist_ok=True)

PHOTOS = {
    "manhattan": "https://commons.wikimedia.org/wiki/Special:Redirect/file/Manhattan_Cocktail.jpg",
    "dry-martini": "https://commons.wikimedia.org/wiki/Special:Redirect/file/Dry_martini.jpg",
    "negroni": "https://commons.wikimedia.org/wiki/Special:Redirect/file/Negroni_(cocktail).jpg",
    "sidecar": "https://commons.wikimedia.org/wiki/Special:Redirect/file/Sidecar-cocktail.jpg",
    "singapore-sling": "https://commons.wikimedia.org/wiki/Special:Redirect/file/Singapore_Sling_Cocktail.jpg",
    "whiskey-sour": "https://commons.wikimedia.org/wiki/Special:Redirect/file/Whiskey_Sour.jpg",
    "pina-colada": "https://commons.wikimedia.org/wiki/Special:Redirect/file/Pina_Colada_(Cocktail).jpg",
}

USER_AGENT = "VirtualBartender/1.0 (recipe-photo-builder; GitHub Actions)"
MAX_ATTEMPTS = 6
BASE_BACKOFF_SECONDS = 15
BETWEEN_IMAGES_SECONDS = 8


def download_with_retry(url: str, slug: str) -> bytes:
    """Download one image while respecting Wikimedia rate limits."""
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
                f"  Wikimedia rate-limited {slug} (HTTP 429). "
                f"Waiting {wait_seconds}s before retry {attempt + 1}/{MAX_ATTEMPTS}...",
                flush=True,
            )
            time.sleep(wait_seconds)

    raise RuntimeError(f"Unable to download {slug}")


for index, (slug, url) in enumerate(PHOTOS.items()):
    if index:
        print(f"Waiting {BETWEEN_IMAGES_SECONDS}s before the next Wikimedia request...", flush=True)
        time.sleep(BETWEEN_IMAGES_SECONDS)

    print(f"Downloading {slug}...", flush=True)
    raw = download_with_retry(url, slug)

    with Image.open(BytesIO(raw)) as source:
        image = ImageOps.exif_transpose(source).convert("RGB")
        image.thumbnail((800, 800), Image.Resampling.LANCZOS)
        dest = OUT / f"{slug}.webp"
        image.save(dest, "WEBP", quality=80, method=6)
        print(f"  {dest}: {image.width}x{image.height}, {dest.stat().st_size} bytes", flush=True)
