from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import sqlite3

app = FastAPI(title="AI Engineering Task API")

# ============================================================
# STAGE 0: SQLITE DATABASE SETUP
# ============================================================

# SQLite database file.
# SQLite will automatically create this file if it doesn't exist.
DATABASE = "tasks.db"


def get_db():
    """Create a connection to the SQLite database."""
    connection = sqlite3.connect(DATABASE)

    # Allows database rows to be accessed using column names.
    connection.row_factory = sqlite3.Row

    return connection


def initialize_database():
    """
    Create the tasks table if it doesn't exist.

    Insert the three example tasks only when the database
    is completely empty.
    """

    connection = get_db()
    cursor = connection.cursor()

    # Create the tasks table.
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY,
            title TEXT NOT NULL,
            done BOOLEAN NOT NULL DEFAULT 0
        )
        """
    )

    # Check how many tasks are already in the database.
    cursor.execute("SELECT COUNT(*) FROM tasks")

    task_count = cursor.fetchone()[0]

    # Insert the example tasks ONLY on the first run.
    if task_count == 0:

        example_tasks = [
            ("Learn FastAPI", False),
            ("Build CRUD API", False),
            ("Test Swagger", True)
        ]

        cursor.executemany(
            """
            INSERT INTO tasks (title, done)
            VALUES (?, ?)
            """,
            example_tasks
        )

    connection.commit()
    connection.close()


# Initialize the database when the application starts.
initialize_database()