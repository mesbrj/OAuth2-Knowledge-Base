from os import environ
from contextlib import asynccontextmanager
from fastapi import FastAPI
import uvicorn

from adapter.sql.data_base import init_db, close_session
from adapter.rest.routes import health_routes, crud_routes

@asynccontextmanager
async def lifespan(app: FastAPI):
    if environ.get("ENVIRONMENT", "development") == "development":
        await init_db()
    yield
    await close_session()

web_app = FastAPI(lifespan=lifespan)
web_app.include_router(health_routes)
web_app.include_router(crud_routes)

async def start_web_server():
    await uvicorn.Server(
        uvicorn.Config(
            web_app,
            host="0.0.0.0",
            port=8080,
            log_level="info",
        )
    ).serve()
