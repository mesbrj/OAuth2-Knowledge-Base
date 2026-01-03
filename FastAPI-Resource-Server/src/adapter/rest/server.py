from os import environ
from contextlib import asynccontextmanager
from fastapi import FastAPI
import uvicorn

from adapter.sql.data_base import init_db, close_session
from adapter.rest.routes import health_routers, crud_routers

@asynccontextmanager
async def lifespan(app: FastAPI):
    if environ.get("ENVIRONMENT", "development") in ["development", "test"]:
        await init_db()
    yield
    await close_session()

web_app = FastAPI(lifespan=lifespan)
web_app.include_router(health_routers)
web_app.include_router(crud_routers)

async def start_web_server():
    await uvicorn.Server(
        uvicorn.Config(
            web_app,
            host="127.0.0.1",
            port=8080,
            log_level="info",
        )
    ).serve()
