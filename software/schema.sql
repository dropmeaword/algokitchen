-- Enable FOREIGN KEY syntax
PRAGMA foreign_keys = ON;

-- Create DB is a single transaction
BEGIN TRANSACTION;

CREATE TABLE webpages (
    id INTEGER PRIMARY KEY,
    title TEXT,
    url TEXT,
    html TEXT,
    source VARCHAR(255)
);

CREATE TABLE foodstuffs (
  id INTEGER PRIMARY KEY,
  name TEXT,
  normalized TEXT,
  photo BLOB
);

CREATE TABLE images (
  id INTEGER PRIMARY KEY,
  url TEXT,
  filename TEXT,
  description TEXT,
  mime TEXT,
  width INTEGER,
  height INTEGER,
  image BLOB
);

CREATE TABLE recipes (
  id INTEGER PRIMARY KEY,
  name VARCHAR(255),
  description TEXT,
  serves INTEGER,
  time_prep TEXT,
  time_cooking TEXT,
);

CREATE TABLE preparations (
    id INTEGER PRIMARY KEY,
    description TEXT
);

CREATE TABLE preparations_foodstuffs (
  foodstuff_id INT,
  preparation_id INT
);

CREATE TABLE categories (
  id INTEGER PRIMARY KEY,
  name VARCHAR(255)
);

CREATE TABLE recipe_categories (
  id INTEGER PRIMARY KEY,
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
