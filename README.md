# CA Firm MIS — Full Stack

Backend API + React frontend for CA firm compliance tracking and management.

## Tech Stack

- **Backend**: FastAPI 0.109.0 (Python 3.11+)
- **ORM**: SQLAlchemy 2.0.25
- **Database**: PostgreSQL 16
- **Migrations**: Alembic 1.13.1
- **Validation**: Pydantic v2
- **Frontend**: React + Vite + Tailwind CSS
- **Container**: Docker + Docker Compose

## Prerequisites

- Docker Desktop (running)
- Docker Compose v2+

## Quick Start

```bash
git clone <repository-url>
cd ca-firm-mis-backend

# Start all 3 services: database, backend API, and frontend
docker compose up --build

# In a separate terminal — seed the database
curl -X POST http://localhost:8000/seed
```

## Access Points

| Service | URL |
|---------|-----|
| **Frontend** | http://localhost:3000 |
| API Root | http://localhost:8000 |
| Swagger UI | http://localhost:8000/docs |
| ReDoc | http://localhost:8000/redoc |
| Health Check | http://localhost:8000/health |
| PostgreSQL | localhost:5432 (user: postgres, pass: postgres, db: ca_firm_mis) |

---

## Frontend Features

Open **http://localhost:3000** in your browser after running `docker compose up --build`.

### Dashboard Page
- **Summary cards**: Due This Week, Overdue, Awaiting Client, Total Open
- **Workload table**: Per-assignee task count broken down by status (Not Started / In Progress / Awaiting Client / Filed)
- **Task lists**: Collapsible sections for Overdue, Due This Week, and Awaiting Client tasks
- **Generate panel**: Trigger recurring task generation for any month/year directly from the UI

### Tasks Page
- Full task list with **6 filters**: Client, Status, Task Type, Assignee, Due From, Due To
- **Inline status updates**: Change any task's status via a dropdown — saves immediately
- Supports large task counts with pagination via `skip`/`limit` query params

### Clients Page
- Paginated client list (name, entity type, PAN, partner, contact)
- **Add client**: Click "+ Add Client" for a form modal
- **Edit client**: Click Edit on any row to modify all fields
- **Delete client**: Cascades to all their tasks and documents

---

## Recurring Task Generation

### Endpoint
```
POST /tasks/generate
Content-Type: application/json

{ "year": 2026, "month": 8 }
```

### Example
```bash
# Generate tasks for August 2026
curl -X POST http://localhost:8000/tasks/generate \
  -H "Content-Type: application/json" \
  -d '{"year": 2026, "month": 8}'

# Response
{
  "period": "August 2026",
  "tasks_created": 54,
  "tasks_skipped": 0,
  "documents_created": 198
}
```

Running the endpoint again for the same period is **idempotent** — existing tasks are detected by `(client_id, task_type, period_label)` and skipped.

### Recurrence Rules

| Task Type | Frequency | Due Date | Notes |
|-----------|-----------|----------|-------|
| GSTR-3B | Monthly | 20th of next month | All clients |
| GSTR-1 | Monthly | 11th of next month | All clients |
| TDS | Monthly | 7th of next month | All clients |
| GST Quarterly | Quarterly | 30th of month after quarter end | Quarter end months: Mar, Jun, Sep, Dec |
| Income Tax Audit | Annual | 30 September | Triggers in September |
| ROC Annual Filing | Annual | 30 November | Triggers in November |

Rules are defined in `backend/app/recurrence.py` as a Python config dict — easy to extend without DB changes.

---

## Dashboard Endpoint

```
GET /tasks/dashboard
```

Returns a single JSON response with:
- `summary`: counts for `due_this_week_count`, `overdue_count`, `awaiting_client_count`, `total_open_tasks`
- `due_this_week`: tasks due in next 7 days (non-Filed)
- `overdue`: tasks past due date and not Filed
- `awaiting_client`: tasks with status "Awaiting Client"
- `workload_per_assignee`: per-assignee breakdown by status

---

## API Endpoints

### Clients
```
POST   /clients           Create client
GET    /clients           List clients (pagination supported)
GET    /clients/{id}      Get single client
PUT    /clients/{id}      Update client
DELETE /clients/{id}      Delete client (cascades to tasks)
```

### Tasks
```
POST   /tasks             Create task
GET    /tasks             List/filter tasks
GET    /tasks/{id}        Get task with documents
PUT    /tasks/{id}        Update task
DELETE /tasks/{id}        Delete task (cascades to documents)
POST   /tasks/generate    Generate recurring tasks for a period
GET    /tasks/dashboard   Consolidated dashboard metrics
```

### Legacy Dashboard Endpoints (still available)
```
GET /tasks/dashboard/due-this-week
GET /tasks/dashboard/overdue
GET /tasks/dashboard/awaiting-client
GET /tasks/dashboard/workload
```

### Documents
```
POST   /tasks/{task_id}/documents    Add document to task
GET    /tasks/{task_id}/documents    List task documents
PATCH  /documents/{id}               Update received status
DELETE /documents/{id}               Delete document
```

---

## Development

### Database Reset
```bash
docker compose down -v
docker compose up --build
curl -X POST http://localhost:8000/seed
```

### View Logs
```bash
docker compose logs -f api
docker compose logs -f frontend
docker compose logs -f db
```

### Access Database
```bash
docker exec -it ca_firm_mis_db psql -U postgres -d ca_firm_mis
```

### Run API Tests
```bash
# Re-seed first (resets ID sequences), then run tests
curl -X POST http://localhost:8000/seed
./test_api.sh
```

---

## Seed Data

The seed script creates:
- 18 clients across 5 entity types
- 65 compliance tasks across 6 task types
- 200+ document items (2-5 per task)
- Realistic distribution of statuses and assignees

---

## Project Structure

```
backend/
├── app/
│   ├── main.py              FastAPI app
│   ├── config.py            Settings
│   ├── database.py          DB connection
│   ├── models.py            SQLAlchemy models
│   ├── schemas.py           Pydantic schemas
│   ├── recurrence.py        Recurrence rules config + helpers (Day 2)
│   ├── seed.py              Data seeding
│   └── routers/
│       ├── clients.py       Client endpoints
│       ├── tasks.py         Task endpoints + dashboard
│       ├── generate.py      Recurring task generation (Day 2)
│       └── documents.py     Document endpoints
├── alembic/                 Database migrations
├── Dockerfile
└── requirements.txt

frontend/
├── src/
│   ├── api.js               Centralized API calls
│   ├── App.jsx              Root component + tab routing
│   ├── main.jsx             React entry point
│   ├── index.css            Tailwind CSS import
│   ├── components/
│   │   └── Navbar.jsx       Top navigation bar
│   └── pages/
│       ├── Dashboard.jsx    Dashboard page
│       ├── Tasks.jsx        Tasks list + filters
│       └── Clients.jsx      Clients list + add/edit
├── Dockerfile               Multi-stage: Node build → nginx serve
└── package.json
```

---

## Assumptions

1. **Recurrence rules are config-based** (not stored in DB): simpler, more predictable, easy to extend by editing `recurrence.py`.
2. **GSTR-1 is treated as monthly** for all clients (same as GSTR-3B). In practice, some clients may file quarterly — this can be extended by adding a `filing_frequency` field to the `clients` table.
3. **Assignees are auto-assigned** using deterministic round-robin based on `(client_id, task_type)`. This spreads workload evenly without requiring manual assignment at generation time.
4. **The frontend API URL** is embedded at build time via `VITE_API_URL` build arg (defaults to `http://localhost:8000`). The browser makes API calls directly to the backend — this works correctly on a single developer machine.
5. **No authentication**: internal tool only.

---

## License

Internal use only
