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
IMAGE_METADATA['bramble'] = {'image_path': '/media/bramble.webp', 'image_source_url': 'https://commons.wikimedia.org/wiki/File:Bramble_Cocktail_(float).jpg', 'image_license': 'CC BY-SA 4.0', 'image_attribution': 'Erich Wagner (www.eventografie.de)', 'image_ai_generated': False}
IMAGE_METADATA['brandy-alexander'] = {'image_path': '/media/brandy-alexander.webp', 'image_source_url': 'https://commons.wikimedia.org/wiki/File:Brandy_Alexander_on_the_Rocks.jpg', 'image_license': 'CC BY-SA 3.0', 'image_attribution': 'Will Shenton', 'image_ai_generated': False}
IMAGE_METADATA['brandy-cola'] = {'image_path': '/media/brandy-cola.webp', 'image_source_url': 'https://commons.wikimedia.org/wiki/File:Kirk-a-kola.jpg', 'image_license': 'CC0', 'image_attribution': 'Shisma', 'image_ai_generated': False}
IMAGE_METADATA['brandy-crusta'] = {'image_path': '/media/brandy-crusta.webp', 'image_source_url': 'https://commons.wikimedia.org/wiki/File:Bellocq_brandy_crusta,_New_Orleans.jpg', 'image_license': 'CC BY 2.0', 'image_attribution': 'Krista', 'image_ai_generated': False}
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
IMAGE_METADATA['corpse-reviver-2'] = {'image_path': '/media/corpse-reviver-2.webp', 'image_source_url': 'https://commons.wikimedia.org/wiki/File:Corpse_Reviver_2.jpg', 'image_license': 'CC BY-SA 3.0', 'image_attribution': 'Will Shenton', 'image_ai_generated': False}
IMAGE_METADATA['cosmopolitan'] = {'image_path': '/media/cosmopolitan.webp', 'image_source_url': 'https://commons.wikimedia.org/wiki/File:Cosmopolitan_cocktail_ingredients.png', 'image_license': 'CC BY-SA 4.0', 'image_attribution': 'GeoO', 'image_ai_generated': False}
IMAGE_METADATA['cuba-libre'] = {'image_path': '/media/cuba-libre.webp', 'image_source_url': 'https://commons.wikimedia.org/wiki/File:15-09-26-RalfR-WLC-0056.jpg', 'image_license': 'CC BY-SA 3.0', 'image_attribution': 'Ralf Roletschek', 'image_ai_generated': False}
IMAGE_METADATA['cucumber-cooler'] = {'image_path': '/media/cucumber-cooler.webp', 'image_source_url': 'https://commons.wikimedia.org/wiki/File:Cucumber_pachadi-_My_home_Bangalore_-Karnataka_-pic_08.jpg', 'image_license': 'CC BY-SA 4.0', 'image_attribution': 'Shruthi Gaurav Alva', 'image_ai_generated': False}
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

# BEGIN GENERATED FINAL IMAGE METADATA
IMAGE_METADATA['cardinale'] = {'image_path': '/media/cardinale.webp', 'image_source_url': 'https://commons.wikimedia.org/wiki/File:Rosa_%27Claudia_Cardinale%27,_Ch%C3%A2teau_d%27Eu-76_(2)_%27.jpg', 'image_license': 'CC BY-SA 4.0', 'image_attribution': 'APictche', 'image_ai_generated': False}
IMAGE_METADATA['club-pineapple-mocktail'] = {'image_path': '/media/club-pineapple-mocktail.webp', 'image_source_url': 'https://commons.wikimedia.org/wiki/File:Recipes_for_the_Manufacture_of_Aerated_%26_Mineral_Waters_and_Non-Alcoholic_Cordials_-_DPLA_-_f0f1ad85cbe19998d323fc350788106e_(page_51).jpg', 'image_license': 'Public domain', 'image_attribution': 'Bush, William Ernest, 1861-1903', 'image_ai_generated': False}
IMAGE_METADATA['gimlet'] = {'image_path': '/media/gimlet.webp', 'image_source_url': 'https://commons.wikimedia.org/wiki/File:A_Gimlet_cocktail_(Isla_Holbox).jpg', 'image_license': 'CC BY-SA 2.0', 'image_attribution': 'Bruno Rijsman', 'image_ai_generated': False}
IMAGE_METADATA['gin-basil-smash'] = {'image_path': '/media/gin-basil-smash.webp', 'image_source_url': 'https://commons.wikimedia.org/wiki/File:Gin_Basil_Smash.jpg', 'image_license': 'CC BY-SA 4.0', 'image_attribution': 'Erich Wagner (www.eventografie.de)', 'image_ai_generated': False}
IMAGE_METADATA['gin-cranberry'] = {'image_path': '/media/gin-cranberry.webp', 'image_source_url': 'https://commons.wikimedia.org/wiki/File:Water_Grill_-_Las_Vegas_-_Dec_2019_-_Stierch_06.jpg', 'image_license': 'CC BY 4.0', 'image_attribution': 'Missvain', 'image_ai_generated': False}
IMAGE_METADATA['gin-fizz'] = {'image_path': '/media/gin-fizz.webp', 'image_source_url': 'https://commons.wikimedia.org/wiki/File:Tropical_Gin_Fizz_Cocktail.jpg', 'image_license': 'CC BY-SA 2.0', 'image_attribution': 'mkorcuska', 'image_ai_generated': False}
IMAGE_METADATA['gin-grapefruit'] = {'image_path': '/media/gin-grapefruit.webp', 'image_source_url': 'https://commons.wikimedia.org/wiki/File:Self-made_gin_grapefruit_long_drink.jpg', 'image_license': 'CC BY-SA 3.0', 'image_attribution': 'JIP', 'image_ai_generated': False}
IMAGE_METADATA['gin-lemonade'] = {'image_path': '/media/gin-lemonade.webp', 'image_source_url': 'https://commons.wikimedia.org/wiki/File:Self-made_gin_pink_grapefruit_long_drink.jpg', 'image_license': 'CC BY-SA 3.0', 'image_attribution': 'JIP', 'image_ai_generated': False}
IMAGE_METADATA['gin-rickey'] = {'image_path': '/media/gin-rickey.webp', 'image_source_url': 'https://commons.wikimedia.org/wiki/File:Gin_Rickey.jpg', 'image_license': 'CC BY 2.0', 'image_attribution': 'Scott Veg', 'image_ai_generated': False}
IMAGE_METADATA['gin-soda'] = {'image_path': '/media/gin-soda.webp', 'image_source_url': 'https://commons.wikimedia.org/wiki/File:Gin_and_tonic_at_Grand_Marina_terrace_with_Vappu_decorations.jpg', 'image_license': 'CC BY-SA 3.0', 'image_attribution': 'JIP', 'image_ai_generated': False}
IMAGE_METADATA['gin-sour'] = {'image_path': '/media/gin-sour.webp', 'image_source_url': 'https://commons.wikimedia.org/wiki/File:Spiced_Sloe_Sour.jpg', 'image_license': 'CC BY-SA 4.0', 'image_attribution': 'SyrupDee', 'image_ai_generated': False}
IMAGE_METADATA['gin-spritz'] = {'image_path': '/media/gin-spritz.webp', 'image_source_url': 'https://commons.wikimedia.org/wiki/File:Red_Spritz.jpg', 'image_license': 'CC BY-SA 4.0', 'image_attribution': 'JIP', 'image_ai_generated': False}
IMAGE_METADATA['gin-tonic'] = {'image_path': '/media/gin-tonic.webp', 'image_source_url': 'https://commons.wikimedia.org/wiki/File:Gin_and_tonic_cocktail_with_wedge_of_lime.jpg', 'image_license': 'CC BY-SA 4.0', 'image_attribution': 'Davidnuescheler', 'image_ai_generated': False}
IMAGE_METADATA['godfather'] = {'image_path': '/media/godfather.webp', 'image_source_url': 'https://commons.wikimedia.org/wiki/File:Godfather_cocktail.jpg', 'image_license': 'CC BY 2.0', 'image_attribution': 'Stuart Webster from Southampton, England', 'image_ai_generated': False}
IMAGE_METADATA['grasshopper'] = {'image_path': '/media/grasshopper.webp', 'image_source_url': 'https://commons.wikimedia.org/wiki/File:Grasshopper_Cocktail,_French_Quarter,_New_Orleans.jpg', 'image_license': 'CC BY-SA 2.0', 'image_attribution': 'Miguel Discart', 'image_ai_generated': False}
IMAGE_METADATA['greyhound'] = {'image_path': '/media/greyhound.webp', 'image_source_url': 'https://commons.wikimedia.org/wiki/File:Greyhound_Cocktail.jpg', 'image_license': 'CC BY 2.0', 'image_attribution': 'Scott Veg', 'image_ai_generated': False}
IMAGE_METADATA['hanky-panky'] = {'image_path': '/media/hanky-panky.webp', 'image_source_url': 'https://commons.wikimedia.org/wiki/File:Hanky_Panky_cocktail.jpg', 'image_license': 'CC BY-SA 2.0', 'image_attribution': 'Tim Sackton from Somerville, MA', 'image_ai_generated': False}
IMAGE_METADATA['horses-neck'] = {'image_path': '/media/horses-neck.webp', 'image_source_url': 'https://commons.wikimedia.org/wiki/File:Horse%27s_Neck_cocktail.jpg', 'image_license': 'CC BY-SA 3.0', 'image_attribution': 'Plume.janvier', 'image_ai_generated': False}
IMAGE_METADATA['iba-tiki'] = {'image_path': '/media/iba-tiki.webp', 'image_source_url': 'https://commons.wikimedia.org/wiki/File:IBA_Tiki_at_Civil_Liberties_in_Toronto.jpg', 'image_license': 'CC0', 'image_attribution': 'Adanicklmao', 'image_ai_generated': False}
IMAGE_METADATA['illegal'] = {'image_path': '/media/illegal.webp', 'image_source_url': 'https://commons.wikimedia.org/wiki/File:Illegal_cocktail.jpg', 'image_license': 'CC BY 4.0', 'image_attribution': 'BanjoZebra', 'image_ai_generated': False}
IMAGE_METADATA['john-collins'] = {'image_path': '/media/john-collins.webp', 'image_source_url': 'https://commons.wikimedia.org/wiki/File:IBA_Cocktail_John_Collins_(29221732881).jpg', 'image_license': 'CC BY-SA 2.0', 'image_attribution': 'Michael Styne from Averill Park, NY, USA', 'image_ai_generated': False}
IMAGE_METADATA['jungle-bird'] = {'image_path': '/media/jungle-bird.webp', 'image_source_url': 'https://commons.wikimedia.org/wiki/File:Jungle_bird_cocktail.jpg', 'image_license': 'CC BY 4.0', 'image_attribution': 'BanjoZebra', 'image_ai_generated': False}
IMAGE_METADATA['kir'] = {'image_path': '/media/kir.webp', 'image_source_url': 'https://commons.wikimedia.org/wiki/File:Kir_cocktail.jpg', 'image_license': 'CC BY 2.0', 'image_attribution': 'Stuart Webster from Southampton, England', 'image_ai_generated': False}
IMAGE_METADATA['last-word'] = {'image_path': '/media/last-word.webp', 'image_source_url': 'https://commons.wikimedia.org/wiki/File:Last_Word_cocktail,_Baton_Rouge_2025.jpg', 'image_license': 'CC BY 4.0', 'image_attribution': 'Paul Lowry', 'image_ai_generated': False}
IMAGE_METADATA['lemon-soda-mocktail'] = {'image_path': '/media/lemon-soda-mocktail.webp', 'image_source_url': 'https://commons.wikimedia.org/wiki/File:Long_Shot_Lemon.jpg', 'image_license': 'CC BY-SA 4.0', 'image_attribution': 'JIP', 'image_ai_generated': False}
IMAGE_METADATA['lime-tonic-mocktail'] = {'image_path': '/media/lime-tonic-mocktail.webp', 'image_source_url': 'https://commons.wikimedia.org/wiki/File:Lime_tonic_water.jpg', 'image_license': 'CC BY-SA 4.0', 'image_attribution': 'Corn cheese', 'image_ai_generated': False}
IMAGE_METADATA['long-island-iced-tea'] = {'image_path': '/media/long-island-iced-tea.webp', 'image_source_url': 'https://commons.wikimedia.org/wiki/File:Long_Island_Iced_Tea_with_Lemon_and_Straw.jpg', 'image_license': 'CC BY 2.0', 'image_attribution': 'Alisdair McDiarmid from Glasgow, United Kingdom', 'image_ai_generated': False}
IMAGE_METADATA['mai-tai'] = {'image_path': '/media/mai-tai.webp', 'image_source_url': 'https://commons.wikimedia.org/wiki/File:Love_in_Goa_%26_Mai_Tai_-_Calcutta_16_2026-07-11.jpg', 'image_license': 'CC0', 'image_attribution': 'Andy Li', 'image_ai_generated': False}
IMAGE_METADATA['margarita'] = {'image_path': '/media/margarita.webp', 'image_source_url': 'https://commons.wikimedia.org/wiki/File:MargaritaReal.jpg', 'image_license': 'CC BY-SA 3.0', 'image_attribution': 'Akke Monasso', 'image_ai_generated': False}
IMAGE_METADATA['martinez'] = {'image_path': '/media/martinez.webp', 'image_source_url': 'https://commons.wikimedia.org/wiki/File:Martinez_Cocktail.jpg', 'image_license': 'CC BY-SA 3.0', 'image_attribution': 'Will Shenton', 'image_ai_generated': False}
IMAGE_METADATA['mary-pickford'] = {'image_path': '/media/mary-pickford.webp', 'image_source_url': 'https://commons.wikimedia.org/wiki/File:Mary_Pickford_Cocktail.jpg', 'image_license': 'CC BY-SA 3.0', 'image_attribution': 'Will Shenton', 'image_ai_generated': False}
IMAGE_METADATA['mezcal-ginger'] = {'image_path': '/media/mezcal-ginger.webp', 'image_source_url': 'https://commons.wikimedia.org/wiki/File:Har_Mar_Superstar_Mezcal,_Ginger,_Lemon,_Local_Honey,_Thyme_(34320058573).jpg', 'image_license': 'CC BY 2.0', 'image_attribution': 'T.Tseng', 'image_ai_generated': False}
IMAGE_METADATA['mezcal-margarita'] = {'image_path': '/media/mezcal-margarita.webp', 'image_source_url': 'https://commons.wikimedia.org/wiki/File:El_Grito_at_Kina%27s_Kitchen_and_Bar,_Sonoma,_California_-_Sarah_Stierch_10.jpg', 'image_license': 'CC BY 4.0', 'image_attribution': 'Missvain', 'image_ai_generated': False}
IMAGE_METADATA['mezcal-pineapple'] = {'image_path': '/media/mezcal-pineapple.webp', 'image_source_url': 'https://commons.wikimedia.org/wiki/File:Sip_I,_M%C3%A9rida,_Yucat%C3%A1n_2024.jpg', 'image_license': 'CC BY 2.0', 'image_attribution': 'edenpictures', 'image_ai_generated': False}
IMAGE_METADATA['mezcal-sour'] = {'image_path': '/media/mezcal-sour.webp', 'image_source_url': 'https://commons.wikimedia.org/wiki/File:Delicious_Mezcal_Sour.jpg', 'image_license': 'CC BY 2.0', 'image_attribution': 'https://www.flickr.com/photos/bexwalton/', 'image_ai_generated': False}
IMAGE_METADATA['mimosa'] = {'image_path': '/media/mimosa.webp', 'image_source_url': 'https://commons.wikimedia.org/wiki/File:Mimosa_cocktail_ingredients.png', 'image_license': 'CC BY-SA 4.0', 'image_attribution': 'GeoO', 'image_ai_generated': False}
IMAGE_METADATA['mint-julep'] = {'image_path': '/media/mint-julep.webp', 'image_source_url': 'https://commons.wikimedia.org/wiki/File:Mint_julep_at_Revel_in_New_Orleans.jpg', 'image_license': 'CC BY-SA 4.0', 'image_attribution': 'Jami430', 'image_ai_generated': False}
IMAGE_METADATA['missionarys-downfall'] = {'image_path': '/media/missionarys-downfall.webp', 'image_source_url': 'https://commons.wikimedia.org/wiki/File:Missionary%27s_downfall.jpg', 'image_license': 'CC BY 4.0', 'image_attribution': 'BanjoZebra', 'image_ai_generated': False}
IMAGE_METADATA['monkey-gland'] = {'image_path': '/media/monkey-gland.webp', 'image_source_url': 'https://commons.wikimedia.org/wiki/File:Monkey_Gland_(11677703163).jpg', 'image_license': 'CC BY-SA 2.0', 'image_attribution': 'Adrian Scottow from London, England', 'image_ai_generated': False}
IMAGE_METADATA['moscow-mule'] = {'image_path': '/media/moscow-mule.webp', 'image_source_url': 'https://commons.wikimedia.org/wiki/File:Moscow_mule_Cocktail_im_Kupferbecher.jpg', 'image_license': 'CC BY-SA 4.0', 'image_attribution': 'Gordito1869', 'image_ai_generated': False}
IMAGE_METADATA['naked-and-famous'] = {'image_path': '/media/naked-and-famous.webp', 'image_source_url': 'https://commons.wikimedia.org/wiki/File:Naked_and_Famous_cocktail.jpg', 'image_license': 'CC BY 4.0', 'image_attribution': 'Rascalisimo', 'image_ai_generated': False}
IMAGE_METADATA['new-york-sour'] = {'image_path': '/media/new-york-sour.webp', 'image_source_url': 'https://commons.wikimedia.org/wiki/File:New_York_Sour.jpg', 'image_license': 'CC BY-SA 4.0', 'image_attribution': 'Erich Wagner (www.eventografie.de)', 'image_ai_generated': False}
IMAGE_METADATA['old-cuban'] = {'image_path': '/media/old-cuban.webp', 'image_source_url': 'https://commons.wikimedia.org/wiki/File:15-09-26-RalfR-WLC-0312.jpg', 'image_license': 'CC BY-SA 3.0', 'image_attribution': 'Ralf Roletschek', 'image_ai_generated': False}
IMAGE_METADATA['orange-blossom'] = {'image_path': '/media/orange-blossom.webp', 'image_source_url': 'https://commons.wikimedia.org/wiki/File:Kitchen_Table_Caf%C3%A9,_Arabi,_Louisiana_-_Orange_Blossom_Special_cocktail.jpg', 'image_license': 'CC BY 2.0', 'image_attribution': 'Infrogmation of New Orleans', 'image_ai_generated': False}
IMAGE_METADATA['paloma'] = {'image_path': '/media/paloma.webp', 'image_source_url': 'https://commons.wikimedia.org/wiki/File:C%C3%B3ctel_paloma_y_sangrita,_Mazatl%C3%A1n,_23_de_noviembre_de_2022_02.jpg', 'image_license': 'CC0', 'image_attribution': 'El Nuevo Doge', 'image_ai_generated': False}
IMAGE_METADATA['paper-plane'] = {'image_path': '/media/paper-plane.webp', 'image_source_url': 'https://commons.wikimedia.org/wiki/File:Taub_Famiy_Outpost_-_June_9_2021_-_Sarah_Stierch.jpg', 'image_license': 'CC BY 4.0', 'image_attribution': 'Missvain', 'image_ai_generated': False}
IMAGE_METADATA['paradise'] = {'image_path': '/media/paradise.webp', 'image_source_url': 'https://commons.wikimedia.org/wiki/File:Rainbow-paradise-cocktail-scaled-scaled-735x1102.webp', 'image_license': 'CC0', 'image_attribution': 'Nicole Goldman', 'image_ai_generated': False}
IMAGE_METADATA['penicillin'] = {'image_path': '/media/penicillin.webp', 'image_source_url': 'https://commons.wikimedia.org/wiki/File:Penicillin_Cocktail.png', 'image_license': 'CC BY-SA 4.0', 'image_attribution': 'Matthias Friedlein (www.augustine-bar.de)', 'image_ai_generated': False}
IMAGE_METADATA['pineapple-daiquiri'] = {'image_path': '/media/pineapple-daiquiri.webp', 'image_source_url': 'https://commons.wikimedia.org/wiki/File:Garden_Daiquiri_and_Cocktail_Snacks_(42941099655).jpg', 'image_license': 'CC BY 2.0', 'image_attribution': 'T.Tseng', 'image_ai_generated': False}
IMAGE_METADATA['pineapple-fizz'] = {'image_path': '/media/pineapple-fizz.webp', 'image_source_url': 'https://commons.wikimedia.org/wiki/File:Virgin_Pina_Colada_and_Strawberry_Fizz_-_Etci_Kitchen_2025-09-22.jpg', 'image_license': 'CC0', 'image_attribution': 'Andy Li', 'image_ai_generated': False}
IMAGE_METADATA['pineapple-ginger-mocktail'] = {'image_path': '/media/pineapple-ginger-mocktail.webp', 'image_source_url': 'https://commons.wikimedia.org/wiki/File:Sobo_Juice_In_Northern_Nigeria_5.jpg', 'image_license': 'CC BY-SA 4.0', 'image_attribution': 'Hajjare', 'image_ai_generated': False}
IMAGE_METADATA['pisco-punch'] = {'image_path': '/media/pisco-punch.webp', 'image_source_url': 'https://commons.wikimedia.org/wiki/File:Pisco_Punch.jpg', 'image_license': 'CC BY-SA 2.0', 'image_attribution': 'Ministerio de Relaciones Exteriores', 'image_ai_generated': False}
IMAGE_METADATA['pisco-sour'] = {'image_path': '/media/pisco-sour.webp', 'image_source_url': 'https://commons.wikimedia.org/wiki/File:P%C3%A9rou_Pr%C3%A9paration_d%27un_cocktail_Pisco_Sour.jpg', 'image_license': 'CC BY-SA 4.0', 'image_attribution': 'Pierre André Leclercq', 'image_ai_generated': False}
IMAGE_METADATA['planters-punch'] = {'image_path': '/media/planters-punch.webp', 'image_source_url': 'https://commons.wikimedia.org/wiki/File:Planters_Punch_1.jpg', 'image_license': 'CC BY-SA 3.0 de', 'image_attribution': 'Achim Schleuning (E-Mail: comander02_de@yahoo.de)', 'image_ai_generated': False}
IMAGE_METADATA['porn-star-martini'] = {'image_path': '/media/porn-star-martini.webp', 'image_source_url': 'https://commons.wikimedia.org/wiki/File:Porn_star_martini_cocktail.jpg', 'image_license': 'CC BY 2.0', 'image_attribution': 'Ben Sutherland', 'image_ai_generated': False}
IMAGE_METADATA['porto-flip'] = {'image_path': '/media/porto-flip.webp', 'image_source_url': 'https://commons.wikimedia.org/wiki/File:Porto_Flip.jpg', 'image_license': 'CC BY 2.0', 'image_attribution': 'Stuart Webster', 'image_ai_generated': False}
IMAGE_METADATA['rabo-de-galo'] = {'image_path': '/media/rabo-de-galo.webp', 'image_source_url': 'https://commons.wikimedia.org/wiki/File:Rabo_de_Galo_(1511113688).jpg', 'image_license': 'CC BY-SA 2.0', 'image_attribution': 'Stella Dauer from São Bernardo do Campo, Brasil', 'image_ai_generated': False}
IMAGE_METADATA['ramos-fizz'] = {'image_path': '/media/ramos-fizz.webp', 'image_source_url': 'https://commons.wikimedia.org/wiki/File:Ramos_Fizz.jpg', 'image_license': 'CC BY 2.0', 'image_attribution': 'Stuart Webster', 'image_ai_generated': False}
IMAGE_METADATA['remember-the-maine'] = {'image_path': '/media/remember-the-maine.webp', 'image_source_url': 'https://commons.wikimedia.org/wiki/File:Remember_the_Maine_-_Cocktail.jpg', 'image_license': 'CC BY-SA 2.0', 'image_attribution': 'Adrian Scottow', 'image_ai_generated': False}
IMAGE_METADATA['rob-roy'] = {'image_path': '/media/rob-roy.webp', 'image_source_url': 'https://commons.wikimedia.org/wiki/File:Rob_Roy_Cocktail.jpg', 'image_license': 'CC BY 2.0', 'image_attribution': 'TheCulinaryGeek', 'image_ai_generated': False}
IMAGE_METADATA['rum-lemonade'] = {'image_path': '/media/rum-lemonade.webp', 'image_source_url': 'https://commons.wikimedia.org/wiki/File:Cocktails_(5297823968).jpg', 'image_license': 'CC BY-SA 2.0', 'image_attribution': 'Rishabh Mathur from Bangalore, India', 'image_ai_generated': False}
IMAGE_METADATA['rum-old-fashioned'] = {'image_path': '/media/rum-old-fashioned.webp', 'image_source_url': 'https://commons.wikimedia.org/wiki/File:Rum,_Manhattan,_Tequila_Old_Fashioned_(1).jpg', 'image_license': 'CC BY-SA 3.0', 'image_attribution': 'File:Rum, Manhattan, Tequila Old Fashioned.jpg: Cocktailmarler\nderivative work: Jocian', 'image_ai_generated': False}
IMAGE_METADATA['rum-punch'] = {'image_path': '/media/rum-punch.webp', 'image_source_url': 'https://commons.wikimedia.org/wiki/File:2_1-2_dollar_note_and_rum_punch_-_Paramaribo_(23728395922).jpg', 'image_license': 'CC BY-SA 2.0', 'image_attribution': 'Dan Sloan', 'image_ai_generated': False}
IMAGE_METADATA['rusty-nail'] = {'image_path': '/media/rusty-nail.webp', 'image_source_url': 'https://commons.wikimedia.org/wiki/File:Rusty_Nail_a_cocktail_by_@tokenchick13_(16503594826).jpg', 'image_license': 'CC BY-SA 2.0', 'image_attribution': 'Brian Child', 'image_ai_generated': False}
IMAGE_METADATA['rye-sour'] = {'image_path': '/media/rye-sour.webp', 'image_source_url': 'https://commons.wikimedia.org/wiki/File:VTR_-_Rye_Sour.jpg', 'image_license': 'CC BY-SA 2.0', 'image_attribution': 'Edsel L', 'image_ai_generated': False}
IMAGE_METADATA['salty-dog'] = {'image_path': '/media/salty-dog.webp', 'image_source_url': 'https://commons.wikimedia.org/wiki/File:Salty_Dog.jpg', 'image_license': 'CC BY-SA 3.0', 'image_attribution': 'Momoji3', 'image_ai_generated': False}
IMAGE_METADATA['sazerac'] = {'image_path': '/media/sazerac.webp', 'image_source_url': 'https://commons.wikimedia.org/wiki/File:Sazerac_Cocktail_-_New_Orleans_April_2022.jpg', 'image_license': 'CC BY 2.0', 'image_attribution': 'Carnaval.com Studios', 'image_ai_generated': False}
IMAGE_METADATA['scotch-soda'] = {'image_path': '/media/scotch-soda.webp', 'image_source_url': 'https://commons.wikimedia.org/wiki/File:Glass_of_Scotch_and_soda.jpg', 'image_license': 'CC BY-SA 4.0', 'image_attribution': 'DoubleGrazing', 'image_ai_generated': False}
IMAGE_METADATA['scotch-sour'] = {'image_path': '/media/scotch-sour.webp', 'image_source_url': 'https://commons.wikimedia.org/wiki/File:NewYork_Sour_scotch.jpg', 'image_license': 'CC BY-SA 4.0', 'image_attribution': 'Corvus', 'image_ai_generated': False}
IMAGE_METADATA['screwdriver'] = {'image_path': '/media/screwdriver.webp', 'image_source_url': 'https://commons.wikimedia.org/wiki/File:Screwdriver_cocktail_ingredients.png', 'image_license': 'CC BY-SA 4.0', 'image_attribution': 'GeoO', 'image_ai_generated': False}
IMAGE_METADATA['sex-on-the-beach'] = {'image_path': '/media/sex-on-the-beach.webp', 'image_source_url': 'https://commons.wikimedia.org/wiki/File:Sex_On_The_Beach_Cocktail_@_Clare_Hotel_20250123-124727.jpg', 'image_license': 'CC0', 'image_attribution': 'RegionVisitor90', 'image_ai_generated': False}
IMAGE_METADATA['sherry-cobbler'] = {'image_path': '/media/sherry-cobbler.webp', 'image_source_url': 'https://commons.wikimedia.org/wiki/File:Sherry_cobbler.jpg', 'image_license': 'CC BY 4.0', 'image_attribution': 'BanjoZebra', 'image_ai_generated': False}
IMAGE_METADATA['shirley-temple'] = {'image_path': '/media/shirley-temple.webp', 'image_source_url': 'https://commons.wikimedia.org/wiki/File:Shirley_Temple_%26_Cosmopolitan_cocktails.jpg', 'image_license': 'CC BY-SA 2.0', 'image_attribution': 'cbgrfx123', 'image_ai_generated': False}
IMAGE_METADATA['southside'] = {'image_path': '/media/southside.webp', 'image_source_url': 'https://commons.wikimedia.org/wiki/File:Clover_club_southside_fizz_(3285775440).jpg', 'image_license': 'CC BY 2.0', 'image_attribution': 'Krista', 'image_ai_generated': False}
IMAGE_METADATA['spicy-fifty'] = {'image_path': '/media/spicy-fifty.webp', 'image_source_url': 'https://commons.wikimedia.org/wiki/File:Spicy_Fifty.jpg', 'image_license': 'CC BY 4.0', 'image_attribution': 'BanjoZebra', 'image_ai_generated': False}
IMAGE_METADATA['stinger'] = {'image_path': '/media/stinger.webp', 'image_source_url': 'https://commons.wikimedia.org/wiki/File:Stinger_Cocktail.jpg', 'image_license': 'CC BY-SA 3.0', 'image_attribution': 'Will Shenton', 'image_ai_generated': False}
IMAGE_METADATA['strawberry-daiquiri'] = {'image_path': '/media/strawberry-daiquiri.webp', 'image_source_url': 'https://commons.wikimedia.org/wiki/File:Rose,_Strawberry_Daiquiri,_%E3%83%90%E3%83%A9,_%E3%82%B9%E3%83%88%E3%83%AD%E3%83%99%E3%83%AA%E3%83%BC_%E3%83%80%E3%82%A4%E3%82%AD%E3%83%AA,_(15712192726).jpg', 'image_license': 'CC BY-SA 2.0', 'image_attribution': 'T.Kiya from Japan', 'image_ai_generated': False}
IMAGE_METADATA['suffering-bastard'] = {'image_path': '/media/suffering-bastard.webp', 'image_source_url': 'https://commons.wikimedia.org/wiki/File:Suffering_Bastard_Cocktail.jpg', 'image_license': 'CC BY-SA 3.0', 'image_attribution': 'Will Shenton', 'image_ai_generated': False}
IMAGE_METADATA['tequila-grapefruit'] = {'image_path': '/media/tequila-grapefruit.webp', 'image_source_url': 'https://commons.wikimedia.org/wiki/File:TequilaPaloma.JPG', 'image_license': 'Public domain', 'image_attribution': 'Antonio Cavallo', 'image_ai_generated': False}
IMAGE_METADATA['tequila-lemonade'] = {'image_path': '/media/tequila-lemonade.webp', 'image_source_url': 'https://commons.wikimedia.org/wiki/File:Cheers_!!!_(5297201751).jpg', 'image_license': 'CC BY-SA 2.0', 'image_attribution': 'Rishabh Mathur from Bangalore, India', 'image_ai_generated': False}
IMAGE_METADATA['tequila-old-fashioned'] = {'image_path': '/media/tequila-old-fashioned.webp', 'image_source_url': 'https://commons.wikimedia.org/wiki/File:Rum,_Manhattan,_Tequila_Old_Fashioned.jpg', 'image_license': 'CC BY-SA 3.0', 'image_attribution': 'Cocktailmarler', 'image_ai_generated': False}
IMAGE_METADATA['tequila-orange'] = {'image_path': '/media/tequila-orange.webp', 'image_source_url': 'https://commons.wikimedia.org/wiki/File:Mardi_Gras_Carnival_and_Mexican_Melon_-_Montagues_Tex_Mex_2026-06-03.jpg', 'image_license': 'CC0', 'image_attribution': 'Andy Li', 'image_ai_generated': False}
IMAGE_METADATA['tequila-pineapple'] = {'image_path': '/media/tequila-pineapple.webp', 'image_source_url': 'https://commons.wikimedia.org/wiki/File:La_base_del_tequila_agave_azul_tequilana_Weber.jpg', 'image_license': 'CC BY-SA 4.0', 'image_attribution': 'Alfonso Jiménez', 'image_ai_generated': False}
IMAGE_METADATA['tequila-sour'] = {'image_path': '/media/tequila-sour.webp', 'image_source_url': 'https://commons.wikimedia.org/wiki/File:Tequila_sour.jpg', 'image_license': 'Public domain', 'image_attribution': 'Jennight', 'image_ai_generated': False}
IMAGE_METADATA['tequila-sunrise'] = {'image_path': '/media/tequila-sunrise.webp', 'image_source_url': 'https://commons.wikimedia.org/wiki/File:Tequila_Sunrise_2013.JPG', 'image_license': 'CC BY 3.0', 'image_attribution': 'stavros1', 'image_ai_generated': False}
IMAGE_METADATA['tequila-tonic'] = {'image_path': '/media/tequila-tonic.webp', 'image_source_url': 'https://commons.wikimedia.org/wiki/File:Tequila_%26_Tonic.jpg', 'image_license': 'CC BY-SA 3.0', 'image_attribution': 'Surv1v4l1st', 'image_ai_generated': False}
IMAGE_METADATA['three-dots-and-a-dash'] = {'image_path': '/media/three-dots-and-a-dash.webp', 'image_source_url': 'https://commons.wikimedia.org/wiki/File:Three_Dots_and_a_Dash_cocktail.jpg', 'image_license': 'CC BY 4.0', 'image_attribution': 'BanjoZebra', 'image_ai_generated': False}
IMAGE_METADATA['tipperary'] = {'image_path': '/media/tipperary.webp', 'image_source_url': 'https://commons.wikimedia.org/wiki/File:Tipperary.jpg', 'image_license': 'CC BY 4.0', 'image_attribution': 'BanjoZebra', 'image_ai_generated': False}
IMAGE_METADATA['tom-collins'] = {'image_path': '/media/tom-collins.webp', 'image_source_url': 'https://commons.wikimedia.org/wiki/File:Tom_Collins_cocktail.jpg', 'image_license': 'CC BY 2.0', 'image_attribution': 'Daniel Nguyen', 'image_ai_generated': False}
IMAGE_METADATA['tommys-margarita'] = {'image_path': '/media/tommys-margarita.webp', 'image_source_url': 'https://commons.wikimedia.org/wiki/File:TommysMargarita.jpg', 'image_license': 'CC BY 2.0', 'image_attribution': 'Rick Audet', 'image_ai_generated': False}
IMAGE_METADATA['trinidad-sour'] = {'image_path': '/media/trinidad-sour.webp', 'image_source_url': 'https://commons.wikimedia.org/wiki/File:VTR_-_Trinidad_Sour_(18045674468).jpg', 'image_license': 'CC BY-SA 2.0', 'image_attribution': 'Edsel Little', 'image_ai_generated': False}
IMAGE_METADATA['tuxedo'] = {'image_path': '/media/tuxedo.webp', 'image_source_url': 'https://commons.wikimedia.org/wiki/File:Tuxedo_No._2_cocktail.jpg', 'image_license': 'CC BY 4.0', 'image_attribution': 'BanjoZebra', 'image_ai_generated': False}
IMAGE_METADATA['ve-n-to'] = {'image_path': '/media/ve-n-to.webp', 'image_source_url': 'https://commons.wikimedia.org/wiki/File:Ve.n.to_cocktail.jpg', 'image_license': 'CC BY-SA 4.0', 'image_attribution': 'Jonsico', 'image_ai_generated': False}
IMAGE_METADATA['vesper'] = {'image_path': '/media/vesper.webp', 'image_source_url': 'https://commons.wikimedia.org/wiki/File:Vesper_cocktail_ingredients.png', 'image_license': 'CC BY-SA 4.0', 'image_attribution': 'GeoO', 'image_ai_generated': False}
IMAGE_METADATA['vieux-carre'] = {'image_path': '/media/vieux-carre.webp', 'image_source_url': 'https://commons.wikimedia.org/wiki/File:Vieux_Carre_Cocktail.jpg', 'image_license': 'CC BY-SA 2.0', 'image_attribution': 'Adrian Scottow', 'image_ai_generated': False}
IMAGE_METADATA['virgin-pina-colada'] = {'image_path': '/media/virgin-pina-colada.webp', 'image_source_url': 'https://commons.wikimedia.org/wiki/File:Pina_Colada_at_Aruba.jpg', 'image_license': 'CC BY-SA 4.0', 'image_attribution': 'DDJJ', 'image_ai_generated': False}
IMAGE_METADATA['vodka-collins'] = {'image_path': '/media/vodka-collins.webp', 'image_source_url': 'https://commons.wikimedia.org/wiki/File:Vodka-1972.jpg', 'image_license': 'CC BY-SA 4.0', 'image_attribution': 'Vanwalker', 'image_ai_generated': False}
IMAGE_METADATA['vodka-cranberry'] = {'image_path': '/media/vodka-cranberry.webp', 'image_source_url': 'https://commons.wikimedia.org/wiki/File:Vodka_Cranberry_Cocktail_(5408164203).jpg', 'image_license': 'CC BY 2.0', 'image_attribution': 'MoneyBlogNewz', 'image_ai_generated': False}
IMAGE_METADATA['vodka-pineapple'] = {'image_path': '/media/vodka-pineapple.webp', 'image_source_url': 'https://commons.wikimedia.org/wiki/File:Catwalk_cocktail.jpg', 'image_license': 'CC BY-SA 3.0', 'image_attribution': 'Charandeep Singh', 'image_ai_generated': False}
IMAGE_METADATA['vodka-soda'] = {'image_path': '/media/vodka-soda.webp', 'image_source_url': 'https://commons.wikimedia.org/wiki/File:Vodka_Soda_(cropped).jpg', 'image_license': 'CC BY-SA 4.0', 'image_attribution': 'Molly1900', 'image_ai_generated': False}
IMAGE_METADATA['vodka-sour'] = {'image_path': '/media/vodka-sour.webp', 'image_source_url': 'https://commons.wikimedia.org/wiki/File:Sour_Fisk_Watermelon.jpg', 'image_license': 'CC BY-SA 4.0', 'image_attribution': 'JIP', 'image_ai_generated': False}
IMAGE_METADATA['vodka-tonic'] = {'image_path': '/media/vodka-tonic.webp', 'image_source_url': 'https://commons.wikimedia.org/wiki/File:Vodka_tonic.jpg', 'image_license': 'Public domain', 'image_attribution': 'FIshstick at English Wikipedia', 'image_ai_generated': False}
IMAGE_METADATA['whiskey-ginger'] = {'image_path': '/media/whiskey-ginger.webp', 'image_source_url': 'https://commons.wikimedia.org/wiki/File:Whiskey_Ginger,_London_Bridge,_SE1.jpg', 'image_license': 'CC BY-SA 2.0', 'image_attribution': 'Ewan-M', 'image_ai_generated': False}
IMAGE_METADATA['white-lady'] = {'image_path': '/media/white-lady.webp', 'image_source_url': 'https://commons.wikimedia.org/wiki/File:White_Lady_(cocktail).jpg', 'image_license': 'CC BY-SA 3.0', 'image_attribution': 'Momoji3', 'image_ai_generated': False}
IMAGE_METADATA['white-russian'] = {'image_path': '/media/white-russian.webp', 'image_source_url': 'https://commons.wikimedia.org/wiki/File:White_Russian_-_CrystalMixer.jpg', 'image_license': 'CC BY 4.0', 'image_attribution': 'CrystalMixer - CrystalMixer.com', 'image_ai_generated': False}
IMAGE_METADATA['zombie'] = {'image_path': '/media/zombie.webp', 'image_source_url': 'https://commons.wikimedia.org/wiki/File:Zombie_cocktail_gianni_zottola.jpg', 'image_license': 'CC BY-SA 4.0', 'image_attribution': 'GianniZottola', 'image_ai_generated': False}
# END GENERATED FINAL IMAGE METADATA

# BEGIN APPROVED AI IMAGE METADATA
IMAGE_METADATA['brandy-daisy'] = {'image_path': '/media/brandy-daisy.webp', 'image_source_url': None, 'image_license': 'Original Virtual Bartender AI-generated image', 'image_attribution': 'Virtual Bartender / OpenAI image generation', 'image_ai_generated': True}
IMAGE_METADATA['brandy-ginger'] = {'image_path': '/media/brandy-ginger.webp', 'image_source_url': None, 'image_license': 'Original Virtual Bartender AI-generated image', 'image_attribution': 'Virtual Bartender / OpenAI image generation', 'image_ai_generated': True}
IMAGE_METADATA['brandy-soda'] = {'image_path': '/media/brandy-soda.webp', 'image_source_url': None, 'image_license': 'Original Virtual Bartender AI-generated image', 'image_attribution': 'Virtual Bartender / OpenAI image generation', 'image_ai_generated': True}
IMAGE_METADATA['brandy-spritz'] = {'image_path': '/media/brandy-spritz.webp', 'image_source_url': None, 'image_license': 'Original Virtual Bartender AI-generated image', 'image_attribution': 'Virtual Bartender / OpenAI image generation', 'image_ai_generated': True}
IMAGE_METADATA['bronx'] = {'image_path': '/media/bronx.webp', 'image_source_url': None, 'image_license': 'Original Virtual Bartender AI-generated image', 'image_attribution': 'Virtual Bartender / OpenAI image generation', 'image_ai_generated': True}
IMAGE_METADATA['coffee-liqueur-cola'] = {'image_path': '/media/coffee-liqueur-cola.webp', 'image_source_url': None, 'image_license': 'Original Virtual Bartender AI-generated image', 'image_attribution': 'Virtual Bartender / OpenAI image generation', 'image_ai_generated': True}
IMAGE_METADATA['cognac-cola'] = {'image_path': '/media/cognac-cola.webp', 'image_source_url': None, 'image_license': 'Original Virtual Bartender AI-generated image', 'image_attribution': 'Virtual Bartender / OpenAI image generation', 'image_ai_generated': True}
IMAGE_METADATA['cognac-collins'] = {'image_path': '/media/cognac-collins.webp', 'image_source_url': None, 'image_license': 'Original Virtual Bartender AI-generated image', 'image_attribution': 'Virtual Bartender / OpenAI image generation', 'image_ai_generated': True}
IMAGE_METADATA['cognac-ginger'] = {'image_path': '/media/cognac-ginger.webp', 'image_source_url': None, 'image_license': 'Original Virtual Bartender AI-generated image', 'image_attribution': 'Virtual Bartender / OpenAI image generation', 'image_ai_generated': True}
IMAGE_METADATA['cognac-sour'] = {'image_path': '/media/cognac-sour.webp', 'image_source_url': None, 'image_license': 'Original Virtual Bartender AI-generated image', 'image_attribution': 'Virtual Bartender / OpenAI image generation', 'image_ai_generated': True}
IMAGE_METADATA['virgin-whiskey-sour'] = {'image_path': '/media/virgin-whiskey-sour.webp', 'image_source_url': None, 'image_license': 'Original Virtual Bartender AI-generated image', 'image_attribution': 'Virtual Bartender / OpenAI image generation', 'image_ai_generated': True}
# END APPROVED AI IMAGE METADATA

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
