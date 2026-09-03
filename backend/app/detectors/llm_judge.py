"""Detector zero-shot: usa a própria API do Gemini como "juiz" forense.

Não precisa de dataset nem treino — só de uma GEMINI_API_KEY. Envia a
imagem com um prompt estruturado pedindo análise de artefatos de síntese
(textura, luz/sombra, padrões repetidos, upscaling) e força saída em JSON
via `response_schema`, evitando parsing frágil de texto livre.

Limitação a documentar no TCC: um LLM multimodal generalista não é um
classificador forense especializado — a literatura mostra desempenho
mediano nesse tipo de tarefa comparado a detectores dedicados. Entra no
`EnsembleDetector` como mais um sinal, não como decisor único.
"""

from PIL import Image
from pydantic import BaseModel, Field

from app.core.config import get_settings

_FORENSIC_PROMPT = """\
Você é um analista forense de imagens. Examine esta imagem em busca de
sinais de que ela foi gerada ou editada por um modelo de IA generativa
(GAN, difusão, upscaling por IA): texturas artificiais ou repetitivas,
inconsistências de luz/sombra, bordas ou padrões geométricos anômalos,
detalhes deformados (mãos, texto, olhos), ou sinais de super-resolução
sintética. Uma foto real de câmera também pode ter sido comprimida ou
levemente editada (brilho/contraste/nitidez) sem deixar de ser real —
não confunda edição leve com geração sintética.

Responda no formato JSON pedido com sua probabilidade estimada de a
imagem ter sido gerada/sintetizada por IA (0.0 = certamente real e sem
edição sintética perceptível, 1.0 = certamente gerada/sintetizada por IA)
e uma justificativa curta.\
"""


class _ForensicVerdict(BaseModel):
    prob_ai: float = Field(ge=0.0, le=1.0)
    reasoning: str


class LlmJudgeDetector:
    name: str
    is_mock = False

    def __init__(self):
        settings = get_settings()
        if not settings.GEMINI_API_KEY:
            raise ValueError(
                "GEMINI_API_KEY não configurada — LlmJudgeDetector indisponível. "
                "Defina no .env para ativar esse sinal do ensemble."
            )

        from google import genai

        self._model = settings.GEMINI_LLM_JUDGE_MODEL
        self.name = f"llm-judge ({self._model})"
        self._client = genai.Client(api_key=settings.GEMINI_API_KEY)

    def predict(self, image: Image.Image) -> float:
        from google.genai import types

        response = self._client.models.generate_content(
            model=self._model,
            contents=[image, _FORENSIC_PROMPT],
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=_ForensicVerdict,
            ),
        )
        verdict = _ForensicVerdict.model_validate_json(response.text)
        return verdict.prob_ai
