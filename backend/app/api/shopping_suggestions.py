from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.services.shopping_intelligence import smart_suggestions

router = APIRouter(prefix="/api/shopping-suggestions", tags=["shopping intelligence"])


@router.get("")
def suggestions(
    context_type: str = "my_bar",
    context_id: int | None = None,
    db: Session = Depends(get_db),
):
    return smart_suggestions(
        db,
        context_type=context_type,
        context_id=context_id,
    )
