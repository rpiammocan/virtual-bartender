from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, HttpUrl
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Ingredient, Recipe, RecipeIngredient, RecipeSource, Unit
from app.schemas_import import ImportedIngredientDraft, SaveImportedRecipeRequest
from app.services.duplicate_detection import find_possible_duplicates
from app.services.import_parser import parse_ingredient_line
from app.services.importer import import_recipe_url, scan_recipe_collection
from app.services.ingredient_normalization import find_ingredient

router = APIRouter(prefix="/api/import", tags=["recipe import"])


class UrlImportRequest(BaseModel):
    url: HttpUrl


@router.post("/collection")
async def scan_collection(payload: UrlImportRequest):
    try:
        return await scan_recipe_collection(str(payload.url))
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"Unable to scan collection: {exc}")


@router.post("/url")
async def import_url(payload: UrlImportRequest, db: Session = Depends(get_db)):
    try:
        raw = await import_recipe_url(str(payload.url))
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"Unable to import recipe: {exc}")
    parsed = [ImportedIngredientDraft(**parse_ingredient_line(line).__dict__) for line in raw.get("raw_ingredients", [])]
    duplicates = find_possible_duplicates(db, raw.get("name") or "Untitled Recipe", [item.name for item in parsed])
    return {**raw, "ingredients": [item.model_dump() for item in parsed], "possible_duplicates": duplicates}


@router.post("/save")
def save_imported_recipe(payload: SaveImportedRecipeRequest, db: Session = Depends(get_db)):
    duplicates = find_possible_duplicates(db, payload.name, [item.name for item in payload.ingredients])
    recipe = Recipe(name=payload.name.strip(), description=payload.description, recipe_type=payload.recipe_type, source_type="imported", instructions="\n".join(step.strip() for step in payload.instructions if step.strip()), image_path=payload.image_path, is_active=True)
    db.add(recipe)
    db.flush()
    for order, item in enumerate(payload.ingredients, start=1):
        ingredient = find_ingredient(db, item.name.strip())
        if not ingredient:
            ingredient = Ingredient(name=item.name.strip(), category="Imported", is_user_created=True, is_active=True)
            db.add(ingredient)
            db.flush()
        unit = db.scalar(select(Unit).where(Unit.abbreviation == item.unit)) if item.unit else None
        db.add(RecipeIngredient(recipe_id=recipe.id, ingredient_id=ingredient.id, quantity=item.quantity, unit_id=unit.id if unit else None, is_optional=False, display_order=order, notes=item.notes))
    db.add(RecipeSource(recipe_id=recipe.id, url=payload.source_url, source_name=payload.source_name, original_title=payload.name))
    db.commit()
    db.refresh(recipe)
    return {"recipe_id":recipe.id,"name":recipe.name,"possible_duplicates":duplicates,"status":"saved"}
