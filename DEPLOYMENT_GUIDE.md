# Deployment Guide

## Quick Start

```bash
docker compose up --build
curl -X POST http://localhost:8000/seed
```

API available at http://localhost:8000/docs

## System Requirements

- Docker Desktop
- 2GB free disk space
- Ports 8000 and 5432 available

## Step-by-Step Deployment

### 1. Start Services
```bash
docker compose up --build
```

Wait for "Application startup complete" message (~30 seconds).

### 2. Verify Services
```bash
docker compose ps
```

Expected output:
```
NAME                  STATUS    PORTS
ca_firm_mis_db        Up        0.0.0.0:5432->5432/tcp
ca_firm_mis_api       Up        0.0.0.0:8000->8000/tcp
```

### 3. Health Check
```bash
curl http://localhost:8000/health
```

Expected: `{"status":"healthy","database":"connected"}`

### 4. Seed Database
```bash
curl -X POST http://localhost:8000/seed
```

Creates 18 clients, 65 tasks, 150+ documents.

### 5. Access API
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Troubleshooting

### Port 8000 Already in Use
```bash
# Find process
lsof -i :8000

# Kill process
kill -9 <PID>

# Or change port in docker-compose.yml
ports:
  - "8001:8000"
```

### Port 5432 Already in Use
```bash
# Stop local PostgreSQL
brew services stop postgresql  # macOS
sudo service postgresql stop   # Linux

# Or change port in docker-compose.yml
ports:
  - "5433:5432"
```

### Database Connection Failed
```bash
# Check logs
docker compose logs db

# Restart services
docker compose restart

# Full rebuild
docker compose down -v
docker compose up --build
```

### Seed Script Fails
```bash
# Re-run seed (it drops existing data)
curl -X POST http://localhost:8000/seed

# Or reset database
docker compose down -v
docker compose up --build
curl -X POST http://localhost:8000/seed
```

## Common Operations

### View Logs
```bash
docker compose logs -f api
docker compose logs -f db
```

### Restart Services
```bash
docker compose restart
```

### Stop Services
```bash
docker compose down
```

### Reset Database
```bash
docker compose down -v
docker compose up --build
curl -X POST http://localhost:8000/seed
```

### Access Database Console
```bash
docker exec -it ca_firm_mis_db psql -U postgres -d ca_firm_mis
```

## Data Persistence

Database data persists in Docker volume `postgres_data`. Data survives container restarts but not `docker compose down -v`.

## Testing

### Manual Test
```bash
curl http://localhost:8000/clients
curl http://localhost:8000/tasks/dashboard/overdue
```

### Automated Test
```bash
./test_api.sh
```

## Production Considerations

- Change CORS settings in `main.py`
- Add authentication/authorization
- Use environment variables for secrets
- Set up proper logging
- Configure backup strategy
- Add monitoring and alerting
- Use production-grade ASGI server config
