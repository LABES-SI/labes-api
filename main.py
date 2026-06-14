import os
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware

from app.core.exceptions import AppError, app_error_handler
from app.core.logging import configure_logging
from app.routes.acessibilidade import router as acessibilidade_router
from app.routes.filtros import router as filtros_router
from app.routes.health import router as health_router

configure_logging()

def _get_allowed_origins() -> list[str]:
    """
    Read the `ALLOW_ORIGINS` env var (comma-separated URLs) and
    return a clean list. If the variable is missing, returns an empty list.
    """
    origins = os.getenv("ALLOW_ORIGINS", "")
    return [o.strip() for o in origins.split(",") if o.strip()]

app = FastAPI(title="labes-api", version="0.7.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:4200",
        "http://127.0.0.1:4200",
    ] + _get_allowed_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(GZipMiddleware, minimum_size=1024)

app.add_exception_handler(AppError, app_error_handler)
app.include_router(health_router)
app.include_router(acessibilidade_router)
app.include_router(filtros_router)


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
