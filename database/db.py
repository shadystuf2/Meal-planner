from pathlib import Path
import sqlite3

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "meal_planner.db"
SCHEMA_PATH = BASE_DIR / "schema.sql"


def build_database(db_path: str | Path = DB_PATH) -> Path:
    """Create the SQLite database file and initialize the required tables."""
    db_path = Path(db_path)
    db_path.parent.mkdir(parents=True, exist_ok=True)

    with SCHEMA_PATH.open("r", encoding="utf-8") as schema_file:
        schema_sql = schema_file.read()

    with sqlite3.connect(db_path) as conn:
        conn.execute("PRAGMA foreign_keys = ON;")
        conn.executescript(schema_sql)
        conn.commit()

    return db_path


class Database:
    """
    Wraps a single SQLite connection to mealplanner.db.

    An "object" here just bundles the connection together with the
    methods that use it, so the rest of the app can say
    db.execute_read(...) instead of juggling a raw sqlite3 connection
    everywhere. This class only knows how to run SQL - it has no idea
    what ingredients or recipes are (that logic belongs elsewhere).
    """

    def __init__(self, db_path: str | Path = DB_PATH):
        # __init__ runs automatically when you write Database(...).
        # It opens the connection once and keeps it on self.connection
        # so every other method on this object can reuse it.
        self.connection = sqlite3.connect(db_path)

        # sqlite3.Row lets query results be accessed by column name
        # (row["name"]) as well as by index (row[0]), which is easier
        # to read than a plain tuple.
        self.connection.row_factory = sqlite3.Row

        # SQLite ignores FOREIGN KEY constraints unless this pragma is
        # set on the connection, so it must be run every time a new
        # connection is opened (it does not persist in the db file).
        self.connection.execute("PRAGMA foreign_keys = ON;")

    def execute_write(self, query: str, params: tuple = ()) -> int:
        """
        Run an INSERT, UPDATE, or DELETE statement.

        `query` should contain "?" placeholders instead of real values,
        e.g. "INSERT INTO ingredients (name) VALUES (?)". The actual
        values are passed separately in `params`. SQLite then inserts
        them safely itself, instead of the values being pasted into
        the SQL text - which is what keeps this safe from SQL
        injection. Never build the query with f-strings/.format()/+.

        Returns the id of the last inserted row (useful after an
        INSERT); for UPDATE/DELETE this value can be ignored.
        """
        cursor = self.connection.execute(query, params)
        self.connection.commit()  # save the change to the .db file
        return cursor.lastrowid

    def execute_read(self, query: str, params: tuple = ()) -> list:
        """
        Run a SELECT statement and return every matching row.

        Same rule as execute_write: put "?" placeholders in `query`
        and pass the real values through `params`, never string-format
        them into the query.

        Returns a list of sqlite3.Row objects. Each row can be read
        like a dict (row["column_name"]) or like a tuple (row[0]).
        """
        cursor = self.connection.execute(query, params)
        return cursor.fetchall()

    def execute_many_writes(self, statements: list) -> None:
        """
        Run several INSERT/UPDATE/DELETE statements as one atomic
        transaction: `statements` is a list of (query, params) tuples,
        each following the same "?" placeholder rule as execute_write.

        Nothing is committed until every statement in the list has
        run successfully - if any one of them raises an exception,
        every change made so far in this call is rolled back instead
        of being saved, so the database is never left half-updated.
        This is what makes a multi-step change (like cooking a recipe,
        which updates several ingredients at once) safe to interrupt.
        """
        try:
            for query, params in statements:
                self.connection.execute(query, params)
            self.connection.commit()
        except Exception:
            self.connection.rollback()
            raise

    def close(self):
        # Closes the connection to the database file. Call this when
        # the program is done using the database, so SQLite can
        # release the file cleanly.
        self.connection.close()


if __name__ == "__main__":
    created_db = build_database()
    print(f"Database created at: {created_db}")
