from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from uvicorn import run as uvicorn_run

from api.v1.routes import routers as api_v1_routes
from core.config import (
    host_settings,  # host configuration
    log_setting,
    sentry_config,
)
from static.static import router as static_router

log = log_setting.get_configure_logging(__name__)
sentry_config.run_sentry()

app = FastAPI()

app.mount("/css", StaticFiles(directory="static/css"), name="css")
app.mount("/js", StaticFiles(directory="static/js"), name="js")
app.mount("/img", StaticFiles(directory="static/img"), name="img")
app.mount("/icon", StaticFiles(directory="static/icon"), name="icon")
app.mount("/fonts", StaticFiles(directory="static/fonts"), name="fonts")

app.include_router(api_v1_routes)
app.include_router(static_router)


if __name__ == "__main__":
    log.info("App start.")
    uvicorn_run(
        "app:app",
        host=host_settings.host,
        port=host_settings.port,
        reload=True,
    )
    log.info("App often.")
