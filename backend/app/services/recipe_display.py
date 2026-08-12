from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Ingredient, Recipe, RecipeIngredient, Unit


def display_recipe(db: Session, recipe_id: int, metric: bool = False) -> dict:
    recipe = db.get(Recipe, recipe_id)
    if not recipe:
        raise ValueError("Recipe not found")

    rows = db.scalars(
        select(RecipeIngredient)
        .where(RecipeIngredient.recipe_id == recipe_id)
        .order_by(RecipeIngredient.display_order, RecipeIngredient.id)
    ).all()

    ingredients = []
    for row in rows:
        ingredient = db.get(Ingredient, row.ingredient_id)
        unit = db.get(Unit, row.unit_id) if row.unit_id else None
        qty = row.quantity
        unit_label = unit.abbreviation if unit else None

        if metric and qty is not None and unit and unit.metric_equivalent and unit.metric_unit:
            qty = round(qty * unit.metric_equivalent, 1)
            unit_label = unit.metric_unit

        ingredients.append({
            "ingredient_id": row.ingredient_id,
            "name": ingredient.name if ingredient else f"Ingredient #{row.ingredient_id}",
            "quantity": qty,
            "unit": unit_label,
            "optional": row.is_optional,
            "notes": row.notes,
        })

    return {
        "id": recipe.id,
        "name": recipe.name,
        "description": recipe.description,
        "instructions": recipe.instructions,
        "metric": metric,
        "ingredients": ingredients,
        "image_path": recipe.image_path,
        "image_source_url": recipe.image_source_url,
        "image_license": recipe.image_license,
        "image_attribution": recipe.image_attribution,
        "image_ai_generated": recipe.image_ai_generated,
    }
