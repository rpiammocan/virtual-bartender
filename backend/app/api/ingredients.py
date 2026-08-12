from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Ingredient
from app.schemas import IngredientCreate, IngredientRead

router = APIRouter(prefix="/api/ingredients", tags=["ingredients"])


@router.get("", response_model=list[IngredientRead])
def list_ingredients(db: Session = Depends(get_db)):
    return list(db.scalars(select(Ingredient).where(Ingredient.is_active.is_(True)).order_by(Ingredient.name)).all())


@router.post("", response_model=IngredientRead, status_code=201)
def create_ingredient(payload: IngredientCreate, db: Session = Depends(get_db)):
    existing = db.scalar(select(Ingredient).where(Ingredient.name.ilike(payload.name)))
    if existing:
        raise HTTPException(status_code=409, detail="Ingredient already exists")

    item = Ingredient(
        name=payload.name.strip(),
        category=payload.category,
        is_user_created=True,
    )
    db.add(item)
    db.commit()
    db.refresh(item)
    return item
