import os, sys
project_dir_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(f"{project_dir_path}/src")

from pytest import fixture

from adapter.sql.data_base import init_db, get_session, close_session

os.environ["PYTEST_ASYNCIO_MODE"] = "auto"
os.environ["ENVIRONMENT"] = "test"

@fixture
def db_sesseiom():
    async def _session():
        await init_db()
        yield get_session()
        await close_session()
    return _session

@fixture
def db_create_tables():
    async def _init():
        await init_db()
    return _init

@fixture
def db_close():
    async def _close():
        await close_session()
    return _close

@fixture
def team_db_values():
    return {
        "valid_values":[
            {
            "name": "testteam",
            "description": "A team for testing"
            },
            {
            "name": "testteam2",
            "description": "Another team for testing"
            },
        ],
        "invalid_attribute": [
            {
                "team_name": "testteam3",
                "description": "A team for testing"
            },
            {
                "name": "testteam3",
                "desc": "Another team for testing"
            },
        ],
    }

@fixture
def user_db_values():
    return {
        "valid_values":[
            {
            "name": "testuser",
            "email": "testuser@example.com"
            },
            {
            "name": "testuser2",
            "email": "testuser2@example.com",
            "team_name": "testteam"
            },
        ],
        "invalid_attribute": [
            {
                "name": "testuser3",
                "e-mail": "testuser3@example.com"
            },
            {
                "username": "testuser3",
                "email": "testuser3@example.com"
            },
        ],
        "invalid_value": [
            {
                "name": "testuser4",
                "email": "testuser4_example.com"
            },
            {
                "name": "testuser",
                "email": "testuser@example.com",
                "team_name" : "nonexistentteam"
            }
        ]
    }