# Quick Reference Guide

Fast reference for common operations during development and demo.

## 🚀 Startup Commands

```bash
# First time setup
docker compose up --build

# Seed the database
curl -X POST http://localhost:8000/seed

# Subsequent startups
docker compose up

# Stop everything
docker compose down

# Reset database (warning: deletes all data)
docker compose down -v
docker compose up --build
curl -X POST http://localhost:8000/seed
```

## 🔗 Important URLs

| Service | URL |
|---------|-----|
| API Root | http://localhost:8000 |
| Swagger Docs | http://localhost:8000/docs |
| ReDoc | http://localhost:8000/redoc |
| Health Check | http://localhost:8000/health |
| PostgreSQL | localhost:5432 (user: postgres, pass: postgres, db: ca_firm_mis) |

## 📋 Common API Calls

### Clients

```bash
# List all clients
curl http://localhost:8000/clients

# Get specific client
curl http://localhost:8000/clients/1

# Create client
curl -X POST http://localhost:8000/clients \
  -H "Content-Type: application/json" \
  -d '{
    "name": "New Client Ltd",
    "entity_type": "Company",
    "pan": "NEWCO1234P",
    "partner_in_charge": "Rajesh Kumar"
  }'

# Update client
curl -X PUT http://localhost:8000/clients/1 \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Updated Name",
    "entity_type": "Company",
    "pan": "NEWCO1234P",
    "partner_in_charge": "Rajesh Kumar"
  }'

# Delete client
curl -X DELETE http://localhost:8000/clients/1
```

### Tasks

```bash
# List all tasks
curl http://localhost:8000/tasks

# Filter by client
curl "http://localhost:8000/tasks?client_id=1"

# Filter by status
curl "http://localhost:8000/tasks?status=Awaiting%20Client"

# Filter by assignee
curl "http://localhost:8000/tasks?assignee=Vikram%20Singh"

# Multiple filters
curl "http://localhost:8000/tasks?status=Not%20Started&assignee=Anjali%20Mehta"

# Get specific task with documents
curl http://localhost:8000/tasks/1

# Create task
curl -X POST http://localhost:8000/tasks \
  -H "Content-Type: application/json" \
  -d '{
    "client_id": 1,
    "task_type": "GSTR-3B",
    "period_label": "Aug 2026",
    "due_date": "2026-09-20",
    "assignee": "Vikram Singh",
    "status": "Not Started"
  }'

# Update task status
curl -X PUT http://localhost:8000/tasks/1 \
  -H "Content-Type: application/json" \
  -d '{"status": "Filed"}'

# Delete task
curl -X DELETE http://localhost:8000/tasks/1
```

### Dashboard

```bash
# Tasks due this week
curl http://localhost:8000/tasks/dashboard/due-this-week

# Overdue tasks
curl http://localhost:8000/tasks/dashboard/overdue

# Tasks awaiting client
curl http://localhost:8000/tasks/dashboard/awaiting-client

# Workload per assignee
curl http://localhost:8000/tasks/dashboard/workload
```

### Documents

```bash
# Add document to task
curl -X POST http://localhost:8000/tasks/1/documents \
  -H "Content-Type: application/json" \
  -d '{
    "document_name": "Sales Register",
    "is_received": false
  }'

# List task documents
curl http://localhost:8000/tasks/1/documents

# Mark document as received
curl -X PATCH http://localhost:8000/documents/1 \
  -H "Content-Type: application/json" \
  -d '{"is_received": true}'

# Delete document
curl -X DELETE http://localhost:8000/documents/1
```

## 🔍 Database Access

```bash
# Connect to PostgreSQL
docker exec -it ca_firm_mis_db psql -U postgres -d ca_firm_mis

# Useful SQL queries
SELECT COUNT(*) FROM clients;
SELECT COUNT(*) FROM compliance_tasks;
SELECT COUNT(*) FROM task_documents;

SELECT * FROM clients LIMIT 5;
SELECT * FROM compliance_tasks WHERE status = 'Awaiting Client';
SELECT * FROM task_documents WHERE is_received = false;
```

## 📊 Pretty JSON Output

Add `| jq` to curl commands for formatted output (requires jq installation):

```bash
curl http://localhost:8000/clients | jq

curl http://localhost:8000/tasks/dashboard/workload | jq
```

## 🐛 Debugging

```bash
# View API logs
docker compose logs -f api

# View database logs
docker compose logs -f db

# Restart API only
docker compose restart api

# Execute commands in API container
docker exec -it ca_firm_mis_api bash

# Run seed script manually
docker exec -it ca_firm_mis_api python -m app.seed

# Check Alembic version
docker exec -it ca_firm_mis_api alembic current

# Run migrations manually
docker exec -it ca_firm_mis_api alembic upgrade head
```

## 📈 Demo Flow

**Recommended demo sequence to show all features:**

1. **Show API Documentation**
   ```bash
   open http://localhost:8000/docs
   ```

2. **Show Seed Data**
   ```bash
   curl http://localhost:8000/clients | jq
   curl http://localhost:8000/tasks | jq 'length'
   ```

3. **Demonstrate Filtering**
   ```bash
   curl "http://localhost:8000/tasks?status=Awaiting%20Client" | jq
   ```

4. **Show Dashboard - Due This Week**
   ```bash
   curl http://localhost:8000/tasks/dashboard/due-this-week | jq
   ```

5. **Show Dashboard - Overdue**
   ```bash
   curl http://localhost:8000/tasks/dashboard/overdue | jq
   ```

6. **Show Workload Distribution**
   ```bash
   curl http://localhost:8000/tasks/dashboard/workload | jq
   ```

7. **Create New Client**
   ```bash
   curl -X POST http://localhost:8000/clients \
     -H "Content-Type: application/json" \
     -d '{
       "name": "Demo Company Ltd",
       "entity_type": "Company",
       "pan": "DEMOC1234D",
       "partner_in_charge": "Rajesh Kumar"
     }' | jq
   ```

8. **Create Task for New Client**
   ```bash
   # Use client_id from previous response
   curl -X POST http://localhost:8000/tasks \
     -H "Content-Type: application/json" \
     -d '{
       "client_id": 19,
       "task_type": "GSTR-3B",
       "period_label": "Aug 2026",
       "due_date": "2026-09-20",
       "assignee": "Vikram Singh",
       "status": "Not Started"
     }' | jq
   ```

9. **Update Task Status**
   ```bash
   curl -X PUT http://localhost:8000/tasks/66 \
     -H "Content-Type: application/json" \
     -d '{"status": "In Progress"}' | jq
   ```

10. **Show Data Persistence**
    ```bash
    docker compose down
    docker compose up -d
    sleep 5
    curl http://localhost:8000/clients | jq 'length'
    ```

## 🎯 Key Demo Talking Points

1. **Single Command Setup**: "Entire backend runs with `docker compose up --build`"
2. **Realistic Data**: "Seed script creates 18 clients, 65 tasks with realistic CA firm data"
3. **Dashboard Focus**: "Dashboard shows what needs attention today - overdue, due soon, blocked on client"
4. **Flexible Filtering**: "Tasks filterable by client, assignee, status, type, date range"
5. **Data Persistence**: "PostgreSQL with Docker volumes - data survives restarts"
6. **Clean Architecture**: "Separated models, schemas, routers - easy to extend"
7. **Production Schema**: "Foreign keys, indexes, cascade deletes, timestamps"
8. **Interactive Docs**: "OpenAPI auto-generated from code with try-it-out feature"

## ⚡ Performance Tips

```bash
# With pagination
curl "http://localhost:8000/clients?limit=10&skip=0"

# Filter early to reduce result set
curl "http://localhost:8000/tasks?status=Filed&limit=100"

# Use specific endpoints instead of filtering
curl http://localhost:8000/tasks/dashboard/overdue
# Better than:
# curl "http://localhost:8000/tasks?date_to=$(date +%Y-%m-%d)&status!=Filed"
```

## 🔧 Troubleshooting

| Issue | Solution |
|-------|----------|
| Port 8000 already in use | Change port in docker-compose.yml or stop other service |
| Port 5432 already in use | Change PostgreSQL port or stop local PostgreSQL |
| Database connection fails | Check `docker compose logs db` for errors |
| Migration errors | Run `docker compose down -v` and rebuild |
| Seed data not appearing | Check `docker compose logs api` for errors |
| 404 on all endpoints | API container may not have started, check logs |

## 📝 Quick Edit & Reload

```bash
# Code changes auto-reload (volume mounted)
# Edit backend/app/routers/tasks.py
# Changes reflect immediately (uvicorn --reload)

# For model changes, run migration:
docker exec -it ca_firm_mis_api alembic revision --autogenerate -m "description"
docker exec -it ca_firm_mis_api alembic upgrade head
```

---

**Tip**: Bookmark http://localhost:8000/docs - it's your best friend for testing!
