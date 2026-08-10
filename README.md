# CA Firm MIS Backend

Backend API for CA firm compliance tracking and management.

## Tech Stack

- **Backend**: FastAPI 0.109.0 (Python 3.11+)
- **ORM**: SQLAlchemy 2.0.25
- **Database**: PostgreSQL 16
- **Migrations**: Alembic 1.13.1
- **Validation**: Pydantic v2
- **Container**: Docker + Docker Compose

## Prerequisites

- Docker Desktop
- Docker Compose v2+

## Setup

```bash
git clone <repository-url>
cd ca-firm-mis-backend
docker compose up --build
```

Database will auto-migrate on startup. Seed data can be loaded via:

```bash
curl -X POST http://localhost:8000/seed
```

## API Documentation

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/health

## Features

### Client Management
- Create, read, update, delete clients
- Track entity type, PAN, GSTIN, contact details, partner in charge
- Unique constraints on PAN and GSTIN

### Compliance Task Management
- Full CRUD for compliance tasks
- Task types: GSTR-3B, GSTR-1, TDS, GST Quarterly, Income Tax Audit, ROC Filing
- Status tracking: Not Started, In Progress, Awaiting Client, Filed
- Multi-criteria filtering: client, assignee, status, type, date range

### Document Checklists
- Per-task document tracking
- Mark documents as received or pending
- Document templates per task type

### Dashboard Views
- **Due This Week**: Tasks with due dates in next 7 days
- **Overdue**: Past due tasks not yet filed
- **Awaiting Client**: Tasks blocked on client input
- **Workload**: Task counts per assignee

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
```

### Dashboards
```
GET /tasks/dashboard/due-this-week      Tasks due in next 7 days
GET /tasks/dashboard/overdue             Past due, not filed
GET /tasks/dashboard/awaiting-client     Tasks awaiting client
GET /tasks/dashboard/workload            Task counts per assignee
```

### Documents
```
POST   /tasks/{task_id}/documents    Add document to task
GET    /tasks/{task_id}/documents    List task documents
PATCH  /documents/{id}               Update received status
DELETE /documents/{id}               Delete document
```

## Data Model

```
clients (PK: id)
├── name, entity_type, pan, gstin
├── contact_name, contact_email, contact_phone
├── partner_in_charge
└── timestamps

compliance_tasks (PK: id, FK: client_id)
├── task_type, period_label
├── due_date, assignee, status
└── timestamps

task_documents (PK: id, FK: task_id)
├── document_name
├── is_received
└── timestamp
```

**Relationships**:
- Client → Tasks (one-to-many, CASCADE DELETE)
- Task → Documents (one-to-many, CASCADE DELETE)

**Indexes**: Primary keys, foreign keys, pan, gstin, task_type, due_date, assignee, status

## Example Usage

```bash
# List all clients
curl http://localhost:8000/clients

# Filter tasks by status
curl "http://localhost:8000/tasks?status=Awaiting%20Client"

# Get overdue tasks
curl http://localhost:8000/tasks/dashboard/overdue

# Get workload distribution
curl http://localhost:8000/tasks/dashboard/workload

# Create client
curl -X POST http://localhost:8000/clients \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test Company Ltd",
    "entity_type": "Company",
    "pan": "TESTC1234T",
    "partner_in_charge": "Rajesh Kumar"
  }'
```

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
docker compose logs -f db
```

### Access Database
```bash
docker exec -it ca_firm_mis_db psql -U postgres -d ca_firm_mis
```

## Seed Data

The seed script creates:
- 18 clients across 5 entity types
- 65 compliance tasks across 6 task types
- 150+ document items (2-5 per task)
- Realistic distribution of statuses and assignees

## Project Structure

```
backend/
├── app/
│   ├── main.py              FastAPI app
│   ├── config.py            Settings
│   ├── database.py          DB connection
│   ├── models.py            SQLAlchemy models
│   ├── schemas.py           Pydantic schemas
│   ├── seed.py              Data seeding
│   └── routers/
│       ├── clients.py       Client endpoints
│       ├── tasks.py         Task endpoints + dashboards
│       └── documents.py     Document endpoints
├── alembic/                 Database migrations
├── Dockerfile               Container definition
└── requirements.txt         Python dependencies
```

## Assumptions

- No authentication/authorization (internal use)
- No billing module
- No government portal integration
- Recurring task rules encoded as constants (can be moved to DB)
- Single-tenant architecture
- CORS allows all origins (adjust for production)

## Future Enhancements

- Automated recurring task generation (scheduled jobs)
- Email/Slack notifications for due dates
- Document file upload and storage
- Audit trail for task changes
- Role-based access control
- Task assignment workflow
- Client portal for document submission
- Reporting and analytics
- Government portal API integration

## License

Internal use only
