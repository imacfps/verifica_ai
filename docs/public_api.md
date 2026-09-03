# API pública (terceiros)

Distinta do uso interno do site/extensão (`POST /v1/analyze`, sem
autenticação, restrito por CORS): `POST /v1/public/analyze` é pensada pra
outros desenvolvedores integrarem — exige uma API key e tem cota própria
por cliente.

## Obtendo uma chave

Não há endpoint HTTP de emissão (decisão deliberada — evita ter que
desenhar autenticação de admin nesta rodada). Quem administra a API roda
localmente:

```bash
cd backend && source .venv/bin/activate
python -m app.cli create-api-key --name "Nome do cliente"
```

A chave (`vai_...`) é mostrada **uma única vez** — só o hash fica no banco
(`api_clients.key_hash`). Se perder, emita outra; não há como recuperar.

## Usando

```bash
curl -X POST https://sua-api.exemplo.com/v1/public/analyze \
  -H "X-API-Key: vai_..." \
  -F "file=@imagem.jpg"
```

Mesmo contrato de resposta de `/v1/analyze` (`AnalysisResult`: `prob_ai`,
`prob_real`, `label`, `model`).

## Rate limit

`RATE_LIMIT_PUBLIC_API` (padrão `30/minute`) — por **chave de API**, não
por IP. Cada cliente tem cota independente, mesmo atrás do mesmo IP/NAT que
outro cliente.

## CORS não se aplica

CORS é um mecanismo de enforcement do **navegador** — não bloqueia chamadas
servidor-a-servidor (curl, backend de outro serviço, etc.). Um cliente
terceiro **não precisa** ser adicionado a `CORS_ORIGINS` ou
`ALLOWED_EXTENSION_ORIGINS` — essas variáveis só importam pra clientes que
rodam dentro de um navegador (o site e a extensão).

## Erros

| Status | Motivo |
|---|---|
| 401 | `X-API-Key` ausente, inválida ou desativada |
| 413 | Upload maior que `MAX_UPLOAD_MB` |
| 422 | Imagem corrompida ou tipo de conteúdo não suportado |
| 429 | Cota (`RATE_LIMIT_PUBLIC_API`) excedida |
