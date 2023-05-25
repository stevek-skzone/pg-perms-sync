from fastapi import APIRouter
from app.routers.endpoints.external_mock import router as mock_router

router = APIRouter()

router.include_router(mock_router, tags=["mock"])
