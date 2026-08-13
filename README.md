# CA Firm MIS (Management Information System)

A production-ready full-stack compliance management system designed for Chartered Accountancy (CA) firms to replace Excel spreadsheets. Tracks client filings, generates recurring tasks automatically, monitors document checklists, and presents operational metrics via an executive dashboard.

---

## Tech Stack & Architecture Choices

| Layer | Technology | Rationale |
|-------|------------|-----------|
| **Backend Framework** | FastAPI 0.109.0 (Python 3.11) | High performance, automatic OpenAPI / Swagger generation, strict type safety via Pydantic v2. |
| **ORM & Database** | SQLAlchemy 2.0 + PostgreSQL 16 | Relational consistency, transactional integrity, foreign key CASCADE rules, durable persistence across restarts. |
| **Migrations** | Alembic 1.13.1 | Version-controlled database schema evolution. |
| **Frontend** | React 18 + Vite + Tailwind CSS | Fast rendering, modular component architecture, responsive single-page layout. |
| **Containerization** | Docker + Docker Compose v2 | Multi-container orchestration (DB, API, Frontend) running seamlessly on fresh clones. |

---

## Quick Start (Run from Fresh Clone)

### 1. Start Services
Make sure Docker Desktop is running, then execute:
```bash
git clone https://github.com/intenzee/hsdg-intern.git
cd hsdg-intern

docker compose up --build -d
```

### 2. Seed Database
Run the seed endpoint to populate initial clients, tasks, and document checklists:
```bash
curl -X POST http://localhost:8000/seed
```

### 3. Access Points
- **Frontend App**: [http://localhost:3000](http://localhost:3000)
- **API Swagger Docs**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **API Health Check**: [http://localhost:8000/health](http://localhost:8000/health)

---

## Quick-Check Guide for Evaluators

1. **Dashboard (`http://localhost:3000`)**:
   - High-level metric cards (**Due This Week**, **Overdue**, **Awaiting Client**, **Total Open**).
   - **Workload per Assignee** table showing task distribution by status.
   - Collapsible task tables answering "what needs attention today".
   - **Generate Recurring Tasks** panel to simulate periodic task creation.

2. **Tasks Page (`http://localhost:3000` -> Tasks)**:
   - Filter by Client, Status, Task Type, Assignee, Date Range.
   - Change task status via dropdown (instant inline update).
   - Click `▶` on any row to open the **Document Checklist drawer**, mark items received/pending, or add custom document items.
   - Click **+ Add Task** to manually create single compliance tasks.

3. **Clients Page (`http://localhost:3000` -> Clients)**:
   - Full master list of clients across entities (Company, Individual, LLP, etc.).
   - Add/Edit clients via modal forms with PAN/GSTIN constraints.
   - Delete client (cascades to tasks & documents).

4. **Recurring Task Generation**:
   - Call `POST /tasks/generate` with `{"year": 2026, "month": 8}` or use the Dashboard UI button.
   - Evaluates recurrence rules and generates applicable tasks idempotently.

---

## Requirements & Core Features Implemented

### 1. Client Master
- Full CRUD for clients (`name`, `entity_type`, `pan`, `gstin`, `contact_name`, `contact_email`, `contact_phone`, `partner_in_charge`).
- Unique constraints on PAN & GSTIN.

### 2. Compliance Tasks
- Multi-criteria filtering (client, assignee, status, task_type, due date range).
- 4 status lifecycle states: `Not Started`, `In Progress`, `Awaiting Client`, `Filed`.
- Inline status updating.

### 3. Document Checklists
- Each task includes an associated document checklist template (e.g. Sales Register, Bank Statement, Computation).
- Toggle document status (`is_received: true/false`).
- Dynamic addition of custom document items per task.

### 4. Recurring Task Engine
- Rules defined for:
  - **GSTR-3B**: Monthly, due 20th of following month.
  - **GSTR-1**: Monthly, due 11th of following month.
  - **TDS**: Monthly, due 7th of following month.
  - **GST Quarterly**: Quarterly (Mar, Jun, Sep, Dec), due 30th of following month.
  - **Income Tax Audit**: Annual, due 30th September.
  - **ROC Annual Filing**: Annual, due 30th November.
- Endpoint: `POST /tasks/generate` (idempotent; skips existing tasks for same `client_id` + `task_type` + `period_label`).

### 5. Consolidated Dashboard
- Endpoint `GET /tasks/dashboard` returns:
  - Metrics: `due_this_week_count`, `overdue_count`, `awaiting_client_count`, `total_open_tasks`.
  - Filtered task lists for immediate focus.
  - Per-assignee breakdown of workload across all 4 statuses.

---

## Data Model

```
 ┌────────────────┐         1:N         ┌──────────────────┐         1:N         ┌──────────────────┐
 │     Client     │ ──────────────────> │  ComplianceTask  │ ──────────────────> │   TaskDocument   │
 ├────────────────┤ (CASCADE DELETE)    ├──────────────────┤ (CASCADE DELETE)    ├──────────────────┤
 │ id (PK)        │                     │ id (PK)          │                     │ id (PK)          │
 │ name           │                     │ client_id (FK)   │                     │ task_id (FK)     │
 │ entity_type    │                     │ task_type        │                     │ document_name    │
 │ pan (UNIQUE)   │                     │ period_label     │                     │ is_received      │
 │ gstin (UNIQUE) │                     │ due_date         │                     │ created_at       │
 │ contact_name   │                     │ assignee         │                     └──────────────────┘
 │ contact_email  │                     │ status           │
 │ contact_phone  │                     │ created_at       │
 │ partner_charge │                     │ updated_at       │
 │ created_at     │                     └──────────────────┘
 │ updated_at     │
 └────────────────┘
```

---

## API Summary

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/seed` | Reset & seed database with realistic data |
| `GET` | `/health` | DB connection health check |
| `GET` / `POST` | `/clients` | List (with pagination) & create client |
| `GET` / `PUT` / `DELETE` | `/clients/{id}` | Retrieve, update, or delete client |
| `GET` / `POST` | `/tasks` | List (with filters) & create task |
| `GET` / `PUT` / `DELETE` | `/tasks/{id}` | Retrieve, update, or delete task |
| `GET` | `/tasks/dashboard` | Consolidated dashboard response |
| `POST` | `/tasks/generate` | Generate recurring tasks for year/month |
| `GET` / `POST` | `/tasks/{id}/documents` | List or add documents for a task |
| `PATCH` / `DELETE` | `/documents/{id}` | Toggle document received state or delete |

---

## Assumptions

1. **Config-Driven Recurrence**: Rules are defined cleanly in `backend/app/recurrence.py` as a Python structure rather than a separate database table. This simplifies rule extension without requiring schema migrations.
2. **Deterministic Auto-Assignment**: Auto-generated tasks are assigned round-robin based on `(client_id, task_type)` to distribute team workload evenly.
3. **Frontend API Binding**: In Docker Compose, the Vite build uses `VITE_API_URL=http://localhost:8000` because API calls originate directly from the host browser.
4. **Scope Boundaries**: Authentication, billing, and government portal API integrations are omitted per brief guidelines.

---

## What I Would Build Next

1. **Authentication & RBAC**: Role-based access control (Partners, Senior CAs, Articles) with JWT authentication.
2. **Automated Client Notifications**: Email/SMS reminders for pending documents triggered automatically when status moves to `Awaiting Client`.
3. **Bulk Document Uploads**: Cloud storage (AWS S3 / GCP Storage) integration to allow uploading actual document PDFs against checklist items.
4. **Audit Logs & Activity Timelines**: Track status change history, due date changes, and compliance audit trail per client.

---

## License
Internal CA Firm MIS — Developed for Internship Assessment.
