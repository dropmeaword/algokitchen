from storm.locals import *

class Ingredient(Storm):
  __storm_table__ = 'ingredients'
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

class Procedure(Storm):
  __storm_table__ = 'procedures'
  id = Int(primary=True)
  description = Unicode()

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

class RecipeIngredient(Storm):
  __storm_table__ = 'recipe_ingredients'
  id = Int(primary=True)
  name = Unicode()
  description = Unicode()
  amount = Unicode()
  unit = Unicode()
  prep = Unicode()   # crushed, peeled, sliced, pitted
  ingredient_id = Int()
  recipe_id = Int()
  ingredient = ReferenceSet(ingredient_id, Ingredient.id)
  recipe = ReferenceSet(recipe_id, Recipe.id)
