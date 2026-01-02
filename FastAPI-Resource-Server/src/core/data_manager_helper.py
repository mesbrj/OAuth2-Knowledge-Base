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

            case ['dataManagerImpl', 'process', 'read', _]:
                if not kwargs.get("record_id") and not kwargs.get("record_name"):
                    raise ValueError(
                        "'record_id' or 'record_name' must be provided."
                    )

        return await func(*args, **kwargs)

    return wrapper