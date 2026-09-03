"""Emissão e autenticação de chaves da API pública (`/v1/public/analyze`).

A chave crua só existe em memória no momento da criação — só o hash fica
no banco (mesmo `hash_identifier` usado para os demais identificadores em
`core/security.py`). Não há como recuperar uma chave perdida, só emitir
outra.
"""

import secrets
from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import hash_identifier
from app.models.api_client import ApiClient

KEY_PREFIX = "vai_"


async def create_client(db: AsyncSession, name: str) -> tuple[ApiClient, str]:
    raw_key = KEY_PREFIX + secrets.token_urlsafe(32)
    client = ApiClient(name=name, key_hash=hash_identifier(raw_key))
    db.add(client)
    await db.commit()
    await db.refresh(client)
    return client, raw_key


async def authenticate(db: AsyncSession, raw_key: str) -> ApiClient | None:
    key_hash = hash_identifier(raw_key)
    result = await db.execute(
        select(ApiClient).where(ApiClient.key_hash == key_hash, ApiClient.is_active.is_(True))
    )
    client = result.scalar_one_or_none()
    if client is not None:
        client.last_used_at = datetime.now(UTC)
        await db.commit()
    return client
