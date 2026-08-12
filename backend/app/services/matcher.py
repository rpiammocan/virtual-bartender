from dataclasses import dataclass
from enum import Enum

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import (
    Ingredient,
    IngredientSubstitution,
    InventoryItem,
    Recipe,
    RecipeIngredient,
)
from app.services.units import quantities_sufficient


class MatchStatus(str, Enum):
    EXACT = "exact"
    SUBSTITUTION = "substitution"
    VARIANT = "variant"
    ALMOST_THERE = "almost_there"
    NOT_MAKEABLE = "not_makeable"


@dataclass
class InventorySnapshot:
    ingredient_id: int
    quantity: float | None
    unit_id: int | None


@dataclass
class RecipeMatch:
    recipe_id: int
    recipe_name: str
    status: MatchStatus
    missing_required: list[str]
    available_required: list[str]
    optional_missing: list[str]
    substitutions: list[str]
    quantity_issues: list[str]
    variant_recipe_id: int | None
    variant_recipe_name: str | None
    explanation: str


def _inventory_for_context(
    db: Session,
    context_type: str,
    context_id: int | None = None,
) -> dict[int, InventorySnapshot]:
    query = select(InventoryItem).where(
        InventoryItem.context_type == context_type,
        InventoryItem.have.is_(True),
    )
    if context_id is not None:
        query = query.where(InventoryItem.context_id == context_id)

    rows = db.scalars(query).all()
    return {
        row.ingredient_id: InventorySnapshot(
            ingredient_id=row.ingredient_id,
            quantity=row.quantity,
            unit_id=row.unit_id,
        )
        for row in rows
    }


def _substitutes_for(db: Session, ingredient_id: int) -> list[int]:
    rows = db.scalars(
        select(IngredientSubstitution)
        .where(IngredientSubstitution.required_ingredient_id == ingredient_id)
        .order_by(
            IngredientSubstitution.is_user_preferred.desc(),
            IngredientSubstitution.priority,
        )
    ).all()
    return [row.substitute_ingredient_id for row in rows]


def _ingredient_name(db: Session, ingredient_id: int) -> str:
    ingredient = db.get(Ingredient, ingredient_id)
    return ingredient.name if ingredient else f"Ingredient #{ingredient_id}"


def _quantity_sufficient(
    db: Session,
    recipe_item: RecipeIngredient,
    inventory_item: InventorySnapshot,
) -> bool:
    return quantities_sufficient(
        db,
        recipe_item.quantity,
        recipe_item.unit_id,
        inventory_item.quantity,
        inventory_item.unit_id,
    )


def _evaluate_recipe(
    db: Session,
    recipe: Recipe,
    inventory: dict[int, InventorySnapshot],
) -> RecipeMatch:
    recipe_ingredients = db.scalars(
        select(RecipeIngredient)
        .where(RecipeIngredient.recipe_id == recipe.id)
        .order_by(RecipeIngredient.display_order, RecipeIngredient.id)
    ).all()

    missing_required: list[str] = []
    available_required: list[str] = []
    optional_missing: list[str] = []
    substitutions: list[str] = []
    quantity_issues: list[str] = []

    for item in recipe_ingredients:
        name = _ingredient_name(db, item.ingredient_id)
        exact_inventory = inventory.get(item.ingredient_id)

        if exact_inventory:
            if not _quantity_sufficient(db, item, exact_inventory):
                if item.is_optional:
                    optional_missing.append(name)
                else:
                    quantity_issues.append(name)
                continue

            if not item.is_optional:
                available_required.append(name)
            continue

        matched_substitute_id = None
        matched_substitute_inventory = None
        for substitute_id in _substitutes_for(db, item.ingredient_id):
            candidate = inventory.get(substitute_id)
            if candidate:
                matched_substitute_id = substitute_id
                matched_substitute_inventory = candidate
                break

        if matched_substitute_id and matched_substitute_inventory:
            substitute_name = _ingredient_name(db, matched_substitute_id)
            if not _quantity_sufficient(db, item, matched_substitute_inventory):
                if item.is_optional:
                    optional_missing.append(name)
                else:
                    quantity_issues.append(f"{name} (substitute: {substitute_name})")
                continue

            substitutions.append(f"{name} → {substitute_name}")
            if not item.is_optional:
                available_required.append(name)
            continue

        if item.is_optional:
            optional_missing.append(name)
        else:
            missing_required.append(name)

    blockers = len(missing_required) + len(quantity_issues)

    if blockers == 0:
        status = MatchStatus.SUBSTITUTION if substitutions else MatchStatus.EXACT
        explanation = (
            "You have all required ingredients."
            if not substitutions
            else "You can make this using approved substitutions."
        )
    elif blockers == 1:
        status = MatchStatus.ALMOST_THERE
        explanation = "You are one required ingredient or quantity short."
    else:
        status = MatchStatus.NOT_MAKEABLE
        explanation = f"You are missing or short on {blockers} required items."

    return RecipeMatch(
        recipe_id=recipe.id,
        recipe_name=recipe.name,
        status=status,
        missing_required=missing_required,
        available_required=available_required,
        optional_missing=optional_missing,
        substitutions=substitutions,
        quantity_issues=quantity_issues,
        variant_recipe_id=None,
        variant_recipe_name=None,
        explanation=explanation,
    )


def _find_makeable_variant(
    db: Session,
    parent_recipe: Recipe,
    inventory: dict[int, InventorySnapshot],
) -> RecipeMatch | None:
    variants = db.scalars(
        select(Recipe)
        .where(
            Recipe.parent_recipe_id == parent_recipe.id,
            Recipe.is_active.is_(True),
        )
        .order_by(Recipe.name)
    ).all()

    for variant in variants:
        result = _evaluate_recipe(db, variant, inventory)
        if result.status in {MatchStatus.EXACT, MatchStatus.SUBSTITUTION}:
            return RecipeMatch(
                recipe_id=parent_recipe.id,
                recipe_name=parent_recipe.name,
                status=MatchStatus.VARIANT,
                missing_required=result.missing_required,
                available_required=result.available_required,
                optional_missing=result.optional_missing,
                substitutions=result.substitutions,
                quantity_issues=result.quantity_issues,
                variant_recipe_id=variant.id,
                variant_recipe_name=variant.name,
                explanation=f"You can make the linked variant: {variant.name}.",
            )
    return None


def match_recipe(
    db: Session,
    recipe: Recipe,
    inventory: dict[int, InventorySnapshot] | set[int],
) -> RecipeMatch:
    # Backward compatibility for tests/older callers that pass a simple set
    # of ingredient IDs. A set means "have it; quantity unknown".
    if isinstance(inventory, set):
        inventory = {
            ingredient_id: InventorySnapshot(
                ingredient_id=ingredient_id,
                quantity=None,
                unit_id=None,
            )
            for ingredient_id in inventory
        }

    direct = _evaluate_recipe(db, recipe, inventory)
    if direct.status in {
        MatchStatus.EXACT,
        MatchStatus.SUBSTITUTION,
        MatchStatus.ALMOST_THERE,
    }:
        return direct

    variant = _find_makeable_variant(db, recipe, inventory)
    return variant or direct


def find_recipe_matches(
    db: Session,
    context_type: str = "my_bar",
    context_id: int | None = None,
    include_not_makeable: bool = False,
) -> list[RecipeMatch]:
    inventory = _inventory_for_context(db, context_type, context_id)

    recipes = db.scalars(
        select(Recipe)
        .where(
            Recipe.is_active.is_(True),
            Recipe.parent_recipe_id.is_(None),
        )
        .order_by(Recipe.name)
    ).all()

    results = [match_recipe(db, recipe, inventory) for recipe in recipes]

    order = {
        MatchStatus.EXACT: 0,
        MatchStatus.SUBSTITUTION: 1,
        MatchStatus.VARIANT: 2,
        MatchStatus.ALMOST_THERE: 3,
        MatchStatus.NOT_MAKEABLE: 4,
    }
    results.sort(key=lambda r: (order[r.status], r.recipe_name.lower()))

    if not include_not_makeable:
        results = [r for r in results if r.status != MatchStatus.NOT_MAKEABLE]

    return results


def find_makeable_recipes(
    db: Session,
    context_type: str = "my_bar",
    context_id: int | None = None,
    include_almost_there: bool = True,
) -> list[RecipeMatch]:
    results = find_recipe_matches(
        db,
        context_type=context_type,
        context_id=context_id,
        include_not_makeable=False,
    )
    if include_almost_there:
        return results
    return [
        r for r in results
        if r.status in {MatchStatus.EXACT, MatchStatus.SUBSTITUTION, MatchStatus.VARIANT}
    ]
