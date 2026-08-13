# AI Usage Documentation

This project was developed with AI assistance. This document provides transparency about the development process.

## AI Tools Used

- Kiro
- Antigravity
- Claude Sonnet 4.5

## Development Process

### Areas Where AI Was Used

#### 1. Project Structure
- Initial FastAPI project setup
- Docker and Docker Compose configuration
- Alembic migration setup
- Directory structure organization

#### 2. Database Models
- SQLAlchemy model definitions
- Relationship configurations
- Index definitions
- Cascade delete rules

#### 3. API Endpoints
- CRUD endpoint implementations
- Request/response schemas
- Error handling patterns
- Dashboard query logic

#### 4. Data Generation
- Seed script structure
- Realistic test data generation
- Document template definitions

#### 5. Documentation
- README structure
- API documentation
- Setup instructions

### Human Review and Modifications

- Reviewed all database relationships for correctness
- Modified error messages for clarity
- Adjusted seed data for realism
- Verified business logic against CA firm workflows
- Tested all endpoints manually


## Issues Encountered

### Issue 1: Docker Volume Mount Shadowing
**AI Generated**: The Dockerfile created a startup script directly at `/app/start.sh` during the build phase, and set `CMD ["/app/start.sh"]`.
**Problem**: In `docker-compose.yml`, the host directory `./backend` was mounted directly to `/app` inside the container. This runtime mount shadowed the `/app` folder created during the build, hiding the generated `start.sh` script and causing the container to crash on startup.
**Fix Applied**: Relocated the startup script generation path in the `Dockerfile` to `/start.sh` (outside the `/app` directory), which prevented it from being masked by the volume mount.

### Issue 2: Pydantic Forward Reference crash
**AI Generated**: Defined response schemas with `List["TaskDocumentResponse"]` as a forward reference annotation, but defined the `TaskDocumentResponse` schema class at the bottom of `schemas.py`.
**Problem**: The application crashed on startup with `PydanticUndefinedAnnotation` because the forward reference could not be resolved at the time Pydantic initialized the schema metadata.
**Fix Applied**: Reordered the schema classes in `schemas.py` so that `TaskDocumentResponse` is defined sequentially before `ComplianceTaskWithDocuments`, which references it.

### Issue 3: SQLAlchemy 2.0 Raw SQL Execution Error
**AI Generated**: The `/health` endpoint checked the database connection using `db.execute("SELECT 1")`.
**Problem**: Under SQLAlchemy 2.0, passing raw SQL strings directly to `.execute()` is deprecated and raises an error. The endpoint returned an unhealthy status.
**Fix Applied**: Imported `text` from `sqlalchemy` and wrapped the query explicitly: `db.execute(text("SELECT 1"))`.

### Issue 4: Database Seed Autoincrement Sequence Issue
**AI Generated**: The `seed.py` database clearing logic used simple model `.delete()` calls.
**Problem**: Delete calls do not reset the auto-increment primary key sequence generators in PostgreSQL. Seeding the database multiple times caused client/task IDs to exceed `1` (e.g. starting at `19`, `66`), which broke the test suite (`test_api.sh`) which expected hardcoded IDs starting at `1`.
**Fix Applied**: Updated `seed.py` to run raw SQL TRUNCATE statements with `RESTART IDENTITY CASCADE` to reset the sequence generators whenever the database is seeded.

## Testing and Validation

### Manual and Automated Testing
- Tested health check, root, and documentation endpoints.
- Verified all client endpoints (`GET /clients`, `POST /clients`, `GET /clients/{id}`, `PUT /clients/{id}`, `DELETE /clients/{id}`).
- Verified all task endpoints including status filtering and assignee filtering.
- Validated dashboard query endpoints (due this week, overdue, awaiting client, and workload distribution).
- Verified document addition, list, and status update endpoints.
- Checked error handling and constraints (e.g., trying to create clients with invalid types/names or creating tasks for non-existent clients).

### Code Review
- Reviewed all model relationships
- Verified foreign key constraints
- Checked error handling
- Validated business logic

## What AI Did Well

- Rapid bootstrapping of the initial FastAPI app structure, routers, and DB configuration.
- Boilerplate code generation (SQLAlchemy models and schemas).
- Consistent code patterns and RESTful routing design.
- Documentation structure and quick reference setup.

## What Required Human Expertise

- Debugging and fixing container build runtime conflicts (the volume shadowing problem).
- Diagnosing database connection check faults with SQLAlchemy 2.0.
- Resolving forward reference dependency orders in Pydantic models.
- Understanding CA firm workflows and verifying compliance task business logic.
- Building the automated testing script to ensure high endpoint reliability.

## Code Quality Assessment

### Strengths
- Clear Separation of Concerns (Routers, Schemas, Models, Seeds).
- Dynamic reload and containerized development environment.
- Standardized error handling and detailed response types.

### Areas for Improvement
- Adding more granular schema validations for PAN/GSTIN formats.
- Integrating Alembic migrations seamlessly during compose up (currently ran automatically on start).

## Lessons Learned

### About AI-Assisted Development
- AI is highly effective for bootstrapping boilerplate, but requires a strong developer's oversight to resolve orchestration and runtime-specific errors (like Docker mount issues).

### About the Tech Stack
- Learned the strict difference in SQLAlchemy 2.0 query syntax (using `text()` wrappers for query strings).
- Gained a deeper understanding of how Docker mounts interact with filesystem state defined during the image build phase.

### About CA Firm Requirements
- CA firms have complex, date-based recurring rules that are best managed by clean, well-tested database entities rather than unstructured spreadsheets.

## Honesty Statement

This document represents an honest assessment of AI contribution to this project. The code was reviewed, tested, and modified as needed to ensure correctness and alignment with requirements.

**Developer**: Tanmay Roy
**Date**: 2026-08-11
**AI Tool(s)**: Kiro, Antigravity, Claude

---

## Notes for Evaluators

This project demonstrates:
1. Effective use of AI for development acceleration
2. Critical human review and validation
3. Understanding of when to rely on AI vs human expertise
4. Ability to identify and fix AI-generated issues
5. Honest documentation of the development process

---

## Day 2 — Extensions (Recurring Tasks, Dashboard, Frontend)

### Areas Where AI Was Used

#### 6. Recurrence Engine (`backend/app/recurrence.py`)
- AI generated the Python config-based recurrence rules dict structure
- AI implemented `get_period_label()` and `get_due_date()` helper functions
- AI suggested the round-robin assignee assignment approach for auto-generated tasks

#### 7. Task Generation Endpoint (`backend/app/routers/generate.py`)
- AI implemented the `POST /tasks/generate` endpoint structure
- AI implemented the idempotency check using `(client_id, task_type, period_label)` as a composite key
- AI correctly used `db.flush()` to get the task ID before the commit (for document creation)

#### 8. Consolidated Dashboard Endpoint (`backend/app/routers/tasks.py`)
- AI implemented the `GET /tasks/dashboard` endpoint with all 4 metric queries
- AI aggregated per-assignee status breakdowns using a two-pass approach (query → dict → list)

#### 9. Frontend (`frontend/`)
- AI scaffolded the React+Vite project structure
- AI implemented the centralized `api.js` module with VITE_API_URL env var support
- AI generated the Dashboard, Tasks, and Clients page components
- AI wrote the multi-stage frontend Dockerfile (Node build → nginx serve)
- AI updated the docker-compose.yml to add the frontend service

---

### Day 2 Issues Encountered

### Issue 5: FastAPI Route Ordering Conflict
**AI Generated**: Added `GET /tasks/dashboard` after `GET /tasks/{task_id}` in the same router.
**Problem**: FastAPI matched requests to `/tasks/dashboard` against the `/{task_id}` route first, treating `"dashboard"` as an integer task ID and returning a Pydantic validation error (`Input should be a valid integer`).
**Fix Applied**: Rewrote `tasks.py` to place all `/dashboard/*` and `/dashboard` routes ABOVE the `/{task_id}` parameterized route. Specific routes must always precede wildcard/parameterized ones in FastAPI.

### Issue 6: Vite Build Not Injecting API URL at Runtime
**AI Generated**: Suggested using `process.env.VITE_API_URL` in the frontend.
**Problem**: Vite replaces `import.meta.env.VITE_API_URL` at build time (not runtime), so the API URL must be provided as a Docker build arg (`VITE_API_URL`), not a container runtime env var.
**Fix Applied**: Passed `VITE_API_URL` as an `ARG` in the Dockerfile and set it as an `ENV` before the build step. In docker-compose.yml, it is set under `args` (not `environment`) for the frontend build.

---

### Day 2 What Required Human Expertise

- Recognizing the FastAPI route ordering issue (required understanding of how FastAPI resolves routes)
- Choosing config-based recurrence rules over a DB table (simpler for this scope, easier to demo)
- Deciding that `VITE_API_URL=http://localhost:8000` is correct for a single-machine Docker setup (browser calls host, not container name)
- Reviewing all idempotency logic to ensure the composite key check was correct

