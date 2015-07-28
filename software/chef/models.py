from storm.locals import *

class Trail(Storm):
  __storm_table__ = 'trails'
  id = Int(primary=True)
  what = RawStr()
  script = RawStr()
  tstamp = DateTime()

class Fail(Storm):
  __storm_table__ = 'fails'
  id = Int(primary=True)
  url = RawStr()
  reason = RawStr()
  phase = RawStr()

class Foodstuff(Storm):
  __storm_table__ = 'foodstuffs'
  id = Int(primary=True)
  name = Unicode()
  photo = Pickle()
  normalized = Unicode()

# class Amount:
#   __storm_table__ = 'amounts'
#   id = Int(primary=True)
#   qty = Float()
#   unit = Unicode()

class Image(Storm):
  __storm_table__ = 'images'
  id = Int(primary=True)
  url = RawStr()
  filename = RawStr()
  description = Unicode()
  mime = RawStr()
  width = Int()
  height = Int()
  image = Pickle()


class Webpage(Storm):
  __storm_table__ = 'webpages'
  id = Int(primary=True)
  title = Unicode()
  url = Unicode() #should be RawStr()
  html = Unicode()
  source = RawStr()

  def __str__(self):
    return "\turl: "+self.url+" title: "+self.title

class RecipeIngredients(Storm):
    __storm_table__ = "recipes_ingredients"
    __storm_primary__ = "recipe_id", "ingredient_id"
    recipe_id = Int()
    ingredient_id = Int()
    ordinal = Int()
    stage = Unicode()

class Ingredient(Storm):
  __storm_table__ = 'ingredients'
  id = Int(primary=True)
  name = Unicode()
  description = Unicode()
  amount = RawStr()
  unit = RawStr()
  prep = Unicode()   # crushed, peeled, sliced, pitted
  # stage = Unicode()  # sauce, garnish, filling
  # recipe_id = Int()
  # recipe = ReferenceSet(recipe_id, Recipe.id)

class Recipe(Storm):
  __storm_table__ = 'recipes'
  id = Int(primary=True)
  url = RawStr()
  name = Unicode()
  description = Unicode()
  serves = Int()
  serves_txt = RawStr()
  time_prep = RawStr()
  time_cook = RawStr()
  photo_id = Int()
  photo = ReferenceSet(photo_id, Image.id)

class Category(Storm):
  __storm_table__ = 'categories'
  id = Int(primary=True)
  name = Unicode()

class RecipeCategories(Storm):
  __storm_table__ = 'recipe_categories'
  id = Int(primary=True)
  recipe_id = Int()
  category_id = Int()
  recipe = ReferenceSet(recipe_id, Recipe.id)
  category = ReferenceSet(category_id, Category.id)

class IngredientFoodstuffs(Storm):
    __storm_table__ = "ingredients_foodstuffs"
    __storm_primary__ = "foodstuff_id", "ingredient_id"
    foodstuff_id = Int()
    ingredient_id = Int()

class PreparationFoodstuffs(Storm):
    __storm_table__ = "preparations_foodstuffs"
    __storm_primary__ = "foodstuff_id", "preparation_id"
    foodstuff_id = Int()
    preparation_id = Int()

class Preparation(Storm):
  __storm_table__ = 'preparations'
  id = Int(primary=True)
  ordinal = Int()
  description = Unicode()
  recipe_id = Int()
  recipe = ReferenceSet(recipe_id, Recipe.id)

# m2m preparations in recipes
Preparation.foodstuffs = ReferenceSet(Preparation.id, PreparationFoodstuffs.preparation_id, PreparationFoodstuffs.foodstuff_id, Foodstuff.id)
# m2m foodstuffs in ingredients
Ingredient.foodstuffs = ReferenceSet(Ingredient.id, IngredientFoodstuffs.ingredient_id, IngredientFoodstuffs.foodstuff_id, Foodstuff.id)
# m2m ingredients in recipes
Recipe.ingredients = ReferenceSet(Recipe.id, RecipeIngredients.recipe_id, RecipeIngredients.ingredient_id, Ingredient.id)
