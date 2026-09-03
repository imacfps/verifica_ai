"""Regressão do caso real que motivou o ensemble (ver docs/public_api.md e
a conversa que criou este arquivo): uma foto real (`red_carpet_real.jpg`,
450px) enviada ao Gemini pedindo "melhorar qualidade/brilho/contraste"
voltou upscalada para 1024px (`red_carpet_gemini_upscaled.jpg`) e, sem
nenhum detector real rodando (fallback silencioso pro MockDetector — ver
app/detectors/mock.py), foi classificada como "real".

As duas imagens são a mesma foto de tapete vermelho de uma pessoa pública
(Dwayne Johnson) — usada aqui com autorização explícita do usuário, ciente
do risco de direitos autorais de fixar essa foto específica no repositório.

Achado honesto (medido, não hipotético): o `FrequencyDetector` sozinho
erra a direção neste caso específico (pontua a versão real mais alta que a
gerada) — a heurística espectral não captura bem upscaling leve como este.
Quem carrega o sinal correto aqui é o baseline HF. O teste abaixo cobra do
`EnsembleDetector` como um todo, não de cada sinal isoladamente — é
exatamente por isso que a combinação existe.
"""

from pathlib import Path

from PIL import Image

from app.detectors.ensemble import EnsembleDetector

_FIXTURES = Path(__file__).parent / "fixtures"


def test_ensemble_scores_gemini_upscaled_version_higher_than_the_real_photo():
    real = Image.open(_FIXTURES / "red_carpet_real.jpg")
    gemini_upscaled = Image.open(_FIXTURES / "red_carpet_gemini_upscaled.jpg")

    detector = EnsembleDetector()
    prob_real = detector.predict(real)
    prob_gemini = detector.predict(gemini_upscaled)

    # Não exigimos que ultrapasse o limiar de 0.5 (label "ai-generated") —
    # isso dependeria de pesos calibrados que ainda não existem (ver
    # docstring do EnsembleDetector). O que importa aqui é a direção:
    # a versão processada pelo Gemini deve pontuar mensuravelmente mais
    # "IA" que a original, ao contrário do que o MockDetector produzia.
    assert prob_gemini > prob_real
    assert prob_gemini - prob_real > 0.1
