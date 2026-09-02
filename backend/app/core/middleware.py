"""Middlewares transversais: cabeçalhos de segurança e limite de tamanho de requisição."""

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from app.core.config import get_settings


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Cabeçalhos padrão de defesa em profundidade (OWASP Secure Headers)."""

    async def dispatch(self, request: Request, call_next) -> Response:
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Referrer-Policy"] = "no-referrer"
        response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"
        response.headers["Cross-Origin-Resource-Policy"] = "same-site"
        if get_settings().ENVIRONMENT == "production":
            response.headers["Strict-Transport-Security"] = "max-age=63072000; includeSubDomains"
        return response


class MaxBodySizeMiddleware(BaseHTTPMiddleware):
    """Rejeita cedo (via Content-Length) requisições maiores que o limite configurado.

    Isso é uma primeira barreira contra DoS por payload gigante; a validação
    definitiva ainda ocorre em stream no endpoint de upload, pois o cabeçalho
    Content-Length pode ser omitido ou mentiroso.
    """

    def __init__(self, app, max_bytes: int):
        super().__init__(app)
        self.max_bytes = max_bytes

    async def dispatch(self, request: Request, call_next) -> Response:
        content_length = request.headers.get("content-length")
        if content_length is not None:
            try:
                if int(content_length) > self.max_bytes:
                    return Response(status_code=413, content="Payload excede o limite permitido.")
            except ValueError:
                pass
        return await call_next(request)
