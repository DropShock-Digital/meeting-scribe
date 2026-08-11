from __future__ import annotations

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from .api import router
from .config import Settings
from .service import MeetingService
from .store import Store


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    settings = Settings.from_env()
    settings.ensure_directories()
    store = Store(settings.database_path)
    store.initialize()
    app.state.settings = settings
    app.state.service = MeetingService(settings, store)
    yield


def create_app() -> FastAPI:
    app = FastAPI(title="Meeting Scribe", version="0.1.0", lifespan=lifespan, docs_url="/docs")
    app.include_router(router)
    static_dir = Path(__file__).parent / "static"
    app.mount("/", StaticFiles(directory=static_dir, html=True), name="console")
    return app


app = create_app()
