import uvicorn
from fastapi import FastAPI
from fastapi.middleware.gzip import GZipMiddleware

from app.core.exceptions import AppError, app_error_handler
from app.core.logging import configure_logging
from app.routes.acessibilidade import router as acessibilidade_router
from app.routes.health import router as health_router

configure_logging()

app = FastAPI(title="labes-api")
app.add_middleware(GZipMiddleware, minimum_size=1024)

app.add_exception_handler(AppError, app_error_handler)
app.include_router(health_router)
app.include_router(acessibilidade_router)


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
