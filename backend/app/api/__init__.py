from fastapi import APIRouter
from backend.app.api.auth import router as auth_router
from backend.app.api.documents import router as doc_router
from backend.app.api.jobs import router as jobs_router
from backend.app.api.admin import router as admin_router

api_router = APIRouter()
api_router.include_router(auth_router)
api_router.include_router(doc_router)
api_router.include_router(jobs_router)
api_router.include_router(admin_router)
