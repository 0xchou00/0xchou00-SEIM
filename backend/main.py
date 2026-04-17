from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.api.routes import router
from app.storage.sqlite import SQLiteStorage


def create_app() -> FastAPI:
    frontend_dir = Path(__file__).resolve().parent.parent / "frontend"
    app = FastAPI(
        title="0xchou00 Detection Tool",
        version="0.2.0",
        description="Lightweight single-node security detection tool for SSH and web telemetry.",
    )

    @app.on_event("startup")
    def startup() -> None:
        SQLiteStorage().initialize()

    app.include_router(router)

    if frontend_dir.exists():
        app.mount("/assets", StaticFiles(directory=str(frontend_dir)), name="assets")

        @app.get("/", include_in_schema=False)
        def landing() -> FileResponse:
            return FileResponse(frontend_dir / "landing.html")

        @app.get("/dashboard", include_in_schema=False)
        def dashboard() -> FileResponse:
            return FileResponse(frontend_dir / "dashboard.html")

    return app


app = create_app()
