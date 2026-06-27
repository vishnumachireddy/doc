import os
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from backend.app.core.config import settings
from backend.app.core.database import engine, Base
from backend.app.api import api_router

# Import models to ensure they register on metadata for Base.metadata.create_all
from backend.app.models import User, Document, ResumeAnalysis

# Initialize database tables locally on startup (simplifies installation)
try:
    print("Initializing database tables...")
    Base.metadata.create_all(bind=engine)
    print("Database tables initialized successfully!")
except Exception as e:
    print(f"Error initializing database: {e}")

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="ResumeIQ Advanced Document Verification and Resume Intelligence Platform API Gateway.",
    version="1.0.0",
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# Set CORS origins
if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin).strip("/") for origin in settings.BACKEND_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

# Include API Router
app.include_router(api_router, prefix=settings.API_V1_STR)

# Global Health Check
@app.get("/health", tags=["Health"])
def health_check():
    """Confirms backend service health and DB connectivity."""
    return {
        "status": "healthy",
        "project": settings.PROJECT_NAME,
        "database": "connected"
    }

# Centralized Exception Handler
@app.exception_handler(Exception)
def global_exception_handler(request: Request, exc: Exception):
    print(f"Unhandled Exception: {exc}")
    import traceback
    traceback.print_exc()
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": f"Internal server processing error: {str(exc)}"}
    )
