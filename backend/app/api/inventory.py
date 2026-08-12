from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Ingredient, InventoryItem
from app.schemas import InventoryCreate, InventoryRead, InventoryUpdate

router = APIRouter(prefix="/api/inventory", tags=["inventory"])


@router.get("", response_model=list[InventoryRead])
def list_inventory(context_type: str = "my_bar", context_id: int | None = None, db: Session = Depends(get_db)):
    query = select(InventoryItem).where(InventoryItem.context_type == context_type)
    if context_id is not None:
        query = query.where(InventoryItem.context_id == context_id)
    return list(db.scalars(query.order_by(InventoryItem.id)).all())


@router.post("", response_model=InventoryRead, status_code=201)
def add_inventory(payload: InventoryCreate, db: Session = Depends(get_db)):
    if not db.get(Ingredient, payload.ingredient_id):
        raise HTTPException(status_code=404, detail="Ingredient not found")
    item = InventoryItem(**payload.model_dump())
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


@router.patch("/{item_id}", response_model=InventoryRead)
def update_inventory(item_id: int, payload: InventoryUpdate, db: Session = Depends(get_db)):
    item = db.get(InventoryItem, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Inventory item not found")
    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(item, key, value)
    db.commit()
    db.refresh(item)
    return item


@router.delete("/{item_id}", status_code=204)
def delete_inventory(item_id: int, db: Session = Depends(get_db)):
    item = db.get(InventoryItem, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Inventory item not found")
    db.delete(item)
    db.commit()
