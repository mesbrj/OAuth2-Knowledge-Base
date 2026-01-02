from os import environ

from sqlmodel import SQLModel, StaticPool
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine, AsyncEngine
from sqlalchemy import event


def db_engine(env: str) -> AsyncEngine:
    if env == "production" or env == "staging":
        connection_string = environ.get("PSQL_DATABASE_URL")
        return create_async_engine(
            connection_string,
            echo=False,
            future=True,
            pool_pre_ping=True,
            pool_size=20,
            max_overflow=2,
            pool_timeout=30,
            pool_recycle=7200,
        )

    elif env == "development":
        dev_engine = create_async_engine(
            "sqlite+aiosqlite:///dev.db",
            echo=True if environ.get("DEBUG_SQLALCHEMY", "False") == "True" else False,
            pool_pre_ping=True,
        )
        @event.listens_for(dev_engine.sync_engine, "connect")
        def set_sqlite_pragma(dbapi_conn, connection_record):
            cursor = dbapi_conn.cursor()
            cursor.execute("PRAGMA foreign_keys=ON;")
            cursor.close()
        return dev_engine

    elif env == "test":
        test_engine = create_async_engine(
            "sqlite+aiosqlite:///:memory:",
            echo=False,
            poolclass=StaticPool
        )
        @event.listens_for(test_engine.sync_engine, "connect")
        def set_sqlite_pragma(dbapi_conn, connection_record):
            cursor = dbapi_conn.cursor()
            cursor.execute("PRAGMA foreign_keys=ON;")
            cursor.close()
        return test_engine

def get_session() -> AsyncSession:
    return AsyncSession(engine)

async def close_session() -> None:
    await engine.dispose()

async def init_db() -> None:
    current_env = environ.get("ENVIRONMENT", "development")
    if current_env == "test" or current_env == "development": 
        async with engine.begin() as conn:
            await conn.run_sync(SQLModel.metadata.create_all)

engine = db_engine(
    environ.get("ENVIRONMENT", "development")
)