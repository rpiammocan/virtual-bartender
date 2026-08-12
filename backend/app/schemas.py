from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field


class IngredientCreate(BaseModel):
    name: str = Field(min_length=1, max_length=200)
    category: str | None = None


class IngredientRead(IngredientCreate):
    model_config = ConfigDict(from_attributes=True)
    id: int
    is_user_created: bool
    is_active: bool


class InventoryCreate(BaseModel):
    ingredient_id: int
    context_type: str = "my_bar"
    context_id: int | None = None
    quantity: float | None = None
    unit_id: int | None = None
    have: bool = True
    notes: str | None = None


class InventoryUpdate(BaseModel):
    quantity: float | None = None
    unit_id: int | None = None
    have: bool | None = None
    notes: str | None = None


class InventoryRead(InventoryCreate):
    model_config = ConfigDict(from_attributes=True)
    id: int


class RecipeCreate(BaseModel):
    name: str = Field(min_length=1, max_length=200)
    description: str | None = None
    recipe_type: str = "cocktail"
    source_type: str = "user"
    instructions: str | None = None
    image_path: str | None = None


class RecipeRead(RecipeCreate):
    model_config = ConfigDict(from_attributes=True)
    id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime


class RecipeIngredientRead(BaseModel):
    id: int
    ingredient_id: int
    ingredient_name: str
    quantity: float | None
    unit: str | None
    is_optional: bool
    notes: str | None


class RecipeDetailRead(RecipeRead):
    ingredients: list[RecipeIngredientRead]
    favorite: bool


class BarSessionCreate(BaseModel):
    name: str
    session_date: date
    source_type: str = "empty"


class BarSessionRead(BarSessionCreate):
    model_config = ConfigDict(from_attributes=True)
    id: int
    created_at: datetime
    updated_at: datetime


class ShoppingCreate(BaseModel):
    ingredient_id: int | None = None
    custom_name: str | None = None
    quantity: float | None = None
    unit_id: int | None = None
    category: str | None = None


class ShoppingRead(ShoppingCreate):
    model_config = ConfigDict(from_attributes=True)
    id: int
    purchased: bool
    created_at: datetime


class HistoryCreate(BaseModel):
    recipe_id: int
    session_id: int | None = None
    rating: int | None = Field(default=None, ge=1, le=5)
    notes: str | None = None


class HistoryRead(HistoryCreate):
    model_config = ConfigDict(from_attributes=True)
    id: int
    made_at: datetime


class MatchRead(BaseModel):
    recipe_id: int
    recipe_name: str
    status: str
    missing_required: list[str]
    available_required: list[str]
    optional_missing: list[str]
    substitutions: list[str]
    quantity_issues: list[str]
    variant_recipe_id: int | None
    variant_recipe_name: str | None
    explanation: str
