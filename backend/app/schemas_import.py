from pydantic import BaseModel, Field


class ImportedIngredientDraft(BaseModel):
    original: str
    quantity: float | None = None
    unit: str | None = None
    name: str
    notes: str | None = None


class ImportedRecipeDraft(BaseModel):
    source_url: str
    source_name: str | None = None
    name: str = Field(min_length=1, max_length=200)
    recipe_type: str = "cocktail"
    instructions: list[str] = []
    ingredients: list[ImportedIngredientDraft]
    warnings: list[str] = []
    extraction_method: str | None = None


class SaveImportedRecipeRequest(ImportedRecipeDraft):
    description: str | None = None
    image_path: str | None = None
