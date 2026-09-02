"""Application factory da API Verifica.AI."""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from app.api.v1.router import api_router
from app.core.config import get_settings
from app.core.exceptions import register_exception_handlers
from app.core.logging import configure_logging, get_logger
from app.core.middleware import MaxBodySizeMiddleware, SecurityHeadersMiddleware
from app.core.security import limiter

settings = get_settings()
configure_logging()
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Iniciando %s [%s]", settings.APP_NAME, settings.ENVIRONMENT)
    yield
    logger.info("Encerrando %s", settings.APP_NAME)


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.APP_NAME,
        description="Classifica imagens como reais ou geradas por IA (foco: gerador Gemini).",
        version="0.2.0",
        debug=settings.DEBUG,
        lifespan=lifespan,
        # Em produção, considerar desabilitar /docs e /redoc (docs_url=None).
    )

    app.state.limiter = limiter
    # slowapi tipa o handler para Exception genérica; mypy não reconhece a
    # variância como compatível, mas é o wiring padrão documentado pela lib.
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)  # type: ignore[arg-type]

    app.add_middleware(SecurityHeadersMiddleware)
    app.add_middleware(MaxBodySizeMiddleware, max_bytes=settings.MAX_UPLOAD_BYTES)

    if settings.ALLOWED_HOSTS:
        app.add_middleware(TrustedHostMiddleware, allowed_hosts=settings.ALLOWED_HOSTS)

    cors_origins = [*settings.CORS_ORIGINS, *settings.ALLOWED_EXTENSION_ORIGINS]
    app.add_middleware(
        CORSMiddleware,
        allow_origins=cors_origins,
        allow_credentials=False,
        allow_methods=["GET", "POST"],
        allow_headers=["Content-Type"],
    )

    register_exception_handlers(app)
    app.include_router(api_router, prefix=settings.API_PREFIX)

    return app


app = create_app()
