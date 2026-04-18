from fastapi import FastAPI

from app.api.routes import router
from app.storage.sqlite import SQLiteStorage


def create_app() -> FastAPI:
    app = FastAPI(
        title="0xchou00 — Lightweight Security Detection Tool",
        version="0.3.0",
        description="Local logs. Typed events. Bounded detections.",
    )

    @app.on_event("startup")
    def startup() -> None:
        SQLiteStorage().initialize()

    app.include_router(router)
    return app


app = create_app()
