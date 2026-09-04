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


if __name__ == "__main__":
    created_db = build_database()
    print(f"Database created at: {created_db}")
