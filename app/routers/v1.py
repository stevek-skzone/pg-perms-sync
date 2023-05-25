from fastapi import APIRouter
from app.routers.endpoints.groups import router as group_router

router = APIRouter()

router.include_router(group_router, tags=["groups"])
