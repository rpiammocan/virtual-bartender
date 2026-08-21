#!/usr/bin/env python3
from pathlib import Path

path = Path('backend/app/seed.py')
text = path.read_text(encoding='utf-8')

old = '''    recipes_by_key = {}\n    for data in all_recipes:\n        recipe = db.scalar(select(Recipe).where(Recipe.built_in_key == data["key"]))\n        if not recipe:\n            recipe = Recipe(name=data["name"], description=data["description"], recipe_type=data["type"], source_type="built_in", built_in_key=data["key"], version=data["version"], instructions=data["instructions"], is_active=True)\n            db.add(recipe)\n            db.flush()\n            for order, (ingredient_name, quantity, unit_abbr, optional) in enumerate(data["ingredients"], 1):\n                db.add(RecipeIngredient(recipe_id=recipe.id, ingredient_id=ingredients[ingredient_name].id, quantity=quantity, unit_id=units[unit_abbr].id, is_optional=optional, display_order=order))\n            db.add(RecipeSource(recipe_id=recipe.id, url=data["url"], source_name=data["source"], original_title=data["name"]))\n            recipes_added += 1\n        image_meta = IMAGE_METADATA.get(data["key"])\n'''

new = '''    recipes_by_key = {}\n    canonical_builtin_keys = {data["key"] for data in all_recipes}\n    stale_builtins_retired = 0\n\n    # Retire built-in recipes that were removed from the canonical catalog.\n    # User-created/imported recipes are intentionally untouched.\n    existing_builtins = db.scalars(select(Recipe).where(Recipe.source_type == "built_in", Recipe.built_in_key.is_not(None))).all()\n    for existing_recipe in existing_builtins:\n        if existing_recipe.built_in_key not in canonical_builtin_keys and existing_recipe.is_active:\n            existing_recipe.is_active = False\n            stale_builtins_retired += 1\n\n    for data in all_recipes:\n        recipe = db.scalar(select(Recipe).where(Recipe.built_in_key == data["key"]))\n        if not recipe:\n            recipe = Recipe(name=data["name"], description=data["description"], recipe_type=data["type"], source_type="built_in", built_in_key=data["key"], version=data["version"], instructions=data["instructions"], is_active=True)\n            db.add(recipe)\n            db.flush()\n            for order, (ingredient_name, quantity, unit_abbr, optional) in enumerate(data["ingredients"], 1):\n                db.add(RecipeIngredient(recipe_id=recipe.id, ingredient_id=ingredients[ingredient_name].id, quantity=quantity, unit_id=units[unit_abbr].id, is_optional=optional, display_order=order))\n            db.add(RecipeSource(recipe_id=recipe.id, url=data["url"], source_name=data["source"], original_title=data["name"]))\n            recipes_added += 1\n        else:\n            # A recipe restored to the canonical catalog should become active again.\n            recipe.is_active = True\n        image_meta = IMAGE_METADATA.get(data["key"])\n'''

if old not in text:
    raise SystemExit('Expected recipe seeding block not found')
text = text.replace(old, new, 1)

old_return = '''    return {"units":len(units),"ingredients":len(ingredients),"recipes_total_catalog":len(all_recipes),"recipes_added":recipes_added,"substitutions_added":substitution_count,"variant_links_updated":variant_links,"aliases_added":aliases_added}\n'''
new_return = '''    return {"units":len(units),"ingredients":len(ingredients),"recipes_total_catalog":len(all_recipes),"recipes_added":recipes_added,"stale_builtins_retired":stale_builtins_retired,"substitutions_added":substitution_count,"variant_links_updated":variant_links,"aliases_added":aliases_added}\n'''
if old_return not in text:
    raise SystemExit('Expected seed return block not found')
text = text.replace(old_return, new_return, 1)

path.write_text(text, encoding='utf-8')
print('Patched seed.py to retire stale built-in recipes safely')
