# Banco de imagens consolidado (Fase 2)

## Objetivo

Dataset curado para treinar e avaliar o detector focado especificamente no
gerador de imagens do **Gemini** (Imagen 3, "Nano Banana" e sucessores),
complementando os detectores genéricos usados hoje (mock / HuggingFace).

## Status atual

O detector próprio (`GeminiDetectorModel`, transfer learning sobre
ResNet-18) e o pipeline de treino/avaliação já existem em
`backend/app/detectors/gemini*.py` e `backend/training/` (ver
[`training/README.md`](../backend/training/README.md)). O que falta é o
**dado em si**: hoje o treino lê de uma pasta local (`data/train/...`); o
banco de imagens consolidado abaixo é o que vai alimentar essa pasta em
escala, com proveniência rastreada.

O schema do catálogo já está modelado em
`backend/app/models/dataset_image.py` e versionado na migração
`0001_initial`:

| Campo         | Descrição                                                        |
|---------------|--------------------------------------------------------------------|
| `sha256`      | Hash do conteúdo — deduplicação automática                        |
| `label`       | `real` \| `ai_generated`                                          |
| `generator`   | Gerador de origem quando `ai_generated` (ex.: `gemini-2`, `imagen-3`) |
| `split`       | `train` \| `validation` \| `test`                                 |
| `storage_path`| Caminho no object storage (MinIO/S3) — o Postgres guarda só metadado |
| `source_note` | Proveniência (dataset público, geração própria, etc.)             |

Ainda **não há endpoints de ingestão** expostos pela API — este é o
próximo passo de implementação, não algo pendente de decisão de design.

## Próximos passos

1. Object storage (MinIO em dev, S3-compatible em produção) para os arquivos
   de imagem; Postgres guarda apenas metadados (nunca blobs).
2. Endpoints administrativos autenticados (`POST /v1/admin/dataset/images`)
   para ingestão em lote — fora do escopo do site público.
3. Pipeline de geração própria via API do Gemini (imagens sintéticas com
   proveniência garantida) + curadoria de imagens reais (ex.: CIFAKE,
   GenImage) para a classe `real`.
4. Exportar os `split`s do catálogo para a convenção de pastas usada por
   `backend/training/` e rodar `python -m training.train` — o
   `GeminiDetector` já implementa o `Detector` Protocol
   (`app/detectors/base.py`) e é ativado via `DETECTOR_MODE=gemini`.
