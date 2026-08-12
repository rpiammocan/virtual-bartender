from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Ingredient, Recipe, RecipeIngredient


def _recipe_ingredient_names(db: Session, recipe_id: int) -> set[str]:
    rows = db.execute(
        select(Ingredient.name)
        .join(RecipeIngredient, RecipeIngredient.ingredient_id == Ingredient.id)
        .where(RecipeIngredient.recipe_id == recipe_id)
    ).scalars().all()
    return {name.strip().lower() for name in rows}


def find_possible_duplicates(
    db: Session,
    name: str,
    ingredient_names: list[str],
) -> list[dict]:
    normalized_name = name.strip().lower()
    incoming = {x.strip().lower() for x in ingredient_names if x.strip()}

    candidates = db.scalars(
        select(Recipe).where(Recipe.is_active.is_(True))
    ).all()

    results = []
    for recipe in candidates:
        score = 0

        if recipe.name.strip().lower() == normalized_name:
            score += 70
        elif normalized_name in recipe.name.strip().lower() or recipe.name.strip().lower() in normalized_name:
            score += 40

        existing = _recipe_ingredient_names(db, recipe.id)
        if incoming and existing:
            overlap = len(incoming & existing) / max(len(incoming | existing), 1)
            score += int(overlap * 30)

        if score >= 50:
            results.append({
                "recipe_id": recipe.id,
                "name": recipe.name,
                "score": min(score, 100),
            })

    results.sort(key=lambda x: (-x["score"], x["name"].lower()))
    return results[:10]
