from functools import wraps

from ports.repository import repo_factory


def validation_helper(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        wrapped = func.__qualname__.split('.')
        wrapped.append(kwargs.get("operation"))
        wrapped.append(kwargs.get("entity"))
        match wrapped:

            case ['dataManagerImpl', 'process', 'create', 'users']:
                if kwargs.get("team_name"):
                    db = repo_factory("database")
                    record = await db.read_record(
                        table_id = "teams",
                        record_name = kwargs.get("team_name")
                    )
                    if not record:
                        raise ValueError(
                            f"Team with name '{kwargs.get('team_name')}' does not exist."
                        )
                    kwargs["team_id"] = record.id

            case ['dataManagerImpl', 'process', 'create', 'teams']:
                if kwargs.get("manager_email"):
                    # The read_record function from data_access (SQL adapter) needs to be improved to support filtering... 
                    from adapter.sql.models import User
                    from sqlmodel import select
                    from adapter.sql.data_base import get_session

                    async with get_session() as session:
                        statement = select(User).where(User.email == kwargs.get("manager_email"))
                        result = await session.exec(statement)
                        user = result.first()

                    if not user:
                        raise ValueError(
                            f"User with email '{kwargs.get('manager_email')}' does not exist."
                        )
                    kwargs["manager_id"] = user.id

        return await func(*args, **kwargs)

    return wrapper