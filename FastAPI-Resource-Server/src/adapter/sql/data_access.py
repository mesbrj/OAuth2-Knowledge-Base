import uuid
import logging

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
    "roles": ProjectRole,
}

class dbAccessImpl(dbAccess):
    @classmethod
    async def create_record(cls, table_id: str, attributes: dict):
        if not table_id or table_id not in table.keys():
            logging.error(f"Table '{table_id}' does not exist.")
            return
        try:
            table[table_id].model_validate(attributes)
            async with get_session() as db:
                rec = table[table_id](**attributes)
                db.add(rec)
                await db.commit()
                await db.refresh(rec)
                return rec
        except (SQLAlchemyError, ValidationError) as error:
            logging.error(f"Error occurred: {error}")



#async def test_update(user_id: str | uuid.UUID, new_location: str):
#    if isinstance(user_id, str):
#        user_id = uuid.UUID(user_id)
#    async with get_session() as db:
#        statement = select(
#            table["users"]).where(
#                table["users"].id == user_id
#            )
#        result = await db.exec(statement)
#        user = result.first()
#        if user:
#            user.location = new_location
#            db.add(user)
#            await db.commit()
#            await db.refresh(user)
