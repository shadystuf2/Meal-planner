from database.db import Database


class Ingredient:
    """
    Represents one row of the `ingredients` table as a Python object.

    Instead of passing raw tuples or dicts of ingredient data around
    the app, other code can create an Ingredient(...) object and call
    methods on it (like .save()) to read/write that data. The class
    itself doesn't hold a database connection - each method opens a
    Database() when it needs one and closes it when it's done.
    """

    def __init__(self, name, quantity=0, unit=None, category="", id=None):
        # __init__ is the constructor: it runs automatically whenever
        # someone writes Ingredient(...), and its job is to set up the
        # attributes (the pieces of data) that this particular object
        # will hold.
        #
        # `self` refers to the specific object being built. Every
        # method in this class takes `self` as its first parameter so
        # it knows *which* Ingredient's data to use - e.g. if you
        # create two Ingredient objects, each has its own self.name,
        # self.quantity, etc, completely independent of the other's.
        #
        # Each attribute below corresponds directly to a column in
        # the ingredients table (see database/schema.sql):
        self.id = id                # ingredients.id  (None until this row exists in the db)
        self.name = name            # ingredients.name
        self.quantity = quantity    # ingredients.quantity
        self.unit = unit            # ingredients.unit
        self.category = category    # ingredients.category

    def save(self):
        """
        Write this ingredient's current attributes to the database.

        - If self.id is None, this object has never been saved
          before, so we INSERT a new row. SQLite then generates a new
          id for that row, which we store back onto self.id so this
          object now "knows" which database row it corresponds to.
        - If self.id is already set, this object represents a row
          that already exists (either loaded from the db, or saved
          once already), so we UPDATE that row instead of creating a
          duplicate one.
        """
        db = Database()  # open a connection to run this query

        if self.id is None:
            new_id = db.execute_write(
                """
                INSERT INTO ingredients (name, quantity, unit, category)
                VALUES (?, ?, ?, ?)
                """,
                (self.name, self.quantity, self.unit, self.category),
            )
            self.id = new_id  # now this object matches the new row
        else:
            db.execute_write(
                """
                UPDATE ingredients
                SET name = ?, quantity = ?, unit = ?, category = ?
                WHERE id = ?
                """,
                (self.name, self.quantity, self.unit, self.category, self.id),
            )

        db.close()  # release the connection now that we're done with it

    def delete(self):
        """
        Delete this ingredient's row from the database.

        Only makes sense once the ingredient has actually been saved
        (i.e. self.id is set) - if it's still None there is no
        matching row in the database to remove.
        """
        if self.id is None:
            return  # nothing to delete - this ingredient was never saved

        db = Database()
        db.execute_write("DELETE FROM ingredients WHERE id = ?", (self.id,))
        db.close()

        self.id = None  # this object no longer corresponds to a db row

    def __repr__(self):
        # __repr__ controls what is shown when you print(ingredient)
        # or inspect one in a debugger/REPL. It's just a readability
        # convenience for development - not part of the save/delete
        # logic above.
        return (
            f"Ingredient(id={self.id}, name={self.name!r}, "
            f"quantity={self.quantity}, unit={self.unit!r}, "
            f"category={self.category!r})"
        )
