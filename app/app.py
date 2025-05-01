from core.config import host_settings  # host configuration
from fastapi import FastAPI
from uvicorn import run as uvicorn_run

app = FastAPI()

if __name__ == "__main__":
    uvicorn_run(
        "app:app",
        host=host_settings.host,
        port=host_settings.port,
    )
