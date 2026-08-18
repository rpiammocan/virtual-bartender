"""Build locally hosted Virtual Bartender recipe photos from licensed sources.

Each source image is downloaded from Wikimedia Commons, resized proportionally so
its longest side is at most 800 px, and saved as WebP at quality 80. No cropping
or zooming is performed.
"""
from pathlib import Path
from urllib.request import Request, urlopen
from io import BytesIO
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

for slug, url in PHOTOS.items():
    print(f"Downloading {slug}...")
    req = Request(url, headers={"User-Agent": "VirtualBartender/1.0 recipe-photo-builder"})
    with urlopen(req, timeout=60) as response:
        raw = response.read()
    with Image.open(BytesIO(raw)) as source:
        image = ImageOps.exif_transpose(source).convert("RGB")
        image.thumbnail((800, 800), Image.Resampling.LANCZOS)
        dest = OUT / f"{slug}.webp"
        image.save(dest, "WEBP", quality=80, method=6)
        print(f"  {dest}: {image.width}x{image.height}, {dest.stat().st_size} bytes")
