from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Ingredient, Recipe, RecipeIngredient, RecipeSource, Unit


def _recipe_parts(db: Session, recipe_id: int):
    recipe = db.get(Recipe, recipe_id)
    if not recipe or not recipe.is_active:
        return None

    rows = db.scalars(
        select(RecipeIngredient)
        .where(RecipeIngredient.recipe_id == recipe_id)
        .order_by(RecipeIngredient.display_order, RecipeIngredient.id)
    ).all()

    ingredients = []
    for row in rows:
        ingredient = db.get(Ingredient, row.ingredient_id)
        unit = db.get(Unit, row.unit_id) if row.unit_id else None
        ingredients.append({
            "name": ingredient.name if ingredient else f"Ingredient #{row.ingredient_id}",
            "quantity": row.quantity,
            "unit": unit.abbreviation if unit else None,
            "optional": row.is_optional,
            "notes": row.notes,
        })

    source = db.get(RecipeSource, recipe_id)
    return recipe, ingredients, source


def recipe_to_markdown(db: Session, recipe_id: int) -> str:
    parts = _recipe_parts(db, recipe_id)
    if not parts:
        raise ValueError("Recipe not found")
    recipe, ingredients, source = parts

    lines = [f"# {recipe.name}", ""]
    if recipe.description:
        lines += [recipe.description, ""]

    lines += ["## Ingredients", ""]
    for item in ingredients:
        qty = "" if item["quantity"] is None else f'{item["quantity"]:g}'
        unit = item["unit"] or ""
        optional = " _(optional)_" if item["optional"] else ""
        note = f' — {item["notes"]}' if item["notes"] else ""
        prefix = " ".join(x for x in [qty, unit, item["name"]] if x)
        lines.append(f"- {prefix}{optional}{note}")

    lines += ["", "## Instructions", "", recipe.instructions or "No instructions provided.", ""]

    if source:
        lines += [
            "## Source",
            "",
            f"- Source: {source.source_name or 'Imported source'}",
            f"- URL: {source.url}",
            "",
        ]

    return "\n".join(lines).rstrip() + "\n"


def recipe_to_text(db: Session, recipe_id: int) -> str:
    parts = _recipe_parts(db, recipe_id)
    if not parts:
        raise ValueError("Recipe not found")
    recipe, ingredients, source = parts

    lines = [recipe.name.upper(), "=" * len(recipe.name), ""]
    if recipe.description:
        lines += [recipe.description, ""]

    lines += ["INGREDIENTS", "-----------"]
    for item in ingredients:
        qty = "" if item["quantity"] is None else f'{item["quantity"]:g}'
        unit = item["unit"] or ""
        optional = " (optional)" if item["optional"] else ""
        note = f' - {item["notes"]}' if item["notes"] else ""
        prefix = " ".join(x for x in [qty, unit, item["name"]] if x)
        lines.append(f"{prefix}{optional}{note}")

    lines += ["", "INSTRUCTIONS", "------------", recipe.instructions or "No instructions provided.", ""]

    if source:
        lines += [
            "SOURCE",
            "------",
            source.source_name or "Imported source",
            source.url,
            "",
        ]

    return "\n".join(lines).rstrip() + "\n"
