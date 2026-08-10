# System Architecture

## High-Level Architecture

```
Client Layer (Browser/curl/Postman)
           ↓
    FastAPI Application
    (Port 8000)
           ↓
    SQLAlchemy ORM
           ↓
    PostgreSQL Database
    (Port 5432, Docker Volume)
```

## Application Structure

```
FastAPI App (main.py)
│
├── Routers
│   ├── clients.py    (Client CRUD)
│   ├── tasks.py      (Task CRUD + Dashboards)
│   └── documents.py  (Document management)
│
├── Schemas (Pydantic v2)
│   ├── Request validation
│   └── Response serialization
│
├── Models (SQLAlchemy)
│   ├── Client
│   ├── ComplianceTask
│   └── TaskDocument
│
├── Database
│   ├── Engine (connection pool)
│   ├── SessionLocal (session factory)
│   └── get_db() (dependency injection)
│
└── Config
    └── Settings (environment variables)
```

## Database Schema

```
clients (PK: id)
    ↓ (1:N, CASCADE DELETE)
compliance_tasks (PK: id, FK: client_id)
    ↓ (1:N, CASCADE DELETE)
task_documents (PK: id, FK: task_id)
```

### Indexes
- Primary keys: All tables
- Foreign keys: client_id, task_id
- Query optimization: pan, gstin, task_type, due_date, assignee, status

## Request Flow

```
1. HTTP Request
   ↓
2. FastAPI Router
   ↓
3. Pydantic Validation
   ↓
4. Business Logic
   ↓
5. SQLAlchemy ORM
   ↓
6. PostgreSQL
   ↓
7. Response Serialization
   ↓
8. HTTP Response
```

## Error Handling

- **422**: Pydantic validation errors
- **404**: Resource not found
- **400**: Business logic errors, constraint violations
- **500**: Server errors

## Docker Architecture

```
Docker Compose
│
├── Service: db
│   ├── Image: postgres:16
│   ├── Volume: postgres_data (persistent)
│   └── Port: 5432
│
└── Service: api
    ├── Build: backend/Dockerfile
    ├── Depends on: db (with health check)
    ├── Port: 8000
    └── Startup:
        1. Wait for database
        2. Run Alembic migrations
        3. Start Uvicorn server
```

## API Endpoints

### Clients (5 endpoints)
- POST /clients
- GET /clients
- GET /clients/{id}
- PUT /clients/{id}
- DELETE /clients/{id}

### Tasks (5 endpoints)
- POST /tasks
- GET /tasks (with filters)
- GET /tasks/{id}
- PUT /tasks/{id}
- DELETE /tasks/{id}

### Dashboards (4 endpoints)
- GET /tasks/dashboard/due-this-week
- GET /tasks/dashboard/overdue
- GET /tasks/dashboard/awaiting-client
- GET /tasks/dashboard/workload

### Documents (4 endpoints)
- POST /tasks/{task_id}/documents
- GET /tasks/{task_id}/documents
- PATCH /documents/{id}
- DELETE /documents/{id}

### System (3 endpoints)
- GET / (API info)
- GET /health (health check)
- POST /seed (dev only)

## Technology Stack

| Layer | Technology |
|-------|-----------|
| API Framework | FastAPI 0.109.0 |
| Validation | Pydantic v2.5.3 |
| ORM | SQLAlchemy 2.0.25 |
| Database | PostgreSQL 16 |
| Migrations | Alembic 1.13.1 |
| Server | Uvicorn (ASGI) |
| Container | Docker + Docker Compose |

## Security Features

- Input validation (Pydantic)
- SQL injection prevention (ORM parameterization)
- Foreign key constraints
- Type safety throughout
- Error message sanitization

## Performance Optimizations

- Database connection pooling
- Strategic indexes
- Query optimization (filters, pagination)
- Foreign key indexes
- Eager loading for relationships

## Scalability Considerations

### Current
- Single API container
- Single database container
- Synchronous request handling

### Future
- Horizontal API scaling (load balancer)
- Database read replicas
- Connection pooling (PgBouncer)
- Caching layer (Redis)
- Async SQLAlchemy
- Task queue (Celery)
