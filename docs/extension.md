# Extensão de navegador (Fase 2)

## Objetivo

Extensão Chrome/Firefox (Manifest V3) que adiciona um item de menu de
contexto em qualquer `<img>` de uma página ("Verificar com Verifica.AI"),
envia a imagem para a mesma API (`POST /v1/analyze`) e mostra o veredito.

## Status atual

Implementada em [`extension/`](../extension/) — ver
[`extension/README.md`](../extension/README.md) para instruções de teste em
modo desenvolvedor. Testada no Chrome; no Firefox, `background.service_worker`
do Manifest V3 exige Firefox 121+ (ou o fallback `background.scripts` em
versões anteriores) — não validado nesta rodada.

## Por que só foi construída depois da reestruturação da API/site

O escopo da rodada anterior foi reestruturar a API e o site com uma base
sólida e segura o bastante para suportar múltiplos clientes (site +
extensão) sem retrabalho. A extensão é um cliente HTTP a mais da mesma API —
só fazia sentido construí-la depois que o contrato (`/v1/analyze`,
`/v1/health`) estivesse estável, o que é garantido por `backend/tests/`.

## Pontos de extensão já preparados na API

- `app.core.config.Settings.ALLOWED_EXTENSION_ORIGINS`: lista de origens
  `chrome-extension://<id>` / `moz-extension://<id>` autorizadas no CORS —
  basta adicionar o ID da extensão publicada, sem alterar código.
- Rate limiting (`slowapi`) já protege `/v1/analyze` contra abuso vindo de
  qualquer cliente, extensão inclusa.
- Resposta da API é estável e tipada (`AnalysisResult`), documentada em
  `/docs` (OpenAPI) — a extensão pode ser desenvolvida contra o schema sem
  depender do código do backend.

## Estrutura implementada

```
extension/
├── manifest.json     # Manifest V3: permissions contextMenus/storage/notifications
├── background.js     # cria o menu de contexto, chama a API, mostra notificação
├── options.html/js   # configurar URL da API (dev vs. produção)
├── icons/             # 16/48/128px
└── README.md
```

## Próximos passos

- Validar no Firefox (background scripts do MV3).
- Depois de publicada, adicionar o ID real da extensão a
  `ALLOWED_EXTENSION_ORIGINS` na API (hoje só documentado, não testado
  contra uma extensão empacotada/assinada).
