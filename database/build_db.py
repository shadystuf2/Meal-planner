"""Builds the SQLite database file for the Meal Planner app from schema.sql."""

import sqlite3
from pathlib import Path

SCHEMA_PATH = Path(__file__).parent / "schema.sql"
DB_PATH = Path(__file__).parent / "meal_planner.db"


def build_db(db_path: Path = DB_PATH, schema_path: Path = SCHEMA_PATH) -> None:
    schema_sql = schema_path.read_text()

    connection = sqlite3.connect(db_path)
    try:
        connection.executescript(schema_sql)
        connection.commit()
    finally:
        connection.close()


if __name__ == "__main__":
    build_db()
    print(f"Database built at {DB_PATH}")
