from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app import __version__
from app.api.routes import health, predict
from app.core.config import get_settings
from app.core.logging import setup_logging
from app.services.inference import inference_service


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncIterator[None]:
    setup_logging()
    settings = get_settings()
    inference_service.load(settings)
    yield
    inference_service.unload()


def create_app() -> FastAPI:
    settings = get_settings()

    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version or __version__,
        description=(
            "FastAPI wrapper for the Anvarjon Multi-Attention Module (MAM) "
            "CNN age/gender classifiers (Age-Gender-Classification repo)."
        ),
        lifespan=lifespan,
        docs_url="/docs" if settings.environment != "production" or settings.debug else None,
        redoc_url="/redoc" if settings.environment != "production" or settings.debug else None,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origin_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(_request: Request, exc: StarletteHTTPException):
        return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(_request: Request, exc: RequestValidationError):
        return JSONResponse(status_code=422, content={"detail": exc.errors()})

    app.include_router(health.router, prefix=settings.api_prefix)
    app.include_router(predict.router, prefix=settings.api_prefix)

    @app.get("/", include_in_schema=False)
    def root():
        return {
            "service": settings.app_name,
            "version": settings.app_version,
            "docs": "/docs",
            "health": f"{settings.api_prefix}/health",
            "predict": f"{settings.api_prefix}/predict",
            "backend": "MAM CNN (Age-Gender-Classification)",
        }

    return app


app = create_app()
