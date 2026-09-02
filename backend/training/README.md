# Treinando o GeminiDetector

Pipeline de treino do detector próprio (Fase 2 do TCC), focado em
diferenciar imagens reais de imagens geradas pelo Gemini.

## Instalação

```bash
cd backend
pip install -r requirements-train.txt
```

## 1. Preparar os dados

Estrutura de diretórios esperada (uma pasta por split, uma subpasta por classe):

```
data/
  train/
    real/*.jpg
    ai_generated/*.jpg
  validation/
    real/*.jpg
    ai_generated/*.jpg
  test/
    real/*.jpg
    ai_generated/*.jpg
```

Fontes recomendadas (ver [`docs/dataset.md`](../../docs/dataset.md)):
imagens reais de datasets públicos (ex.: subconjunto do CIFAKE/GenImage) e
imagens `ai_generated` geradas propositalmente pela API do Gemini, cobrindo
prompts e estilos variados para reduzir overfitting a um único padrão visual.

## 2. Treinar

```bash
python -m training.train \
  --data-dir data \
  --output models/gemini_detector.pt \
  --epochs 10 \
  --batch-size 32
```

Por padrão só a cabeça de classificação é treinada (backbone ResNet-18
congelado). Para fine-tuning completo a partir de uma época específica:

```bash
python -m training.train --unfreeze-epoch 6 --epochs 10 --lr 1e-3
```

O melhor checkpoint (menor loss de validação) é salvo em `--output`.

## 3. Avaliar no conjunto de teste

```bash
python -m training.evaluate --checkpoint models/gemini_detector.pt --data-dir data
```

Reporta acurácia, precisão, recall, F1 e ROC-AUC.

## 4. Usar na API

```bash
# backend/.env
DETECTOR_MODE=gemini
GEMINI_MODEL_PATH=models/gemini_detector.pt
```

Reinicie a API — `app/detectors/registry.py` carrega o checkpoint na
primeira chamada e o mantém em memória (singleton).

## Notas

- Checkpoints (`*.pt`) nunca são versionados no git (ver `.gitignore`) —
  são artefatos de treino, não código.
- O checkpoint é carregado com `torch.load(..., weights_only=True)`, que
  restringe o unpickling a tensores — não coloque o arquivo em um caminho
  gravável por terceiros não confiáveis.
