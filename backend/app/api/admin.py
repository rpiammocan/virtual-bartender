from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.seed import seed_builtin_data

router = APIRouter(prefix="/api/admin", tags=["admin"])


@router.post("/seed")
def seed_database(db: Session = Depends(get_db)):
    return seed_builtin_data(db)
