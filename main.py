from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import sqlite3

app = FastAPI(title="AI Engineering Task API")


# ============================================================
# STAGE 0: SQLITE DATABASE SETUP
# ============================================================

# SQLite database file.
# SQLite automatically creates this file if it doesn't exist.
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

    # Check how many tasks already exist.
    cursor.execute("SELECT COUNT(*) FROM tasks")

    task_count = cursor.fetchone()[0]

    # Insert the three example tasks only on the first run.
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


# ============================================================
# PYDANTIC MODELS
# ============================================================

class TaskCreate(BaseModel):
    title: str
    done: bool = False


class TaskUpdate(BaseModel):
    title: str
    done: bool


# ============================================================
# ROOT ENDPOINT
# ============================================================

@app.get("/")
def root():
    return {
        "name": "Task API",
        "version": "1.0",
        "endpoints": ["/tasks"]
    }


# ============================================================
# HEALTH CHECK
# ============================================================

@app.get("/health")
def health():
    return {"status": "ok"}


# ============================================================
# STAGE 1: GET ALL TASKS FROM DATABASE
# ============================================================

@app.get("/tasks")
def get_tasks():

    # Open a connection to the SQLite database.
    connection = get_db()
    cursor = connection.cursor()

    # Retrieve all tasks from the database.
    cursor.execute(
        """
        SELECT id, title, done
        FROM tasks
        """
    )

    rows = cursor.fetchall()

    # Close the database connection.
    connection.close()

    # Convert SQLite rows into JSON-compatible dictionaries.
    return [
        {
            "id": row["id"],
            "title": row["title"],
            "done": bool(row["done"])
        }
        for row in rows
    ]


# ============================================================
# STAGE 1: GET ONE TASK FROM DATABASE
# ============================================================

@app.get("/tasks/{task_id}")
def get_task(task_id: int):

    # Open a connection to the SQLite database.
    connection = get_db()
    cursor = connection.cursor()

    # Search for the requested task by ID.
    cursor.execute(
        """
        SELECT id, title, done
        FROM tasks
        WHERE id = ?
        """,
        (task_id,)
    )

    row = cursor.fetchone()

    # Close the database connection.
    connection.close()

    # Return 404 if the task does not exist.
    if row is None:
        raise HTTPException(
            status_code=404,
            detail=f"Task {task_id} not found"
        )

    # Return the task using the same API response format
    # as the original Week 2 implementation.
    return {
        "id": row["id"],
        "title": row["title"],
        "done": bool(row["done"])
    }


# ============================================================
# STAGE 2: CREATE TASK
# ============================================================
# NOTE:
# This still uses the old in-memory implementation.
# We will replace it with SQLite in Stage 2.

# Temporary in-memory list used by POST/PUT/DELETE
# until those stages are completed.
tasks = [
    {
        "id": 1,
        "title": "Learn FastAPI",
        "done": False
    },
    {
        "id": 2,
        "title": "Build CRUD API",
        "done": False
    },
    {
        "id": 3,
        "title": "Test Swagger",
        "done": True
    }
]


# ============================================================
# STAGE 2: INSERT TASK INTO SQLITE DATABASE
# ============================================================

@app.post("/tasks", status_code=201)
def create_task(task: TaskCreate):
    connection = get_db()
    cursor = connection.cursor()

    # Insert the new task into the database
    cursor.execute(
        """
        INSERT INTO tasks (title, done)
        VALUES (?, ?)
        """,
        (task.title, task.done)
    )

    # Get the ID automatically generated by SQLite
    task_id = cursor.lastrowid

    connection.commit()

    # Return the newly created task
    cursor.execute(
        """
        SELECT id, title, done
        FROM tasks
        WHERE id = ?
        """,
        (task_id,)
    )

    row = cursor.fetchone()
    connection.close()

    return {
        "id": row["id"],
        "title": row["title"],
        "done": bool(row["done"])
    }

# ============================================================
# STAGE 3: UPDATE TASK
# ============================================================
# NOTE:
# This will be replaced with SQLite in Stage 3.

@app.put("/tasks/{task_id}")
def update_task(task_id: int, task: TaskUpdate):

    # Search for the task in the temporary in-memory list.
    for existing_task in tasks:

        if existing_task["id"] == task_id:

            existing_task["title"] = task.title
            existing_task["done"] = task.done

            return existing_task

    # Return 404 if the task doesn't exist.
    raise HTTPException(
        status_code=404,
        detail=f"Task {task_id} not found"
    )


# ============================================================
# STAGE 3: DELETE TASK
# ============================================================
# NOTE:
# This will be replaced with SQLite in Stage 3.

@app.delete("/tasks/{task_id}", status_code=204)
def delete_task(task_id: int):

    # Search for the task in the temporary in-memory list.
    for i, task in enumerate(tasks):

        if task["id"] == task_id:

            tasks.pop(i)

            return

    # Return 404 if the task doesn't exist.
    raise HTTPException(
        status_code=404,
        detail=f"Task {task_id} not found"
    )