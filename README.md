# Verifica.AI — Detector de imagens geradas por IA

TCC (Engenharia da Computação). Classifica imagens como **reais** ou
**geradas por IA**, com foco no gerador de imagens do **Gemini**, retornando
uma probabilidade.

O projeto tem três frentes:

1. **API** (`backend/`) — classifica imagens enviadas por upload. Pronta.
2. **Site** (`frontend/`) — upload e visualização do veredito. Pronto.
3. **Extensão de navegador** e **banco de imagens consolidado** — Fase 2,
   com pontos de extensão já preparados no código (ver [`docs/`](docs/)).

## Estrutura

```
verifica.ai/
├── backend/                 # API (FastAPI) + detector + treino do modelo
│   ├── app/
│   │   ├── api/v1/          # rotas HTTP (/health, /analyze)
│   │   ├── core/            # config, logging, segurança, middlewares
│   │   ├── detectors/       # mock | huggingface | gemini (Detector Protocol)
│   │   ├── models/          # SQLAlchemy — analysis_logs, dataset_images
│   │   ├── schemas/         # contratos Pydantic
│   │   ├── services/        # orquestra validação + inferência
│   │   └── utils/           # validação segura de upload de imagem
│   ├── training/            # pipeline de treino/avaliação do GeminiDetector
│   ├── alembic/              # migrações do banco
│   └── tests/
├── frontend/                 # Site em React (Vite)
│   └── src/
│       ├── components/       # UploadPanel, VerdictPanel, Gauge, ...
│       ├── hooks/             # useImageAnalysis
│       └── services/          # cliente da API
├── docs/                      # decisões de arquitetura, privacidade, roadmap
└── docker-compose.yml          # api + db + web
```

## Como rodar

### Opção A — Docker Compose (recomendado para demonstrar)

```bash
cp backend/.env.example backend/.env
docker compose up --build
```

- Site: http://localhost:8080
- API: http://localhost:8000/docs

### Opção B — desenvolvimento local

**1. Backend**

```bash
cd backend
python3.12 -m venv .venv && source .venv/bin/activate
pip install -r requirements-dev.txt
cp .env.example .env

# Sobe um Postgres local (ou use docker: docker compose up db -d)
alembic upgrade head

DETECTOR_MODE=mock uvicorn app.main:app --reload
```

API em `http://localhost:8000`. Docs interativas em `/docs`.

**2. Frontend**

```bash
cd frontend
npm install
npm run dev
```

Abra `http://localhost:5173`. O Vite faz proxy de `/api/*` para o backend
(sem problema de CORS em desenvolvimento).

## Testes e qualidade

```bash
# backend
cd backend && source .venv/bin/activate
pytest -v
ruff check .

# frontend
cd frontend
npm run lint
npm test
```

CI roda os dois lados a cada push/PR (`.github/workflows/ci.yml`).

## Trocando o detector

Toda a lógica de inferência está isolada atrás do `Detector` Protocol
(`backend/app/detectors/base.py`). Três implementações hoje:

| `DETECTOR_MODE` | Descrição |
|---|---|
| `mock` | determinístico, sem IA real — só para desenvolver o fluxo completo |
| `hf` | baseline pré-treinado da Hugging Face |
| `gemini` | modelo próprio (ResNet-18 + fine-tuning), treinado para o gerador do Gemini — ver [`backend/training/README.md`](backend/training/README.md) |

`auto` (padrão) tenta `gemini` → `hf` → `mock`, na ordem de qualidade.

## Segurança

- Upload validado em stream (nunca confia só no `Content-Length`), com
  limite de tamanho e proteção contra decompression bombs.
- CORS restrito por lista explícita de origens — nunca `*`.
- Rate limiting por IP em `/analyze`.
- Nenhuma imagem de usuário é persistida por padrão (ver
  [`docs/privacy.md`](docs/privacy.md)).
- Checkpoints do modelo são carregados com `torch.load(weights_only=True)`.
- Cabeçalhos de segurança (`X-Frame-Options`, `X-Content-Type-Options`, etc.)
  em API e site.

## Próximas fases

Ver [`docs/extension.md`](docs/extension.md) e [`docs/dataset.md`](docs/dataset.md).

## Aviso

O resultado é **probabilístico** e não constitui prova de autenticidade.
Detectores de imagens sintéticas têm limitações conhecidas de generalização.
