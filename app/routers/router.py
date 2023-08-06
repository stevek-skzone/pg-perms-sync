from fastapi import APIRouter

from app.routers.endpoints.jobs import router as job_router

router = APIRouter()

router.include_router(job_router, tags=["jobs"], prefix="/v1")
