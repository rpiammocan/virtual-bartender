from app.database import Base, engine, SessionLocal
from app.models import Ingredient, Recipe, RecipeIngredient, IngredientSubstitution, InventoryItem
from app.services.matcher import MatchStatus, match_recipe


def test_recipe_is_makeable_with_all_required_ingredients():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    gin = Ingredient(name="Test Gin")
    tonic = Ingredient(name="Test Tonic")
    db.add_all([gin, tonic])
    db.commit()
    db.refresh(gin)
    db.refresh(tonic)

    recipe = Recipe(name="Test G&T", source_type="user")
    db.add(recipe)
    db.commit()
    db.refresh(recipe)

    db.add_all([
        RecipeIngredient(recipe_id=recipe.id, ingredient_id=gin.id, display_order=1),
        RecipeIngredient(recipe_id=recipe.id, ingredient_id=tonic.id, display_order=2),
    ])
    db.commit()

    result = match_recipe(db, recipe, {gin.id, tonic.id})
    assert result.status == MatchStatus.EXACT

    db.close()


def test_recipe_is_almost_there_with_one_missing_required_ingredient():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    spirit = Ingredient(name="Test Spirit")
    mixer = Ingredient(name="Test Mixer")
    db.add_all([spirit, mixer])
    db.commit()
    db.refresh(spirit)
    db.refresh(mixer)

    recipe = Recipe(name="Test Almost", source_type="user")
    db.add(recipe)
    db.commit()
    db.refresh(recipe)

    db.add_all([
        RecipeIngredient(recipe_id=recipe.id, ingredient_id=spirit.id, display_order=1),
        RecipeIngredient(recipe_id=recipe.id, ingredient_id=mixer.id, display_order=2),
    ])
    db.commit()

    result = match_recipe(db, recipe, {spirit.id})
    assert result.status == MatchStatus.ALMOST_THERE
    assert result.missing_required == ["Test Mixer"]

    db.close()


def test_recipe_uses_approved_substitution():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    bourbon = Ingredient(name="Test Bourbon")
    rye = Ingredient(name="Test Rye")
    db.add_all([bourbon, rye])
    db.commit()
    db.refresh(bourbon)
    db.refresh(rye)

    db.add(IngredientSubstitution(
        required_ingredient_id=bourbon.id,
        substitute_ingredient_id=rye.id,
        priority=10,
    ))

    recipe = Recipe(name="Test Substitution", source_type="user")
    db.add(recipe)
    db.commit()
    db.refresh(recipe)

    db.add(RecipeIngredient(
        recipe_id=recipe.id,
        ingredient_id=bourbon.id,
        display_order=1,
    ))
    db.commit()

    result = match_recipe(db, recipe, {rye.id})
    assert result.status == MatchStatus.SUBSTITUTION
    assert result.substitutions == ["Test Bourbon → Test Rye"]

    db.close()
