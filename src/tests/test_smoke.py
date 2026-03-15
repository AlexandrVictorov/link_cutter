import pytest

@pytest.mark.anyio
async def test_dummy(client):
    resp = await client.get("/")
    assert resp.status_code in (200, 404)

