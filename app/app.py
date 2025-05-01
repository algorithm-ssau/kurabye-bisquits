from fastapi import FastAPI
from uvicorn import run as uvicorn_run

from api.v1.routes import routers as api_v1_routes
from core.config import host_settings  # host configuration

app = FastAPI()
app.include_router(api_v1_routes)

if __name__ == "__main__":
    uvicorn_run(
        "app:app",
        host=host_settings.host,
        port=host_settings.port,
        reload=True,
    )
