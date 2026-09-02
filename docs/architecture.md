# Arquitetura

## Visão geral

```
┌─────────────┐      HTTPS       ┌──────────────────┐      asyncpg      ┌────────────┐
│  Frontend    │ ───────────────▶ │   API (FastAPI)   │ ─────────────────▶ │ PostgreSQL │
│  (React/Vite)│ ◀─────────────── │   backend/app/     │ ◀───────────────── │            │
└─────────────┘   JSON (analyze) └──────────────────┘                     └────────────┘
                                          │
                                          ▼
                                  ┌───────────────┐
                                  │   Detector     │  (mock | HuggingFace | modelo próprio)
                                  │  (pluggable)   │
                                  └───────────────┘

Fase 2 (scaffold pronto, endpoints ainda não expostos):
  extensão de navegador ──▶ mesma API (/v1/analyze)
  banco de imagens consolidado (dataset_images) ──▶ object storage (MinIO/S3) + Postgres (metadados)
```

## Backend — camadas

- `app/api/` — rotas HTTP (FastAPI routers), sem lógica de negócio.
- `app/services/` — orquestra validação + detecção + persistência opcional.
- `app/detectors/` — abstração do modelo (`Detector` Protocol). Trocar de
  detector mock/HuggingFace para o modelo próprio treinado para o Gemini
  significa implementar essa interface e registrar em `registry.py` — nada
  em `api/` precisa mudar.
- `app/models/` — ORM (SQLAlchemy 2.0, assíncrono).
- `app/schemas/` — contratos Pydantic de entrada/saída da API.
- `app/core/` — configuração, logging, segurança, middlewares, exceções.
- `app/utils/image_validation.py` — leitura em stream e decodificação segura
  de imagens (proteção contra payloads gigantes e decompression bombs).

## Por que essas escolhas

- **FastAPI + Pydantic**: validação de schema automática, OpenAPI gerado
  (`/docs`), assíncrono nativo.
- **SQLAlchemy assíncrono + Alembic**: migrações versionadas, sem `create_all`
  mágico em produção.
- **Detector plugável**: o modelo final (treinado do zero, focado no gerador
  do Gemini) é o entregável central do TCC — a API não pode depender da sua
  implementação interna.
- **Sem armazenamento de imagem do usuário por padrão**: decisão de
  privacidade registrada em [`privacy.md`](./privacy.md).
