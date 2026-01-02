from os import path

import pytest
from unittest.mock import MagicMock

from ports.inbound import inbound_factory

@pytest.mark.asyncio
async def test_inbound_factory(mocker):
    data_manager = inbound_factory("data")

    mock_module = MagicMock()
    mock_module.__name__ = "adapter.rest.mocked"
    mocker.patch('inspect.getmodule', return_value=mock_module)
    pub_data_manager = inbound_factory("data")

    assert data_manager.__class__.__name__ == "dataManagerImpl"
    assert pub_data_manager.__class__.__name__ == "publicCrud"

@pytest.mark.asyncio
async def test_general_data_manager(
    db_create_tables,
    db_close,
    delete_db_file,
    sample_teams_data,
    ):

    data_manager = inbound_factory("data")

    await db_create_tables()
    for team_attrs in sample_teams_data["valid_values"]:
        await data_manager.process(
            operation="create",
            entity="teams",
            **team_attrs
        )
    teams_1 = await data_manager.process(
        operation="read",
        entity="teams",
        record_name=sample_teams_data["valid_values"][0]["name"]
    )
    teams_2 = await data_manager.process(
        operation="read",
        entity="teams",
        record_name=sample_teams_data["valid_values"][1]["name"]
    )

    assert teams_1.description == sample_teams_data["valid_values"][0]["description"]
    assert teams_2.description == sample_teams_data["valid_values"][1]["description"]

    await db_close()
    delete_db_file()

    assert not path.exists("test.db")

@pytest.mark.asyncio
async def test_pub_data_manager(
    db_create_tables,
    db_close,
    delete_db_file,
    sample_teams_data,
    sample_users_data,
    mocker,
    ):

    mock_module = MagicMock()
    mock_module.__name__ = "adapter.rest.mocked"
    mocker.patch('inspect.getmodule', return_value=mock_module)
    public_data_manager = inbound_factory("data")

    assert public_data_manager.__class__.__name__ == "publicCrud"

    await db_create_tables()

    for team_attrs in sample_teams_data["valid_values"]:
        await public_data_manager.process(
            operation="create",
            entity="teams",
            **team_attrs
        )
    teams_1 = await public_data_manager.process(
        operation="read",
        entity="teams",
        record_name=sample_teams_data["valid_values"][0]["name"]
    )
    teams_2 = await public_data_manager.process(
        operation="read",
        entity="teams",
        record_name=sample_teams_data["valid_values"][1]["name"]
    )

    assert teams_1.description == sample_teams_data["valid_values"][0]["description"]
    assert teams_2.description == sample_teams_data["valid_values"][1]["description"]

    for user_attrs in sample_users_data["valid_values"]:
        await public_data_manager.process(
            operation="create",
            entity="users",
            **user_attrs
        )
    users_1 = await public_data_manager.process(
        operation="read",
        entity="users",
        record_name=sample_users_data["valid_values"][0]["name"]
    )
    users_2 = await public_data_manager.process(
        operation="read",
        entity="users",
        record_name=sample_users_data["valid_values"][1]["name"]
    )

    assert users_1.email == sample_users_data["valid_values"][0]["email"]
    assert users_2.email == sample_users_data["valid_values"][1]["email"]
    assert users_1.team_id is None
    assert users_2.team_id == teams_1.id

    await db_close()
    delete_db_file()

    assert not path.exists("test.db")