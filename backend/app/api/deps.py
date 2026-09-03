from collections.abc import AsyncGenerator

from fastapi import Depends, Header, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db_session
from app.detectors.base import Detector
from app.detectors.registry import get_detector
from app.models.api_client import ApiClient
from app.services.api_clients_service import authenticate


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async for session in get_db_session():
        yield session


def get_current_detector() -> Detector:
    return get_detector()


async def get_api_client(
    x_api_key: str | None = Header(default=None),
    db: AsyncSession = Depends(get_db),
) -> ApiClient:
    if not x_api_key:
        raise HTTPException(
            status.HTTP_401_UNAUTHORIZED, detail="Cabeçalho X-API-Key ausente."
        )
    client = await authenticate(db, x_api_key)
    if client is None:
        raise HTTPException(
            status.HTTP_401_UNAUTHORIZED, detail="Chave de API inválida ou inativa."
        )
    return client
