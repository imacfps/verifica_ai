import io
import os

# Configuração de teste precisa ser definida ANTES de importar `app` (Settings
# é lida uma única vez via lru_cache no import da aplicação).
os.environ.setdefault("DETECTOR_MODE", "mock")
os.environ.setdefault("DATABASE_URL", "sqlite+aiosqlite:///./test.db")
os.environ.setdefault("ENABLE_ANALYSIS_LOGGING", "false")
os.environ.setdefault("RATE_LIMIT_ANALYZE", "1000/minute")
os.environ.setdefault("RATE_LIMIT_DEFAULT", "1000/minute")
os.environ.setdefault("CORS_ORIGINS", "http://localhost:5173")
os.environ.setdefault("LOG_JSON", "false")

import pytest
from httpx import ASGITransport, AsyncClient
from PIL import Image

from app.main import app


@pytest.fixture
async def client():
    transport = ASGITransport(app=app)
    # TrustedHostMiddleware valida o header Host — "localhost" está na allowlist
    # padrão (ALLOWED_HOSTS), diferente do "test" default do httpx.
    async with AsyncClient(transport=transport, base_url="http://localhost") as ac:
        yield ac


def make_png_bytes(
    size: tuple[int, int] = (32, 32), color: tuple[int, int, int] = (10, 20, 30)
) -> bytes:
    buf = io.BytesIO()
    Image.new("RGB", size, color).save(buf, format="PNG")
    return buf.getvalue()


@pytest.fixture
def png_bytes() -> bytes:
    return make_png_bytes()
