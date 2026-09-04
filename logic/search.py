"""
Functions for searching and filtering recipes.

Each function builds a SQL SELECT with a WHERE (and sometimes HAVING)
clause and runs it through Database.execute_read(). Every value that
comes from a caller is passed as a "?" placeholder parameter, never
pasted into the query text itself (not even with an f-string) - that
is what keeps these queries safe from SQL injection, exactly like
logic/crud.py.

All functions return a list of sqlite3.Row objects with the same
columns as the recipes table (id, name, meal_category,
cooking_time_minutes, instructions), so the GUI can read
row["name"], row["cooking_time_minutes"], etc. from any of them.
"""

from database.db import Database


# ---------------------------------------------------------------------------
# search - look recipes up by a single criterion
# ---------------------------------------------------------------------------

def search_by_ingredient_name(ingredient_name):
    """
    Find every recipe that uses an ingredient whose name contains
    `ingredient_name` (case-insensitive, partial match - searching
    "onion" matches a recipe using "Green Onion").

    recipe_ingredients only stores ingredient ids, so reaching the
    ingredient's name means joining recipes -> recipe_ingredients ->
    ingredients. DISTINCT stops a recipe appearing twice if more than
    one of its ingredients matches the search text.
    """
    db = Database()
    rows = db.execute_read(
        """
        SELECT DISTINCT recipes.*
        FROM recipes
        JOIN recipe_ingredients ON recipe_ingredients.recipe_id = recipes.id
        JOIN ingredients ON ingredients.id = recipe_ingredients.ingredient_id
        WHERE ingredients.name LIKE ?
        ORDER BY recipes.name
        """,
        # "%" either side of the value makes LIKE match it anywhere in
        # the ingredient name, not just an exact/whole-string match.
        (f"%{ingredient_name}%",),
    )
    db.close()
    return rows


def search_by_meal_category(meal_category):
    """
    Find every recipe in a given meal category (e.g. "breakfast").
    Uses LIKE rather than "=" so the match is case-insensitive and
    forgiving of a partial category name.
    """
    db = Database()
    rows = db.execute_read(
        "SELECT * FROM recipes WHERE meal_category LIKE ? ORDER BY name",
        (f"%{meal_category}%",),
    )
    db.close()
    return rows


def search_by_cooking_time(max_minutes):
    """Find every recipe that takes at most `max_minutes` to cook."""
    db = Database()
    rows = db.execute_read(
        "SELECT * FROM recipes WHERE cooking_time_minutes <= ? ORDER BY cooking_time_minutes",
        (max_minutes,),
    )
    db.close()
    return rows


# ---------------------------------------------------------------------------
# filter - one combined query across several optional criteria
# ---------------------------------------------------------------------------

def filter_recipes(meal_category=None, max_cooking_time=None, min_ingredients=None, max_ingredients=None):
    """
    Find recipes matching all of the given criteria at once. Every
    parameter is optional - leave it as None to not filter on it, e.g.
    filter_recipes(meal_category="dinner", max_cooking_time=30) finds
    dinner recipes that take 30 minutes or less, regardless of how
    many ingredients they use. Calling it with no arguments returns
    every recipe.

    The WHERE/HAVING clauses are assembled piece by piece: an f-string
    is used here, but only to decide which literal SQL fragments
    (like "meal_category = ?") to include - never to insert a value.
    One "?" is added per criterion actually supplied, and its real
    value is appended to `params` in the same order, so every value
    from a caller still reaches SQLite as a placeholder parameter.
    """
    where_clauses = []
    params = []

    if meal_category is not None:
        where_clauses.append("meal_category LIKE ?")
        params.append(f"%{meal_category}%")

    if max_cooking_time is not None:
        where_clauses.append("cooking_time_minutes <= ?")
        params.append(max_cooking_time)

    where_sql = f"WHERE {' AND '.join(where_clauses)}" if where_clauses else ""

    # Ingredient count isn't a column on recipes - it's how many
    # recipe_ingredients rows join to a recipe - so filtering by it
    # needs GROUP BY (one row per recipe) + HAVING (a WHERE that runs
    # after the grouping/counting, since a plain WHERE can't see an
    # aggregate like COUNT()).
    having_clauses = []
    if min_ingredients is not None:
        having_clauses.append("COUNT(recipe_ingredients.ingredient_id) >= ?")
        params.append(min_ingredients)
    if max_ingredients is not None:
        having_clauses.append("COUNT(recipe_ingredients.ingredient_id) <= ?")
        params.append(max_ingredients)

    having_sql = f"HAVING {' AND '.join(having_clauses)}" if having_clauses else ""

    query = f"""
        SELECT recipes.*
        FROM recipes
        LEFT JOIN recipe_ingredients ON recipe_ingredients.recipe_id = recipes.id
        {where_sql}
        GROUP BY recipes.id
        {having_sql}
        ORDER BY recipes.name
    """
    # LEFT JOIN (rather than JOIN) keeps recipes with zero ingredients
    # in the results - COUNT(...) correctly counts them as 0 instead
    # of the recipe being dropped entirely for having no matching row.

    db = Database()
    rows = db.execute_read(query, tuple(params))
    db.close()
    return rows
