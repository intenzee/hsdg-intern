# Quick Reference

## Startup Commands

```bash
# Start system
docker compose up --build

# Seed database
curl -X POST http://localhost:8000/seed

# Stop system
docker compose down

# Reset database
docker compose down -v
docker compose up --build
curl -X POST http://localhost:8000/seed
```

## Important URLs

| Service | URL |
|---------|-----|
| API Root | http://localhost:8000 |
| Swagger Docs | http://localhost:8000/docs |
| ReDoc | http://localhost:8000/redoc |
| Health Check | http://localhost:8000/health |
| PostgreSQL | localhost:5432 (user: postgres, pass: postgres, db: ca_firm_mis) |

## Common API Calls

### Clients
```bash
# List all clients
curl http://localhost:8000/clients

# Get client
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

# Filter by status
curl "http://localhost:8000/tasks?status=Awaiting%20Client"

# Filter by assignee
curl "http://localhost:8000/tasks?assignee=Vikram%20Singh"

# Multiple filters
curl "http://localhost:8000/tasks?status=Not%20Started&assignee=Anjali%20Mehta"

# Get task with documents
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
```

## Database Access

```bash
# Connect to PostgreSQL
docker exec -it ca_firm_mis_db psql -U postgres -d ca_firm_mis

# Useful queries
SELECT COUNT(*) FROM clients;
SELECT COUNT(*) FROM compliance_tasks;
SELECT COUNT(*) FROM task_documents;

SELECT * FROM clients LIMIT 5;
SELECT * FROM compliance_tasks WHERE status = 'Awaiting Client';
```

## Debugging

```bash
# View API logs
docker compose logs -f api

# View database logs
docker compose logs -f db

# Restart API
docker compose restart api

# Execute commands in API container
docker exec -it ca_firm_mis_api bash

# Check Alembic version
docker exec -it ca_firm_mis_api alembic current

# Run migrations manually
docker exec -it ca_firm_mis_api alembic upgrade head
```

## Pretty JSON Output

Add `| jq` to curl commands for formatted output:

```bash
curl http://localhost:8000/clients | jq
curl http://localhost:8000/tasks/dashboard/workload | jq
```

## Testing

```bash
# Run automated tests
./test_api.sh

# Test specific endpoint
curl -v http://localhost:8000/clients
```
