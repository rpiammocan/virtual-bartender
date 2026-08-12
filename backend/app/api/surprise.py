import random

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.services.matcher import MatchStatus, find_recipe_matches

router = APIRouter(prefix="/api/surprise", tags=["surprise me"])


@router.get("")
def surprise_me(
    context_type: str = "my_bar",
    context_id: int | None = None,
    include_substitutions: bool = True,
    include_variants: bool = True,
    db: Session = Depends(get_db),
):
    matches = find_recipe_matches(
        db,
        context_type=context_type,
        context_id=context_id,
        include_not_makeable=False,
    )

    allowed = {MatchStatus.EXACT}
    if include_substitutions:
        allowed.add(MatchStatus.SUBSTITUTION)
    if include_variants:
        allowed.add(MatchStatus.VARIANT)

    eligible = [m for m in matches if m.status in allowed]
    if not eligible:
        raise HTTPException(status_code=404, detail="No eligible drinks found")

    choice = random.choice(eligible)
    return {
        "recipe_id": choice.recipe_id,
        "recipe_name": choice.recipe_name,
        "status": choice.status,
        "explanation": choice.explanation,
        "substitutions": choice.substitutions,
        "variant_recipe_id": choice.variant_recipe_id,
        "variant_recipe_name": choice.variant_recipe_name,
    }
