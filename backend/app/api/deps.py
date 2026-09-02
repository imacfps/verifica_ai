from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db_session
from app.detectors.base import Detector
from app.detectors.registry import get_detector


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async for session in get_db_session():
        yield session


def get_current_detector() -> Detector:
    return get_detector()
