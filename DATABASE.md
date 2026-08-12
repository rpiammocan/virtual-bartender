# V1 Database Schema

Core entities:

- ingredients: normalized ingredient catalog
- units: US/customary units plus metric conversion metadata
- recipes: built-in and user recipes
- recipe_ingredients: ingredient quantities and optional flags
- ingredient_substitutions: approved substitution relationships and preferences
- glassware / equipment: recipe requirements
- tags / recipe_tags: recipe categorization
- bar_sessions: Tonight's Bar sessions
- inventory_items: My Bar and Tonight's Bar inventory
- favorites: favorite recipes
- drink_history: made drinks, 1–5 rating, optional note
- recipe_notes: persistent recipe notes
- shopping_items: categorized shopping list
- shopping_item_recipes: recipes unlocked/helped by shopping items
- recipe_sources: permanent source URL for imported recipes
- recipe_versions: built-in recipe version tracking
- settings: application settings
- backup_records: local backup history

Important separation:

- My Bar is represented as inventory_items with context_type='my_bar'.
- Tonight's Bar is represented by a bar_sessions row plus inventory_items with context_type='tonight_bar' and context_id equal to the session ID.
- User recipes are separate by source_type and may reference a built-in recipe through parent_recipe_id.
