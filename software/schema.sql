-- Enable FOREIGN KEY syntax
PRAGMA foreign_keys = ON;

-- Create DB is a single transaction
BEGIN TRANSACTION;

CREATE TABLE ingredients (
    id INTEGER PRIMARY KEY,
    name VARCHAR(255)
);

CREATE TABLE procedures (
    id INTEGER PRIMARY KEY,
    description TEXT
);

CREATE TABLE recipes (
  id INTEGER PRIMARY KEY,
  name VARCHAR(255),
  description TEXT,
  serves INTEGER
);

CREATE TABLE categories (
  id INTEGER PRIMARY KEY,
  name VARCHAR(255)
);

CREATE TABLE recipe_categories (
  recipe_id INTEGER,
  category_id INTEGER,
  FOREIGN KEY(recipe_id) REFERENCES recipes(id),
  FOREIGN KEY(category_id) REFERENCES categories(id)
);
CREATE INDEX r2c_recipes_idx ON recipe_categories(recipe_id);
CREATE INDEX r2c_categories_idx ON recipe_categories(category_id);

CREATE TABLE recipe_ingredients (
  id INTEGER PRIMARY KEY,
  name VARCHAR(255),
  description TEXT,
  amount VARCHAR(50),
  unit VARCHAR(20),
  recipe_id INTEGER,
  ingredient_id INTEGER,
  FOREIGN KEY(recipe_id) REFERENCES recipes(id),
  FOREIGN KEY(ingredient_id) REFERENCES ingredients(id)
);
CREATE INDEX r2i_recipes_idx ON recipe_ingredients(recipe_id);
CREATE INDEX r2i_ingredients_idx ON recipe_ingredients(ingredient_id);

COMMIT;