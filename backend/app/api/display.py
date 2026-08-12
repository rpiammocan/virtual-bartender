from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.services.recipe_display import display_recipe

router = APIRouter(prefix="/api/display", tags=["recipe display"])


@router.get("/recipe/{recipe_id}")
def recipe_display(recipe_id: int, metric: bool = False, db: Session = Depends(get_db)):
    try:
        return display_recipe(db, recipe_id, metric=metric)
    except ValueError:
        raise HTTPException(status_code=404, detail="Recipe not found")
