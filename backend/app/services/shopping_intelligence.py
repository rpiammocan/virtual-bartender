from collections import defaultdict

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Ingredient, Recipe
from app.services.matcher import MatchStatus, find_recipe_matches


def smart_suggestions(
    db: Session,
    context_type: str = "my_bar",
    context_id: int | None = None,
) -> list[dict]:
    matches = find_recipe_matches(
        db,
        context_type=context_type,
        context_id=context_id,
        include_not_makeable=True,
    )

    unlocks: dict[str, list[dict]] = defaultdict(list)

    for match in matches:
        if match.status != MatchStatus.ALMOST_THERE:
            continue

        blockers = list(match.missing_required) + list(match.quantity_issues)
        if len(blockers) != 1:
            continue

        missing = blockers[0]
        unlocks[missing].append({
            "recipe_id": match.recipe_id,
            "recipe_name": match.recipe_name,
        })

    suggestions = []
    for ingredient_name, recipes in unlocks.items():
        ingredient = db.scalar(select(Ingredient).where(Ingredient.name == ingredient_name))
        suggestions.append({
            "ingredient_id": ingredient.id if ingredient else None,
            "ingredient_name": ingredient_name,
            "category": ingredient.category if ingredient else "Other",
            "unlock_count": len(recipes),
            "unlocks": recipes,
        })

    suggestions.sort(
        key=lambda x: (-x["unlock_count"], x["ingredient_name"].lower())
    )
    return suggestions
