from uuid import UUID

from sqlmodel import select
from sqlalchemy.exc import SQLAlchemyError
from pydantic import ValidationError

from adapter.sql.models import User, Team, Project, ProjectUserLink, ProjectRole
from adapter.sql.data_base import get_session
from ports.interfaces import dbAccess


table = {
    "users": User,
    "teams": Team,
    "projects": Project,
    "started_projects": ProjectUserLink,
    "project_roles": ProjectRole,
}

class dbAccessImpl(dbAccess):
    @classmethod
    async def create_record(cls, table_id: str, attributes: dict):
        if not table_id or table_id not in table.keys():
            raise ValueError(f"Table '{table_id}' does not exist.")
        try:
            table[table_id].model_validate(attributes)
            async with get_session() as db:
                rec = table[table_id](**attributes)
                db.add(rec)
                await db.commit()
                await db.refresh(rec)
                return rec
        except (SQLAlchemyError, ValidationError) as error:
            raise ValueError(f"Error occurred: {error}")

    @classmethod
    async def read_record(
        cls, table_id: str, record_name: str | None = None, record_id: UUID | None =  None
        ):
        if not table_id or table_id not in table.keys():
            raise ValueError(f"Table '{table_id}' does not exist.")
        try:
            async with get_session() as db:
                if record_id:
                    statement = select(
                        table[table_id]).where(
                            table[table_id].id == record_id
                        )
                elif record_name:
                    statement = select(
                        table[table_id]).where(
                            table[table_id].name == record_name
                        )
                result = await db.exec(statement)
                record = result.first()
                return record
        except (SQLAlchemyError, ValueError) as error:
            raise ValueError(f"Error occurred: {error}")
