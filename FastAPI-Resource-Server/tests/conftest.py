import sys
from os import path, remove
project_dir_path = path.dirname(path.dirname(path.abspath(__file__)))
sys.path.append(f"{project_dir_path}/src")

import gc
from contextlib import asynccontextmanager
from asgi_lifespan import LifespanManager
from httpx import AsyncClient, ASGITransport
from fastapi import FastAPI
from pytest import fixture

from adapter.sql.models import User, Team
from adapter.sql.data_base import init_db, get_session, close_session
from adapter.rest.server import web_app


@fixture()
async def fastapi_client():
    @asynccontextmanager
    async def test_lifespan(app: FastAPI):
        await init_db()
        yield
        await close_session()
        if path.exists("test.db"):
            remove("test.db")
        gc.collect()

    web_app.router.lifespan_context = test_lifespan
    transport = ASGITransport(app=web_app)
    async with LifespanManager(web_app):
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            yield client

@fixture()
def db_tables():
    return {
        "users": User,
        "teams": Team,
    }

@fixture()
def db_create_tables():
    async def _init():
        await init_db()
    return _init

@fixture()
def db_session():
    return get_session()

@fixture()
def db_close():
    async def _close():
        await close_session()
        if path.exists("test.db"):
            remove("test.db")
        gc.collect()
    return _close

@fixture()
def sample_one_team():
    return {"name": "sampleteam", "description": "Sample team for testing"}

@fixture()
def sample_one_user():
    return {"name": "sampleuser", "email": "sample@example.com"}

@fixture()
def sample_teams_data():
    return {
        "valid_values": [
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
                "team_name": "testteam3",  # Wrong field name
                "description": "A team for testing"
            },
            {
                "name": "testteam3",
                "desc": "Another team for testing"  # Wrong field name
            },
        ],
    }

@fixture()
def sample_users_data():
    return {
        "valid_values": [
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
                "e-mail": "testuser3@example.com"  # Wrong field name
            },
            {
                "username": "testuser3",  # Wrong field name
                "email": "testuser3@example.com"
            },
        ],
        "invalid_value": [
            {
                "name": "testuser4",
                "email": "testuser4_example.com"  # Invalid email format
            },
            {
                "name": "testuser",
                "email": "testuser@example.com",
                "team_name": "nonexistentteam"  # Non-existent team
            }
        ]
    }
