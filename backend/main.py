"""
API de detecção de imagens geradas por IA.

Esqueleto para pré-banca: expõe um único endpoint POST /analyze que recebe
uma imagem e devolve a probabilidade de ela ser gerada por IA.

O modelo é encapsulado em detector.py — para trocar o detector no futuro
(ex.: modelo próprio treinado do zero), basta alterar aquele arquivo.
"""

import io

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from PIL import Image

from detector import get_detector

app = FastAPI(
    title="AI Image Detector API",
    description="Classifica imagens como reais ou geradas por IA (probabilístico).",
    version="0.1.0",
)

# CORS liberado para desenvolvimento — em produção, restrinja aos domínios
# do site e das extensões (chrome-extension://<id>, moz-extension://<id>).
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

ALLOWED_TYPES = {"image/jpeg", "image/png", "image/webp"}
MAX_SIZE_MB = 10


@app.get("/health")
def health():
    """Verificação simples de disponibilidade (útil para a extensão)."""
    detector = get_detector()
    return {"status": "ok", "model": detector.name, "mock": detector.is_mock}


@app.post("/analyze")
async def analyze(file: UploadFile = File(...)):
    """
    Recebe uma imagem (multipart/form-data) e retorna:
    {
        "prob_ai": float,      # probabilidade [0, 1] de ser gerada por IA
        "prob_real": float,    # complemento
        "label": str,          # "ai-generated" | "real"
        "model": str           # identificador do modelo usado
    }
    """
    if file.content_type not in ALLOWED_TYPES:
        raise HTTPException(
            status_code=415,
            detail=f"Formato não suportado: {file.content_type}. Use JPEG, PNG ou WebP.",
        )

    raw = await file.read()
    if len(raw) > MAX_SIZE_MB * 1024 * 1024:
        raise HTTPException(status_code=413, detail=f"Imagem excede {MAX_SIZE_MB} MB.")

    try:
        image = Image.open(io.BytesIO(raw)).convert("RGB")
    except Exception:
        raise HTTPException(status_code=422, detail="Arquivo não é uma imagem válida.")

    detector = get_detector()
    prob_ai = detector.predict(image)

    return {
        "prob_ai": round(prob_ai, 4),
        "prob_real": round(1.0 - prob_ai, 4),
        "label": "ai-generated" if prob_ai >= 0.5 else "real",
        "model": detector.name,
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
