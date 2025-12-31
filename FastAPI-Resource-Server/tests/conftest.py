import os
from pytest import fixture

os.environ["PYTEST_ASYNCIO_MODE"] = "auto"
os.environ["ENVIRONMENT"] = "test"

@fixture
def user_db_values():
    return {
        "valid_values":
        {
        "username": "testuser",
        "email": "testuser@example.com"
        },
        "invalid_attribute":
        {
            "username": "testuser2",
            "e-mail": "testuser2@example.com"
        },
        "invalid_value":
        {
            "username": "testuser3",
            "email": "testuser3_example.com"
        }
    }