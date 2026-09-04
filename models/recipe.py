from database.db import Database


class Recipe:
    """
    Will represent one row of the `recipes` table as a Python object,
    the same way Ingredient (see models/ingredient.py) represents a
    row of the `ingredients` table. Use that class as a reference -
    save() and delete() here should follow the same pattern:
      - open a Database()
      - run one parameterised query (never f-string values into SQL)
      - close the Database() when done

    recipes table columns (see database/schema.sql):
      id                     INTEGER PRIMARY KEY
      name                   TEXT
      meal_category          TEXT
      cooking_time_minutes   INTEGER
      instructions           TEXT
    """

    def __init__(self, name, meal_category, cooking_time_minutes, instructions, id=None):
        # TODO: store each parameter on self, one attribute per
        # column above (id, name, meal_category, cooking_time_minutes,
        # instructions) - same idea as Ingredient.__init__.
        pass

    def save(self):
        """
        TODO: write this recipe to the database.

        Same two cases as Ingredient.save():
          - self.id is None  -> INSERT a new row, then store the new
            id SQLite generates back onto self.id
          - self.id is set   -> UPDATE the existing row (WHERE id = ?)

        Remember: use "?" placeholders in the query string and pass
        the real values as a separate params tuple - never build the
        SQL with f-strings/.format()/+.
        """
        pass

    def delete(self):
        """
        TODO: delete this recipe's row from the database.

        Only do anything if self.id is set (nothing to delete
        otherwise). Run a parameterised DELETE ... WHERE id = ?, then
        set self.id back to None since this object no longer matches
        a database row.

        Note: recipe_ingredients rows referencing this recipe are
        removed automatically by the ON DELETE CASCADE foreign key in
        the schema, as long as the Database connection has
        PRAGMA foreign_keys = ON (it does, see database/db.py).
        """
        pass

    def __repr__(self):
        # TODO (optional): return a readable string like
        # Ingredient.__repr__ does, useful for debugging/printing.
        pass
