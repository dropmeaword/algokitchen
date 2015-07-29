-- Enable FOREIGN KEY syntax
PRAGMA foreign_keys = ON;

-- Create DB is a single transaction
BEGIN TRANSACTION;

CREATE TABLE trails (
  id INTEGER PRIMARY KEY,
  what TEXT,
  script TEXT,
  tstamp TIMESTAMP DEFAULT (datetime('now','localtime'))
);

CREATE TABLE webpages (
    id INTEGER PRIMARY KEY,
    title TEXT,
    url TEXT,
    html TEXT,
    source VARCHAR(255)
);

CREATE TABLE fails (
    id INTEGER PRIMARY KEY,
    url TEXT,
    reason TEXT,
    phase TEXT
);

CREATE TABLE foodstuffs (
  id INTEGER PRIMARY KEY,
  name TEXT,
  normalized TEXT,
  photo_id INTEGER
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
  url TEXT,
  name VARCHAR(255),
  description TEXT,
  serves INTEGER,
  serves_txt VARCHAR(80),
  time_prep TEXT,
  time_cook TEXT,
  photo_id INT,
  FOREIGN KEY(photo_id) REFERENCES images(id)
);

CREATE TABLE preparations (
    id INTEGER PRIMARY KEY,
    description TEXT,
    ordinal INT,
    recipe_id INTEGER,
    FOREIGN KEY(recipe_id) REFERENCES recipes(id)
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

CREATE TABLE ingredients (
  id INTEGER PRIMARY KEY,
  name VARCHAR(255),
  description TEXT,
  amount VARCHAR(50),
  unit VARCHAR(20),
  prep TEXT
);

CREATE TABLE recipes_ingredients (
  recipe_id INTEGER,
  ingredient_id INTEGER,
  ordinal INT,
  stage TEXT,
  FOREIGN KEY(recipe_id) REFERENCES recipes(id),
  FOREIGN KEY(ingredient_id) REFERENCES ingredients(id)
);

CREATE INDEX r2i_recipes_idx ON recipe_ingredients(recipe_id);

CREATE TABLE ingredients_foodstuffs (
  foodstuff_id INT,
  ingredient_id INT
);


-- this view links foodstuffs, with ingredients and recipes in a single table
DROP VIEW vw_recipes_foodstuffs;
CREATE VIEW vw_recipes_foodstuffs AS
  SELECT r.id as recipe_id, i.id as ingredient_id, i2f.foodstuff_id as foodstuff_id
  FROM ingredients i, recipes r
  INNER JOIN recipes_ingredients i2r
  ON (i2r.ingredient_id = i.id AND i2r.recipe_id = r.id)
  LEFT JOIN ingredients_foodstuffs i2f
  ON (i2f.ingredient_id = i.id)
  WHERE i2f.foodstuff_id NOT NULL
  ORDER BY recipe_id;

-- LEFT JOIN ingredients_foodstuffs i2f
-- ON (i2f.ingredient_id = i.id AND i2f.foodstuff_id = fs.id)


SELECT r.id as recipe_id, i.id as ingredient_id
FROM recipes r, ingredients i, foodstuffs fs
LEFT JOIN recipes_ingredients r2i
ON (r.id = r2i.ingredient_id);
--ON (r2i.recipe_id = r.id AND r2i.ingredient_id = i.id);
--WHERE r.id = 40;
LEFT JOIN ingredients_foodstuffs i2f
ON (i2f.ingredient_id = r2i.ingredient_id AND i2f.foodstuff_id = fs.id);

COMMIT;


###
DELETE FROM recipes;
DELETE FROM foodstuffs;
DELETE FROM ingredients;
DELETE FROM preparations;
DELETE FROM recipes_ingredients;
DELETE FROM ingredients_foodstuffs;
DELETE FROM preparations_foodstuffs;

###
-- get ingredients for recipe
SELECT i.id, i.name, i2r.stage, i2r.ordinal FROM ingredients i JOIN recipes_ingredients i2r ON i2r.ingredient_id = i.id WHERE i2r.recipe_id = 10 ORDER BY i2r.ordinal;

-- get foodstuffs for ingredient
SELECT fs.* FROM foodstuffs fs JOIN ingredients_foodstuffs i2f ON i2f.foodstuff_id = fs.id WHERE i2f.ingredient_id = 156;

-- get ingredients for foodstuff
SELECT i.id, i.name FROM ingredients i, foodstuffs fs JOIN ingredients_foodstuffs i2f ON (i2f.ingredient_id = i.id AND i2f.foodstuff_id = fs.id) WHERE fs.name LIKE "apricots%";

-- get recipes featuring foodstuff
SELECT r.* FROM recipes r JOIN recipes_ingredients r2i ON r2i.recipe_id = r.id WHERE r2i.ingredient_id IN (SELECT i.id FROM ingredients i, foodstuffs fs JOIN ingredients_foodstuffs i2f ON (i2f.ingredient_id = i.id AND i2f.foodstuff_id = fs.id) WHERE fs.name LIKE "apricot");

SELECT fs.* FROM foodstuffs fs WHERE fs.name LIKE "apricot%";

-- get preparation for recipe
SELECT p.id, p.ordinal, p.description FROM preparations p WHERE p.recipe_id = 5 ORDER BY p.ordinal;

-- get foodstuffs for preparation
SELECT fs.name FROM foodstuffs fs JOIN preparations_foodstuffs p2f ON p2f.foodstuff_id = fs.id WHERE p2f.preparation_id = 55;

-- get preparations for foodstuff
SELECT prep.description FROM foodstuffs fs, preparations prep JOIN preparations_foodstuffs p2f ON (p2f.preparation_id = prep.id AND p2f.foodstuff_id = fs.id) WHERE fs.name LIKE 'red onion';
