from sqlalchemy import select
from sqlalchemy.orm import Session

from app.catalog_v2 import INGREDIENTS_V2, RECIPES_V2, SUBSTITUTIONS_V2
from app.catalog_v3 import RECIPES_V3
from app.catalog_v4 import RECIPES_V4
from app.catalog_v5 import RECIPES_V5
from app.catalog_v6 import INGREDIENTS_V6, RECIPES_V6, UNITS_V6
from app.catalog_v7 import INGREDIENTS_V7, RECIPES_V7, UNITS_V7
from app.catalog_v8 import INGREDIENTS_V8, RECIPES_V8, UNITS_V8
from app.services.ingredient_normalization import seed_aliases
from app.models import Ingredient, IngredientSubstitution, Recipe, RecipeIngredient, RecipeSource, Unit

BUILTIN_UNITS = [
    {"name":"ounce","abbreviation":"oz","metric_equivalent":29.5735,"metric_unit":"ml"},
    {"name":"teaspoon","abbreviation":"tsp","metric_equivalent":4.92892,"metric_unit":"ml"},
    {"name":"tablespoon","abbreviation":"tbsp","metric_equivalent":14.7868,"metric_unit":"ml"},
    {"name":"dash","abbreviation":"dash","metric_equivalent":None,"metric_unit":None},
    {"name":"piece","abbreviation":"pc","metric_equivalent":None,"metric_unit":None},
]

BASE_INGREDIENTS = [
    ("Bourbon","Whiskey"),("Rye Whiskey","Whiskey"),("Scotch Whisky","Whiskey"),
    ("Gin","Spirits"),("Vodka","Spirits"),("White Rum","Rum"),("Dark Rum","Rum"),
    ("Blanco Tequila","Tequila"),("Reposado Tequila","Tequila"),("Triple Sec","Liqueurs"),
    ("Cointreau","Liqueurs"),("Sweet Vermouth","Fortified Wine"),("Dry Vermouth","Fortified Wine"),
    ("Campari","Liqueurs"),("Angostura Bitters","Bitters"),("Simple Syrup","Syrups"),
    ("Grenadine","Syrups"),("Lime Juice","Juices"),("Lemon Juice","Juices"),
    ("Orange Juice","Juices"),("Grapefruit Juice","Juices"),("Pineapple Juice","Juices"),
    ("Ginger Beer","Mixers"),("Ginger Ale","Mixers"),("Tonic Water","Mixers"),
    ("Club Soda","Mixers"),("Cola","Mixers"),("Sprite","Mixers"),("Mint Leaves","Fresh Ingredients"),
    ("Orange Peel","Garnishes"),("Lime Wedge","Garnishes"),("Lemon Peel","Garnishes"),
    ("Salt","Pantry / Kitchen"),("Sugar","Pantry / Kitchen"),("Egg White","Fresh Ingredients"),
]

IMAGE_METADATA = {
    "margarita":{"image_path":"/media/margarita.jpg","image_source_url":"https://commons.wikimedia.org/wiki/File:Margarita.jpg","image_license":"Public domain / CC0","image_attribution":"Jon Sullivan (PD Photo.org)","image_ai_generated":False},
    "old-fashioned":{"image_path":"/media/old-fashioned.jpg","image_source_url":"https://commons.wikimedia.org/wiki/File:Whiskey_Old_Fashioned1.jpg","image_license":"CC BY-SA 4.0","image_attribution":"© Erich Wagner / eventografie.de","image_ai_generated":False},
    "mojito":{"image_path":"/media/mojito.jpg","image_source_url":"https://commons.wikimedia.org/wiki/File:Mojito_Cocktail.jpg","image_license":"CC BY-SA 4.0","image_attribution":"Sunny windy soundy","image_ai_generated":False},
    "manhattan":{"image_path":"/media/manhattan.webp","image_source_url":"https://commons.wikimedia.org/wiki/File:Manhattan_Cocktail.jpg","image_license":"CC BY-SA 3.0","image_attribution":"Hayford Peirce","image_ai_generated":False},
    "martini":{"image_path":"/media/dry-martini.webp","image_source_url":"https://commons.wikimedia.org/wiki/File:Dry_martini.jpg","image_license":"CC BY-SA 4.0","image_attribution":"Arnaud 25","image_ai_generated":False},
    "negroni":{"image_path":"/media/negroni.webp","image_source_url":"https://commons.wikimedia.org/wiki/File:Negroni_(cocktail).jpg","image_license":"CC BY-SA 4.0","image_attribution":"Sudhertzen","image_ai_generated":False},
    "sidecar":{"image_path":"/media/sidecar.webp","image_source_url":"https://commons.wikimedia.org/wiki/File:Sidecar-cocktail.jpg","image_license":"CC BY 2.0","image_attribution":"Evan Swigart / TheCulinaryGeek","image_ai_generated":False},
    "singapore-sling":{"image_path":"/media/singapore-sling.webp","image_source_url":"https://commons.wikimedia.org/wiki/File:Singapore_Sling_Cocktail.jpg","image_license":"CC BY 2.0","image_attribution":"James Cridland","image_ai_generated":False},
    "whiskey-sour":{"image_path":"/media/whiskey-sour.webp","image_source_url":"https://commons.wikimedia.org/wiki/File:Whiskey_Sour.jpg","image_license":"CC BY-SA 3.0","image_attribution":"Jgilgamesh","image_ai_generated":False},
    "pina-colada":{"image_path":"/media/pina-colada.webp","image_source_url":"https://commons.wikimedia.org/wiki/File:Pina_Colada_(Cocktail).jpg","image_license":"CC BY-SA 3.0","image_attribution":"Martin Asche","image_ai_generated":False},
}

# BEGIN GENERATED BATCH 1 IMAGE METADATA
IMAGE_METADATA['agave-lime-soda'] = {'image_path': '/media/agave-lime-soda.webp', 'image_source_url': 'https://commons.wikimedia.org/wiki/File:Mocktails_-_English%27s_of_Brighton_2025-07-29.jpg', 'image_license': 'CC0', 'image_attribution': 'Andy Li', 'image_ai_generated': False}
IMAGE_METADATA['amaretto-coffee'] = {'image_path': '/media/amaretto-coffee.webp', 'image_source_url': 'https://commons.wikimedia.org/wiki/File:Gray_espresso_cup_with_amaretto_1.jpg', 'image_license': 'CC BY-SA 4.0', 'image_attribution': 'Friedrich Haag', 'image_ai_generated': False}
IMAGE_METADATA['amaretto-cream'] = {'image_path': '/media/amaretto-cream.webp', 'image_source_url': 'https://commons.wikimedia.org/wiki/File:Panettone_IMG_3607_(32264620218).jpg', 'image_license': 'CC BY 2.0', 'image_attribution': 'N i c o l a from Fiumicino (Rome), Italy', 'image_ai_generated': False}
IMAGE_METADATA['amaretto-sour'] = {'image_path': '/media/amaretto-sour.webp', 'image_source_url': 'https://commons.wikimedia.org/wiki/File:VTR_-_Ultimate_Amaretto_Sour.jpg', 'image_license': 'CC BY-SA 2.0', 'image_attribution': 'Edsel L', 'image_ai_generated': False}
IMAGE_METADATA['americano'] = {'image_path': '/media/americano.webp', 'image_source_url': 'https://commons.wikimedia.org/wiki/File:Americano_Cocktail_(15052466276).jpg', 'image_license': 'CC BY 2.0', 'image_attribution': 'Personal Creations', 'image_ai_generated': False}
IMAGE_METADATA['angel-face'] = {'image_path': '/media/angel-face.webp', 'image_source_url': 'https://commons.wikimedia.org/wiki/File:IBA_Cocktail_Angel_Face_(28068833805).jpg', 'image_license': 'CC BY-SA 2.0', 'image_attribution': 'Michael Styne from Averill Park, NY, USA', 'image_ai_generated': False}
IMAGE_METADATA['aperol-soda'] = {'image_path': '/media/aperol-soda.webp', 'image_source_url': 'https://commons.wikimedia.org/wiki/File:Ebbelrol_Spritz_Dauth-Schneider-.jpg', 'image_license': 'CC BY-SA 4.0', 'image_attribution': 'Benreis', 'image_ai_generated': False}
IMAGE_METADATA['aperol-spritz'] = {'image_path': '/media/aperol-spritz.webp', 'image_source_url': 'https://commons.wikimedia.org/wiki/File:Mitch_(cocktail).jpg', 'image_license': 'CC BY-SA 3.0', 'image_attribution': 'Andreamicci', 'image_ai_generated': False}
IMAGE_METADATA['aviation'] = {'image_path': '/media/aviation.webp', 'image_source_url': 'https://commons.wikimedia.org/wiki/File:Aviation_Cocktail.jpg', 'image_license': 'Public domain', 'image_attribution': 'Bskinner112 at English Wikipedia', 'image_ai_generated': False}
IMAGE_METADATA['basil-lime-soda'] = {'image_path': '/media/basil-lime-soda.webp', 'image_source_url': 'https://commons.wikimedia.org/wiki/File:Alinea_-_COURSE_22.jpg', 'image_license': 'CC BY 2.0', 'image_attribution': 'Matthew Hine', 'image_ai_generated': False}
IMAGE_METADATA['bees-knees'] = {'image_path': '/media/bees-knees.webp', 'image_source_url': 'https://commons.wikimedia.org/wiki/File:Bee%27s_Knees_(cocktail).jpg', 'image_license': 'CC BY-SA 4.0', 'image_attribution': 'Kenneth C. Zirkel', 'image_ai_generated': False}
IMAGE_METADATA['bellini'] = {'image_path': '/media/bellini.webp', 'image_source_url': 'https://commons.wikimedia.org/wiki/File:Bellini_cocktail_in_a_flute-glass.png', 'image_license': 'CC BY-SA 4.0', 'image_attribution': 'Bruce The Deus', 'image_ai_generated': False}
IMAGE_METADATA['between-the-sheets'] = {'image_path': '/media/between-the-sheets.webp', 'image_source_url': 'https://commons.wikimedia.org/wiki/File:Between_The_Sheets_Cocktail.jpg', 'image_license': 'CC BY-SA 4.0', 'image_attribution': 'Zach', 'image_ai_generated': False}
IMAGE_METADATA['black-russian'] = {'image_path': '/media/black-russian.webp', 'image_source_url': 'https://commons.wikimedia.org/wiki/File:Black_Russian.jpg', 'image_license': 'CC BY-SA 3.0', 'image_attribution': 'Will Shenton', 'image_ai_generated': False}
IMAGE_METADATA['bloody-mary'] = {'image_path': '/media/bloody-mary.webp', 'image_source_url': 'https://commons.wikimedia.org/wiki/File:VTR_-_Bloody_Mary.jpg', 'image_license': 'CC BY-SA 2.0', 'image_attribution': 'Edsel L', 'image_ai_generated': False}
IMAGE_METADATA['boulevardier'] = {'image_path': '/media/boulevardier.webp', 'image_source_url': 'https://commons.wikimedia.org/wiki/File:Boulevardier_Cocktail,_Burgersmith_Baton_Rouge.jpg', 'image_license': 'CC BY 2.0', 'image_attribution': 'Paul Lowry', 'image_ai_generated': False}
IMAGE_METADATA['bourbon-cola'] = {'image_path': '/media/bourbon-cola.webp', 'image_source_url': 'https://commons.wikimedia.org/wiki/File:Skopje_(North)_Macedonia_2023-02-09_-_Bourbon_Street_and_Coca-Cola.jpg', 'image_license': 'CC BY 2.0', 'image_attribution': 'Sharon Hahn Darlin', 'image_ai_generated': False}
IMAGE_METADATA['bramble'] = {'image_path': '/media/bramble.webp', 'image_source_url': 'https://commons.wikimedia.org/wiki/File:Bramble_Cocktail_(float).jpg', 'image_license': 'CC BY-SA 4.0', 'image_attribution': 'Erich Wagner (www.eventografie.de)', 'image_ai_generated': False}
IMAGE_METADATA['brandy-alexander'] = {'image_path': '/media/brandy-alexander.webp', 'image_source_url': 'https://commons.wikimedia.org/wiki/File:Brandy_Alexander_on_the_Rocks.jpg', 'image_license': 'CC BY-SA 3.0', 'image_attribution': 'Will Shenton', 'image_ai_generated': False}
IMAGE_METADATA['brandy-cola'] = {'image_path': '/media/brandy-cola.webp', 'image_source_url': 'https://commons.wikimedia.org/wiki/File:Kirk-a-kola.jpg', 'image_license': 'CC0', 'image_attribution': 'Shisma', 'image_ai_generated': False}
IMAGE_METADATA['brandy-crusta'] = {'image_path': '/media/brandy-crusta.webp', 'image_source_url': 'https://commons.wikimedia.org/wiki/File:Bellocq_brandy_crusta,_New_Orleans.jpg', 'image_license': 'CC BY 2.0', 'image_attribution': 'Krista', 'image_ai_generated': False}
IMAGE_METADATA['brandy-orange'] = {'image_path': '/media/brandy-orange.webp', 'image_source_url': 'https://commons.wikimedia.org/wiki/File:Glass_of_Sangria_-_Tinto_Taperia_2026-05-17.jpg', 'image_license': 'CC0', 'image_attribution': 'Andy Li', 'image_ai_generated': False}
IMAGE_METADATA['brandy-pineapple'] = {'image_path': '/media/brandy-pineapple.webp', 'image_source_url': 'https://commons.wikimedia.org/wiki/File:Brandy_sour_(22656571926).jpg', 'image_license': 'CC BY 2.0', 'image_attribution': 'Walter Schärer from Switzerland', 'image_ai_generated': False}
IMAGE_METADATA['brandy-sour'] = {'image_path': '/media/brandy-sour.webp', 'image_source_url': 'https://commons.wikimedia.org/wiki/File:Brandy_sour_(22656571926).jpg', 'image_license': 'CC BY 2.0', 'image_attribution': 'Walter Schärer from Switzerland', 'image_ai_generated': False}
IMAGE_METADATA['caipirinha'] = {'image_path': '/media/caipirinha.webp', 'image_source_url': 'https://commons.wikimedia.org/wiki/File:Cocktail_Caipirinha_raw.jpg', 'image_license': 'Public domain', 'image_attribution': 'Christian', 'image_ai_generated': False}
IMAGE_METADATA['campari-orange'] = {'image_path': '/media/campari-orange.webp', 'image_source_url': 'https://commons.wikimedia.org/wiki/File:Campari_Orange.jpg', 'image_license': 'CC BY-SA 4.0', 'image_attribution': 'eWikiLearner', 'image_ai_generated': False}
IMAGE_METADATA['campari-soda'] = {'image_path': '/media/campari-soda.webp', 'image_source_url': 'https://commons.wikimedia.org/wiki/File:Campari_Soda_(2).jpg', 'image_license': 'CC BY 2.0', 'image_attribution': 'https://www.flickr.com/photos/mesec/', 'image_ai_generated': False}
IMAGE_METADATA['campari-spritz'] = {'image_path': '/media/campari-spritz.webp', 'image_source_url': 'https://commons.wikimedia.org/wiki/File:20120704_170702_venezia_1584.jpg', 'image_license': 'CC BY-SA 4.0', 'image_attribution': 'Gunther H.G. Geick', 'image_ai_generated': False}
IMAGE_METADATA['campari-tonic'] = {'image_path': '/media/campari-tonic.webp', 'image_source_url': 'https://commons.wikimedia.org/wiki/File:Fiola_-_March_2018_-_Sarah_Stierch_04.jpg', 'image_license': 'CC BY 4.0', 'image_attribution': 'Missvain', 'image_ai_generated': False}
IMAGE_METADATA['canchanchara'] = {'image_path': '/media/canchanchara.webp', 'image_source_url': 'https://commons.wikimedia.org/wiki/File:Canchanchara.jpg', 'image_license': 'CC BY 2.0', 'image_attribution': 'Miriam Gómez Blanes', 'image_ai_generated': False}
IMAGE_METADATA['cape-codder'] = {'image_path': '/media/cape-codder.webp', 'image_source_url': 'https://commons.wikimedia.org/wiki/File:Cape_Codder,_Tommy_Doyles_Irish_Pub,_Hyannis_MA.jpg', 'image_license': 'CC BY-SA 3.0', 'image_attribution': 'John Phelan', 'image_ai_generated': False}
IMAGE_METADATA['casino'] = {'image_path': '/media/casino.webp', 'image_source_url': 'https://commons.wikimedia.org/wiki/File:Bistro_Napa_at_the_Atlantis_Casino_Resort_Spa_in_Reno,_Nevada_-_July_2021_-_Sarah_Stierch_03.jpg', 'image_license': 'CC BY 4.0', 'image_attribution': 'Missvain', 'image_ai_generated': False}
IMAGE_METADATA['champagne-cocktail'] = {'image_path': '/media/champagne-cocktail.webp', 'image_source_url': 'https://commons.wikimedia.org/wiki/File:Pear_cranberry_sparkling_wine_or_champagne_cocktail_in_a_flute_(15668298752).jpg', 'image_license': 'CC BY 2.0', 'image_attribution': 'Personal Creations', 'image_ai_generated': False}
IMAGE_METADATA['chartreuse-swizzle'] = {'image_path': '/media/chartreuse-swizzle.webp', 'image_source_url': 'https://commons.wikimedia.org/wiki/File:Chartreuse_swizzle.jpg', 'image_license': 'CC BY 4.0', 'image_attribution': 'BanjoZebra', 'image_ai_generated': False}
IMAGE_METADATA['cherry-cola-style'] = {'image_path': '/media/cherry-cola-style.webp', 'image_source_url': 'https://commons.wikimedia.org/wiki/File:Cherry_Cola.jpg', 'image_license': 'CC0', 'image_attribution': 'Graciepitts', 'image_ai_generated': False}
IMAGE_METADATA['clover-club'] = {'image_path': '/media/clover-club.webp', 'image_source_url': 'https://commons.wikimedia.org/wiki/File:15-09-26-RalfR-WLC-0120.jpg', 'image_license': 'CC BY-SA 3.0', 'image_attribution': 'Ralf Roletschek', 'image_ai_generated': False}
IMAGE_METADATA['club-cranberry-mocktail'] = {'image_path': '/media/club-cranberry-mocktail.webp', 'image_source_url': 'https://commons.wikimedia.org/wiki/File:SeaDream_II_%E2%80%94_Top_Of_The_Yacht_Bar_%E2%80%94_Drink_of_the_Day.JPG', 'image_license': 'CC BY 2.0 de', 'image_attribution': 'User:Mattes', 'image_ai_generated': False}
IMAGE_METADATA['coffee-cognac'] = {'image_path': '/media/coffee-cognac.webp', 'image_source_url': 'https://commons.wikimedia.org/wiki/File:Br%C3%BBlot_charentais_01.JPG', 'image_license': 'CC BY-SA 4.0', 'image_attribution': 'Salix', 'image_ai_generated': False}
IMAGE_METADATA['coffee-liqueur-cream'] = {'image_path': '/media/coffee-liqueur-cream.webp', 'image_source_url': 'https://commons.wikimedia.org/wiki/File:Heugemeug.jpg', 'image_license': 'CC BY-SA 4.0', 'image_attribution': 'Takeaway', 'image_ai_generated': False}
IMAGE_METADATA['coffee-old-fashioned'] = {'image_path': '/media/coffee-old-fashioned.webp', 'image_source_url': 'https://commons.wikimedia.org/wiki/File:Old_fashioned_doughnut1.jpg', 'image_license': 'CC BY 2.0', 'image_attribution': 'Kenny Louie from Burnaby, Canada', 'image_ai_generated': False}
IMAGE_METADATA['cognac-coffee'] = {'image_path': '/media/cognac-coffee.webp', 'image_source_url': 'https://commons.wikimedia.org/wiki/File:Restaurant_Llu%C3%A7an%C3%A8s_Kaffe,_petit_fours_og_cognac_(4254823806).jpg', 'image_license': 'CC BY-SA 2.0', 'image_attribution': 'cyclonebill from Copenhagen, Denmark', 'image_ai_generated': False}
IMAGE_METADATA['cognac-cranberry'] = {'image_path': '/media/cognac-cranberry.webp', 'image_source_url': 'https://commons.wikimedia.org/wiki/File:Selection_of_hot_dogs.jpg', 'image_license': 'CC BY-SA 2.0', 'image_attribution': 'Paul Goyette', 'image_ai_generated': False}
IMAGE_METADATA['cognac-orange'] = {'image_path': '/media/cognac-orange.webp', 'image_source_url': 'https://commons.wikimedia.org/wiki/File:Sidecar-cocktail.jpg', 'image_license': 'CC BY 2.0', 'image_attribution': 'Evan Swigart from Chicago, USA', 'image_ai_generated': False}
IMAGE_METADATA['corpse-reviver-2'] = {'image_path': '/media/corpse-reviver-2.webp', 'image_source_url': 'https://commons.wikimedia.org/wiki/File:Corpse_Reviver_2.jpg', 'image_license': 'CC BY-SA 3.0', 'image_attribution': 'Will Shenton', 'image_ai_generated': False}
IMAGE_METADATA['cosmopolitan'] = {'image_path': '/media/cosmopolitan.webp', 'image_source_url': 'https://commons.wikimedia.org/wiki/File:Cosmopolitan_cocktail_ingredients.png', 'image_license': 'CC BY-SA 4.0', 'image_attribution': 'GeoO', 'image_ai_generated': False}
IMAGE_METADATA['cuba-libre'] = {'image_path': '/media/cuba-libre.webp', 'image_source_url': 'https://commons.wikimedia.org/wiki/File:15-09-26-RalfR-WLC-0056.jpg', 'image_license': 'CC BY-SA 3.0', 'image_attribution': 'Ralf Roletschek', 'image_ai_generated': False}
IMAGE_METADATA['cucumber-cooler'] = {'image_path': '/media/cucumber-cooler.webp', 'image_source_url': 'https://commons.wikimedia.org/wiki/File:Cucumber_pachadi-_My_home_Bangalore_-Karnataka_-pic_08.jpg', 'image_license': 'CC BY-SA 4.0', 'image_attribution': 'Shruthi Gaurav Alva', 'image_ai_generated': False}
IMAGE_METADATA['cucumber-gimlet'] = {'image_path': '/media/cucumber-gimlet.webp', 'image_source_url': 'https://commons.wikimedia.org/wiki/File:Cucumbers!_(4921518956).jpg', 'image_license': 'CC BY 2.0', 'image_attribution': 'Karen and Brad Emerson', 'image_ai_generated': False}
IMAGE_METADATA['daiquiri'] = {'image_path': '/media/daiquiri.webp', 'image_source_url': 'https://commons.wikimedia.org/wiki/File:Classic_Daiquiri_in_Cocktail_Glass.jpg', 'image_license': 'CC BY-SA 3.0', 'image_attribution': 'Will Shenton', 'image_ai_generated': False}
IMAGE_METADATA['dark-rum-cola'] = {'image_path': '/media/dark-rum-cola.webp', 'image_source_url': 'https://commons.wikimedia.org/wiki/File:Coca-Cola-signature_mixers-smoky_notes-back.jpg', 'image_license': 'CC0', 'image_attribution': 'FlippyFlink', 'image_ai_generated': False}
IMAGE_METADATA['dark-rum-pineapple'] = {'image_path': '/media/dark-rum-pineapple.webp', 'image_source_url': 'https://commons.wikimedia.org/wiki/File:Zombiecocktail.jpg', 'image_license': 'CC BY-SA 3.0', 'image_attribution': 'Magnetic Rag', 'image_ai_generated': False}
IMAGE_METADATA['dark-rum-sour'] = {'image_path': '/media/dark-rum-sour.webp', 'image_source_url': 'https://commons.wikimedia.org/wiki/File:Punch_Davy_Jones%27s_Locker.png', 'image_license': 'Public domain', 'image_attribution': 'John Tenniel', 'image_ai_generated': False}
IMAGE_METADATA['dark-stormy'] = {'image_path': '/media/dark-stormy.webp', 'image_source_url': 'https://commons.wikimedia.org/wiki/File:15-09-26-RalfR-WLC-0202.jpg', 'image_license': 'CC BY-SA 3.0', 'image_attribution': 'Ralf Roletschek', 'image_ai_generated': False}
IMAGE_METADATA['espresso-martini'] = {'image_path': '/media/espresso-martini.webp', 'image_source_url': 'https://commons.wikimedia.org/wiki/File:Espresso_Martini_on_a_bar.jpg', 'image_license': 'CC BY-SA 4.0', 'image_attribution': 'AlphaLemur', 'image_ai_generated': False}
IMAGE_METADATA['french-75'] = {'image_path': '/media/french-75.webp', 'image_source_url': 'https://commons.wikimedia.org/wiki/File:French_75.jpg', 'image_license': 'CC BY-SA 2.0', 'image_attribution': 'https://www.flickr.com/people/garyjwood/', 'image_ai_generated': False}
IMAGE_METADATA['french-connection'] = {'image_path': '/media/french-connection.webp', 'image_source_url': 'https://commons.wikimedia.org/wiki/File:French_Connection_(cocktail).jpg', 'image_license': 'CC BY-SA 4.0', 'image_attribution': 'Arnaud 25', 'image_ai_generated': False}
IMAGE_METADATA['french-martini'] = {'image_path': '/media/french-martini.webp', 'image_source_url': 'https://commons.wikimedia.org/wiki/File:Chambord_French_Martini_Cocktail.jpg', 'image_license': 'CC BY-SA 3.0', 'image_attribution': 'Brown-Forman Corporation', 'image_ai_generated': False}
IMAGE_METADATA['garibaldi'] = {'image_path': '/media/garibaldi.webp', 'image_source_url': 'https://commons.wikimedia.org/wiki/File:Garibaldi_cocktail_bright.jpg', 'image_license': 'CC BY 4.0', 'image_attribution': 'User:BanjoZebra', 'image_ai_generated': False}
# END GENERATED BATCH 1 IMAGE METADATA

BASE_RECIPES = [
    {"key":"old-fashioned","name":"Old Fashioned","type":"cocktail","version":"1.0","description":"A classic whiskey cocktail built around spirit, sugar, and bitters.","instructions":"Add bourbon, simple syrup, and bitters to a rocks glass with ice. Stir until chilled. Garnish with orange peel.","source":"IBA reference","url":"https://iba-world.com/cocktails/","ingredients":[("Bourbon",2.0,"oz",False),("Simple Syrup",0.25,"oz",False),("Angostura Bitters",2.0,"dash",False),("Orange Peel",1.0,"pc",True)]},
    {"key":"manhattan","name":"Manhattan","type":"cocktail","version":"1.0","description":"Whiskey, sweet vermouth, and bitters.","instructions":"Stir whiskey, sweet vermouth, and bitters with ice until chilled, then strain into a chilled glass.","source":"IBA reference","url":"https://iba-world.com/cocktails/","ingredients":[("Rye Whiskey",2.0,"oz",False),("Sweet Vermouth",1.0,"oz",False),("Angostura Bitters",2.0,"dash",False)]},
    {"key":"margarita","name":"Margarita","type":"cocktail","version":"1.0","description":"A tequila sour with orange liqueur and lime.","instructions":"Shake tequila, triple sec, and lime juice with ice. Strain into a chilled glass, optionally with a salted rim.","source":"IBA reference","url":"https://iba-world.com/cocktails/","ingredients":[("Blanco Tequila",2.0,"oz",False),("Triple Sec",1.0,"oz",False),("Lime Juice",1.0,"oz",False),("Salt",1.0,"tsp",True)]},
    {"key":"daiquiri","name":"Daiquiri","type":"cocktail","version":"1.0","description":"A simple rum sour with lime and sugar.","instructions":"Shake white rum, lime juice, and simple syrup with ice, then strain into a chilled glass.","source":"IBA reference","url":"https://iba-world.com/cocktails/","ingredients":[("White Rum",2.0,"oz",False),("Lime Juice",1.0,"oz",False),("Simple Syrup",0.75,"oz",False)]},
    {"key":"gin-tonic","name":"Gin and Tonic","type":"cocktail","version":"1.0","description":"Gin lengthened with tonic water.","instructions":"Build gin and tonic water over ice in a highball glass. Stir gently.","source":"Open classic reference","url":"https://en.wikibooks.org/wiki/Bartending/Cocktails","ingredients":[("Gin",2.0,"oz",False),("Tonic Water",4.0,"oz",False),("Lime Wedge",1.0,"pc",True)]},
    {"key":"moscow-mule","name":"Moscow Mule","type":"cocktail","version":"1.0","description":"Vodka, ginger beer, and lime.","instructions":"Build vodka and lime juice over ice, top with ginger beer, and stir gently.","source":"Open classic reference","url":"https://en.wikibooks.org/wiki/Bartending/Cocktails","ingredients":[("Vodka",2.0,"oz",False),("Ginger Beer",4.0,"oz",False),("Lime Juice",0.5,"oz",False)]},
    {"key":"virgin-moscow-mule","name":"Virgin Moscow Mule","type":"mocktail","version":"1.0","description":"A non-alcoholic mule-style drink with ginger beer and lime.","instructions":"Build lime juice over ice, top with ginger beer and club soda, then stir gently.","source":"Virtual Bartender curated mocktail","url":"local://virtual-bartender/curated","parent":"moscow-mule","ingredients":[("Ginger Beer",4.0,"oz",False),("Lime Juice",0.75,"oz",False),("Club Soda",1.0,"oz",False)]},
    {"key":"whiskey-ginger","name":"Whiskey Ginger","type":"cocktail","version":"1.0","description":"Whiskey topped with ginger ale.","instructions":"Build whiskey and ginger ale over ice and stir gently.","source":"Virtual Bartender curated highball","url":"local://virtual-bartender/curated","ingredients":[("Bourbon",2.0,"oz",False),("Ginger Ale",4.0,"oz",False)]},
    {"key":"rum-sprite","name":"Rum and Sprite","type":"cocktail","version":"1.0","description":"A simple rum highball with lemon-lime soda.","instructions":"Build rum and Sprite over ice and stir gently.","source":"Virtual Bartender curated highball","url":"local://virtual-bartender/curated","ingredients":[("White Rum",2.0,"oz",False),("Sprite",4.0,"oz",False)]},
    {"key":"tequila-tonic","name":"Tequila Tonic","type":"cocktail","version":"1.0","description":"Tequila and tonic water over ice.","instructions":"Build tequila and tonic water over ice and stir gently.","source":"Virtual Bartender curated highball","url":"local://virtual-bartender/curated","ingredients":[("Blanco Tequila",2.0,"oz",False),("Tonic Water",4.0,"oz",False),("Lime Wedge",1.0,"pc",True)]},
]

def seed_builtin_data(db: Session) -> dict[str, int]:
    units = {}
    for data in BUILTIN_UNITS + UNITS_V6 + UNITS_V7 + UNITS_V8:
        unit = db.scalar(select(Unit).where(Unit.abbreviation == data["abbreviation"]))
        if not unit:
            unit = Unit(**data)
            db.add(unit)
            db.flush()
        units[unit.abbreviation] = unit

    ingredients = {}
    for name, category in BASE_INGREDIENTS + INGREDIENTS_V2 + INGREDIENTS_V6 + INGREDIENTS_V7 + INGREDIENTS_V8:
        ingredient = db.scalar(select(Ingredient).where(Ingredient.name == name))
        if not ingredient:
            ingredient = Ingredient(name=name, category=category, is_user_created=False, is_active=True)
            db.add(ingredient)
            db.flush()
        ingredients[name] = ingredient

    substitution_count = 0
    for required, substitute, priority in SUBSTITUTIONS_V2:
        existing = db.scalar(select(IngredientSubstitution).where(IngredientSubstitution.required_ingredient_id == ingredients[required].id, IngredientSubstitution.substitute_ingredient_id == ingredients[substitute].id))
        if not existing:
            db.add(IngredientSubstitution(required_ingredient_id=ingredients[required].id, substitute_ingredient_id=ingredients[substitute].id, priority=priority))
            substitution_count += 1

    recipes_added = 0
    all_recipes = BASE_RECIPES + RECIPES_V2 + RECIPES_V3 + RECIPES_V4 + RECIPES_V5 + RECIPES_V6 + RECIPES_V7 + RECIPES_V8

    # Catalog validation safety net: every ingredient referenced by a recipe must
    # exist before recipe rows are inserted. This keeps a metadata omission from
    # crashing the entire application at startup.
    for recipe_data in all_recipes:
        for ingredient_name, _quantity, _unit_abbr, _optional in recipe_data["ingredients"]:
            if ingredient_name not in ingredients:
                ingredient = db.scalar(select(Ingredient).where(Ingredient.name == ingredient_name))
                if not ingredient:
                    ingredient = Ingredient(name=ingredient_name, category="Other", is_user_created=False, is_active=True)
                    db.add(ingredient)
                    db.flush()
                ingredients[ingredient_name] = ingredient

    recipes_by_key = {}
    for data in all_recipes:
        recipe = db.scalar(select(Recipe).where(Recipe.built_in_key == data["key"]))
        if not recipe:
            recipe = Recipe(name=data["name"], description=data["description"], recipe_type=data["type"], source_type="built_in", built_in_key=data["key"], version=data["version"], instructions=data["instructions"], is_active=True)
            db.add(recipe)
            db.flush()
            for order, (ingredient_name, quantity, unit_abbr, optional) in enumerate(data["ingredients"], 1):
                db.add(RecipeIngredient(recipe_id=recipe.id, ingredient_id=ingredients[ingredient_name].id, quantity=quantity, unit_id=units[unit_abbr].id, is_optional=optional, display_order=order))
            db.add(RecipeSource(recipe_id=recipe.id, url=data["url"], source_name=data["source"], original_title=data["name"]))
            recipes_added += 1
        image_meta = IMAGE_METADATA.get(data["key"])
        if image_meta:
            for field, value in image_meta.items():
                setattr(recipe, field, value)
        recipes_by_key[data["key"]] = recipe

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
    return {"units":len(units),"ingredients":len(ingredients),"recipes_total_catalog":len(all_recipes),"recipes_added":recipes_added,"substitutions_added":substitution_count,"variant_links_updated":variant_links,"aliases_added":aliases_added}
