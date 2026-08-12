from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Favorite, Ingredient, Recipe, RecipeIngredient, Unit
from app.schemas import RecipeCreate, RecipeDetailRead, RecipeIngredientRead, RecipeRead

router = APIRouter(prefix="/api/recipes", tags=["recipes"])


@router.get("", response_model=list[RecipeRead])
def list_recipes(search: str | None = None, db: Session = Depends(get_db)):
    query = select(Recipe).where(Recipe.is_active.is_(True))
    if search:
        query = query.where(Recipe.name.ilike(f"%{search}%"))
    return list(db.scalars(query.order_by(Recipe.name)).all())


@router.get("/{recipe_id}", response_model=RecipeDetailRead)
def get_recipe(recipe_id: int, db: Session = Depends(get_db)):
    recipe = db.get(Recipe, recipe_id)
    if not recipe or not recipe.is_active:
        raise HTTPException(status_code=404, detail="Recipe not found")

    items = db.scalars(
        select(RecipeIngredient)
        .where(RecipeIngredient.recipe_id == recipe_id)
        .order_by(RecipeIngredient.display_order, RecipeIngredient.id)
    ).all()

    ingredients = []
    for item in items:
        ingredient = db.get(Ingredient, item.ingredient_id)
        unit = db.get(Unit, item.unit_id) if item.unit_id else None
        ingredients.append(
            RecipeIngredientRead(
                id=item.id,
                ingredient_id=item.ingredient_id,
                ingredient_name=ingredient.name if ingredient else f"Ingredient #{item.ingredient_id}",
                quantity=item.quantity,
                unit=unit.abbreviation if unit else None,
                is_optional=item.is_optional,
                notes=item.notes,
            )
        )

    return RecipeDetailRead(
        id=recipe.id,
        name=recipe.name,
        description=recipe.description,
        recipe_type=recipe.recipe_type,
        source_type=recipe.source_type,
        instructions=recipe.instructions,
        image_path=recipe.image_path,
        is_active=recipe.is_active,
        created_at=recipe.created_at,
        updated_at=recipe.updated_at,
        ingredients=ingredients,
        favorite=db.get(Favorite, recipe.id) is not None,
    )


@router.post("", response_model=RecipeRead, status_code=201)
def create_recipe(payload: RecipeCreate, db: Session = Depends(get_db)):
    recipe = Recipe(**payload.model_dump())
    db.add(recipe)
    db.commit()
    db.refresh(recipe)
    return recipe
