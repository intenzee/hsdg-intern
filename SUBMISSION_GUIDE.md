# Submission & Evaluator Guide

This document maps all implemented features against the official internship assignment evaluation criteria and provides a step-by-step guide for recording the 5-minute demo video.

---

## 1. Requirement Completion Matrix

| Requirement from Brief | Status | Implementation Details |
|------------------------|--------|------------------------|
| **Client Master** | ✅ **100% Complete** | Add/edit/list/delete clients with PAN, GSTIN, entity type, contact, partner in charge (`/clients` API & UI page). |
| **Compliance Tasks** | ✅ **100% Complete** | Tasks with type, period, due date, assignee, status (`Not Started`, `In Progress`, `Awaiting Client`, `Filed`). |
| **Recurring Task Engine** | ✅ **100% Complete** | Automatic generation of monthly (GSTR-3B, GSTR-1, TDS), quarterly (GST Qtr), and annual (IT Audit, ROC) tasks via `POST /tasks/generate`. Fully idempotent. |
| **Document Checklist** | ✅ **100% Complete** | Per-task document checklist with toggleable received/pending state and dynamic item addition (`▶` drawer in UI & `/documents` API). |
| **Executive Dashboard** | ✅ **100% Complete** | `GET /tasks/dashboard` returning Due This Week, Overdue, Awaiting Client, and Workload per Assignee (broken down by status). |
| **Multi-Criteria Filters** | ✅ **100% Complete** | Filter task list by Client, Assignee, Status, Task Type, and Due Date range. |
| **Real Database** | ✅ **100% Complete** | PostgreSQL 16 database with persistent volume mount (`postgres_data`). Data survives restarts. |
| **Database Seed Script** | ✅ **100% Complete** | `POST /seed` endpoint creates 18 clients, 65 compliance tasks, and 200+ document checklist items with ID sequence reset. |
| **Docker Compose** | ✅ **100% Complete** | Single command `docker compose up --build` starts PostgreSQL, FastAPI backend, and React/Nginx frontend. |
| **Documentation** | ✅ **100% Complete** | Comprehensive `README.md`, `AI_USAGE.md` (transparency log), and `SUBMISSION_GUIDE.md`. |
| **Out of Scope Exclusions** | ✅ **Respected** | Login, billing, and government portal integrations explicitly skipped per assignment guidelines. |

---

## 2. Recommended 5-Minute Video Presentation Script

When recording your 5-minute screen capture, use this structured flow:

### **Part 1: Live Software Demo (2.5 to 3 Minutes)**

1. **Setup & Startup (30s)**
   - Show terminal running `docker compose up --build` and all 3 containers starting (`ca_firm_mis_db`, `ca_firm_mis_api`, `ca_firm_mis_frontend`).
   - Run `curl -X POST http://localhost:8000/seed` to show seed data loading.

2. **Dashboard Overview (1m)**
   - Open [http://localhost:3000](http://localhost:3000) in browser.
   - Point out the 4 summary metric cards (**Due This Week**, **Overdue**, **Awaiting Client**, **Total Open**).
   - Show the **Workload per Assignee** table displaying team breakdown across all statuses.
   - Highlight how this answers *"What needs attention today?"* in one glance.
   - Show the **Generate Recurring Tasks** panel: generate tasks for a period (e.g. August 2026) and show stats update live.

3. **Tasks & Document Checklist (45s)**
   - Navigate to the **Tasks** tab.
   - Demonstrate multi-criteria filtering (e.g. filter by Client or Status).
   - Change a task status via the inline dropdown (e.g. `In Progress` -> `Filed`).
   - Click `▶` on a task row to expand the **Document Checklist drawer**.
   - Check off a document item (mark received) and add a custom document item.

4. **Client Master (30s)**
   - Navigate to the **Clients** tab.
   - Click **+ Add Client**, fill in form (Company name, PAN, Partner), and save.
   - Show inline edit and delete operations.

---

### **Part 2: Code Walkthrough & Technical Discussion (2 Minutes)**

1. **Data Model (`backend/app/models.py`) (30s)**
   - Show `Client` -> `ComplianceTask` -> `TaskDocument` relationships with `cascade="all, delete-orphan"`.
   - Explain PAN & GSTIN unique indexes.

2. **Recurring Task Engine (`backend/app/recurrence.py` & `routers/generate.py`) (45s)**
   - Show rule configuration dict defining compliance frequencies (monthly, quarterly, annual).
   - Explain the idempotency guard checking `(client_id, task_type, period_label)` before insertion.

3. **Consolidated Dashboard API (`backend/app/routers/tasks.py`) (30s)**
   - Show `GET /tasks/dashboard` query logic and path ordering fix (placing static `/dashboard` path before `/{task_id}`).

4. **Code Self-Reflection (15s)**
   - **Most proud of**: Idempotent recurrence engine & clean multi-container Docker setup.
   - **What to improve next**: Add authentication & automated client email reminders.

---

## 3. Submission Checklist

- [x] Repository pushed to GitHub (`intenzee/hsdg-intern`) with meaningful commit history.
- [x] `README.md` contains clear run instructions, stack choices, data model, and evaluator guide.
- [x] `AI_USAGE.md` documents tool usage, AI mistakes, and human corrections.
- [x] `SUBMISSION_GUIDE.md` provides video script & requirement mapping.
- [ ] 5-minute video recorded and link generated (Loom / Google Drive / YouTube).
- [ ] WhatsApp message sent with GitHub repo link + video link.
