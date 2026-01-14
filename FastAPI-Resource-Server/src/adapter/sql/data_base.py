from os import environ

from sqlmodel import SQLModel
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine, AsyncEngine
from sqlalchemy import event


def db_engine(env: str) -> AsyncEngine:
    if env not in ["development", "test"]:
        connection_string = environ.get("PSQL_DATABASE_URL")
        return create_async_engine(
            connection_string,
            echo = False,
            future = True,
            pool_pre_ping = True,
            pool_size = 20,
            max_overflow = 2,
            pool_timeout = 30,
            pool_recycle = 7200,
        )

    else:
        if env == "development":
            connection_string = "sqlite+aiosqlite:///dev.db"
        elif env == "test":
            connection_string = "sqlite+aiosqlite:///test.db"
        else:
            raise ValueError("Invalid ENVIRONMENT value")
        dev_engine = create_async_engine(
            connection_string,
            echo = True if environ.get("DEBUG_SQLALCHEMY", "False") == "True" else False,
            connect_args = {
                "check_same_thread": False
                },
            future = True,
            pool_pre_ping = True,
        )
        @event.listens_for(dev_engine.sync_engine, "connect")
        def set_sqlite_pragma(dbapi_conn, connection_record):
            cursor = dbapi_conn.cursor()
            cursor.execute("PRAGMA foreign_keys=ON;")
            cursor.close()
        return dev_engine

async def init_db() -> None:
    if current_environment in ["development", "test"]:
        from adapter.sql.models import User, Team, Project, ProjectRole, ProjectUserLink
        async with engine.begin() as conn:
            await conn.run_sync(SQLModel.metadata.create_all)

def get_session() -> AsyncSession:
    return AsyncSession(engine)

async def close_session() -> bool:
    await engine.dispose()
    return True


current_environment = environ.get("ENVIRONMENT", "development")
engine = db_engine(current_environment)