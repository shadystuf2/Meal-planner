"""
Functions that match recipes to the ingredients currently in stock -
working out which recipes can be made right now, and "cooking" one by
deducting its ingredients from stock.
"""

from database.db import Database
from logic.crud import get_all_recipes, get_recipe_ingredients, get_ingredient


def is_recipe_makeable(recipe_id):
    """
    Return True if every ingredient a recipe requires is currently in
    stock in at least the quantity required, False otherwise.
    """
    for row in get_recipe_ingredients(recipe_id):
        ingredient = get_ingredient(row["ingredient_id"])
        if ingredient is None or ingredient.quantity < row["quantity_required"]:
            return False
    return True


def get_makeable_recipes():
    """Return every Recipe whose ingredient requirements are all currently in stock."""
    return [recipe for recipe in get_all_recipes() if is_recipe_makeable(recipe.id)]


def cook_recipe(recipe_id):
    """
    "Cook" a recipe: subtract each required quantity from the
    matching ingredient's stock, deleting any ingredient whose
    quantity reaches zero.

    All of the stock changes are collected into one list of
    statements and sent to Database.execute_many_writes() together,
    so they run as a single transaction - either every ingredient's
    stock is updated, or (if something goes wrong partway through)
    none of them are, rather than the pantry being left half-updated.

    Raises ValueError, without changing anything, if the recipe isn't
    actually makeable right now (not enough stock of some
    ingredient) - check is_recipe_makeable() first if you want to
    avoid the exception, e.g. to decide whether to show a "Cook this"
    button at all.
    """
    ingredient_rows = get_recipe_ingredients(recipe_id)

    statements = []
    for row in ingredient_rows:
        ingredient = get_ingredient(row["ingredient_id"])
        if ingredient is None or ingredient.quantity < row["quantity_required"]:
            name = row["name"] if ingredient is None else ingredient.name
            raise ValueError(f"Not enough {name} in stock to cook this recipe.")

        remaining = ingredient.quantity - row["quantity_required"]
        if remaining <= 0:
            statements.append(("DELETE FROM ingredients WHERE id = ?", (ingredient.id,)))
        else:
            statements.append(
                ("UPDATE ingredients SET quantity = ? WHERE id = ?", (remaining, ingredient.id))
            )

    db = Database()
    db.execute_many_writes(statements)
    db.close()
