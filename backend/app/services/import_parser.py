import re
from dataclasses import dataclass


UNIT_ALIASES = {
    "oz": "oz",
    "ounce": "oz",
    "ounces": "oz",
    "tsp": "tsp",
    "teaspoon": "tsp",
    "teaspoons": "tsp",
    "tbsp": "tbsp",
    "tablespoon": "tbsp",
    "tablespoons": "tbsp",
    "dash": "dash",
    "dashes": "dash",
}

FRACTIONS = {
    "¼": 0.25,
    "½": 0.5,
    "¾": 0.75,
    "⅓": 1 / 3,
    "⅔": 2 / 3,
    "⅛": 0.125,
    "⅜": 0.375,
    "⅝": 0.625,
    "⅞": 0.875,
}


@dataclass
class ParsedIngredient:
    original: str
    quantity: float | None
    unit: str | None
    name: str
    notes: str | None = None


def _fraction_to_float(token: str) -> float | None:
    token = token.strip()
    if token in FRACTIONS:
        return FRACTIONS[token]
    if "/" in token:
        try:
            num, den = token.split("/", 1)
            return float(num) / float(den)
        except Exception:
            return None
    try:
        return float(token)
    except Exception:
        return None


def parse_ingredient_line(line: str) -> ParsedIngredient:
    original = line.strip()
    text = original

    quantity = None
    unit = None

    # Handles examples like "1 1/2 oz Gin", "¾ oz lime juice", "2 dashes bitters".
    m = re.match(
        r"^\s*(?:(\d+(?:\.\d+)?)\s+([¼½¾⅓⅔⅛⅜⅝⅞]|\d+/\d+)|([¼½¾⅓⅔⅛⅜⅝⅞]|\d+(?:\.\d+)?|\d+/\d+))\s+([A-Za-z]+)\s+(.*)$",
        text,
    )
    if m:
        if m.group(1) and m.group(2):
            whole = float(m.group(1))
            frac = _fraction_to_float(m.group(2))
            quantity = whole + (frac or 0)
        else:
            quantity = _fraction_to_float(m.group(3))
        raw_unit = (m.group(4) or "").lower()
        unit = UNIT_ALIASES.get(raw_unit)
        if unit:
            text = m.group(5).strip()

    if quantity is None:
        m2 = re.match(
            r"^\s*([¼½¾⅓⅔⅛⅜⅝⅞]|\d+(?:\.\d+)?|\d+/\d+)\s+([A-Za-z]+)\s+(.*)$",
            text,
        )
        if m2:
            quantity = _fraction_to_float(m2.group(1))
            raw_unit = m2.group(2).lower()
            unit = UNIT_ALIASES.get(raw_unit)
            if unit:
                text = m2.group(3).strip()

    # Strip common separators and parenthetical notes.
    notes = None
    note_match = re.search(r"\(([^)]+)\)\s*$", text)
    if note_match:
        notes = note_match.group(1).strip()
        text = text[: note_match.start()].strip()

    text = re.sub(r"^[\-–—,:;\s]+", "", text).strip()
    text = re.sub(r"\s+(for garnish|to garnish)$", "", text, flags=re.I).strip()

    return ParsedIngredient(
        original=original,
        quantity=quantity,
        unit=unit,
        name=text,
        notes=notes,
    )
