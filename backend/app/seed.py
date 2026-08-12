from sqlalchemy import select
from sqlalchemy.orm import Session

from app.catalog_v2 import INGREDIENTS_V2, RECIPES_V2, SUBSTITUTIONS_V2
from app.catalog_v3 import RECIPES_V3
from app.catalog_v4 import RECIPES_V4
from app.catalog_v5 import RECIPES_V5
from app.services.ingredient_normalization import seed_aliases
from app.models import (
    Ingredient,
    IngredientSubstitution,
    Recipe,
    RecipeIngredient,
    RecipeSource,
    Unit,
)


BUILTIN_UNITS = [
    {"name": "ounce", "abbreviation": "oz", "metric_equivalent": 29.5735, "metric_unit": "ml"},
    {"name": "teaspoon", "abbreviation": "tsp", "metric_equivalent": 4.92892, "metric_unit": "ml"},
    {"name": "tablespoon", "abbreviation": "tbsp", "metric_equivalent": 14.7868, "metric_unit": "ml"},
    {"name": "dash", "abbreviation": "dash", "metric_equivalent": None, "metric_unit": None},
    {"name": "piece", "abbreviation": "pc", "metric_equivalent": None, "metric_unit": None},
]

BASE_INGREDIENTS = [
    ("Bourbon", "Whiskey"), ("Rye Whiskey", "Whiskey"), ("Scotch Whisky", "Whiskey"),
    ("Gin", "Spirits"), ("Vodka", "Spirits"), ("White Rum", "Rum"), ("Dark Rum", "Rum"),
    ("Blanco Tequila", "Tequila"), ("Reposado Tequila", "Tequila"), ("Triple Sec", "Liqueurs"),
    ("Cointreau", "Liqueurs"), ("Sweet Vermouth", "Fortified Wine"), ("Dry Vermouth", "Fortified Wine"),
    ("Campari", "Liqueurs"), ("Angostura Bitters", "Bitters"), ("Simple Syrup", "Syrups"),
    ("Grenadine", "Syrups"), ("Lime Juice", "Juices"), ("Lemon Juice", "Juices"),
    ("Orange Juice", "Juices"), ("Grapefruit Juice", "Juices"), ("Pineapple Juice", "Juices"),
    ("Ginger Beer", "Mixers"), ("Ginger Ale", "Mixers"), ("Tonic Water", "Mixers"),
    ("Club Soda", "Mixers"), ("Cola", "Mixers"), ("Sprite", "Mixers"), ("Mint Leaves", "Fresh Ingredients"),
    ("Orange Peel", "Garnishes"), ("Lime Wedge", "Garnishes"), ("Lemon Peel", "Garnishes"),
    ("Salt", "Pantry / Kitchen"), ("Sugar", "Pantry / Kitchen"), ("Egg White", "Fresh Ingredients"),
]


IMAGE_METADATA = {
    "margarita": {
        "image_path": "/media/margarita.jpg",
        "image_source_url": "https://commons.wikimedia.org/wiki/File:Margarita.jpg",
        "image_license": "Public domain / CC0",
        "image_attribution": "Jon Sullivan (PD Photo.org)",
        "image_ai_generated": False,
    },
    "old-fashioned": {
        "image_path": "/media/old-fashioned.jpg",
        "image_source_url": "https://commons.wikimedia.org/wiki/File:Whiskey_Old_Fashioned1.jpg",
        "image_license": "CC BY-SA 4.0",
        "image_attribution": "© Erich Wagner / eventografie.de",
        "image_ai_generated": False,
    },
    "mojito": {
        "image_path": "/media/mojito.jpg",
        "image_source_url": "https://commons.wikimedia.org/wiki/File:Mojito_Cocktail.jpg",
        "image_license": "CC BY-SA 4.0",
        "image_attribution": "Sunny windy soundy",
        "image_ai_generated": False,
    },
}

BASE_RECIPES = [
    {
        "key":"old-fashioned","name":"Old Fashioned","type":"cocktail","version":"1.0",
        "description":"A classic whiskey cocktail built around spirit, sugar, and bitters.",
        "instructions":"Add bourbon, simple syrup, and bitters to a rocks glass with ice. Stir until chilled. Garnish with orange peel.",
        "source":"IBA reference","url":"https://iba-world.com/cocktails/",
        "ingredients":[("Bourbon",2.0,"oz",False),("Simple Syrup",0.25,"oz",False),("Angostura Bitters",2.0,"dash",False),("Orange Peel",1.0,"pc",True)]
    },
    {
        "key":"manhattan","name":"Manhattan","type":"cocktail","version":"1.0",
        "description":"Whiskey, sweet vermouth, and bitters.",
        "instructions":"Stir whiskey, sweet vermouth, and bitters with ice until chilled, then strain into a chilled glass.",
        "source":"IBA reference","url":"https://iba-world.com/cocktails/",
        "ingredients":[("Rye Whiskey",2.0,"oz",False),("Sweet Vermouth",1.0,"oz",False),("Angostura Bitters",2.0,"dash",False)]
    },
    {
        "key":"margarita","name":"Margarita","type":"cocktail","version":"1.0",
        "description":"A tequila sour with orange liqueur and lime.",
        "instructions":"Shake tequila, triple sec, and lime juice with ice. Strain into a chilled glass, optionally with a salted rim.",
        "source":"IBA reference","url":"https://iba-world.com/cocktails/",
        "ingredients":[("Blanco Tequila",2.0,"oz",False),("Triple Sec",1.0,"oz",False),("Lime Juice",1.0,"oz",False),("Salt",1.0,"tsp",True)]
    },
    {
        "key":"daiquiri","name":"Daiquiri","type":"cocktail","version":"1.0",
        "description":"A simple rum sour with lime and sugar.",
        "instructions":"Shake white rum, lime juice, and simple syrup with ice, then strain into a chilled glass.",
        "source":"IBA reference","url":"https://iba-world.com/cocktails/",
        "ingredients":[("White Rum",2.0,"oz",False),("Lime Juice",1.0,"oz",False),("Simple Syrup",0.75,"oz",False)]
    },
    {
        "key":"gin-tonic","name":"Gin and Tonic","type":"cocktail","version":"1.0",
        "description":"Gin lengthened with tonic water.",
        "instructions":"Build gin and tonic water over ice in a highball glass. Stir gently.",
        "source":"Open classic reference","url":"https://en.wikibooks.org/wiki/Bartending/Cocktails",
        "ingredients":[("Gin",2.0,"oz",False),("Tonic Water",4.0,"oz",False),("Lime Wedge",1.0,"pc",True)]
    },
    {
        "key":"moscow-mule","name":"Moscow Mule","type":"cocktail","version":"1.0",
        "description":"Vodka, ginger beer, and lime.",
        "instructions":"Build vodka and lime juice over ice, top with ginger beer, and stir gently.",
        "source":"Open classic reference","url":"https://en.wikibooks.org/wiki/Bartending/Cocktails",
        "ingredients":[("Vodka",2.0,"oz",False),("Ginger Beer",4.0,"oz",False),("Lime Juice",0.5,"oz",False)]
    },
    {
        "key":"virgin-moscow-mule","name":"Virgin Moscow Mule","type":"mocktail","version":"1.0",
        "description":"A non-alcoholic mule-style drink with ginger beer and lime.",
        "instructions":"Build lime juice over ice, top with ginger beer and club soda, then stir gently.",
        "source":"Virtual Bartender curated mocktail","url":"local://virtual-bartender/curated",
        "parent":"moscow-mule",
        "ingredients":[("Ginger Beer",4.0,"oz",False),("Lime Juice",0.75,"oz",False),("Club Soda",1.0,"oz",False)]
    },
    {
        "key":"whiskey-ginger","name":"Whiskey Ginger","type":"cocktail","version":"1.0",
        "description":"Whiskey topped with ginger ale.",
        "instructions":"Build whiskey and ginger ale over ice and stir gently.",
        "source":"Virtual Bartender curated highball","url":"local://virtual-bartender/curated",
        "ingredients":[("Bourbon",2.0,"oz",False),("Ginger Ale",4.0,"oz",False)]
    },
    {
        "key":"rum-sprite","name":"Rum and Sprite","type":"cocktail","version":"1.0",
        "description":"A simple rum highball with lemon-lime soda.",
        "instructions":"Build rum and Sprite over ice and stir gently.",
        "source":"Virtual Bartender curated highball","url":"local://virtual-bartender/curated",
        "ingredients":[("White Rum",2.0,"oz",False),("Sprite",4.0,"oz",False)]
    },
    {
        "key":"tequila-tonic","name":"Tequila Tonic","type":"cocktail","version":"1.0",
        "description":"Tequila and tonic water over ice.",
        "instructions":"Build tequila and tonic water over ice and stir gently.",
        "source":"Virtual Bartender curated highball","url":"local://virtual-bartender/curated",
        "ingredients":[("Blanco Tequila",2.0,"oz",False),("Tonic Water",4.0,"oz",False),("Lime Wedge",1.0,"pc",True)]
    },
]

def seed_builtin_data(db: Session) -> dict[str, int]:
    units = {}
    for data in BUILTIN_UNITS:
        unit = db.scalar(select(Unit).where(Unit.abbreviation == data["abbreviation"]))
        if not unit:
            unit = Unit(**data)
            db.add(unit)
            db.flush()
        units[unit.abbreviation] = unit

    ingredients = {}
    for name, category in BASE_INGREDIENTS + INGREDIENTS_V2:
        ingredient = db.scalar(select(Ingredient).where(Ingredient.name == name))
        if not ingredient:
            ingredient = Ingredient(name=name, category=category, is_user_created=False, is_active=True)
            db.add(ingredient)
            db.flush()
        ingredients[name] = ingredient

    substitution_count = 0
    for required, substitute, priority in SUBSTITUTIONS_V2:
        existing = db.scalar(
            select(IngredientSubstitution).where(
                IngredientSubstitution.required_ingredient_id == ingredients[required].id,
                IngredientSubstitution.substitute_ingredient_id == ingredients[substitute].id,
            )
        )
        if not existing:
            db.add(IngredientSubstitution(
                required_ingredient_id=ingredients[required].id,
                substitute_ingredient_id=ingredients[substitute].id,
                priority=priority,
            ))
            substitution_count += 1

    recipes_added = 0
    all_recipes = BASE_RECIPES + RECIPES_V2 + RECIPES_V3 + RECIPES_V4 + RECIPES_V5

    # First pass creates recipes so parent links can resolve.
    recipes_by_key = {}
    for data in all_recipes:
        recipe = db.scalar(select(Recipe).where(Recipe.built_in_key == data["key"]))
        if not recipe:
            recipe = Recipe(
                name=data["name"],
                description=data["description"],
                recipe_type=data["type"],
                source_type="built_in",
                built_in_key=data["key"],
                version=data["version"],
                instructions=data["instructions"],
                is_active=True,
            )
            db.add(recipe)
            db.flush()

            for order, (ingredient_name, quantity, unit_abbr, optional) in enumerate(data["ingredients"], 1):
                db.add(RecipeIngredient(
                    recipe_id=recipe.id,
                    ingredient_id=ingredients[ingredient_name].id,
                    quantity=quantity,
                    unit_id=units[unit_abbr].id,
                    is_optional=optional,
                    display_order=order,
                ))
            db.add(RecipeSource(
                recipe_id=recipe.id,
                url=data["url"],
                source_name=data["source"],
                original_title=data["name"],
            ))
            recipes_added += 1
        image_meta = IMAGE_METADATA.get(data["key"])
        if image_meta:
            for field, value in image_meta.items():
                setattr(recipe, field, value)

        recipes_by_key[data["key"]] = recipe

    # Second pass applies variant/mocktail parent links.
    variant_links = 0
    for data in all_recipes:
        parent_key = data.get("parent")
        if parent_key:
            recipe = recipes_by_key[data["key"]]
            parent = recipes_by_key.get(parent_key)
            if parent and recipe.parent_recipe_id != parent.id:
                recipe.parent_recipe_id = parent.id
                variant_links += 1

    db.commit()
    aliases_added = seed_aliases(db)
    return {
        "units": len(units),
        "ingredients": len(ingredients),
        "recipes_total_catalog": len(all_recipes),
        "recipes_added": recipes_added,
        "substitutions_added": substitution_count,
        "variant_links_updated": variant_links,
        "aliases_added": aliases_added,
    }
