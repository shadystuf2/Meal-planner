PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS ingredients (
    id       INTEGER PRIMARY KEY AUTOINCREMENT,
    name     TEXT    NOT NULL UNIQUE,
    quantity REAL    NOT NULL DEFAULT 0 CHECK (quantity >= 0),
    unit     TEXT    NOT NULL,
    category TEXT
);

CREATE TABLE IF NOT EXISTS recipes (
    id                   INTEGER PRIMARY KEY AUTOINCREMENT,
    name                 TEXT    NOT NULL,
    meal_category        TEXT    NOT NULL,
    cooking_time_minutes INTEGER NOT NULL CHECK (cooking_time_minutes > 0),
    instructions         TEXT
);

CREATE TABLE IF NOT EXISTS recipe_ingredients (
    recipe_id         INTEGER NOT NULL,
    ingredient_id     INTEGER NOT NULL,
    quantity_required REAL    NOT NULL CHECK (quantity_required > 0),
    PRIMARY KEY (recipe_id, ingredient_id),
    FOREIGN KEY (recipe_id)     REFERENCES recipes(id)     ON DELETE CASCADE,
    FOREIGN KEY (ingredient_id) REFERENCES ingredients(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_recipe_ingredients_ingredient
    ON recipe_ingredients(ingredient_id);
