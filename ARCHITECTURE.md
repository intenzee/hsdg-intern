# 🏗️ System Architecture

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         CLIENT LAYER                            │
│  (Browser, curl, Postman, Future Frontend Application)         │
└────────────────────────────┬────────────────────────────────────┘
                             │ HTTP/REST
                             │ Port 8000
┌────────────────────────────▼────────────────────────────────────┐
│                      DOCKER CONTAINER: API                      │
│  ┌───────────────────────────────────────────────────────────┐ │
│  │                   FastAPI Application                     │ │
│  │                                                           │ │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐     │ │
│  │  │   Routers   │  │   Schemas   │  │    Models   │     │ │
│  │  │ (clients.py)│◄─┤  (Pydantic) │─►│(SQLAlchemy) │     │ │
│  │  │  (tasks.py) │  │ Validation  │  │   ORM       │     │ │
│  │  │  (docs.py)  │  └─────────────┘  └──────┬──────┘     │ │
│  │  └─────────────┘                           │            │ │
│  │        │                                    │            │ │
│  │        │                            ┌───────▼──────┐    │ │
│  │        │                            │   Database   │    │ │
│  │        │                            │   Session    │    │ │
│  │        │                            └───────┬──────┘    │ │
│  │        │                                    │            │ │
│  └────────┼────────────────────────────────────┼────────────┘ │
│           │                                    │              │
│           │ OpenAPI/Swagger                    │ SQLAlchemy  │
│           │ Auto-Documentation                 │ Connection  │
└───────────┼────────────────────────────────────┼──────────────┘
            │                                    │
            ▼                                    ▼
    ┌───────────────┐              ┌─────────────────────────────┐
    │   /docs       │              │ DOCKER CONTAINER: DATABASE  │
    │   /redoc      │              │                             │
    │ (Swagger UI)  │              │    PostgreSQL 16            │
    │               │              │                             │
    └───────────────┘              │  ┌─────────────────────┐   │
                                   │  │   clients           │   │
                                   │  │   compliance_tasks  │   │
                                   │  │   task_documents    │   │
                                   │  └─────────────────────┘   │
                                   │                             │
                                   │  Volume: postgres_data      │
                                   │  (Persistent Storage)       │
                                   └─────────────────────────────┘
```

---

## Application Layer Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        FastAPI Application                      │
│                            (main.py)                            │
└──────────┬──────────────────────────────────────────────────────┘
           │
           ├── Routers Layer (API Endpoints)
           │   ├── clients.py    (Client CRUD)
           │   ├── tasks.py      (Task CRUD + Dashboards)
           │   └── documents.py  (Document Management)
           │
           ├── Schemas Layer (Validation)
           │   ├── ClientCreate, ClientUpdate, ClientResponse
           │   ├── TaskCreate, TaskUpdate, TaskResponse
           │   └── DocumentCreate, DocumentUpdate, DocumentResponse
           │
           ├── Models Layer (Database ORM)
           │   ├── Client (clients table)
           │   ├── ComplianceTask (compliance_tasks table)
           │   └── TaskDocument (task_documents table)
           │
           ├── Database Layer (Connection)
           │   ├── engine (SQLAlchemy connection)
           │   ├── SessionLocal (session factory)
           │   └── get_db() (dependency injection)
           │
           ├── Config Layer (Settings)
           │   └── Settings (environment variables)
           │
           └── Seed Layer (Data Population)
               └── seed.py (generate test data)
```

---

## Data Flow

### Request Flow (Create Task Example)

```
1. Client Request
   POST /tasks
   {
     "client_id": 1,
     "task_type": "GSTR-3B",
     "period_label": "Aug 2026",
     "due_date": "2026-09-20",
     "assignee": "Vikram Singh",
     "status": "Not Started"
   }
   │
   ▼
2. Router (tasks.py)
   @router.post("/tasks")
   def create_task(task: ComplianceTaskCreate, db: Session)
   │
   ▼
3. Pydantic Validation (schemas.py)
   ComplianceTaskCreate schema validates:
   - client_id is integer
   - task_type is non-empty string
   - due_date is valid date
   - status is valid enum
   │
   ▼
4. Business Logic (tasks.py)
   - Check if client exists
   - Validate status is in allowed list
   │
   ▼
5. Database Operation (SQLAlchemy)
   db_task = ComplianceTask(**task.dict())
   db.add(db_task)
   db.commit()
   db.refresh(db_task)
   │
   ▼
6. Response
   Return ComplianceTaskResponse(
     id=1,
     client_id=1,
     task_type="GSTR-3B",
     ...
     created_at="2026-08-11T10:00:00",
     updated_at="2026-08-11T10:00:00"
   )
```

### Query Flow (Dashboard Example)

```
1. Client Request
   GET /tasks/dashboard/overdue
   │
   ▼
2. Router (tasks.py)
   @router.get("/dashboard/overdue")
   def get_overdue_tasks(db: Session)
   │
   ▼
3. Database Query
   db.query(ComplianceTask).filter(
     and_(
       ComplianceTask.due_date < today,
       ComplianceTask.status != "Filed"
     )
   ).all()
   │
   ▼
4. Relationship Loading (SQLAlchemy)
   Automatically loads related Client data
   via foreign key relationship
   │
   ▼
5. Response Serialization (Pydantic)
   ComplianceTaskWithClient schema
   converts ORM objects to JSON
   │
   ▼
6. Response
   [
     {
       "id": 5,
       "client": {"id": 2, "name": "Tech Corp", ...},
       "task_type": "GSTR-3B",
       "due_date": "2026-08-01",
       "status": "In Progress",
       ...
     },
     ...
   ]
```

---

## Database Schema Relationships

```
┌─────────────────────────────────────┐
│           clients                   │
│  ─────────────────────────────────  │
│  id (PK)                           │
│  name                              │
│  entity_type                       │
│  pan (UNIQUE)                      │
│  gstin (UNIQUE)                    │
│  contact_name                      │
│  contact_email                     │
│  contact_phone                     │
│  partner_in_charge                 │
│  created_at                        │
│  updated_at                        │
└──────────────┬──────────────────────┘
               │
               │ One-to-Many
               │ CASCADE DELETE
               ▼
┌─────────────────────────────────────┐
│       compliance_tasks              │
│  ─────────────────────────────────  │
│  id (PK)                           │
│  client_id (FK) ───────────────────┼─── References clients.id
│  task_type                         │
│  period_label                      │
│  due_date                          │
│  assignee                          │
│  status                            │
│  created_at                        │
│  updated_at                        │
└──────────────┬──────────────────────┘
               │
               │ One-to-Many
               │ CASCADE DELETE
               ▼
┌─────────────────────────────────────┐
│        task_documents               │
│  ─────────────────────────────────  │
│  id (PK)                           │
│  task_id (FK) ─────────────────────┼─── References compliance_tasks.id
│  document_name                     │
│  is_received                       │
│  created_at                        │
└─────────────────────────────────────┘
```

---

## API Endpoint Organization

```
FastAPI App (main.py)
│
├── Root Endpoints
│   ├── GET  /              (API info)
│   ├── GET  /health        (health check)
│   └── POST /seed          (database seeding)
│
├── Client Router (clients.py)
│   ├── POST   /clients           (create)
│   ├── GET    /clients           (list with pagination)
│   ├── GET    /clients/{id}      (get one)
│   ├── PUT    /clients/{id}      (update)
│   └── DELETE /clients/{id}      (delete)
│
├── Task Router (tasks.py)
│   ├── POST   /tasks             (create)
│   ├── GET    /tasks             (list/filter)
│   ├── GET    /tasks/{id}        (get one with documents)
│   ├── PUT    /tasks/{id}        (update)
│   ├── DELETE /tasks/{id}        (delete)
│   │
│   └── Dashboard Sub-routes
│       ├── GET /tasks/dashboard/due-this-week
│       ├── GET /tasks/dashboard/overdue
│       ├── GET /tasks/dashboard/awaiting-client
│       └── GET /tasks/dashboard/workload
│
└── Document Router (documents.py)
    ├── POST   /tasks/{task_id}/documents  (create)
    ├── GET    /tasks/{task_id}/documents  (list)
    ├── PATCH  /documents/{id}             (update status)
    └── DELETE /documents/{id}             (delete)
```

---

## Dependency Injection Pattern

```
FastAPI Request
│
├── Dependency: get_db()
│   │
│   ├── Creates SessionLocal()
│   ├── Yields database session
│   └── Closes session after request
│
└── Endpoint Handler
    │
    ├── Receives db: Session
    ├── Performs database operations
    └── Returns response

Example:
@router.get("/clients")
def list_clients(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)  ◄─── Dependency injection
):
    clients = db.query(Client).offset(skip).limit(limit).all()
    return clients
```

---

## Error Handling Flow

```
Request
│
├── Pydantic Validation Error
│   ├── 422 Unprocessable Entity
│   └── Detailed field-level errors
│
├── Business Logic Error
│   ├── 404 Not Found (resource doesn't exist)
│   ├── 400 Bad Request (invalid input)
│   └── 409 Conflict (constraint violation)
│
├── Database Error
│   ├── IntegrityError → 400 Bad Request
│   └── OperationalError → 500 Internal Server Error
│
└── Uncaught Exception
    └── 500 Internal Server Error
```

---

## Docker Architecture

```
Docker Compose
│
├── Network: default
│   │
│   ├── Service: db
│   │   ├── Image: postgres:16
│   │   ├── Container: ca_firm_mis_db
│   │   ├── Port: 5432:5432
│   │   ├── Volume: postgres_data:/var/lib/postgresql/data
│   │   └── Health Check: pg_isready
│   │
│   └── Service: api
│       ├── Build: ./backend/Dockerfile
│       ├── Container: ca_firm_mis_api
│       ├── Port: 8000:8000
│       ├── Depends On: db (healthy)
│       ├── Environment: DATABASE_URL
│       └── Startup:
│           ├── 1. Wait for database
│           ├── 2. Run Alembic migrations
│           └── 3. Start Uvicorn server
│
└── Volume: postgres_data (persistent storage)
```

---

## Migration Strategy

```
Code Change
│
├── 1. Update Models (models.py)
│   └── Add/modify SQLAlchemy model classes
│
├── 2. Generate Migration
│   └── alembic revision --autogenerate -m "description"
│
├── 3. Review Migration
│   └── Check alembic/versions/xxx_description.py
│
├── 4. Apply Migration
│   └── alembic upgrade head
│
└── 5. Verify Schema
    └── Check database tables
```

---

## Security Layers

```
Request
│
├── Input Validation (Pydantic)
│   ├── Type checking
│   ├── Field validation
│   └── Length constraints
│
├── SQL Injection Prevention (SQLAlchemy ORM)
│   ├── Parameterized queries
│   └── No raw SQL with user input
│
├── Foreign Key Constraints (Database)
│   ├── Referential integrity
│   └── Cascade delete rules
│
└── Error Message Sanitization
    ├── No stack traces to client
    └── Generic error messages
```

---

## Performance Optimizations

```
Database Layer
│
├── Indexes
│   ├── Primary keys (id columns)
│   ├── Foreign keys (client_id, task_id)
│   ├── Query fields (status, due_date, assignee)
│   └── Unique constraints (pan, gstin)
│
├── Connection Pooling
│   └── SQLAlchemy engine with pool_pre_ping
│
├── Query Optimization
│   ├── Eager loading (relationships)
│   ├── Pagination (skip/limit)
│   └── Filtered queries (WHERE clauses)
│
└── Database Constraints
    └── Enforce at DB level (not just app)
```

---

## Scalability Considerations

### Current Architecture
- Single API container
- Single database container
- Synchronous request handling

### Future Scaling Options

```
Horizontal Scaling
│
├── Load Balancer
│   │
│   ├── API Instance 1
│   ├── API Instance 2
│   └── API Instance N
│       │
│       └── Database (shared)
│
├── Database Scaling
│   ├── Read replicas
│   ├── Connection pooling (PgBouncer)
│   └── Caching layer (Redis)
│
└── Async Operations
    ├── Task queue (Celery)
    ├── Background jobs
    └── Async SQLAlchemy
```

---

## Monitoring Points (Future)

```
Application Monitoring
│
├── Health Endpoints
│   └── GET /health (current)
│
├── Metrics (Future)
│   ├── Request rate
│   ├── Response time
│   ├── Error rate
│   └── Database query time
│
├── Logging (Future)
│   ├── Structured logs
│   ├── Request/response logs
│   └── Error logs
│
└── Alerting (Future)
    ├── High error rate
    ├── Slow response times
    └── Database connection failures
```

---

## Tech Stack Summary

```
┌─────────────────────────────────────────┐
│         Application Layer               │
│  ─────────────────────────────────────  │
│  FastAPI 0.109.0                       │
│  Pydantic 2.5.3                        │
│  Python 3.11+                          │
└──────────────┬──────────────────────────┘
               │
┌──────────────▼──────────────────────────┐
│            ORM Layer                    │
│  ─────────────────────────────────────  │
│  SQLAlchemy 2.0.25                     │
│  Alembic 1.13.1                        │
└──────────────┬──────────────────────────┘
               │
┌──────────────▼──────────────────────────┐
│         Database Layer                  │
│  ─────────────────────────────────────  │
│  PostgreSQL 16                         │
│  psycopg2-binary 2.9.9                 │
└──────────────┬──────────────────────────┘
               │
┌──────────────▼──────────────────────────┐
│      Infrastructure Layer               │
│  ─────────────────────────────────────  │
│  Docker + Docker Compose               │
│  Uvicorn (ASGI server)                 │
└─────────────────────────────────────────┘
```

---

This architecture provides:
✅ Clean separation of concerns
✅ Easy to test and maintain
✅ Scalable foundation
✅ Production-ready patterns
✅ Security by design
