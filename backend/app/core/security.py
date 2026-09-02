"""Rate limiting e utilidades de segurança transversais."""

import hashlib

from slowapi import Limiter
from slowapi.util import get_remote_address

from app.core.config import get_settings

settings = get_settings()

# Limiter por IP remoto. Em produção atrás de proxy/load balancer, configurar
# ProxyHeadersMiddleware do uvicorn ou X-Forwarded-For confiável antes de expor.
limiter = Limiter(key_func=get_remote_address, default_limits=[settings.RATE_LIMIT_DEFAULT])


def hash_identifier(value: bytes | str) -> str:
    """Hash one-way estável (sha256) — usado para chaves de log sem expor dado bruto."""
    data = value.encode("utf-8") if isinstance(value, str) else value
    return hashlib.sha256(data).hexdigest()
