"""
Create/Read/Update/Delete functions for ingredients and recipes.

These are plain functions (not methods) because they operate on the
database as a whole - e.g. "get every recipe" isn't something a
single Recipe object can answer about itself. Each function opens its
own Database() connection and closes it before returning, and every
query uses "?" placeholders with a separate params tuple, never
f-strings, to stay safe from SQL injection.
"""

from database.db import Database
from models.ingredient import Ingredient
from models.recipe import Recipe


# ---------------------------------------------------------------------------
# helpers - turn a raw sqlite3.Row from the database into a model object
# ---------------------------------------------------------------------------

def _row_to_ingredient(row):
    return Ingredient(
        id=row["id"],
        name=row["name"],
        quantity=row["quantity"],
        unit=row["unit"],
        category=row["category"],
    )


def _row_to_recipe(row):
    return Recipe(
        id=row["id"],
        name=row["name"],
        meal_category=row["meal_category"],
        cooking_time_minutes=row["cooking_time_minutes"],
        instructions=row["instructions"],
    )


# ---------------------------------------------------------------------------
# ingredients
# ---------------------------------------------------------------------------

def create_ingredient(name, quantity=0, unit=None, category=""):
    """Create a new ingredient and save it to the database."""
    ingredient = Ingredient(name=name, quantity=quantity, unit=unit, category=category)
    ingredient.save()
    return ingredient


def get_ingredient(ingredient_id):
    """Fetch a single ingredient by id, or None if it doesn't exist."""
    db = Database()
    rows = db.execute_read("SELECT * FROM ingredients WHERE id = ?", (ingredient_id,))
    db.close()
    return _row_to_ingredient(rows[0]) if rows else None


def get_all_ingredients():
    """Fetch every ingredient, ordered by name."""
    db = Database()
    rows = db.execute_read("SELECT * FROM ingredients ORDER BY name")
    db.close()
    return [_row_to_ingredient(row) for row in rows]


def update_ingredient(ingredient_id, **fields):
    """
    Update one or more fields of an existing ingredient.

    Usage: update_ingredient(3, quantity=2.5, unit="kg")
    Only the attributes passed as keyword arguments are changed; the
    rest keep their current value. Returns the updated Ingredient, or
    None if no ingredient with that id exists.
    """
    ingredient = get_ingredient(ingredient_id)
    if ingredient is None:
        return None

    for field, value in fields.items():
        setattr(ingredient, field, value)

    ingredient.save()
    return ingredient


def delete_ingredient(ingredient_id):
    """Delete an ingredient by id. Does nothing if it doesn't exist."""
    ingredient = get_ingredient(ingredient_id)
    if ingredient is not None:
        ingredient.delete()


# ---------------------------------------------------------------------------
# recipes
# ---------------------------------------------------------------------------
#
# A recipe's ingredients are represented as a list of
# {"ingredient_id": int, "quantity_required": float} dicts, matching
# the recipe_ingredients junction table (recipe_id, ingredient_id,
# quantity_required).

def _set_recipe_ingredients(db, recipe_id, ingredients):
    """
    Replace all recipe_ingredients rows for a recipe with a new set.

    Deleting the old rows and inserting the new ones is simpler than
    figuring out which rows changed, and recipe_ingredients has no
    data worth preserving beyond recipe_id/ingredient_id/quantity.
    """
    db.execute_write("DELETE FROM recipe_ingredients WHERE recipe_id = ?", (recipe_id,))

    for item in ingredients:
        db.execute_write(
            """
            INSERT INTO recipe_ingredients (recipe_id, ingredient_id, quantity_required)
            VALUES (?, ?, ?)
            """,
            (recipe_id, item["ingredient_id"], item["quantity_required"]),
        )


def create_recipe(name, meal_category, cooking_time_minutes, instructions, ingredients=None):
    """
    Create a new recipe, along with its list of required ingredients.

    `ingredients` is a list of {"ingredient_id": ..., "quantity_required": ...}
    dicts referencing existing rows in the ingredients table. Pass an
    empty list (or leave it as None) for a recipe with no ingredients
    recorded yet.
    """
    recipe = Recipe(
        name=name,
        meal_category=meal_category,
        cooking_time_minutes=cooking_time_minutes,
        instructions=instructions,
    )
    recipe.save()  # INSERTs the recipe row and sets recipe.id

    db = Database()
    _set_recipe_ingredients(db, recipe.id, ingredients or [])
    db.close()

    return recipe


def get_recipe(recipe_id):
    """Fetch a single recipe by id, or None if it doesn't exist."""
    db = Database()
    rows = db.execute_read("SELECT * FROM recipes WHERE id = ?", (recipe_id,))
    db.close()
    return _row_to_recipe(rows[0]) if rows else None


def get_recipe_ingredients(recipe_id):
    """
    Fetch the ingredients required by a recipe, joined with the
    ingredients table so names/units are included, not just ids.

    Returns a list of sqlite3.Row objects with columns:
    ingredient_id, name, unit, category, quantity_required.
    """
    db = Database()
    rows = db.execute_read(
        """
        SELECT ingredients.id AS ingredient_id,
               ingredients.name,
               ingredients.unit,
               ingredients.category,
               recipe_ingredients.quantity_required
        FROM recipe_ingredients
        JOIN ingredients ON ingredients.id = recipe_ingredients.ingredient_id
        WHERE recipe_ingredients.recipe_id = ?
        ORDER BY ingredients.name
        """,
        (recipe_id,),
    )
    db.close()
    return rows


def get_all_recipes():
    """Fetch every recipe, ordered by name."""
    db = Database()
    rows = db.execute_read("SELECT * FROM recipes ORDER BY name")
    db.close()
    return [_row_to_recipe(row) for row in rows]


def update_recipe(recipe_id, ingredients=None, **fields):
    """
    Update one or more fields of an existing recipe.

    Usage: update_recipe(1, cooking_time_minutes=25, name="New name")
    Pass `ingredients` (a list of {"ingredient_id", "quantity_required"}
    dicts, see create_recipe) to replace the recipe's ingredient list;
    leave it as None to leave the ingredients unchanged. Returns the
    updated Recipe, or None if no recipe with that id exists.
    """
    recipe = get_recipe(recipe_id)
    if recipe is None:
        return None

    for field, value in fields.items():
        setattr(recipe, field, value)
    recipe.save()

    if ingredients is not None:
        db = Database()
        _set_recipe_ingredients(db, recipe.id, ingredients)
        db.close()

    return recipe


def delete_recipe(recipe_id):
    """
    Delete a recipe by id. Does nothing if it doesn't exist.

    Its recipe_ingredients rows are removed automatically by the
    ON DELETE CASCADE foreign key in the schema.
    """
    recipe = get_recipe(recipe_id)
    if recipe is not None:
        recipe.delete()
