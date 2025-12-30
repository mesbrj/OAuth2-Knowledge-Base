from adapter.SQL.data_access import dbAccessImpl


def repo_factory(repo_type: str):
    if repo_type == "database":
        return dbAccessImpl()
    else:
        None

