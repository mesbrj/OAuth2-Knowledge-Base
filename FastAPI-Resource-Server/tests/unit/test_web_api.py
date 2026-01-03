from pytest import mark


@mark.anyio
async def test_health_check(fastapi_client):
    response = await fastapi_client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


@mark.anyio
async def test_create_team(fastapi_client, sample_teams_data):
    team_data = sample_teams_data["valid_values"][0]
    response = await fastapi_client.post("/teams", json=team_data)

    assert response.status_code == 201

    data = response.json()

    assert data["record_name"] == team_data["name"]
    assert data["entity"] == "teams"
    assert "record_id" in data


@mark.anyio
async def test_create_user(fastapi_client, sample_users_data):
    user_data = sample_users_data["valid_values"][0]
    response = await fastapi_client.post("/users", json=user_data)

    assert response.status_code == 201

    data = response.json()

    assert data["record_name"] == user_data["name"]
    assert data["entity"] == "users"
    assert "record_id" in data