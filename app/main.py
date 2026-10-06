from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes.files import router as files_router
from app.core.config import settings
from app.core.logging import configure_logging
from app.db.database import init_db

init_db()


@asynccontextmanager
async def lifespan(_: FastAPI):
    configure_logging()
    init_db()
    yield


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description=settings.app_description,
    openapi_tags=[
        {"name": "files", "description": "Geospatial file upload and metadata endpoints."},
        {"name": "measurements", "description": "Feature measurement and geometry retrieval."},
        {"name": "system", "description": "Operational health and status endpoints."},
    ],
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(files_router)


@app.get("/health", tags=["system"])
async def health() -> dict[str, str]:
    return {"status": "ok"}
