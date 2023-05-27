from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from app.routers.v1 import router as v1_router
from app.services.scheduler import scheduler
from app.services.processor import sync_roles

app = FastAPI()
app.include_router(v1_router, prefix="/api/v1")

@app.get("/", include_in_schema=False)
async def index():
    return RedirectResponse(url="/docs")


@app.on_event("startup")
async def load_schedule_or_create_blank():
    scheduler.add_job(sync_roles, "date")
    scheduler.add_job(sync_roles, "interval", minutes=1)
    scheduler.start()


