from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import DrinkHistory
from app.schemas import HistoryCreate, HistoryRead

router = APIRouter(prefix="/api/history", tags=["history"])


@router.get("", response_model=list[HistoryRead])
def list_history(db: Session = Depends(get_db)):
    return list(db.scalars(select(DrinkHistory).order_by(DrinkHistory.made_at.desc())).all())


@router.post("", response_model=HistoryRead, status_code=201)
def create_history(payload: HistoryCreate, db: Session = Depends(get_db)):
    item = DrinkHistory(**payload.model_dump())
    db.add(item)
    db.commit()
    db.refresh(item)
    return item
