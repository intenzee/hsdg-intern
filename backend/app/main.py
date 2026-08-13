from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from sqlalchemy.orm import Session
from app.config import get_settings
from app.database import get_db
from app.routers import clients, tasks, documents, generate
from app.schemas import SeedResponse
from app.seed import seed_database

settings = get_settings()

app = FastAPI(
    title=settings.api_title,
    version=settings.api_version,
    description=settings.api_description,
    docs_url="/docs",
    redoc_url="/redoc"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(clients.router)
app.include_router(tasks.router)
app.include_router(documents.router)
app.include_router(generate.router)


@app.get("/", tags=["Root"])
def root():
    return {
        "message": "CA Firm MIS API",
        "version": settings.api_version,
        "docs": "/docs",
        "endpoints": {
            "clients": "/clients",
            "tasks": "/tasks",
            "documents": "/tasks/{task_id}/documents",
            "dashboard": "/tasks/dashboard",
            "generate_tasks": "/tasks/generate",
        }
    }


@app.get("/health", tags=["Health"])
def health_check(db: Session = Depends(get_db)):
    try:
        db.execute(text("SELECT 1"))
        return {"status": "healthy", "database": "connected"}
    except Exception as e:
        return {"status": "unhealthy", "database": "disconnected", "error": str(e)}


@app.post("/seed", response_model=SeedResponse, tags=["Development"])
def seed_data():
    result = seed_database()
    return {"message": "Database seeded successfully", **result}
