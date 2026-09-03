"""Detector heurístico baseado em análise espectral — sem treino, sem dataset.

Modelos generativos (GANs, difusão, upsampling/super-resolução) tendem a
deixar padrões periódicos característicos no domínio de frequência —
artefatos de camadas de deconvolução/interpolação que uma foto capturada
por um sensor real não produz. Fotos reais têm espectros de potência que
decaem suavemente (~1/f); imagens sintéticas costumam ter picos anômalos
de energia em bandas de média/alta frequência.

Isto é uma heurística, não um classificador calibrado: o mapeamento
logístico abaixo (`_MIDPOINT`/`_SLOPE`) foi escolhido a olho, não ajustado
sobre um conjunto de validação rotulado (não existe um ainda — ver
docs/dataset.md). Serve como um sinal entre outros dentro do
`EnsembleDetector`, não como detector standalone de produção.

Limitação conhecida: uma imagem com um gradiente linear muito forte e
dominante numa única direção (raro em fotos reais, que têm textura/bordas
em várias orientações) pode gerar falso positivo — os múltiplos harmônicos
de um "dente de serra" decaem devagar o suficiente pra parecer um pico.
Verificado empiricamente com gradientes radiais e texturas sintéticas mais
realistas, que pontuam baixo como esperado.
"""

import numpy as np
from PIL import Image

# Raio (fração da menor dimensão) que separa a banda de baixa frequência
# (conteúdo/composição da imagem) da banda de média/alta frequência onde
# procuramos os artefatos periódicos.
_LOW_FREQ_RADIUS_FRACTION = 0.08

# Logística usada para converter a métrica de "pico espectral" (não limitada)
# em uma probabilidade [0, 1] — valores escolhidos heuristicamente.
_MIDPOINT = 6.0
_SLOPE = 1.2


def _radial_band_masks(
    height: int, width: int, low_radius_frac: float
) -> tuple[np.ndarray, np.ndarray]:
    cy, cx = height / 2, width / 2
    yy, xx = np.mgrid[0:height, 0:width]
    dist = np.sqrt((yy - cy) ** 2 + (xx - cx) ** 2)
    low_radius = low_radius_frac * min(height, width)
    low_mask = dist <= low_radius
    high_mask = ~low_mask
    return low_mask, high_mask


def _hann_window_2d(height: int, width: int) -> np.ndarray:
    # Sem janelamento, a FFT trata a imagem como periódica: qualquer
    # descontinuidade entre bordas opostas (comum em fotos reais — céu
    # claro de um lado, fundo escuro do outro) vaza energia espúria pra
    # alta frequência ("spectral leakage") e é confundida com artefato
    # sintético. A janela de Hann atenua as bordas suavemente pra zero
    # antes da transformada, eliminando esse falso positivo.
    return np.outer(np.hanning(height), np.hanning(width))


def spectral_peakiness(image: Image.Image) -> float:
    """Mede o quão "pontudo" (não suave) é o espectro de potência fora do
    núcleo de baixa frequência — quanto maior, mais provável ser sintética.
    """
    gray = np.asarray(image.convert("L"), dtype=np.float64)
    height, width = gray.shape
    gray = gray * _hann_window_2d(height, width)
    spectrum = np.fft.fftshift(np.fft.fft2(gray))
    power = np.abs(spectrum) ** 2

    low_mask, high_mask = _radial_band_masks(height, width, _LOW_FREQ_RADIUS_FRACTION)
    high_band = power[high_mask]
    if high_band.size == 0 or high_band.mean() <= 0:
        return 0.0

    # Razão entre o pico e a média da banda: um espectro real decai suave
    # (razão baixa); artefatos periódicos geram picos isolados bem acima da
    # média local (razão alta). log1p mantém a escala tratável.
    return float(np.log1p(high_band.max() / high_band.mean()))


class FrequencyDetector:
    name = "frequency-v0 (heurístico)"
    is_mock = False

    def predict(self, image: Image.Image) -> float:
        peakiness = spectral_peakiness(image)
        # Logística: converte a métrica não limitada em probabilidade.
        return float(1.0 / (1.0 + np.exp(-_SLOPE * (peakiness - _MIDPOINT))))
