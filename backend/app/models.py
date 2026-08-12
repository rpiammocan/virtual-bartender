from datetime import date, datetime

from sqlalchemy import Boolean, Date, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Ingredient(Base):
    __tablename__ = "ingredients"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(200), unique=True, index=True)
    category: Mapped[str | None] = mapped_column(String(100))
    parent_id: Mapped[int | None] = mapped_column(ForeignKey("ingredients.id"))
    is_user_created: Mapped[bool] = mapped_column(Boolean, default=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)


class IngredientAlias(Base):
    __tablename__ = "ingredient_aliases"
    id: Mapped[int] = mapped_column(primary_key=True)
    alias: Mapped[str] = mapped_column(String(200), unique=True, index=True)
    ingredient_id: Mapped[int] = mapped_column(ForeignKey("ingredients.id"))
    source: Mapped[str] = mapped_column(String(50), default="built_in")


class Unit(Base):
    __tablename__ = "units"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50), unique=True)
    abbreviation: Mapped[str] = mapped_column(String(20), unique=True)
    metric_equivalent: Mapped[float | None] = mapped_column(Float)
    metric_unit: Mapped[str | None] = mapped_column(String(20))


class Glassware(Base):
    __tablename__ = "glassware"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), unique=True)
    description: Mapped[str | None] = mapped_column(Text)


class Equipment(Base):
    __tablename__ = "equipment"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), unique=True)
    description: Mapped[str | None] = mapped_column(Text)


class Recipe(Base):
    __tablename__ = "recipes"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(200), index=True)
    description: Mapped[str | None] = mapped_column(Text)
    recipe_type: Mapped[str] = mapped_column(String(50), default="cocktail")
    source_type: Mapped[str] = mapped_column(String(50), default="built_in")
    parent_recipe_id: Mapped[int | None] = mapped_column(ForeignKey("recipes.id"))
    built_in_key: Mapped[str | None] = mapped_column(String(200), index=True)
    version: Mapped[str | None] = mapped_column(String(50))
    instructions: Mapped[str | None] = mapped_column(Text)
    glassware_id: Mapped[int | None] = mapped_column(ForeignKey("glassware.id"))
    image_path: Mapped[str | None] = mapped_column(String(500))
    image_source_url: Mapped[str | None] = mapped_column(String(2000))
    image_license: Mapped[str | None] = mapped_column(String(200))
    image_attribution: Mapped[str | None] = mapped_column(String(500))
    image_ai_generated: Mapped[bool] = mapped_column(Boolean, default=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class RecipeIngredient(Base):
    __tablename__ = "recipe_ingredients"
    id: Mapped[int] = mapped_column(primary_key=True)
    recipe_id: Mapped[int] = mapped_column(ForeignKey("recipes.id"), index=True)
    ingredient_id: Mapped[int] = mapped_column(ForeignKey("ingredients.id"))
    quantity: Mapped[float | None] = mapped_column(Float)
    unit_id: Mapped[int | None] = mapped_column(ForeignKey("units.id"))
    is_optional: Mapped[bool] = mapped_column(Boolean, default=False)
    display_order: Mapped[int] = mapped_column(Integer, default=0)
    notes: Mapped[str | None] = mapped_column(Text)


class IngredientSubstitution(Base):
    __tablename__ = "ingredient_substitutions"
    id: Mapped[int] = mapped_column(primary_key=True)
    required_ingredient_id: Mapped[int] = mapped_column(ForeignKey("ingredients.id"))
    substitute_ingredient_id: Mapped[int] = mapped_column(ForeignKey("ingredients.id"))
    priority: Mapped[int] = mapped_column(Integer, default=100)
    is_user_preferred: Mapped[bool] = mapped_column(Boolean, default=False)
    notes: Mapped[str | None] = mapped_column(Text)


class Tag(Base):
    __tablename__ = "tags"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), unique=True)


class RecipeTag(Base):
    __tablename__ = "recipe_tags"
    recipe_id: Mapped[int] = mapped_column(ForeignKey("recipes.id"), primary_key=True)
    tag_id: Mapped[int] = mapped_column(ForeignKey("tags.id"), primary_key=True)


class RecipeEquipment(Base):
    __tablename__ = "recipe_equipment"
    recipe_id: Mapped[int] = mapped_column(ForeignKey("recipes.id"), primary_key=True)
    equipment_id: Mapped[int] = mapped_column(ForeignKey("equipment.id"), primary_key=True)
    is_required: Mapped[bool] = mapped_column(Boolean, default=False)


class BarSession(Base):
    __tablename__ = "bar_sessions"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(200))
    session_date: Mapped[date] = mapped_column(Date)
    source_type: Mapped[str] = mapped_column(String(30), default="empty")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class InventoryItem(Base):
    __tablename__ = "inventory_items"
    id: Mapped[int] = mapped_column(primary_key=True)
    context_type: Mapped[str] = mapped_column(String(30), index=True)
    context_id: Mapped[int | None] = mapped_column(Integer, index=True)
    ingredient_id: Mapped[int] = mapped_column(ForeignKey("ingredients.id"))
    quantity: Mapped[float | None] = mapped_column(Float)
    unit_id: Mapped[int | None] = mapped_column(ForeignKey("units.id"))
    have: Mapped[bool] = mapped_column(Boolean, default=True)
    notes: Mapped[str | None] = mapped_column(Text)


class Favorite(Base):
    __tablename__ = "favorites"
    recipe_id: Mapped[int] = mapped_column(ForeignKey("recipes.id"), primary_key=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class DrinkHistory(Base):
    __tablename__ = "drink_history"
    id: Mapped[int] = mapped_column(primary_key=True)
    recipe_id: Mapped[int] = mapped_column(ForeignKey("recipes.id"))
    session_id: Mapped[int | None] = mapped_column(ForeignKey("bar_sessions.id"))
    made_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    rating: Mapped[int | None] = mapped_column(Integer)
    notes: Mapped[str | None] = mapped_column(Text)


class RecipeNote(Base):
    __tablename__ = "recipe_notes"
    id: Mapped[int] = mapped_column(primary_key=True)
    recipe_id: Mapped[int] = mapped_column(ForeignKey("recipes.id"))
    note: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class ShoppingItem(Base):
    __tablename__ = "shopping_items"
    id: Mapped[int] = mapped_column(primary_key=True)
    ingredient_id: Mapped[int | None] = mapped_column(ForeignKey("ingredients.id"))
    custom_name: Mapped[str | None] = mapped_column(String(200))
    quantity: Mapped[float | None] = mapped_column(Float)
    unit_id: Mapped[int | None] = mapped_column(ForeignKey("units.id"))
    category: Mapped[str | None] = mapped_column(String(100))
    purchased: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class ShoppingItemRecipe(Base):
    __tablename__ = "shopping_item_recipes"
    shopping_item_id: Mapped[int] = mapped_column(ForeignKey("shopping_items.id"), primary_key=True)
    recipe_id: Mapped[int] = mapped_column(ForeignKey("recipes.id"), primary_key=True)


class RecipeSource(Base):
    __tablename__ = "recipe_sources"
    recipe_id: Mapped[int] = mapped_column(ForeignKey("recipes.id"), primary_key=True)
    url: Mapped[str] = mapped_column(String(2000))
    source_name: Mapped[str | None] = mapped_column(String(300))
    original_title: Mapped[str | None] = mapped_column(String(300))
    imported_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class RecipeVersion(Base):
    __tablename__ = "recipe_versions"
    id: Mapped[int] = mapped_column(primary_key=True)
    recipe_id: Mapped[int] = mapped_column(ForeignKey("recipes.id"))
    version: Mapped[str] = mapped_column(String(50))
    based_on_version: Mapped[str | None] = mapped_column(String(50))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class Setting(Base):
    __tablename__ = "settings"
    key: Mapped[str] = mapped_column(String(100), primary_key=True)
    value: Mapped[str] = mapped_column(Text)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class BackupRecord(Base):
    __tablename__ = "backup_records"
    id: Mapped[int] = mapped_column(primary_key=True)
    path: Mapped[str] = mapped_column(String(1000))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    size_bytes: Mapped[int | None] = mapped_column(Integer)
    status: Mapped[str] = mapped_column(String(30), default="complete")
