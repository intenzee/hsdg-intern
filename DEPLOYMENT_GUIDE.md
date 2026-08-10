# Deployment & Testing Guide

Complete guide for deploying and validating the CA Firm MIS backend.

## 📋 Pre-Deployment Checklist

### System Requirements
- ✅ Docker Desktop installed and running
- ✅ Docker Compose available (v2.0+)
- ✅ 2GB free disk space (for images and volumes)
- ✅ Ports 8000 and 5432 available

### Verify Docker
```bash
docker --version
docker compose version
```

## 🚀 Step-by-Step Deployment

### Step 1: Navigate to Project Directory
```bash
cd /path/to/ca-firm-mis-backend
```

### Step 2: Build and Start Services
```bash
docker compose up --build
```

**Expected Output:**
```
✓ Database is ready!
✓ Running migrations...
✓ Starting application...
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000
```

**Wait for:** "Application startup complete" message (usually 10-20 seconds)

### Step 3: Verify Services Running

Open a new terminal and check:
```bash
docker compose ps
```

**Expected Output:**
```
NAME                  STATUS    PORTS
ca_firm_mis_db        Up        0.0.0.0:5432->5432/tcp
ca_firm_mis_api       Up        0.0.0.0:8000->8000/tcp
```

### Step 4: Health Check
```bash
curl http://localhost:8000/health
```

**Expected Response:**
```json
{
  "status": "healthy",
  "database": "connected",
  "api_version": "1.0.0"
}
```

### Step 5: Seed Database
```bash
curl -X POST http://localhost:8000/seed
```

**Expected Response:**
```json
{
  "message": "Database seeded successfully",
  "clients_created": 18,
  "tasks_created": 65,
  "documents_created": 150+
}
```

### Step 6: Verify Seed Data
```bash
# Check clients
curl http://localhost:8000/clients | jq 'length'
# Should return: 18

# Check tasks
curl http://localhost:8000/tasks | jq 'length'
# Should return: 65
```

## ✅ Validation Tests

### Test 1: API Documentation
```bash
open http://localhost:8000/docs
```
✓ Swagger UI should load with all endpoints visible

### Test 2: Client CRUD
```bash
# Create client
curl -X POST http://localhost:8000/clients \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test Client Ltd",
    "entity_type": "Company",
    "pan": "TESTC1234T",
    "partner_in_charge": "Test Partner"
  }' | jq

# Should return created client with id
```

### Test 3: Task Filtering
```bash
# Filter by status
curl "http://localhost:8000/tasks?status=Awaiting%20Client" | jq 'length'
# Should return count of awaiting client tasks

# Filter by assignee
curl "http://localhost:8000/tasks?assignee=Vikram%20Singh" | jq 'length'
# Should return count of tasks assigned to Vikram Singh
```

### Test 4: Dashboard Endpoints
```bash
# Due this week
curl http://localhost:8000/tasks/dashboard/due-this-week | jq

# Overdue
curl http://localhost:8000/tasks/dashboard/overdue | jq

# Workload
curl http://localhost:8000/tasks/dashboard/workload | jq
```

### Test 5: Data Persistence
```bash
# Stop containers
docker compose down

# Start again
docker compose up -d

# Wait 10 seconds
sleep 10

# Verify data persists
curl http://localhost:8000/clients | jq 'length'
# Should still return: 18
```

## 🔧 Troubleshooting

### Issue: Port 8000 Already in Use

**Error:**
```
Error starting userland proxy: listen tcp4 0.0.0.0:8000: bind: address already in use
```

**Solution:**
```bash
# Find process using port 8000
lsof -i :8000

# Kill the process
kill -9 <PID>

# Or change port in docker-compose.yml
ports:
  - "8001:8000"  # Change 8000 to 8001
```

### Issue: Port 5432 Already in Use

**Error:**
```
Error starting userland proxy: listen tcp4 0.0.0.0:5432: bind: address already in use
```

**Solution:**
```bash
# Stop local PostgreSQL
brew services stop postgresql  # macOS
sudo service postgresql stop   # Linux

# Or change port in docker-compose.yml
ports:
  - "5433:5432"  # Change 5432 to 5433
```

### Issue: Database Connection Failed

**Error in logs:**
```
sqlalchemy.exc.OperationalError: could not connect to server
```

**Solution:**
```bash
# Check if database is running
docker compose logs db

# Restart services
docker compose restart

# If still failing, rebuild
docker compose down -v
docker compose up --build
```

### Issue: Migration Failed

**Error:**
```
alembic.util.exc.CommandError: Can't locate revision identified by 'xxx'
```

**Solution:**
```bash
# Reset database completely
docker compose down -v
docker compose up --build
```

### Issue: Seed Script Fails

**Error:**
```
IntegrityError: duplicate key value violates unique constraint
```

**Solution:**
```bash
# Re-run seed (it drops existing data first)
curl -X POST http://localhost:8000/seed

# Or reset database
docker compose down -v
docker compose up --build
curl -X POST http://localhost:8000/seed
```

### Issue: API Container Exits Immediately

**Check logs:**
```bash
docker compose logs api
```

**Common causes:**
- Python dependency installation failed
- Syntax error in code
- Database not ready

**Solution:**
```bash
# Rebuild with no cache
docker compose build --no-cache
docker compose up
```

## 🧪 Complete Test Suite

Run all tests to verify full functionality:

```bash
#!/bin/bash
echo "=== CA Firm MIS Backend Test Suite ==="

# Test 1: Health Check
echo -e "\n1. Health Check"
curl -s http://localhost:8000/health | jq

# Test 2: List Clients
echo -e "\n2. List Clients (count)"
curl -s http://localhost:8000/clients | jq 'length'

# Test 3: List Tasks
echo -e "\n3. List Tasks (count)"
curl -s http://localhost:8000/tasks | jq 'length'

# Test 4: Filter by Status
echo -e "\n4. Tasks Awaiting Client"
curl -s "http://localhost:8000/tasks?status=Awaiting%20Client" | jq 'length'

# Test 5: Overdue Tasks
echo -e "\n5. Overdue Tasks"
curl -s http://localhost:8000/tasks/dashboard/overdue | jq 'length'

# Test 6: Due This Week
echo -e "\n6. Tasks Due This Week"
curl -s http://localhost:8000/tasks/dashboard/due-this-week | jq 'length'

# Test 7: Workload Summary
echo -e "\n7. Workload per Assignee"
curl -s http://localhost:8000/tasks/dashboard/workload | jq

# Test 8: Create Client
echo -e "\n8. Create New Client"
curl -s -X POST http://localhost:8000/clients \
  -H "Content-Type: application/json" \
  -d '{
    "name": "API Test Client",
    "entity_type": "Company",
    "pan": "APITC1234A",
    "partner_in_charge": "Test Partner"
  }' | jq '.id, .name'

echo -e "\n=== All Tests Complete ==="
```

Save as `test_suite.sh`, make executable, and run:
```bash
chmod +x test_suite.sh
./test_suite.sh
```

## 📊 Expected Metrics After Seeding

| Metric | Count | Notes |
|--------|-------|-------|
| Clients | 18 | Mix of individuals and businesses |
| Tasks | 65 | Across all task types |
| Documents | 150+ | 2-5 per task |
| Entity Types | 5 | Individual, Company, LLP, Partnership, Trust |
| Task Types | 6 | GSTR-3B, GSTR-1, TDS, GST Quarterly, Income Tax Audit, ROC |
| Statuses | 4 | Not Started, In Progress, Awaiting Client, Filed |
| Assignees | 6 | Realistic CA firm team names |
| Partners | 4 | Senior partners managing clients |

## 🎯 Success Criteria

✅ **Deployment Successful If:**
1. Both containers running (db + api)
2. Health check returns "healthy"
3. Seed creates 15+ clients and 60+ tasks
4. API docs accessible at /docs
5. All CRUD operations work
6. Dashboard endpoints return data
7. Data persists after restart
8. No errors in logs

## 🔄 Maintenance Operations

### Daily Operations
```bash
# View logs
docker compose logs -f

# Restart services
docker compose restart

# Stop services
docker compose stop

# Start stopped services
docker compose start
```

### Database Backup
```bash
# Backup
docker exec ca_firm_mis_db pg_dump -U postgres ca_firm_mis > backup.sql

# Restore
docker exec -i ca_firm_mis_db psql -U postgres ca_firm_mis < backup.sql
```

### Database Console Access
```bash
# Connect to PostgreSQL
docker exec -it ca_firm_mis_db psql -U postgres -d ca_firm_mis

# Run queries
ca_firm_mis=# SELECT COUNT(*) FROM clients;
ca_firm_mis=# SELECT COUNT(*) FROM compliance_tasks;
ca_firm_mis=# \dt  -- List tables
ca_firm_mis=# \q   -- Quit
```

### Clean Rebuild
```bash
# Complete cleanup and rebuild
docker compose down -v
docker system prune -f
docker compose up --build
curl -X POST http://localhost:8000/seed
```

## 📈 Performance Benchmarks

Expected response times (on typical dev machine):

| Endpoint | Expected Time | Notes |
|----------|---------------|-------|
| GET /health | < 50ms | Simple DB ping |
| GET /clients | < 100ms | 18 records |
| GET /tasks | < 200ms | 65 records with joins |
| POST /clients | < 100ms | Single insert |
| Dashboard endpoints | < 200ms | Filtered queries |
| POST /seed | 2-5 seconds | Bulk operations |

## 🎓 Demo Preparation

### Before Demo:
1. ✅ Run `docker compose up --build`
2. ✅ Seed database with `POST /seed`
3. ✅ Open Swagger UI in browser
4. ✅ Test overdue dashboard endpoint
5. ✅ Verify logs are clean
6. ✅ Prepare test client JSON for live creation

### During Demo:
1. Show Swagger UI first (impressive auto-documentation)
2. Demonstrate dashboard insights (overdue, due soon)
3. Show filtering capabilities
4. Create a client live
5. Show data persistence after restart
6. Discuss architecture and database schema

### After Demo:
- Be ready to discuss:
  - Why this tech stack
  - Database schema design decisions
  - How to add recurring task generation
  - How to add authentication
  - Scalability considerations

## 🚦 Deployment Status

After successful deployment, you should see:

```
✅ Docker containers running
✅ PostgreSQL accepting connections
✅ Migrations applied
✅ API responding on port 8000
✅ Swagger UI accessible
✅ Database seeded with test data
✅ All endpoints functional
✅ Data persists across restarts

🎉 System is ready for demo/evaluation!
```

---

**Need Help?** Check:
1. Docker logs: `docker compose logs`
2. API logs: `docker compose logs api`
3. Database logs: `docker compose logs db`
4. GitHub issues (if repository exists)

**System Status:** `docker compose ps`
**Quick Reset:** `docker compose down -v && docker compose up --build`
