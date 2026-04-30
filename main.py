import uvicorn
from fastapi import FastAPI

from app.core.exceptions import AppError, app_error_handler
from app.core.logging import configure_logging
from app.routes.health import router as health_router

configure_logging()

app = FastAPI(title="labes-api")

app.add_exception_handler(AppError, app_error_handler)
app.include_router(health_router)


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
