# Extensão de navegador (Fase 2)

Manifest V3. Adiciona "Verificar com Verifica.AI" ao menu de contexto de
qualquer `<img>`, envia a imagem para `POST /v1/analyze` e mostra o
veredito em uma notificação do sistema.

## Como testar (modo desenvolvedor)

1. Suba a API localmente (`DETECTOR_MODE=mock uvicorn app.main:app --reload`
   em `backend/`, ou `docker compose up api`).
2. Chrome/Edge: `chrome://extensions` → ative "Modo do desenvolvedor" →
   "Carregar sem compactação" → selecione esta pasta (`extension/`).
3. Clique no ícone da extensão para abrir as opções e confirmar a URL da
   API (padrão: `http://localhost:8000`).
4. Clique com o botão direito em qualquer imagem de uma página → "Verificar
   com Verifica.AI".

## Publicando

Depois de publicada (ou carregada localmente com um ID fixo), adicione a
origem `chrome-extension://<id>` (ou `moz-extension://<id>` no Firefox) à
variável `ALLOWED_EXTENSION_ORIGINS` da API — sem isso, o navegador bloqueia
a resposta por CORS. Ver `backend/.env.example` e
[`docs/extension.md`](../docs/extension.md).

## Arquivos

| Arquivo          | Papel                                                          |
| ----------------- | --------------------------------------------------------------- |
| `manifest.json`   | Permissões (`contextMenus`, `storage`, `notifications`), ícones |
| `background.js`   | Service worker: cria o menu, chama a API, dispara a notificação |
| `options.html/js` | Tela de configuração da URL da API (dev vs. produção)           |

Sem etapa de build — JS puro, carregado diretamente pelo navegador.
