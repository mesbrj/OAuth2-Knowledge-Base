from functools import wraps

from ports.repository import repo_factory


def validation_helper(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        wrapped = func.__qualname__.split('.')
        if wrapped[0] == 'dataManagerImpl' and wrapped[1] == 'process':
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
                    db = repo_factory("database")
                    async with db.query_records() as query:
                        user = await (
                            query
                            .select(query.table["users"])
                            .where(query.table["users"].email == kwargs.get("manager_email"))
                            .first()
                        )
                    if not user:
                        raise ValueError(
                            f"User with email '{kwargs.get('manager_email')}' does not exist."
                        )
                    kwargs["manager_id"] = user.id

        return await func(*args, **kwargs)

    return wrapper