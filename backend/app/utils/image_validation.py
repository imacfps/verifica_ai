"""Leitura e validação segura de imagens enviadas por upload.

Camadas de defesa aplicadas aqui:
1. Leitura em stream com corte assim que o limite de tamanho é excedido —
   nunca confia apenas no header Content-Length (pode ser ausente/falso).
2. `Image.MAX_IMAGE_PIXELS` explícito + captura de `DecompressionBombError`
   para mitigar "image bombs" (arquivos pequenos que descomprimem em
   bitmaps gigantes e esgotam memória).
3. `Image.verify()` seguido de reabertura, para rejeitar arquivos truncados
   ou que não são realmente o formato declarado.
"""

import io

from fastapi import UploadFile
from PIL import Image, UnidentifiedImageError

from app.core.config import get_settings
from app.core.exceptions import ImageValidationError

settings = get_settings()
Image.MAX_IMAGE_PIXELS = settings.MAX_IMAGE_PIXELS


async def read_upload_safely(file: UploadFile) -> bytes:
    """Lê o upload em chunks, abortando assim que ultrapassar MAX_UPLOAD_BYTES."""
    if file.content_type not in settings.ALLOWED_CONTENT_TYPES:
        raise ImageValidationError(
            f"Formato não suportado: {file.content_type}. "
            f"Use {', '.join(settings.ALLOWED_CONTENT_TYPES)}.",
            status_code=415,
        )

    max_bytes = settings.MAX_UPLOAD_BYTES
    chunks: list[bytes] = []
    total = 0
    chunk_size = 1024 * 1024

    while True:
        chunk = await file.read(chunk_size)
        if not chunk:
            break
        total += len(chunk)
        if total > max_bytes:
            raise ImageValidationError(
                f"Imagem excede {settings.MAX_UPLOAD_MB} MB.", status_code=413
            )
        chunks.append(chunk)

    if total == 0:
        raise ImageValidationError("Arquivo vazio.", status_code=422)

    return b"".join(chunks)


def decode_image_safely(raw: bytes) -> Image.Image:
    """Decodifica bytes em uma imagem PIL, rejeitando arquivos inválidos/maliciosos."""
    try:
        image = Image.open(io.BytesIO(raw))
        image.verify()  # detecta corrupção/truncamento sem carregar pixels
        # verify() invalida o objeto — precisa reabrir para uso real
        image = Image.open(io.BytesIO(raw))
        image.load()
        return image.convert("RGB")
    except Image.DecompressionBombError as exc:
        raise ImageValidationError(
            "Imagem excede o limite de dimensões permitido.", status_code=422
        ) from exc
    except (UnidentifiedImageError, OSError, ValueError) as exc:
        raise ImageValidationError("Arquivo não é uma imagem válida.", status_code=422) from exc
