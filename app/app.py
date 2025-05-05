from logging import getLogger
from pathlib import Path

from fastapi import FastAPI
from uvicorn import run as uvicorn_run

from api.v1.routes import routers as api_v1_routes
from core.config import (
    host_settings,  # host configuration
    log_setting,
)

log = log_setting.get_configure_logging(Path(__file__).stem)


app = FastAPI(
    servers=[
        {"url": "api/v1", "description": "Staging environment"},
        {"url": "api/v2", "description": "Production environment"},
    ],
)

app.include_router(api_v1_routes)

if __name__ == "__main__":
    log.info("App start.")
    uvicorn_run(
        "app:app",
        host=host_settings.host,
        port=host_settings.port,
        reload=True,
    )
    log.info("App often.")
