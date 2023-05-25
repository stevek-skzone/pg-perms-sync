from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from app.routers.v1 import router as v1_router

app = FastAPI()
app.include_router(v1_router, prefix="/api/v1")

@app.get("/", include_in_schema=False)
async def index():
    return RedirectResponse(url="/docs")


