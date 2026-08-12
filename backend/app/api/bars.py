from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import BarSession, InventoryItem
from app.schemas import BarSessionCreate, BarSessionRead

router = APIRouter(prefix="/api/bars", tags=["bars"])


@router.get("/tonight", response_model=list[BarSessionRead])
def list_tonight_bars(db: Session = Depends(get_db)):
    return list(
        db.scalars(
            select(BarSession)
            .where(BarSession.source_type == "tonight")
            .order_by(BarSession.session_date.desc(), BarSession.id.desc())
        ).all()
    )


@router.post("/tonight", response_model=BarSessionRead, status_code=201)
def create_tonight_bar(payload: BarSessionCreate, db: Session = Depends(get_db)):
    session = BarSession(
        name=payload.name,
        session_date=payload.session_date,
        source_type="tonight",
    )
    db.add(session)
    db.commit()
    db.refresh(session)
    return session


@router.post("/tonight/{session_id}/copy-my-bar", status_code=204)
def copy_my_bar(session_id: int, db: Session = Depends(get_db)):
    session = db.get(BarSession, session_id)
    if not session or session.source_type != "tonight":
        raise HTTPException(status_code=404, detail="Tonight's Bar session not found")

    current_ids = set(
        db.scalars(
            select(InventoryItem.ingredient_id).where(
                InventoryItem.context_type == "tonight_bar",
                InventoryItem.context_id == session_id,
            )
        ).all()
    )
    my_bar = db.scalars(
        select(InventoryItem).where(InventoryItem.context_type == "my_bar")
    ).all()

    for item in my_bar:
        if item.ingredient_id in current_ids:
            continue
        db.add(
            InventoryItem(
                context_type="tonight_bar",
                context_id=session_id,
                ingredient_id=item.ingredient_id,
                quantity=item.quantity,
                unit_id=item.unit_id,
                have=item.have,
                notes=item.notes,
            )
        )
    db.commit()


@router.delete("/tonight/{session_id}", status_code=204)
def delete_tonight_bar(session_id: int, db: Session = Depends(get_db)):
    session = db.get(BarSession, session_id)
    if not session or session.source_type != "tonight":
        raise HTTPException(status_code=404, detail="Tonight's Bar session not found")
    for item in db.scalars(
        select(InventoryItem).where(
            InventoryItem.context_type == "tonight_bar",
            InventoryItem.context_id == session_id,
        )
    ).all():
        db.delete(item)
    db.delete(session)
    db.commit()
