from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Ingredient, IngredientAlias


BUILTIN_ALIASES = {
    "whiskey": "Bourbon",
    "bourbon whiskey": "Bourbon",
    "rye": "Rye Whiskey",
    "scotch": "Scotch Whisky",
    "white rum": "White Rum",
    "light rum": "White Rum",
    "dark rum": "Dark Rum",
    "tequila": "Blanco Tequila",
    "blanco": "Blanco Tequila",
    "silver tequila": "Blanco Tequila",
    "orange liqueur": "Triple Sec",
    "curaçao": "Triple Sec",
    "curacao": "Triple Sec",
    "sweet vermouth": "Sweet Vermouth",
    "red vermouth": "Sweet Vermouth",
    "dry vermouth": "Dry Vermouth",
    "lime": "Lime Juice",
    "fresh lime juice": "Lime Juice",
    "lemon": "Lemon Juice",
    "fresh lemon juice": "Lemon Juice",
    "simple syrup": "Simple Syrup",
    "sugar syrup": "Simple Syrup",
    "soda water": "Club Soda",
    "sparkling water": "Club Soda",
    "gingerbeer": "Ginger Beer",
    "coffee liqueur": "Coffee Liqueur",
}


def seed_aliases(db: Session) -> int:
    count = 0
    for alias, canonical in BUILTIN_ALIASES.items():
        ingredient = db.scalar(select(Ingredient).where(Ingredient.name == canonical))
        if not ingredient:
            continue
        existing = db.scalar(select(IngredientAlias).where(IngredientAlias.alias == alias))
        if not existing:
            db.add(IngredientAlias(alias=alias, ingredient_id=ingredient.id, source="built_in"))
            count += 1
    db.commit()
    return count


def find_ingredient(db: Session, name: str) -> Ingredient | None:
    cleaned = " ".join(name.strip().lower().split())
    direct = db.scalar(select(Ingredient).where(Ingredient.name.ilike(cleaned)))
    if direct:
        return direct

    alias = db.scalar(select(IngredientAlias).where(IngredientAlias.alias == cleaned))
    if alias:
        return db.get(Ingredient, alias.ingredient_id)

    return None
