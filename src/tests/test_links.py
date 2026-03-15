import pytest
from models.models import Link
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timedelta

"""original_url: HttpUrl
    length: int = Field(default=6, ge=2, le=30)  # ge = Greater than or Equal (больше или равно); le = Less than or Equal (меньше или равно)
    alias: Optional[str] = Field(default=None, min_length=2, max_length=30)
    """

@pytest.mark.anyio
async def test_create_link(authenticated_client):
    resp = await authenticated_client.post(
        "/links/shorten",
        json={
            "original_url": "http://example.com",
            "length": 6,
        },
    )
    assert resp.status_code == 200
    data = resp.json()
    assert "short_link" in data
    assert data["short_link"].startswith("https://links/")


@pytest.mark.anyio
async def test_create_custom_link(authenticated_client):
    resp = await authenticated_client.post(
        "/links/shorten",
        json={
            "original_url": "http://example.com",
            "length": 6,
            "alias": "test",
        },
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["short_link"] == "https://links/test"


@pytest.mark.anyio
async def test_redirect_existing_link(client, db_session: AsyncSession):
    link = Link(
        original_url="http://example.com",
        short_code="testcode",
        created_at=datetime.now(),
    )
    db_session.add(link)
    await db_session.commit()
    await db_session.refresh(link)

    resp = await client.get("/links/testcode", follow_redirects=False)

    assert resp.status_code == 307
    assert resp.headers["location"] == "http://example.com"


@pytest.mark.anyio
async def test_redirect_not_found(client: "httpx.AsyncClient"):
    resp = await client.get("/links/does-not-exist", follow_redirects=False)
    
    assert resp.status_code == 404


@pytest.mark.anyio
async def test_stats_for_own_link(active_client, db_session: AsyncSession):
    link = Link(
        original_url="http://example.com",
        short_code="statcode",
        user_id=1,
        created_at=datetime.now(),
        last_used_at=datetime.now(),
    )
    db_session.add(link)
    await db_session.commit()
    await db_session.refresh(link)

    resp = await active_client.get("/links/statcode/stats")
    assert resp.status_code == 200

    data = resp.json()
    assert data["Original_URL"] == "http://example.com"
    assert isinstance(data["Clicks"], int)
    assert "Created" in data
    assert "Last_click" in data
    assert isinstance(data["Clicks_by_day"], list)


@pytest.mark.anyio
async def test_stats_not_found(active_client: "httpx.AsyncClient"):
    resp = await active_client.get("/links/unknowncode/stats")
    assert resp.status_code == 404


@pytest.mark.anyio
async def test_search_links_by_original_url(authenticated_client, db_session: AsyncSession):
    url = "http://example.com/search"
    link1 = Link(
        original_url=url,
        short_code="search1",
        created_at=datetime.now(),
        user_id=1,
    )
    link2 = Link(
        original_url=url,
        short_code="search2",
        created_at=datetime.now(),
        user_id=1,
    )
    db_session.add_all([link1, link2])
    await db_session.commit()
    await db_session.refresh(link1)
    await db_session.refresh(link2)

    resp = await authenticated_client.get(f"/live/links/search?original_url={url}")

    assert resp.status_code == 200
    data = resp.json()
    assert data["original_url"] == url
    assert set(data["aliases"]) == {"search1", "search2"}


@pytest.mark.anyio
async def test_search_links_not_found(authenticated_client):
    resp = await authenticated_client.get("/live/links/search?original_url=http://no-such-url")
    assert resp.status_code == 404


@pytest.mark.anyio
async def test_set_global_inactive_days(active_client):
    resp = await active_client.post("/live/links/shorten/set_n/45")

    assert resp.status_code == 200
    data = resp.json()
    assert "45" in data["status"]


@pytest.mark.anyio
async def test_set_livetime_for_alias(active_client, db_session: AsyncSession):

    alias = "livealias"
    link = Link(
        original_url="http://example.com/live",
        short_code=alias,
        created_at=datetime.now(),
        user_id=1,
    )
    db_session.add(link)
    await db_session.commit()
    await db_session.refresh(link)

    expires_at = (datetime.now() + timedelta(days=1)).replace(second=0, microsecond=0)

    resp = await active_client.post(
        "/live/links/shorten",
        json={
            "alias": alias,
            "expires_at": expires_at.isoformat(),
        },
    )
    assert resp.status_code == 200
    await db_session.refresh(link)
    assert link.expires_at is not None