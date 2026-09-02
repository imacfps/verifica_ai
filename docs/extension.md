# Extensão de navegador (Fase 2)

## Objetivo

Extensão Chrome/Firefox (Manifest V3) que adiciona um item de menu de
contexto em qualquer `<img>` de uma página ("Verificar com Verifica.AI"),
envia a imagem para a mesma API (`POST /v1/analyze`) e mostra o veredito.

## Por que ainda não está implementada nesta etapa

O escopo desta rodada foi reestruturar a API e o site com uma base sólida e
seguros o bastante para suportar múltiplos clientes (site + extensão) sem
retrabalho. A extensão é um cliente HTTP a mais da mesma API — só faz
sentido construí-la depois que o contrato (`/v1/analyze`, `/v1/health`) está
estável, o que agora está garantido por `backend/tests/`.

## Pontos de extensão já preparados na API

- `app.core.config.Settings.ALLOWED_EXTENSION_ORIGINS`: lista de origens
  `chrome-extension://<id>` / `moz-extension://<id>` autorizadas no CORS —
  basta adicionar o ID da extensão publicada, sem alterar código.
- Rate limiting (`slowapi`) já protege `/v1/analyze` contra abuso vindo de
  qualquer cliente, extensão inclusa.
- Resposta da API é estável e tipada (`AnalysisResult`), documentada em
  `/docs` (OpenAPI) — a extensão pode ser desenvolvida contra o schema sem
  depender do código do backend.

## Esboço de implementação (próxima etapa)

```
extension/
├── manifest.json        # Manifest V3, permission: contextMenus, activeTab
├── background.js        # cria o menu de contexto, chama a API, mostra notificação
└── options.html          # configurar URL da API (dev vs. produção)
```
