import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.responses import HTMLResponse, RedirectResponse

from api.config import APP_NAME, APP_VERSION
from api.routes.age_gender import router as age_gender_router
from biometrics import config as biometrics_config
from biometrics.routes import initialize, router as biometrics_router, shutdown


@asynccontextmanager
async def lifespan(app: FastAPI):
    initialize()
    try:
        yield
    finally:
        shutdown()


app = FastAPI(
    title=APP_NAME,
    version=APP_VERSION,
    description="Voice biometrics and age/gender profiling from one service.",
    lifespan=lifespan,
)
app.include_router(age_gender_router)
app.include_router(biometrics_router)


@app.get("/", include_in_schema=False)
async def root():
    return RedirectResponse("/demo")


@app.get("/demo", response_class=HTMLResponse, include_in_schema=False)
async def demo_page():
    path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "demo.html")
    with open(path, encoding="utf-8") as html_file:
        return HTMLResponse(html_file.read())


@app.get("/health", tags=["System"])
async def health():
    return {
        "status": "healthy",
        "service": APP_NAME,
        "biometrics": "enabled",
        "profiling": "enabled",
        "voice_model": os.path.basename(biometrics_config.MODEL_PATH),
    }