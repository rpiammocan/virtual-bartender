from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas import MatchRead
from app.services.matcher import find_recipe_matches

router = APIRouter(prefix="/api/matches", tags=["recipe matching"])


@router.get("", response_model=list[MatchRead])
def find_matches(
    context_type: str = "my_bar",
    context_id: int | None = None,
    include_not_makeable: bool = False,
    db: Session = Depends(get_db),
):
    return find_recipe_matches(
        db,
        context_type=context_type,
        context_id=context_id,
        include_not_makeable=include_not_makeable,
    )
