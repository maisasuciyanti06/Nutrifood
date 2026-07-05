DATA_PATH = "recipes-with-nutrition.csv"

BATAS_KALORI_RENDAH    = 500
BATAS_PROTEIN_TINGGI   = 20
BATAS_PROTEIN_DENSITY  = 0.02
USE_PROTEIN_DENSITY    = True

NON_HALAL_KEYWORDS = [
    'pork','bacon','ham','lard','prosciutto','pepperoni','salami','pancetta',
    'hog','pig','baby back ribs','pork belly','pork chop','pork ribs',
    'pork sausage','alcohol','wine','beer','rum','whiskey','sherry','mirin',
    'sake','angciu','vodka','gin','brandy','cognac','tequila','liqueur',
    'vermouth','bourbon','schnapps','cooking wine','cider','white wine',
    'red wine','gelatin'
]

COOKING_STOPWORDS = [
    'cup','cups','tablespoon','tablespoons','tbsp','teaspoon','teaspoons','tsp',
    'ounce','ounces','oz','pound','pounds','lb','lbs','gram','grams','g','kg','ml',
    'clove','cloves','can','cans','package','packages','packet','packets','bunch',
    'bunches','slice','slices','piece','pieces','chopped','minced','sliced','diced',
    'shredded','crushed','ground','fresh','dried','large','small','medium','taste',
    'salt','pepper','water','oil','divided','optional','inch','halved'
]

MAIN_PROTEINS = [
    'beef','chicken','turkey','fish','salmon','tuna','shrimp','crab',
    'clam','mussel','oyster','duck','lamb'
]

PROTEIN_DERIVATIVES = [
    'broth','stock','bouillon','fat','cube','extract','flavor',
    'powder','kaldu','minyak','sauce'
]

DESSERT_KEYWORDS = [
    'chocolate','cocoa','vanilla','strawberry','raisin','cheese',
    'cream','milk','butter','cake','cookie','flour','rice flour'
]

SAVORY_KEYWORDS = [
    'chili','beef','steak','chicken','garlic','onion','soy sauce'
]

ALERGEN_MAPPING = {
    'susu':    ['milk','cheese','cream','butter','yogurt','yoghurt','mozzarella',
                'cheddar','parmesan','cream cheese','whipping cream','half and half',
                'evaporated milk','condensed milk','ghee','sour cream','ice cream',
                'custard','whey','casein','lactose','dairy'],
    'telur':   ['egg','eggs','egg yolk','egg white','mayonnaise','mayo'],
    'kacang':  ['peanut','peanuts','almond','cashew','cashews','almonds','walnuts',
                'walnut','pecan','pecans','hazelnut','macadamia','pistachio',
                'pistachios','mung bean','mung beans','nut','nuts'],
    'seafood': ['shrimp','prawn','crab','lobster','squid','octopus','clam',
                'mussel','oyster','scallop', 'big clam', 'shel', 'snail', 'sea snail', 'abalone', 'giant clam', 'white clam', 'razor clam','prawn', 'blue crab', 'crawfish', 'crayfish'],
    'gluten':  ['wheat','flour','bread','pasta','noodle','cake','cracker','breadcrumbs'],
    'kedelai': ['soy','soybean','tofu','tempeh','soy sauce','tamari','miso'],
    'wijen':   ['sesame','sesame oil','sesame seed','tahini'],
}
