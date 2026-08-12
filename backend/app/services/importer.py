import json
import re
from urllib.parse import urlparse

import httpx
from bs4 import BeautifulSoup


def _as_list(value):
    if value is None:
        return []
    return value if isinstance(value, list) else [value]


def _find_recipe_jsonld(soup: BeautifulSoup) -> dict | None:
    for script in soup.find_all("script", attrs={"type": "application/ld+json"}):
        try:
            data = json.loads(script.string or "")
        except Exception:
            continue

        candidates = []
        if isinstance(data, dict) and "@graph" in data:
            candidates.extend(_as_list(data["@graph"]))
        else:
            candidates.extend(_as_list(data))

        for item in candidates:
            if not isinstance(item, dict):
                continue
            item_type = item.get("@type")
            types = _as_list(item_type)
            if "Recipe" in types:
                return item
    return None


def _extract_name(soup: BeautifulSoup) -> str | None:
    if soup.title and soup.title.string:
        return soup.title.string.strip()
    h1 = soup.find("h1")
    return h1.get_text(" ", strip=True) if h1 else None


def _fallback_ingredients(soup: BeautifulSoup) -> list[str]:
    lines = []
    for selector in [
        '[class*="ingredient"]',
        '[id*="ingredient"]',
        'li',
    ]:
        for node in soup.select(selector):
            text = node.get_text(" ", strip=True)
            if 2 <= len(text) <= 160 and re.search(r"\b(oz|ounce|ml|tsp|tbsp|dash|cup|teaspoon|tablespoon)\b", text, re.I):
                if text not in lines:
                    lines.append(text)
        if lines:
            break
    return lines[:30]


def _fallback_instructions(soup: BeautifulSoup) -> list[str]:
    steps = []
    for selector in [
        '[class*="instruction"]',
        '[class*="direction"]',
        '[id*="instruction"]',
        '[id*="direction"]',
    ]:
        for node in soup.select(selector):
            text = node.get_text(" ", strip=True)
            if 10 <= len(text) <= 1000 and text not in steps:
                steps.append(text)
        if steps:
            break
    return steps[:20]


async def import_recipe_url(url: str) -> dict:
    parsed = urlparse(url)
    if parsed.scheme not in {"http", "https"}:
        raise ValueError("Only http and https URLs are supported")

    async with httpx.AsyncClient(
        follow_redirects=True,
        timeout=15.0,
        headers={"User-Agent": "VirtualBartender/1.0"},
    ) as client:
        response = await client.get(url)
        response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")
    recipe = _find_recipe_jsonld(soup)

    warnings = []
    if recipe:
        name = recipe.get("name")
        ingredients = _as_list(recipe.get("recipeIngredient"))
        raw_instructions = recipe.get("recipeInstructions")
        instructions = []
        for step in _as_list(raw_instructions):
            if isinstance(step, dict):
                text = step.get("text") or step.get("name")
                if text:
                    instructions.append(str(text))
            elif isinstance(step, str):
                instructions.append(step)

        if not ingredients:
            warnings.append("Structured recipe data did not include ingredients.")
        if not instructions:
            warnings.append("Structured recipe data did not include instructions.")

        return {
            "status": "needs_review",
            "extraction_method": "json_ld",
            "source_url": str(response.url),
            "source_name": parsed.netloc,
            "name": name or _extract_name(soup),
            "raw_ingredients": ingredients,
            "instructions": instructions,
            "warnings": warnings,
        }

    warnings.append("No structured Recipe data found; used webpage fallback extraction.")
    return {
        "status": "needs_review",
        "extraction_method": "fallback",
        "source_url": str(response.url),
        "source_name": parsed.netloc,
        "name": _extract_name(soup),
        "raw_ingredients": _fallback_ingredients(soup),
        "instructions": _fallback_instructions(soup),
        "warnings": warnings,
    }
