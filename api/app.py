from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.database import init_db
from api.routes.data import router as pipeline_router


def create_app() -> FastAPI:
    init_db()
    app = FastAPI(title="Flood Analysis Pipeline API", version="1.0.0")
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[
            "http://localhost:9002",
            "http://127.0.0.1:9002",
            "http://localhost:3000",
            "http://127.0.0.1:3000",
        ],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.get("/health")
    def health() -> dict[str, str]:
        return {"status": "ok"}

    @app.get("/")
    def root() -> dict[str, object]:
        return {
            "name": "Flood Analysis Pipeline API",
            "status": "ok",
            "version": "1.0.0",
            "health": "/health",
            "latest_run": "/api/pipeline/runs/latest",
            "docs": "/docs",
        }

    app.include_router(pipeline_router)
    return app


app = create_app()
