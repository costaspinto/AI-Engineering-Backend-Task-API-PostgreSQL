# AI Engineering Backend Task API

A production-oriented FastAPI CRUD service backed by SQLite, developed as part of the **FlyRank AI Engineering Backend Task API — A2: Connecting to the Database** assignment.

The project replaces the original in-memory task store with a persistent SQLite database while preserving the CRUD API contract.

> **Repository note:** The repository name contains `PostgreSQL`, but this implementation intentionally uses **SQLite**, matching the assignment's Python lane and Stage 0–5 requirements.

---

## Project Overview

```text
In-memory CRUD API
        ↓
SQLite database initialization
        ↓
SQL-based reads
        ↓
SQL-based inserts
        ↓
SQL-based updates and deletes
        ↓
Manual database inspection with DB Browser
        ↓
Persistent, documented CRUD API
```

### Core capabilities

- FastAPI REST API
- SQLite persistence
- Automatic database/table creation
- Seed data on first database initialization only
- SQL-based CRUD operations
- Parameterized SQL queries
- HTTP 404 handling for unknown task IDs
- Pydantic request validation
- Interactive Swagger/OpenAPI documentation
- Database inspection with DB Browser for SQLite
- Persistence across application restarts

---

## Technology Stack

| Layer | Technology |
|---|---|
| Language | Python |
| API framework | FastAPI |
| ASGI server | Uvicorn |
| Validation | Pydantic |
| Database | SQLite |
| Database driver | Python `sqlite3` |
| API documentation | Swagger UI / OpenAPI |
| Database GUI | DB Browser for SQLite |
| Version control | Git / GitHub |

---

## Project Structure

```text
AI-Engineering-Backend-Task-API-PostgreSQL/
│
├── main.py
├── requirements.txt
├── .gitignore
├── README.md
├── screenshots/
│   ├── image(20261002-090136).png
│   ├── image(20261002-090210).png
│   ├── image(20261002-090304).png
│   ├── ...
│   └── image(20261002-093553).png
│
└── tasks.db
```

### Database location

The application creates the SQLite database in the project root:

```text
tasks.db
```

The database file is intentionally excluded from Git because it is a local runtime artifact.

SQLite journal files are also ignored:

```gitignore
*.db
*.sqlite
*.sqlite3
*.db-journal
```

---

# Database Design

The application uses one table:

```sql
CREATE TABLE tasks (
    id INTEGER PRIMARY KEY,
    title TEXT NOT NULL,
    done BOOLEAN NOT NULL DEFAULT 0
);
```

### Schema

| Column | Type | Constraint | Purpose |
|---|---|---|---|
| `id` | INTEGER | PRIMARY KEY | Unique task identifier |
| `title` | TEXT | NOT NULL | Task description |
| `done` | BOOLEAN | NOT NULL, DEFAULT 0 | Completion status |

The application converts SQLite's integer boolean representation (`0` / `1`) into Python/JSON booleans (`false` / `true`) in API responses.

---

# API Endpoints

| Method | Endpoint | Purpose | Success |
|---|---|---|---|
| `GET` | `/` | API metadata | `200` |
| `GET` | `/health` | Health check | `200` |
| `GET` | `/tasks` | Return all tasks | `200` |
| `GET` | `/tasks/{task_id}` | Return one task | `200` / `404` |
| `POST` | `/tasks` | Create a task | `201` |
| `PUT` | `/tasks/{task_id}` | Update a task | `200` / `404` |
| `DELETE` | `/tasks/{task_id}` | Delete a task | `204` / `404` |

Swagger UI:

```text
http://127.0.0.1:8000/docs
```

OpenAPI JSON:

```text
http://127.0.0.1:8000/openapi.json
```

---

# Implementation Details

## Database Connection

The application uses Python's built-in `sqlite3` module:

```python
DATABASE = "tasks.db"

def get_db():
    connection = sqlite3.connect(DATABASE)
    connection.row_factory = sqlite3.Row
    return connection
```

Using `sqlite3.Row` allows database columns to be accessed by name.

Connections are explicitly closed after each database operation.

---

## Automatic Database Initialization

On application startup:

1. `tasks.db` is opened/created.
2. The `tasks` table is created if it does not already exist.
3. The current row count is checked.
4. The three example tasks are inserted only when the table is empty.

This prevents seed data from being duplicated on every restart.

Example seed data:

```text
Learn FastAPI
Build CRUD API
Test Swagger
```

The persistence behavior was verified by restarting the application and confirming that existing data remained available.

---

# SQL Safety

The application uses parameterized SQL rather than string interpolation.

Example:

```python
cursor.execute(
    """
    SELECT id, title, done
    FROM tasks
    WHERE id = ?
    """,
    (task_id,)
)
```

Insert example:

```python
cursor.execute(
    """
    INSERT INTO tasks (title, done)
    VALUES (?, ?)
    """,
    (task.title, task.done)
)
```

This keeps user-supplied values separate from SQL syntax.

---

# Stage-by-Stage Development

## Stage 0 — Create SQLite Database

Stage 0 introduced:

- `tasks.db`
- `tasks` table
- automatic table creation
- three example records on an empty database
- persistence across application restarts

### Database structure

![Stage 0 — SQLite database structure](screenshots/image(20261002-092521).png)

---

## Stage 1 — Database Read Endpoints

The in-memory reads were replaced with SQL queries.

### Get all tasks

```sql
SELECT id, title, done
FROM tasks;
```

### Get one task

```sql
SELECT id, title, done
FROM tasks
WHERE id = ?;
```

Unknown IDs return HTTP `404`.

### API evidence

![Stage 1 — API requests](screenshots/image(20261002-090210).png)

The server log shows successful requests and a `404 Not Found` response for an unknown task ID.

---

## Stage 2 — Insert into SQLite

`POST /tasks` was changed from appending to a Python list to inserting a real database row.

Example request:

```json
{
  "title": "Learn SQLite",
  "done": false
}
```

The endpoint returns the newly created task with HTTP `201 Created`.

![Stage 2 — Created task and persisted API data](screenshots/image(20261002-090136).png)

---

## Stage 3 — Update and Delete with SQL

The final two CRUD operations were moved to SQLite.

### Update

```sql
UPDATE tasks
SET title = ?, done = ?
WHERE id = ?;
```

### Delete

```sql
DELETE FROM tasks
WHERE id = ?;
```

Both operations check whether a matching row exists and return `404` when the requested task does not exist.

The delete flow was verified by updating task `4`, deleting it, requesting `GET /tasks/4`, receiving `404`, restarting the API, and confirming that the deletion persisted.

### API evidence

![Stage 3 — API CRUD verification](screenshots/image(20261002-091112).png)

---

# Stage 4 — SQLite Exploration

Stage 4 verified that the database can be manipulated independently of FastAPI and that the API reflects those database changes.

The database was opened in **DB Browser for SQLite**.

### Query 1 — View all tasks

```sql
SELECT * FROM tasks;
```

### Query 2 — View completed tasks

```sql
SELECT * FROM tasks
WHERE done = 1;
```

### Query 3 — Count tasks

```sql
SELECT COUNT(*) FROM tasks;
```

Initial count:

```text
3
```

![Stage 4 — SQL inspection](screenshots/image(20261002-092845).png)

### Manual UPDATE test

```sql
UPDATE tasks SET done = 1;
```

Result:

```text
3 rows affected
```

The API was then queried and reflected the database modification.

![Stage 4 — Database UPDATE](screenshots/image(20261002-092910).png)

### Manual DELETE test

```sql
DELETE FROM tasks WHERE done = 1;
```

Result:

```text
3 rows affected
```

The database count became:

```text
0
```

![Stage 4 — Database DELETE](screenshots/image(20261002-093352).png)

### Restore final database state

```sql
INSERT INTO tasks (title, done)
VALUES
    ('Learn FastAPI', 0),
    ('Build CRUD API', 0),
    ('Test Swagger', 1);
```

The final API verification returned HTTP `200` with the expected three tasks.

![Stage 4 — Final API verification](screenshots/image(20261002-093553).png)

---

# Final Database State

The project was left with the expected three example records:

```text
ID  Title             Done
1   Learn FastAPI     false
2   Build CRUD API    false
3   Test Swagger      true
```

This final state was verified both directly in SQLite and through `GET /tasks`.

---

# Running the Project

## 1. Clone the repository

```bash
git clone https://github.com/costaspinto/AI-Engineering-Backend-Task-API-PostgreSQL.git
cd AI-Engineering-Backend-Task-API-PostgreSQL
```

## 2. Create a virtual environment

Windows:

```powershell
python -m venv .venv
```

Activate:

```powershell
.venv\Scripts\Activate.ps1
```

## 3. Install dependencies

```powershell
pip install -r requirements.txt
```

## 4. Start the API

```powershell
uvicorn main:app --reload
```

The API starts at:

```text
http://127.0.0.1:8000
```

Swagger:

```text
http://127.0.0.1:8000/docs
```

---

# Example API Requests

## Create

```http
POST /tasks
```

```json
{
  "title": "Learn SQLite",
  "done": false
}
```

## Update

```http
PUT /tasks/4
```

```json
{
  "title": "Learn SQLite Database",
  "done": true
}
```

## Get one

```http
GET /tasks/4
```

## Delete

```http
DELETE /tasks/4
```

Response:

```text
204 No Content
```

---

# Error Handling

Missing task IDs are explicitly handled:

```python
raise HTTPException(
    status_code=404,
    detail=f"Task {task_id} not found"
)
```

Example:

```json
{
  "detail": "Task 999 not found"
}
```

Request bodies are validated using Pydantic/FastAPI.

> Note: FastAPI's default malformed-request-body validation response is HTTP `422 Unprocessable Entity`; the current implementation does not add a custom exception handler that converts this to `400`.

---

# Testing and Verification

The implementation was manually verified through Swagger UI and DB Browser for SQLite.

- Database creation
- Table creation
- Seed data insertion
- GET all tasks
- GET individual task
- Unknown task returns `404`
- POST creates a persistent task
- PUT updates a persistent task
- DELETE removes a persistent task
- Data survives application restart
- Direct SQL UPDATE is reflected by the API
- Direct SQL DELETE is reflected by the API
- Database can be restored through SQL
- Final API state matches database state

---

# Engineering Decisions

### Why SQLite?

SQLite matches the assignment requirements and provides:

- zero external database server
- simple local development
- persistent relational storage
- standard SQL support
- transactional writes
- easy inspection through DB Browser

For a small single-service task API, SQLite provides persistence without requiring separate database infrastructure.

### Why `sqlite3` instead of an ORM?

The assignment permits Python's `sqlite3` module. Using it keeps the implementation close to SQL and makes the database operations transparent:

```text
FastAPI endpoint
      ↓
sqlite3 connection
      ↓
Parameterized SQL
      ↓
SQLite database
```

---

# Repository Hygiene

Runtime and environment files are excluded from Git:

```gitignore
.venv/
*.db
*.sqlite
*.sqlite3
*.db-journal
__pycache__/
```

This prevents local database state, SQLite journal files, and Python environment files from being committed accidentally.

---

# Interview-Ready Technical Summary

### What changed from the previous implementation?

The previous API stored tasks in a Python list, so data existed only in application memory and disappeared when the process restarted.

The new persistence layer is:

```text
Before:
FastAPI → Python list

After:
FastAPI → sqlite3 → tasks.db
```

The HTTP API contract remains essentially unchanged while storage becomes durable.

### How is persistence achieved?

Every CRUD operation interacts with `tasks.db`. Write operations call `connection.commit()`, and reads query the database directly. Because the database file exists independently of the FastAPI process, records survive application restarts.

### How are duplicate seed records prevented?

Startup checks:

```sql
SELECT COUNT(*) FROM tasks;
```

The three examples are inserted only when the table is empty.

### How are SQL injection risks reduced?

Values are passed through SQLite parameter binding:

```python
cursor.execute(
    "SELECT ... WHERE id = ?",
    (task_id,)
)
```

rather than concatenated into SQL strings.

### How was database/API consistency verified?

The database was modified directly in DB Browser:

```sql
UPDATE tasks SET done = 1;
```

The API was then queried and returned the modified values. The same process was repeated with:

```sql
DELETE FROM tasks WHERE done = 1;
```

This demonstrates that the API reads the actual persistent database state rather than maintaining a separate in-memory copy.

---

# Future Improvements

Possible production-oriented extensions:

- SQLModel or SQLAlchemy
- Alembic database migrations
- automated pytest test suite
- dependency-injected database sessions
- structured logging
- environment-based configuration
- Docker containerization
- PostgreSQL for larger/multi-user deployments
- API authentication and authorization
- pagination and filtering
- automated CI/CD
- integration tests

These are outside the scope of the current SQLite assignment.

---

# Assignment Progress

| Stage | Deliverable | Status |
|---|---|---|
| Stage 0 | SQLite database and initialization | Complete |
| Stage 1 | SQL read endpoints | Complete |
| Stage 2 | SQL insert endpoint | Complete |
| Stage 3 | SQL update/delete endpoints | Complete |
| Stage 4 | SQLite exploration and API verification | Complete |
| Stage 5 | Documentation and README | In progress |

---

# Evidence

The `screenshots/` directory contains the timestamped development and verification screenshots from Stages 0–4.

The screenshot archive is:

```text
FlyRank_A2_Stages_0-4_Screenshots.zip
```

---

## Author

**Costas Pinto**

MCA — Artificial Intelligence & Machine Learning

GitHub: https://github.com/costaspinto

Portfolio: https://costas-portfolio-ai.vercel.app/

LinkedIn: https://www.linkedin.com/in/costaspinto/
