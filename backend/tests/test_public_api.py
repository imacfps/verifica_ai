import pytest

from app.db.base import Base
from app.db.session import AsyncSessionLocal, engine
from app.services.api_clients_service import create_client


@pytest.fixture(autouse=True)
async def _api_clients_table():
    # O banco de teste (sqlite local, ver conftest.py) não passa por
    # `alembic upgrade head` — cria só a tabela que este módulo precisa.
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture
async def api_key():
    async with AsyncSessionLocal() as db:
        _, raw_key = await create_client(db, "cliente de teste")
    return raw_key


async def test_public_analyze_without_key_is_rejected(client, png_bytes):
    resp = await client.post(
        "/v1/public/analyze", files={"file": ("test.png", png_bytes, "image/png")}
    )
    assert resp.status_code == 401


async def test_public_analyze_with_invalid_key_is_rejected(client, png_bytes):
    resp = await client.post(
        "/v1/public/analyze",
        files={"file": ("test.png", png_bytes, "image/png")},
        headers={"X-API-Key": "vai_nao-existe"},
    )
    assert resp.status_code == 401


async def test_public_analyze_with_valid_key_returns_same_contract_as_analyze(
    client, png_bytes, api_key
):
    resp = await client.post(
        "/v1/public/analyze",
        files={"file": ("test.png", png_bytes, "image/png")},
        headers={"X-API-Key": api_key},
    )
    assert resp.status_code == 200
    body = resp.json()
    assert 0.0 <= body["prob_ai"] <= 1.0
    assert body["label"] in {"ai-generated", "real"}


async def test_public_analyze_with_inactive_key_is_rejected(client, png_bytes):
    from sqlalchemy import select

    from app.models.api_client import ApiClient

    async with AsyncSessionLocal() as db:
        _, raw_key = await create_client(db, "cliente desativado")
        result = await db.execute(select(ApiClient).where(ApiClient.name == "cliente desativado"))
        db_client = result.scalar_one()
        db_client.is_active = False
        await db.commit()

    resp = await client.post(
        "/v1/public/analyze",
        files={"file": ("test.png", png_bytes, "image/png")},
        headers={"X-API-Key": raw_key},
    )
    assert resp.status_code == 401
