from storm.locals import *

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
  url = Unicode()
  filename = Unicode()
  description = Unicode()
  mime = Unicode()
  width = Int()
  height = Int()
  image = Pickle()


class Webpage(Storm):
  __storm_table__ = 'webpages'
  id = Int(primary=True)
  title = Unicode()
  url = Unicode()
  html = Unicode()
  source = Unicode()

  def __str__(self):
    return "\turl: "+self.url+" title: "+self.title

class Recipe(Storm):
  __storm_table__ = 'recipes'
  id = Int(primary=True)
  name = Unicode()
  description = Unicode()
  photo = Pickle()
  serves = Int()

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

class RecipeIngredient(Storm):
  __storm_table__ = 'recipe_ingredients'
  id = Int(primary=True)
  name = Unicode()
  description = Unicode()
  amount = Unicode()
  unit = Unicode()
  prep = Unicode()   # crushed, peeled, sliced, pitted
  stage = Unicode()  # sauce, garnish, filling
  recipe_id = Int()
  recipe = ReferenceSet(recipe_id, Recipe.id)

RecipeIngredient.foodstuffs = ReferenceSet(RecipeIngredient.id, IngredientFoodstuffs.ingredient_id, IngredientFoodstuffs.foodstuff_id, Foodstuff.id)

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

Preparation.foodstuffs = ReferenceSet(Preparation.id, PreparationFoodstuffs.preparation_id, PreparationFoodstuffs.foodstuff_id, Foodstuff.id)
