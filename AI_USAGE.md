# AI Usage & Transparency Log

This document provides a transparent, detailed breakdown of how AI coding tools were utilized throughout the development of the CA Firm MIS project, including mistakes made by AI, human corrections, and areas requiring human domain expertise.

---

## AI Tools Utilized

- **Antigravity / Gemini 3.6** (Primary Agentic Assistant)
- **Kiro / Claude Sonnet 4.5 & 4.6** (Code generation, planning, refactoring)

---

## Development Contribution Breakdown

| Component | AI Role | Human Developer Role |
|-----------|---------|----------------------|
| **Architecture & DB Schema** | Generated initial SQLAlchemy models (`Client`, `ComplianceTask`, `TaskDocument`) and Alembic setup. | Designed relational constraints, foreign keys with `ON DELETE CASCADE`, unique PAN/GSTIN indexes, and database sequence reset strategy. |
| **CRUD & Core APIs** | Generated FastAPI boilerplate endpoints, router structures, and Pydantic request/response validation schemas. | Fixed route ordering conflict, added transactional rollback exception handling, and resolved Pydantic v2 undefined forward reference bugs. |
| **Recurring Task Engine** | Provided initial logic structure for period label formatting and due date calculation offset logic. | Formulated business rules for Indian CA compliance (GSTR-3B, GSTR-1, TDS, GST Quarterly, Income Tax Audit, ROC) and designed composite key idempotency logic (`client_id` + `task_type` + `period_label`). |
| **Dashboard Aggregations** | Generated basic SQLAlchemy queries for overdue and status filtering. | Designed consolidated `GET /tasks/dashboard` payload format combining summary counts, metric lists, and multi-status workload breakdown per assignee. |
| **Frontend UI (React + Vite)** | Scaffolded React components, Tailwind layout structures, and API fetching boilerplate. | Engineered expandable document checklist panel, integrated inline status drop-downs, connected modal forms, and set up Docker environment variable injection. |
| **Docker & Deployment** | Created initial single-stage Dockerfile and docker-compose.yml configuration. | Converted backend Dockerfile to separate `/start.sh` execution script (preventing volume mount shadowing) and built multi-stage frontend Dockerfile serving production static bundle via Nginx. |

---

## Log of AI Mistakes & Human Corrections

### 1. Pydantic v2 Forward Reference Crash
- **AI Mistake**: Placed nested response schemas (`ComplianceTaskWithClient`, `ComplianceTaskWithDocuments`) before `ClientResponse` definition in `schemas.py`.
- **Impact**: Server crashed on startup with `PydanticUndefinedAnnotation`.
- **Human Fix**: Reordered Pydantic schema classes strictly in order of dependency resolution so referenced base schemas precede dependent models.

### 2. Docker Host Volume Shadowing `/app/start.sh`
- **AI Mistake**: Generated `COPY start.sh /app/start.sh` inside Dockerfile while `docker-compose.yml` mounted host `./backend` to container `/app`.
- **Impact**: Host directory shadowed container files, causing `exec /app/start.sh: no such file or directory`.
- **Human Fix**: Moved startup script outside the mounted volume path to `/start.sh` in the root container filesystem.

### 3. SQLAlchemy 2.0 Raw Text Query Failure
- **AI Mistake**: Executed raw string `db.execute("TRUNCATE TABLE...")` during seed sequence reset.
- **Impact**: SQLAlchemy 2.0 raised `ObjectNotExecutableError` requiring explicit `text()` encapsulation.
- **Human Fix**: Wrapped all raw SQL queries with `from sqlalchemy import text` calls.

### 4. Database ID Sequence Desynchronization
- **AI Mistake**: Used simple `db.query(Model).delete()` in seed script without resetting PostgreSQL auto-increment sequences.
- **Impact**: Hardcoded test IDs in automated test scripts (`test_api.sh`) failed after multiple re-seeds.
- **Human Fix**: Implemented `TRUNCATE TABLE task_documents, compliance_tasks, clients RESTART IDENTITY CASCADE;` raw query to guarantee clean ID sequences starting at 1.

### 5. FastAPI Router Route Ordering Conflict
- **AI Mistake**: Placed `@router.get("/dashboard")` route after `@router.get("/{task_id}")` in `tasks.py`.
- **Impact**: Requests to `/tasks/dashboard` were matched by `/{task_id}`, attempting to parse string `"dashboard"` as an integer ID and returning HTTP 422 error.
- **Human Fix**: Re-ordered FastAPI routes so specific static paths (`/dashboard`, `/dashboard/*`) precede parameterized wildcard paths (`/{task_id}`).

### 6. Vite Build Environment Variable Injection Failure
- **AI Mistake**: Attempted to pass `VITE_API_URL` as a container runtime environment variable in `docker-compose.yml`.
- **Impact**: Vite embeds client environment variables at **build time**, causing client API calls to default to undefined inside containerized Nginx.
- **Human Fix**: Updated frontend `Dockerfile` to accept `ARG VITE_API_URL` and passed it under build `args` in `docker-compose.yml`.

---

## Developer Ownership & Verification Summary

All AI-generated outputs were critically reviewed, modified, and validated through empirical testing:
- **Automated Test Suite**: Executed `./test_api.sh` verifying 20/20 test cases pass cleanly.
- **End-to-End Environment Test**: Validated full Docker Compose stack lifecycle (`docker compose up --build`, seed execution, and browser interaction at `localhost:3000`).
