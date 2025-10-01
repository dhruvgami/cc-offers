"""FastAPI application main entry point"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from shared.config import settings
from shared.database import init_db

# Create FastAPI app
app = FastAPI(
    title="Travel Discount Comparison API",
    description="API for comparing hotel discount rates across multiple programs",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize database on startup
@app.on_event("startup")
async def startup_event():
    """Initialize database on application startup"""
    init_db()
    print("✅ Application started successfully")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on application shutdown"""
    print("👋 Application shutting down")


# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "environment": settings.environment,
        "version": "1.0.0"
    }


# Root endpoint
@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "Travel Discount Comparison API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health"
    }


# Import and include routers
from api.routes import search, results, mock

app.include_router(search.router, prefix="/api", tags=["search"])
app.include_router(results.router, prefix="/api", tags=["results"])
app.include_router(mock.router, prefix="/api", tags=["mock"])


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.api_reload,
        log_level=settings.log_level.lower()
    )
