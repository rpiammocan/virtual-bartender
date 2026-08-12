from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Favorite, Recipe

router = APIRouter(prefix="/api/favorites", tags=["favorites"])


@router.get("")
def list_favorites(db: Session = Depends(get_db)):
    rows = db.execute(
        select(Favorite, Recipe)
        .join(Recipe, Recipe.id == Favorite.recipe_id)
        .order_by(Recipe.name)
    ).all()
    return [{"recipe_id": fav.recipe_id, "name": recipe.name} for fav, recipe in rows]


@router.post("/{recipe_id}", status_code=201)
def add_favorite(recipe_id: int, db: Session = Depends(get_db)):
    if not db.get(Recipe, recipe_id):
        raise HTTPException(status_code=404, detail="Recipe not found")
    if db.get(Favorite, recipe_id):
        return {"recipe_id": recipe_id, "favorite": True}
    db.add(Favorite(recipe_id=recipe_id))
    db.commit()
    return {"recipe_id": recipe_id, "favorite": True}


@router.delete("/{recipe_id}", status_code=204)
def remove_favorite(recipe_id: int, db: Session = Depends(get_db)):
    favorite = db.get(Favorite, recipe_id)
    if favorite:
        db.delete(favorite)
        db.commit()
