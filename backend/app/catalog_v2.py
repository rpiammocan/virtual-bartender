# Curated V1 reference catalog.
# Recipe instructions are original Virtual Bartender wording.
# Ingredient formulas are normalized factual data derived from classic/open references.

INGREDIENTS_V2 = [
    ("Brandy", "Spirits"),
    ("Cognac", "Brandy"),
    ("Irish Whiskey", "Whiskey"),
    ("Canadian Whisky", "Whiskey"),
    ("Aged Rum", "Rum"),
    ("Gold Rum", "Rum"),
    ("Overproof Rum", "Rum"),
    ("Mezcal", "Tequila / Agave"),
    ("Coffee Liqueur", "Liqueurs"),
    ("Amaretto", "Liqueurs"),
    ("Aperol", "Liqueurs"),
    ("Maraschino Liqueur", "Liqueurs"),
    ("Green Chartreuse", "Liqueurs"),
    ("Crème de Cacao", "Liqueurs"),
    ("Crème de Menthe", "Liqueurs"),
    ("Peach Schnapps", "Liqueurs"),
    ("Blue Curaçao", "Liqueurs"),
    ("Falernum", "Liqueurs"),
    ("Absinthe", "Liqueurs"),
    ("Prosecco", "Wine / Sparkling"),
    ("Champagne", "Wine / Sparkling"),
    ("Red Wine", "Wine / Sparkling"),
    ("Cream", "Dairy"),
    ("Milk", "Dairy"),
    ("Coconut Cream", "Mixers"),
    ("Tomato Juice", "Juices"),
    ("Cranberry Juice", "Juices"),
    ("Passion Fruit Puree", "Fresh Ingredients"),
    ("Strawberries", "Fresh Ingredients"),
    ("Raspberries", "Fresh Ingredients"),
    ("Cucumber", "Fresh Ingredients"),
    ("Basil Leaves", "Fresh Ingredients"),
    ("Celery Salt", "Pantry / Kitchen"),
    ("Black Pepper", "Pantry / Kitchen"),
    ("Hot Sauce", "Pantry / Kitchen"),
    ("Worcestershire Sauce", "Pantry / Kitchen"),
    ("Honey Syrup", "Syrups"),
    ("Agave Syrup", "Syrups"),
    ("Orgeat", "Syrups"),
    ("Demerara Syrup", "Syrups"),
    ("Vanilla Syrup", "Syrups"),
    ("Raspberry Syrup", "Syrups"),
    ("Grapefruit Soda", "Mixers"),
    ("Lemon-Lime Soda", "Mixers"),
    ("Root Beer", "Mixers"),
    ("Coffee", "Mixers"),
    ("Espresso", "Mixers"),
    ("Water", "Mixers"),
    ("Orange Bitters", "Bitters"),
    ("Peychaud's Bitters", "Bitters"),
    ("Orange Slice", "Garnishes"),
    ("Lemon Wedge", "Garnishes"),
    ("Cherry", "Garnishes"),
    ("Pineapple Wedge", "Garnishes"),
    ("Mint Sprig", "Garnishes"),
]

SUBSTITUTIONS_V2 = [
    ("Triple Sec", "Cointreau", 10),
    ("Cointreau", "Triple Sec", 20),
    ("Simple Syrup", "Agave Syrup", 30),
    ("Simple Syrup", "Honey Syrup", 40),
    ("Club Soda", "Tonic Water", 90),
    ("White Rum", "Gold Rum", 70),
    ("Bourbon", "Rye Whiskey", 50),
    ("Rye Whiskey", "Bourbon", 50),
]

RECIPES_V2 = [
    {
        "key":"negroni","name":"Negroni","type":"cocktail","version":"1.0",
        "description":"A bitter, spirit-forward aperitivo built from gin, vermouth, and Campari.",
        "instructions":"Stir all ingredients with ice until chilled, then strain over fresh ice.",
        "source":"IBA reference","url":"https://iba-world.com/cocktails/",
        "ingredients":[("Gin",1.0,"oz",False),("Sweet Vermouth",1.0,"oz",False),("Campari",1.0,"oz",False),("Orange Peel",1.0,"pc",True)]
    },
    {
        "key":"americano","name":"Americano","type":"cocktail","version":"1.0",
        "description":"A low-proof bitter aperitivo topped with soda.",
        "instructions":"Build Campari and sweet vermouth over ice, top with club soda, and stir gently.",
        "source":"IBA reference","url":"https://iba-world.com/cocktails/",
        "ingredients":[("Campari",1.0,"oz",False),("Sweet Vermouth",1.0,"oz",False),("Club Soda",2.0,"oz",False),("Orange Slice",1.0,"pc",True)]
    },
    {
        "key":"boulevardier","name":"Boulevardier","type":"cocktail","version":"1.0",
        "description":"A whiskey-forward relative of the Negroni.",
        "instructions":"Stir whiskey, Campari, and sweet vermouth with ice, then strain over fresh ice.",
        "source":"IBA reference","url":"https://iba-world.com/cocktails/",
        "ingredients":[("Bourbon",1.5,"oz",False),("Campari",1.0,"oz",False),("Sweet Vermouth",1.0,"oz",False)]
    },
    {
        "key":"whiskey-sour","name":"Whiskey Sour","type":"cocktail","version":"1.0",
        "description":"A balanced whiskey sour with lemon and syrup.",
        "instructions":"Shake all required ingredients with ice and strain into a chilled or ice-filled glass.",
        "source":"IBA reference","url":"https://iba-world.com/cocktails/",
        "ingredients":[("Bourbon",2.0,"oz",False),("Lemon Juice",0.75,"oz",False),("Simple Syrup",0.75,"oz",False),("Egg White",0.75,"oz",True)]
    },
    {
        "key":"tom-collins","name":"Tom Collins","type":"cocktail","version":"1.0",
        "description":"A sparkling gin sour served long.",
        "instructions":"Shake gin, lemon juice, and syrup with ice. Strain over fresh ice and top with club soda.",
        "source":"Classic reference","url":"https://en.wikibooks.org/wiki/Bartending/Cocktails",
        "ingredients":[("Gin",2.0,"oz",False),("Lemon Juice",1.0,"oz",False),("Simple Syrup",0.75,"oz",False),("Club Soda",2.0,"oz",False)]
    },
    {
        "key":"gimlet","name":"Gimlet","type":"cocktail","version":"1.0",
        "description":"A crisp gin-and-lime sour.",
        "instructions":"Shake gin, lime juice, and syrup with ice, then strain into a chilled glass.",
        "source":"Classic reference","url":"https://en.wikibooks.org/wiki/Bartending/Cocktails",
        "ingredients":[("Gin",2.0,"oz",False),("Lime Juice",0.75,"oz",False),("Simple Syrup",0.75,"oz",False)]
    },
    {
        "key":"martini","name":"Dry Martini","type":"cocktail","version":"1.0",
        "description":"A spirit-forward classic of gin and dry vermouth.",
        "instructions":"Stir gin and dry vermouth with ice until very cold, then strain into a chilled glass.",
        "source":"IBA reference","url":"https://iba-world.com/cocktails/",
        "ingredients":[("Gin",2.5,"oz",False),("Dry Vermouth",0.5,"oz",False),("Lemon Peel",1.0,"pc",True)]
    },
    {
        "key":"black-russian","name":"Black Russian","type":"cocktail","version":"1.0",
        "description":"Vodka and coffee liqueur served over ice.",
        "instructions":"Build vodka and coffee liqueur over ice and stir.",
        "source":"IBA reference","url":"https://iba-world.com/cocktails/",
        "ingredients":[("Vodka",2.0,"oz",False),("Coffee Liqueur",1.0,"oz",False)]
    },
    {
        "key":"white-russian","name":"White Russian","type":"cocktail","version":"1.0",
        "description":"A creamy variation of the Black Russian.",
        "instructions":"Build vodka and coffee liqueur over ice, then add cream and stir gently.",
        "source":"Classic reference","url":"https://en.wikibooks.org/wiki/Bartending/Cocktails",
        "ingredients":[("Vodka",2.0,"oz",False),("Coffee Liqueur",1.0,"oz",False),("Cream",1.0,"oz",False)]
    },
    {
        "key":"cosmopolitan","name":"Cosmopolitan","type":"cocktail","version":"1.0",
        "description":"A tart vodka cocktail with cranberry, lime, and orange liqueur.",
        "instructions":"Shake all ingredients with ice and strain into a chilled cocktail glass.",
        "source":"IBA reference","url":"https://iba-world.com/cocktails/",
        "ingredients":[("Vodka",1.5,"oz",False),("Cointreau",0.75,"oz",False),("Cranberry Juice",1.0,"oz",False),("Lime Juice",0.5,"oz",False)]
    },
    {
        "key":"bloody-mary","name":"Bloody Mary","type":"cocktail","version":"1.0",
        "description":"A savory vodka and tomato cocktail.",
        "instructions":"Combine ingredients with ice and roll or stir gently until chilled.",
        "source":"IBA reference","url":"https://iba-world.com/cocktails/",
        "ingredients":[("Vodka",1.5,"oz",False),("Tomato Juice",3.0,"oz",False),("Lemon Juice",0.5,"oz",False),("Worcestershire Sauce",0.25,"oz",True),("Hot Sauce",0.1,"oz",True),("Celery Salt",0.25,"tsp",True),("Black Pepper",0.25,"tsp",True)]
    },
    {
        "key":"espresso-martini","name":"Espresso Martini","type":"cocktail","version":"1.0",
        "description":"A rich coffee-and-vodka cocktail.",
        "instructions":"Shake vodka, coffee liqueur, espresso, and syrup hard with ice. Strain into a chilled glass.",
        "source":"IBA reference","url":"https://iba-world.com/cocktails/",
        "ingredients":[("Vodka",1.5,"oz",False),("Coffee Liqueur",0.75,"oz",False),("Espresso",1.0,"oz",False),("Simple Syrup",0.25,"oz",True)]
    },
    {
        "key":"mojito","name":"Mojito","type":"cocktail","version":"1.0",
        "description":"A refreshing rum highball with mint, lime, and soda.",
        "instructions":"Gently press mint with lime and syrup. Add rum and ice, top with club soda, and stir.",
        "source":"IBA reference","url":"https://iba-world.com/cocktails/",
        "ingredients":[("White Rum",2.0,"oz",False),("Lime Juice",1.0,"oz",False),("Simple Syrup",0.75,"oz",False),("Mint Leaves",8.0,"pc",False),("Club Soda",2.0,"oz",False),("Mint Sprig",1.0,"pc",True)]
    },
    {
        "key":"dark-stormy","name":"Dark 'n' Stormy","type":"cocktail","version":"1.0",
        "description":"Dark rum with spicy ginger beer and lime.",
        "instructions":"Build ginger beer and lime over ice, then add dark rum and stir gently.",
        "source":"Classic highball reference","url":"https://en.wikibooks.org/wiki/Bartending/Cocktails",
        "ingredients":[("Dark Rum",2.0,"oz",False),("Ginger Beer",4.0,"oz",False),("Lime Juice",0.5,"oz",False)]
    },
    {
        "key":"pina-colada","name":"Piña Colada","type":"cocktail","version":"1.0",
        "description":"A tropical rum drink with pineapple and coconut.",
        "instructions":"Blend or shake rum, pineapple juice, and coconut cream with ice until cold and smooth.",
        "source":"IBA reference","url":"https://iba-world.com/cocktails/",
        "ingredients":[("White Rum",2.0,"oz",False),("Pineapple Juice",3.0,"oz",False),("Coconut Cream",1.5,"oz",False),("Pineapple Wedge",1.0,"pc",True)]
    },
    {
        "key":"mai-tai","name":"Mai Tai","type":"cocktail","version":"1.0",
        "description":"A tiki-style rum sour with orange liqueur and orgeat.",
        "instructions":"Shake all required ingredients with ice and strain over fresh or crushed ice.",
        "source":"IBA reference","url":"https://iba-world.com/cocktails/",
        "ingredients":[("Aged Rum",2.0,"oz",False),("Cointreau",0.5,"oz",False),("Lime Juice",0.75,"oz",False),("Orgeat",0.5,"oz",False),("Simple Syrup",0.25,"oz",False)]
    },
    {
        "key":"cuba-libre","name":"Cuba Libre","type":"cocktail","version":"1.0",
        "description":"Rum, cola, and lime.",
        "instructions":"Build rum and lime over ice, top with cola, and stir gently.",
        "source":"IBA reference","url":"https://iba-world.com/cocktails/",
        "ingredients":[("White Rum",2.0,"oz",False),("Cola",4.0,"oz",False),("Lime Juice",0.5,"oz",False)]
    },
    {
        "key":"paloma","name":"Paloma","type":"cocktail","version":"1.0",
        "description":"A refreshing tequila and grapefruit highball.",
        "instructions":"Build tequila and lime over ice, top with grapefruit soda, and stir gently.",
        "source":"Classic reference","url":"https://en.wikibooks.org/wiki/Bartending/Cocktails",
        "ingredients":[("Blanco Tequila",2.0,"oz",False),("Grapefruit Soda",4.0,"oz",False),("Lime Juice",0.5,"oz",False),("Salt",0.25,"tsp",True)]
    },
    {
        "key":"tequila-sunrise","name":"Tequila Sunrise","type":"cocktail","version":"1.0",
        "description":"Tequila, orange juice, and grenadine.",
        "instructions":"Build tequila and orange juice over ice. Add grenadine slowly so it settles toward the bottom.",
        "source":"IBA reference","url":"https://iba-world.com/cocktails/",
        "ingredients":[("Blanco Tequila",1.5,"oz",False),("Orange Juice",3.0,"oz",False),("Grenadine",0.5,"oz",False)]
    },
    {
        "key":"mezcal-margarita","name":"Mezcal Margarita","type":"cocktail","version":"1.0",
        "description":"A smoky agave variation on the Margarita.",
        "instructions":"Shake mezcal, orange liqueur, and lime juice with ice, then strain into a chilled glass.",
        "source":"Virtual Bartender curated variant","url":"local://virtual-bartender/curated",
        "parent":"margarita",
        "ingredients":[("Mezcal",2.0,"oz",False),("Triple Sec",1.0,"oz",False),("Lime Juice",1.0,"oz",False)]
    },
    {
        "key":"sidecar","name":"Sidecar","type":"cocktail","version":"1.0",
        "description":"A cognac sour with orange liqueur and lemon.",
        "instructions":"Shake cognac, orange liqueur, and lemon juice with ice, then strain into a chilled glass.",
        "source":"IBA reference","url":"https://iba-world.com/cocktails/",
        "ingredients":[("Cognac",2.0,"oz",False),("Cointreau",0.75,"oz",False),("Lemon Juice",0.75,"oz",False)]
    },
    {
        "key":"brandy-alexander","name":"Brandy Alexander","type":"cocktail","version":"1.0",
        "description":"A creamy brandy and chocolate cocktail.",
        "instructions":"Shake brandy, crème de cacao, and cream with ice, then strain into a chilled glass.",
        "source":"IBA reference","url":"https://iba-world.com/cocktails/",
        "ingredients":[("Brandy",1.0,"oz",False),("Crème de Cacao",1.0,"oz",False),("Cream",1.0,"oz",False)]
    },
    {
        "key":"irish-coffee","name":"Irish Coffee","type":"cocktail","version":"1.0",
        "description":"Hot coffee fortified with Irish whiskey and lightly sweetened.",
        "instructions":"Combine hot coffee, Irish whiskey, and syrup in a warmed mug. Float lightly whipped cream on top if desired.",
        "source":"IBA reference","url":"https://iba-world.com/cocktails/",
        "ingredients":[("Irish Whiskey",1.5,"oz",False),("Coffee",4.0,"oz",False),("Simple Syrup",0.5,"oz",False),("Cream",1.0,"oz",True)]
    },
    {
        "key":"aperol-spritz","name":"Aperol Spritz","type":"cocktail","version":"1.0",
        "description":"A sparkling bittersweet aperitivo.",
        "instructions":"Build Prosecco and Aperol over ice, top with club soda, and stir gently.",
        "source":"IBA reference","url":"https://iba-world.com/cocktails/",
        "ingredients":[("Prosecco",3.0,"oz",False),("Aperol",2.0,"oz",False),("Club Soda",1.0,"oz",False),("Orange Slice",1.0,"pc",True)]
    },
    {
        "key":"bellini","name":"Bellini","type":"cocktail","version":"1.0",
        "description":"A sparkling fruit cocktail traditionally based on peach.",
        "instructions":"Add fruit puree to a flute and slowly top with chilled Prosecco, stirring gently.",
        "source":"IBA reference","url":"https://iba-world.com/cocktails/",
        "ingredients":[("Prosecco",4.0,"oz",False),("Peach Schnapps",0.5,"oz",False)]
    },
    {
        "key":"champagne-cocktail","name":"Champagne Cocktail","type":"cocktail","version":"1.0",
        "description":"A sparkling classic accented with sugar and bitters.",
        "instructions":"Add sugar and bitters to a flute, then slowly top with chilled Champagne.",
        "source":"Classic reference","url":"https://en.wikibooks.org/wiki/Bartending/Cocktails",
        "ingredients":[("Champagne",4.0,"oz",False),("Sugar",1.0,"tsp",False),("Angostura Bitters",2.0,"dash",False)]
    },
    {
        "key":"french-75","name":"French 75","type":"cocktail","version":"1.0",
        "description":"A sparkling gin sour.",
        "instructions":"Shake gin, lemon juice, and syrup with ice. Strain into a flute and top with Champagne.",
        "source":"IBA reference","url":"https://iba-world.com/cocktails/",
        "ingredients":[("Gin",1.0,"oz",False),("Lemon Juice",0.5,"oz",False),("Simple Syrup",0.5,"oz",False),("Champagne",2.0,"oz",False)]
    },
    {
        "key":"aviation","name":"Aviation","type":"cocktail","version":"1.0",
        "description":"A floral gin sour with maraschino liqueur.",
        "instructions":"Shake gin, maraschino liqueur, and lemon juice with ice, then strain into a chilled glass.",
        "source":"IBA reference","url":"https://iba-world.com/cocktails/",
        "ingredients":[("Gin",1.5,"oz",False),("Maraschino Liqueur",0.5,"oz",False),("Lemon Juice",0.75,"oz",False)]
    },
    {
        "key":"bees-knees","name":"Bee's Knees","type":"cocktail","version":"1.0",
        "description":"A gin sour sweetened with honey.",
        "instructions":"Shake gin, lemon juice, and honey syrup with ice, then strain into a chilled glass.",
        "source":"IBA reference","url":"https://iba-world.com/cocktails/",
        "ingredients":[("Gin",2.0,"oz",False),("Lemon Juice",0.75,"oz",False),("Honey Syrup",0.75,"oz",False)]
    },
    {
        "key":"last-word","name":"Last Word","type":"cocktail","version":"1.0",
        "description":"An equal-parts herbal gin sour.",
        "instructions":"Shake all ingredients with ice and strain into a chilled cocktail glass.",
        "source":"IBA reference","url":"https://iba-world.com/cocktails/",
        "ingredients":[("Gin",0.75,"oz",False),("Green Chartreuse",0.75,"oz",False),("Maraschino Liqueur",0.75,"oz",False),("Lime Juice",0.75,"oz",False)]
    },
    {
        "key":"sazerac","name":"Sazerac","type":"cocktail","version":"1.0",
        "description":"A New Orleans whiskey classic with Peychaud's bitters and absinthe.",
        "instructions":"Rinse a chilled glass with absinthe. Stir whiskey, syrup, and bitters with ice, then strain into the prepared glass.",
        "source":"IBA reference","url":"https://iba-world.com/cocktails/",
        "ingredients":[("Rye Whiskey",2.0,"oz",False),("Simple Syrup",0.25,"oz",False),("Peychaud's Bitters",3.0,"dash",False),("Absinthe",0.25,"oz",False),("Lemon Peel",1.0,"pc",True)]
    },
    {
        "key":"mint-julep","name":"Mint Julep","type":"cocktail","version":"1.0",
        "description":"Bourbon, mint, and sugar served over crushed ice.",
        "instructions":"Gently press mint with syrup, add bourbon and crushed ice, then stir until chilled.",
        "source":"IBA reference","url":"https://iba-world.com/cocktails/",
        "ingredients":[("Bourbon",2.5,"oz",False),("Simple Syrup",0.5,"oz",False),("Mint Leaves",8.0,"pc",False),("Mint Sprig",1.0,"pc",True)]
    },
    {
        "key":"john-collins","name":"John Collins","type":"cocktail","version":"1.0",
        "description":"A whiskey Collins with lemon, syrup, and soda.",
        "instructions":"Shake whiskey, lemon, and syrup with ice. Strain over ice and top with club soda.",
        "source":"IBA reference","url":"https://iba-world.com/cocktails/",
        "ingredients":[("Bourbon",2.0,"oz",False),("Lemon Juice",1.0,"oz",False),("Simple Syrup",0.75,"oz",False),("Club Soda",2.0,"oz",False)]
    },
    {
        "key":"godfather","name":"Godfather","type":"cocktail","version":"1.0",
        "description":"Scotch softened by amaretto.",
        "instructions":"Build Scotch and amaretto over ice and stir until chilled.",
        "source":"IBA reference","url":"https://iba-world.com/cocktails/",
        "ingredients":[("Scotch Whisky",1.5,"oz",False),("Amaretto",0.75,"oz",False)]
    },
    {
        "key":"godmother","name":"Godmother","type":"cocktail","version":"1.0",
        "description":"Vodka and amaretto served over ice.",
        "instructions":"Build vodka and amaretto over ice and stir.",
        "source":"Classic reference","url":"https://en.wikibooks.org/wiki/Bartending/Cocktails",
        "ingredients":[("Vodka",1.5,"oz",False),("Amaretto",0.75,"oz",False)]
    },
    {
        "key":"sea-breeze","name":"Sea Breeze","type":"cocktail","version":"1.0",
        "description":"A tart vodka highball with cranberry and grapefruit.",
        "instructions":"Build vodka and juices over ice and stir gently.",
        "source":"IBA reference","url":"https://iba-world.com/cocktails/",
        "ingredients":[("Vodka",1.5,"oz",False),("Cranberry Juice",3.0,"oz",False),("Grapefruit Juice",1.5,"oz",False)]
    },
    {
        "key":"sex-on-the-beach","name":"Sex on the Beach","type":"cocktail","version":"1.0",
        "description":"A fruity vodka highball with peach, orange, and cranberry.",
        "instructions":"Build all ingredients over ice and stir gently.",
        "source":"IBA reference","url":"https://iba-world.com/cocktails/",
        "ingredients":[("Vodka",1.5,"oz",False),("Peach Schnapps",0.75,"oz",False),("Orange Juice",1.5,"oz",False),("Cranberry Juice",1.5,"oz",False)]
    },
    {
        "key":"shirley-temple","name":"Shirley Temple","type":"mocktail","version":"1.0",
        "description":"A classic non-alcoholic ginger ale and grenadine highball.",
        "instructions":"Build ginger ale and grenadine over ice, stir gently, and garnish if desired.",
        "source":"Open classic reference","url":"https://en.wikibooks.org/wiki/Bartending/Cocktails",
        "ingredients":[("Ginger Ale",5.0,"oz",False),("Grenadine",0.5,"oz",False),("Cherry",1.0,"pc",True)]
    },
    {
        "key":"virgin-mojito","name":"Virgin Mojito","type":"mocktail","version":"1.0",
        "description":"A mint-and-lime cooler without rum.",
        "instructions":"Gently press mint with lime and syrup, add ice, top with club soda, and stir.",
        "source":"Virtual Bartender curated mocktail","url":"local://virtual-bartender/curated",
        "parent":"mojito",
        "ingredients":[("Lime Juice",1.0,"oz",False),("Simple Syrup",0.75,"oz",False),("Mint Leaves",8.0,"pc",False),("Club Soda",4.0,"oz",False)]
    },
    {
        "key":"virgin-margarita","name":"Virgin Margarita","type":"mocktail","version":"1.0",
        "description":"A tart citrus mocktail inspired by the Margarita.",
        "instructions":"Shake lime juice, orange juice, and agave syrup with ice. Strain into a chilled glass and optionally salt the rim.",
        "source":"Virtual Bartender curated mocktail","url":"local://virtual-bartender/curated",
        "parent":"margarita",
        "ingredients":[("Lime Juice",1.5,"oz",False),("Orange Juice",1.5,"oz",False),("Agave Syrup",0.5,"oz",False),("Club Soda",1.0,"oz",False),("Salt",1.0,"tsp",True)]
    },
    {
        "key":"virgin-pina-colada","name":"Virgin Piña Colada","type":"mocktail","version":"1.0",
        "description":"A creamy pineapple-and-coconut mocktail.",
        "instructions":"Blend pineapple juice and coconut cream with ice until smooth.",
        "source":"Virtual Bartender curated mocktail","url":"local://virtual-bartender/curated",
        "parent":"pina-colada",
        "ingredients":[("Pineapple Juice",4.0,"oz",False),("Coconut Cream",2.0,"oz",False)]
    },
    {
        "key":"cucumber-cooler","name":"Cucumber Cooler","type":"mocktail","version":"1.0",
        "description":"A refreshing cucumber, lime, and soda mocktail.",
        "instructions":"Gently press cucumber with lime and syrup. Add ice, top with club soda, and stir.",
        "source":"Virtual Bartender curated mocktail","url":"local://virtual-bartender/curated",
        "ingredients":[("Cucumber",4.0,"pc",False),("Lime Juice",0.75,"oz",False),("Simple Syrup",0.5,"oz",False),("Club Soda",4.0,"oz",False)]
    },
    {
        "key":"ginger-lime-fizz","name":"Ginger Lime Fizz","type":"mocktail","version":"1.0",
        "description":"A bright ginger and lime highball.",
        "instructions":"Build lime juice over ice, top with ginger ale and club soda, and stir gently.",
        "source":"Virtual Bartender curated mocktail","url":"local://virtual-bartender/curated",
        "ingredients":[("Lime Juice",0.75,"oz",False),("Ginger Ale",3.0,"oz",False),("Club Soda",2.0,"oz",False)]
    },
]
