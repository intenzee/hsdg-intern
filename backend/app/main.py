"""
Main FastAPI application entry point.
Configures the API, includes all routers, and provides seed endpoint.
"""
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from app.config import get_settings
from app.database import get_db
from app.routers import clients, tasks, documents
from app.schemas import SeedResponse
from app.seed import seed_database

settings = get_settings()

# Create FastAPI application
app = FastAPI(
    title=settings.api_title,
    version=settings.api_version,
    description=settings.api_description,
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS (useful for future frontend integration)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, restrict to specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(clients.router)
app.include_router(tasks.router)
app.include_router(documents.router)


@app.get("/", tags=["Root"])
def root():
    """
    Root endpoint - provides API information and links.
    """
    return {
        "message": "CA Firm MIS API",
        "version": settings.api_version,
        "docs": "/docs",
        "redoc": "/redoc",
        "endpoints": {
            "clients": "/clients",
            "tasks": "/tasks",
            "documents": "/tasks/{task_id}/documents",
            "dashboard": {
                "due_this_week": "/tasks/dashboard/due-this-week",
                "overdue": "/tasks/dashboard/overdue",
                "awaiting_client": "/tasks/dashboard/awaiting-client",
                "workload": "/tasks/dashboard/workload"
            },
            "seed": "/seed (POST)"
        }
    }


@app.get("/health", tags=["Health"])
def health_check(db: Session = Depends(get_db)):
    """
    Health check endpoint - verifies API and database connectivity.
    """
    try:
        # Test database connection
        db.execute("SELECT 1")
        return {
            "status": "healthy",
            "database": "connected",
            "api_version": settings.api_version
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "database": "disconnected",
            "error": str(e)
        }


@app.post("/seed", response_model=SeedResponse, tags=["Development"])
def seed_data():
    """
    Seed the database with realistic test data.
    
    **WARNING**: This endpoint drops all existing data and recreates it.
    Only use in development environments.
    
    Creates:
    - 15+ clients with diverse entity types
    - 60+ compliance tasks across multiple task types
    - 2-5 document items per task
    
    This is a development-only endpoint for quickly populating the database.
    """
    result = seed_database()
    return {
        "message": "Database seeded successfully",
        **result
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
