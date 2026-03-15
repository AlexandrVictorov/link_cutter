import pytest
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession

from models.models import Link, Link_click


@pytest.mark.anyio
async def test_full_flow_create_redirect_stats(authenticated_client, active_client, db_session: AsyncSession):
    resp_create = await authenticated_client.post(
        "/links/shorten",
        json={
            "original_url": "http://example.com/full",
            "length": 6,
        },
    )
    assert resp_create.status_code == 200
    data_create = resp_create.json()
    short_link = data_create["short_link"]
    short_code = short_link.rsplit("/", 1)[-1]

    resp_redirect = await authenticated_client.get(f"/links/{short_code}", follow_redirects=False)
    assert resp_redirect.status_code == 307
    assert resp_redirect.headers["location"] == "http://example.com/full"

    resp_stats = await active_client.get(f"/links/{short_code}/stats")
    assert resp_stats.status_code == 200
    data_stats = resp_stats.json()
    assert data_stats["Original_URL"] == "http://example.com/full"
    assert isinstance(data_stats["Clicks"], int)


@pytest.mark.anyio
async def test_search_live_links(authenticated_client, db_session: AsyncSession):
    url = "http://example.com/functional"
    link1 = Link(
        original_url=url,
        short_code="func1",
        created_at=datetime.now(),
        user_id=1,
    )
    link2 = Link(
        original_url=url,
        short_code="func2",
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
    assert set(data["aliases"]) == {"func1", "func2"}


@pytest.mark.anyio
async def test_livetime_and_stats(active_client, db_session: AsyncSession):
    alias = "func_life"
    link = Link(
        original_url="http://example.com/life",
        short_code=alias,
        created_at=datetime.now(),
        user_id=1,
        last_used_at=datetime.now(),
    )
    db_session.add(link)
    await db_session.commit()
    await db_session.refresh(link)

    expires_at = (datetime.now() + timedelta(days=2)).replace(second=0, microsecond=0)

    resp_live = await active_client.post(
        "/live/links/shorten",
        json={
            "alias": alias,
            "expires_at": expires_at.isoformat(),
        },
    )
    assert resp_live.status_code == 200

    resp_stats = await active_client.get(f"/links/{alias}/stats")
    assert resp_stats.status_code == 200
