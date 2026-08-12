from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import ShoppingItem
from app.schemas import ShoppingCreate, ShoppingRead

router = APIRouter(prefix="/api/shopping", tags=["shopping"])


@router.get("", response_model=list[ShoppingRead])
def list_shopping(db: Session = Depends(get_db)):
    return list(db.scalars(select(ShoppingItem).order_by(ShoppingItem.purchased, ShoppingItem.category, ShoppingItem.id)).all())


@router.post("", response_model=ShoppingRead, status_code=201)
def add_shopping(payload: ShoppingCreate, db: Session = Depends(get_db)):
    if not payload.ingredient_id and not payload.custom_name:
        raise HTTPException(status_code=422, detail="Provide an ingredient or custom name")
    item = ShoppingItem(**payload.model_dump())
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


@router.patch("/{item_id}/purchased", response_model=ShoppingRead)
def mark_purchased(item_id: int, purchased: bool = True, db: Session = Depends(get_db)):
    item = db.get(ShoppingItem, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Shopping item not found")
    item.purchased = purchased
    db.commit()
    db.refresh(item)
    return item


@router.delete("/{item_id}", status_code=204)
def delete_shopping(item_id: int, db: Session = Depends(get_db)):
    item = db.get(ShoppingItem, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Shopping item not found")
    db.delete(item)
    db.commit()
