# Verifica.AI — Detector de imagens geradas por IA

Protótipo de TCC (Engenharia da Computação). Classifica imagens como **reais**
ou **geradas por IA**, retornando uma probabilidade.

## Estrutura

```
ai-image-detector/
├── backend/          # API FastAPI + modelo detector
│   ├── main.py       # endpoints /analyze e /health
│   ├── detector.py   # abstração do modelo (mock | pré-treinado HF)
│   └── requirements.txt
└── frontend/         # Site em React (Vite)
    └── src/
        ├── App.jsx   # upload, chamada à API, medidor de veredito
        └── styles.css
```

## Como rodar

### 1. Backend

```bash
cd backend
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt

# Modo mock (sem baixar modelo — ideal para testar o fluxo):
DETECTOR_MODE=mock python main.py

# Modo real (baixa ~350 MB do Hugging Face na 1ª execução):
pip install torch transformers
python main.py
```

A API sobe em `http://localhost:8000`. Documentação interativa (Swagger)
em `http://localhost:8000/docs` — ótimo para mostrar na pré-banca.

### 2. Frontend

```bash
cd frontend
npm install
npm run dev
```

Abra `http://localhost:5173`. O Vite faz proxy de `/api/*` para o backend,
então não há problema de CORS em desenvolvimento.

## Trocando o modelo (fase final do TCC)

Toda a lógica de inferência está isolada em `backend/detector.py`. Para usar
o modelo treinado do zero, crie uma classe com o método
`predict(image: PIL.Image) -> float` (probabilidade de ser IA) e registre-a
em `get_detector()`. Site e extensões não precisam de nenhuma alteração.

## Próximas fases

1. Extensão Chrome/Firefox (Manifest V3, menu de contexto em `<img>`)
2. Treinamento do modelo próprio (dataset: CIFAKE → GenImage)
3. Calibração de probabilidades e avaliação cross-generator

## Aviso

O resultado é **probabilístico** e não constitui prova de autenticidade.
Detectores de imagens sintéticas têm limitações conhecidas de generalização.
