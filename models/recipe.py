from database.db import Database


class Recipe:
    """
    Represents one row of the `recipes` table as a Python object, the
    same way Ingredient (see models/ingredient.py) represents a row
    of the `ingredients` table.

    Note: this class only covers the recipes table itself (id, name,
    meal_category, cooking_time_minutes, instructions). The recipe's
    ingredients live in the separate recipe_ingredients junction
    table (many-to-many), so that's handled by the crud functions in
    logic/crud.py rather than here.
    """

    def __init__(self, name, meal_category, cooking_time_minutes, instructions, id=None):
        self.id = id                                           # recipes.id
        self.name = name                                       # recipes.name
        self.meal_category = meal_category                     # recipes.meal_category
        self.cooking_time_minutes = cooking_time_minutes        # recipes.cooking_time_minutes
        self.instructions = instructions                        # recipes.instructions

    def save(self):
        """
        Write this recipe's current attributes to the database.

        Same insert-or-update pattern as Ingredient.save():
        self.id is None -> INSERT and remember the new id;
        self.id is set  -> UPDATE the existing row.
        """
        db = Database()

        if self.id is None:
            new_id = db.execute_write(
                """
                INSERT INTO recipes (name, meal_category, cooking_time_minutes, instructions)
                VALUES (?, ?, ?, ?)
                """,
                (self.name, self.meal_category, self.cooking_time_minutes, self.instructions),
            )
            self.id = new_id
        else:
            db.execute_write(
                """
                UPDATE recipes
                SET name = ?, meal_category = ?, cooking_time_minutes = ?, instructions = ?
                WHERE id = ?
                """,
                (self.name, self.meal_category, self.cooking_time_minutes, self.instructions, self.id),
            )

        db.close()

    def delete(self):
        """
        Delete this recipe's row from the database.

        recipe_ingredients rows referencing this recipe are removed
        automatically by the ON DELETE CASCADE foreign key in the
        schema, since Database connections run with
        PRAGMA foreign_keys = ON (see database/db.py) - no need to
        delete them here separately.
        """
        if self.id is None:
            return

        db = Database()
        db.execute_write("DELETE FROM recipes WHERE id = ?", (self.id,))
        db.close()

        self.id = None

    def __repr__(self):
        return (
            f"Recipe(id={self.id}, name={self.name!r}, "
            f"meal_category={self.meal_category!r}, "
            f"cooking_time_minutes={self.cooking_time_minutes}, "
            f"instructions={self.instructions!r})"
        )
