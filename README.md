# CA Firm MIS Backend

A Management Information System (MIS) backend API for CA firms to replace Excel-based compliance tracking with a structured, database-driven solution.

## Tech Stack

- **Backend Framework**: FastAPI 0.109.0 (Python 3.11+)
- **ORM**: SQLAlchemy 2.0.25
- **Database**: PostgreSQL 16
- **Migrations**: Alembic 1.13.1
- **Validation**: Pydantic v2
- **Containerization**: Docker + Docker Compose
- **API Documentation**: OpenAPI (Swagger) + ReDoc

### Why This Stack?

- **FastAPI**: Modern, fast, with automatic API documentation and type checking
- **SQLAlchemy**: Industry-standard ORM with excellent PostgreSQL support
- **PostgreSQL**: Robust relational database with strong ACID guarantees
- **Alembic**: Database migration management for schema evolution
- **Docker**: Ensures consistent environment and single-command setup

## Prerequisites

- Docker Desktop (or Docker + Docker Compose)
- Git

## Setup & Run

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd ca-firm-mis-backend
   ```

2. **Start the application**:
   ```bash
   docker compose up --build
   ```

   This will:
   - Start PostgreSQL database with persistent storage
   - Run database migrations automatically
   - Start the FastAPI server on `http://localhost:8000`

3. **Seed the database** (first time only):
   ```bash
   curl -X POST http://localhost:8000/seed
   ```

   Or visit `http://localhost:8000/docs` and use the `/seed` endpoint.

4. **Access the API**:
   - **API Root**: http://localhost:8000
   - **Interactive Docs**: http://localhost:8000/docs
   - **ReDoc**: http://localhost:8000/redoc
   - **Health Check**: http://localhost:8000/health

## Spec / Requirements

### System Overview

The CA Firm MIS is a backend API that manages compliance tracking for CA (Chartered Accountant) firms. It replaces manual Excel-based tracking with a structured system that ensures data persistence, provides dashboard views, and supports recurring task management.

### Core Features

#### 1. Client Master Management
- Create, read, update, and delete client records
- Store client details: name, entity type, PAN, GSTIN, contact info, partner in charge
- Support for multiple entity types: Individual, Company, LLP, Partnership, Trust
- Unique constraints on PAN and GSTIN

#### 2. Compliance Task Management
- Track compliance tasks per client with:
  - Task type (GSTR-3B, GSTR-1, TDS, Income Tax Audit, ROC Filing, etc.)
  - Period labels (monthly: "Jul 2026", quarterly: "Q2 FY26", annual: "FY 2025-26")
  - Due dates, assignees, and status tracking
  - Status values: Not Started, In Progress, Awaiting Client, Filed
- Advanced filtering by client, assignee, status, task type, and date range

#### 3. Document Checklist Management
- Per-task document tracking
- Mark documents as received or pending
- Document templates per task type (Sales Register, Purchase Register, etc.)

#### 4. Dashboard Views
- **Due This Week**: Tasks with due dates in next 7 days
- **Overdue**: Tasks past due date and not filed
- **Awaiting Client**: Tasks blocked on client input
- **Workload Summary**: Task counts per assignee (excluding filed tasks)

#### 5. Data Persistence & Seeding
- PostgreSQL with Docker volumes for data persistence across restarts
- Seed script creates 15+ realistic clients and 60+ tasks with document checklists
- Realistic distribution of entity types, task types, statuses, and assignees

### Data Model

```
clients (15+ records)
├── id (PK)
├── name, entity_type, pan, gstin
├── contact_name, contact_email, contact_phone
├── partner_in_charge
└── timestamps

compliance_tasks (60+ records)
├── id (PK)
├── client_id (FK → clients.id, CASCADE DELETE)
├── task_type, period_label
├── due_date, assignee, status
└── timestamps

task_documents (150+ records)
├── id (PK)
├── task_id (FK → compliance_tasks.id, CASCADE DELETE)
├── document_name
├── is_received
└── timestamp
```

**Relationships**:
- One client has many tasks (cascade delete)
- One task has many documents (cascade delete)

**Recurring Task Rules** (encoded in code for Day 1):
- Monthly tasks: GSTR-3B (due 20th), GSTR-1 (due 11th), TDS (due 7th)
- Quarterly tasks: GST Quarterly (due 30 days after quarter)
- Annual tasks: Income Tax Audit (Sep 30), ROC Filing (Nov 30)

### API Overview

#### Client Endpoints
- `POST /clients` - Create client
- `GET /clients` - List all clients (with pagination)
- `GET /clients/{id}` - Get single client
- `PUT /clients/{id}` - Update client
- `DELETE /clients/{id}` - Delete client (cascades to tasks)

#### Task Endpoints
- `POST /tasks` - Create task
- `GET /tasks` - List tasks with filters (client_id, assignee, status, task_type, date_from, date_to)
- `GET /tasks/{id}` - Get task with documents
- `PUT /tasks/{id}` - Update task
- `DELETE /tasks/{id}` - Delete task (cascades to documents)

#### Dashboard Endpoints
- `GET /tasks/dashboard/due-this-week` - Tasks due in next 7 days
- `GET /tasks/dashboard/overdue` - Past due, not filed
- `GET /tasks/dashboard/awaiting-client` - Tasks awaiting client
- `GET /tasks/dashboard/workload` - Task counts per assignee

#### Document Endpoints
- `POST /tasks/{task_id}/documents` - Add document to task
- `GET /tasks/{task_id}/documents` - List task documents
- `PATCH /documents/{id}` - Update document received status
- `DELETE /documents/{id}` - Delete document

#### Development Endpoints
- `POST /seed` - Seed database with test data (drops existing data)
- `GET /health` - Health check

## Example API Calls

### List all clients
```bash
curl http://localhost:8000/clients
```

### List all tasks
```bash
curl http://localhost:8000/tasks
```

### Filter tasks by status
```bash
curl "http://localhost:8000/tasks?status=Awaiting%20Client"
```

### Get overdue tasks
```bash
curl http://localhost:8000/tasks/dashboard/overdue
```

### Get tasks due this week
```bash
curl http://localhost:8000/tasks/dashboard/due-this-week
```

### Get workload per assignee
```bash
curl http://localhost:8000/tasks/dashboard/workload
```

### Create a new client
```bash
curl -X POST http://localhost:8000/clients \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test Company Ltd",
    "entity_type": "Company",
    "pan": "ABCDE1234F",
    "gstin": "27ABCDE1234F1Z5",
    "contact_name": "John Doe",
    "contact_email": "john@testcompany.com",
    "contact_phone": "+91 9876543210",
    "partner_in_charge": "Rajesh Kumar"
  }'
```

### Update task status
```bash
curl -X PUT http://localhost:8000/tasks/1 \
  -H "Content-Type: application/json" \
  -d '{
    "status": "Filed"
  }'
```

## Assumptions & Design Decisions

### Assumptions Made

1. **No Authentication/Authorization**: Day 1 focuses on core functionality. Auth would be added using JWT tokens or OAuth2 in production.

2. **No Billing Module**: Client billing is out of scope. The system tracks compliance work, not invoicing.

3. **No Government Portal Integration**: Tasks are tracked internally without actual e-filing integration.

4. **Simplified Recurrence Rules**: Recurring task generation logic is encoded as constants in `models.py`. A future version would have a `recurrence_rules` table and a scheduler.

5. **Single Tenant**: Designed for one CA firm. Multi-tenancy would require partition_key or database-per-tenant.

6. **Simplified Period Labels**: Period labels are free-text strings. A production system might have structured period types.

7. **No File Storage**: Document tracking is metadata only. Actual file uploads would use S3 or similar.

8. **No Audit Trail**: Changes to tasks/clients are not logged. Production would need audit tables.

### Design Decisions

1. **Cascade Deletes**: Deleting a client removes all tasks and documents. This is intentional to maintain referential integrity.

2. **Status Enum**: Task statuses are validated strings rather than database enums for easier extension.

3. **Timestamps**: All entities have `created_at` and `updated_at` for audit purposes.

4. **Indexes**: Added indexes on frequently queried fields (client_id, assignee, status, due_date) for performance.

5. **Seed Endpoint**: Provided as a POST endpoint for convenience during development. Would be removed or protected in production.

6. **Synchronous SQLAlchemy**: Used synchronous sessions for simplicity. Async would improve scalability but adds complexity.

## What I Would Build Next

### Phase 2 - Core Features
1. **Recurring Task Generation**:
   - Endpoint or scheduled job to auto-create monthly/quarterly/annual tasks
   - Configurable recurrence rules per client
   - Duplicate detection based on (client_id, task_type, period_label)

2. **Dashboard Enhancements**:
   - Task trends over time (completed vs pending)
   - Client-level compliance health score
   - Document completion percentage per task
   - Filters and date range selectors for dashboards

3. **Advanced Filtering**:
   - Search by client name or task type
   - Sort by due date, created date, priority
   - Bulk status updates

### Phase 3 - User Management
4. **Authentication & Authorization**:
   - JWT-based authentication
   - Role-based access control (Partner, Manager, Associate, Intern)
   - Assignee-specific views (my tasks, my clients)

### Phase 4 - Integration & Automation
5. **Notifications**:
   - Email/SMS alerts for due dates
   - Slack/Teams integration for task updates
   - Daily/weekly digest emails

6. **File Management**:
   - Document upload with S3/cloud storage
   - Version control for documents
   - Document templates and auto-generation

7. **Reporting**:
   - Excel export of tasks and clients
   - Compliance reports per client
   - Team productivity reports

### Phase 5 - Advanced Features
8. **Frontend Application**:
   - React/Next.js dashboard
   - Mobile-responsive design
   - Real-time updates via WebSocket

9. **Integration**:
   - Government portal APIs (GST, Income Tax, MCA)
   - Accounting software integration (Tally, QuickBooks)
   - Calendar sync (Google Calendar, Outlook)

10. **Analytics**:
    - Task completion trends
    - Assignee performance metrics
    - Client engagement patterns

## Development Notes

### Database Reset

To reset the database:

```bash
# Stop containers
docker compose down

# Remove volume
docker volume rm ca-firm-mis-backend_postgres_data

# Restart
docker compose up --build

# Re-seed
curl -X POST http://localhost:8000/seed
```

### Re-seeding

The `/seed` endpoint drops all existing data and creates fresh seed data. Run it whenever you need to reset to a known state.

### Running Tests

Tests are not included in Day 1 but would be added using:
- **pytest** for unit and integration tests
- **httpx** for async API client testing
- **pytest-cov** for coverage reports

### Code Quality

The codebase follows:
- Type hints throughout
- Pydantic validation for all inputs
- Proper error handling with HTTP status codes
- Clear docstrings on all endpoints
- Separation of concerns (models, schemas, routers)

## Project Structure

```
ca-firm-mis-backend/
├── docker-compose.yml          # Docker orchestration
├── README.md                   # This file
├── AI_USAGE.md                 # AI assistance documentation
└── backend/
    ├── Dockerfile              # Container definition
    ├── requirements.txt        # Python dependencies
    ├── alembic.ini            # Alembic configuration
    ├── alembic/               # Database migrations
    │   ├── env.py
    │   ├── script.py.mako
    │   └── versions/
    │       └── 001_initial_schema.py
    └── app/
        ├── __init__.py
        ├── main.py            # FastAPI app entry point
        ├── config.py          # Configuration management
        ├── database.py        # Database connection
        ├── models.py          # SQLAlchemy models
        ├── schemas.py         # Pydantic schemas
        ├── seed.py            # Database seeding
        └── routers/           # API endpoints
            ├── __init__.py
            ├── clients.py     # Client CRUD
            ├── tasks.py       # Task CRUD + dashboards
            └── documents.py   # Document management
```

## License

This project is for educational/assignment purposes.

## Contact

For questions or feedback about this implementation, please refer to the AI_USAGE.md file for details on how this codebase was developed.
