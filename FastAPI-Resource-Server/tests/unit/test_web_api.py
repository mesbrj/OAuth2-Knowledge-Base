from pytest import mark
from httpx import ASGITransport, AsyncClient

from adapter.rest.server import web_app

@mark.anyio
async def test_health_check():
    transport = ASGITransport(app=web_app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as ac:
        response = await ac.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}