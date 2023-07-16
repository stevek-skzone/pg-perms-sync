from fastapi import FastAPI
from fastapi.responses import RedirectResponse

from app.routers.v1 import router as v1_router
from app.services.processor import sync_roles
from app.services.scheduler import scheduler

app = FastAPI()
app.include_router(v1_router, prefix="/api/v1")


def index():
    """
    Redirects to the API documentation page.

    Returns:
        RedirectResponse: A redirect response to the API documentation page.
    """
    return RedirectResponse(url="/docs")


@app.on_event("startup")
async def load_schedule_or_create_blank():
    """
    Loads the scheduler and adds jobs to it.

    Returns:
        None
    """
    scheduler.add_job(sync_roles, "date")
    scheduler.add_job(sync_roles, "interval", minutes=1)
    scheduler.start()
