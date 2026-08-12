from sqlalchemy import select
from app.database import Base, engine, SessionLocal
import app.models  # noqa
from app.seed import seed_builtin_data
from app.models import Recipe, Ingredient, RecipeIngredient, RecipeSource

def main():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        result = seed_builtin_data(db)
        recipe_count = db.scalar(select(Recipe).where(Recipe.is_active.is_(True)).count()) if False else len(db.scalars(select(Recipe).where(Recipe.is_active.is_(True))).all())
        ingredient_count = len(db.scalars(select(Ingredient).where(Ingredient.is_active.is_(True))).all())
        assert recipe_count >= 100, f"Expected >=100 recipes after seeding, got {recipe_count}"
        assert ingredient_count >= 70, f"Expected >=70 ingredients, got {ingredient_count}"

        recipes = db.scalars(select(Recipe).where(Recipe.is_active.is_(True))).all()
        for recipe in recipes:
            ris = db.scalars(select(RecipeIngredient).where(RecipeIngredient.recipe_id == recipe.id)).all()
            assert len(ris) > 0, f"Recipe without ingredients: {recipe.name}"
            source = db.get(RecipeSource, recipe.id)
            assert source is not None, f"Recipe without source: {recipe.name}"

        print({
            "seed_result": result,
            "recipe_count": recipe_count,
            "ingredient_count": ingredient_count,
            "status": "ok",
        })
    finally:
        db.close()

if __name__ == "__main__":
    main()
