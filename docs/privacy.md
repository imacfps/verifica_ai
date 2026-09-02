# Privacidade e retenção de dados

## Decisão

Por padrão, a API **não persiste** as imagens enviadas para análise. O fluxo
é: upload → validação → decodificação em memória → inferência → resposta →
descarte. Nada é escrito em disco ou banco de dados.

Quando `ENABLE_ANALYSIS_LOGGING=true`, apenas metadados são gravados
(`analysis_logs`): hash SHA-256 da imagem, probabilidade, rótulo e nome do
modelo. Nunca os bytes da imagem, IP do usuário ou qualquer identificador
pessoal.

## Por quê

Como o site aceita uploads de imagens de terceiros por usuários anônimos,
armazenar esse conteúdo por padrão criaria uma superfície de dados pessoais
(possivelmente sensíveis) sujeita à LGPD sem uma finalidade clara — para a
fase atual do TCC (demonstração do fluxo site → API → veredito), essa
retenção não é necessária.

## Quando isso muda

O **banco de imagens consolidado** (Fase 2 — ver [`dataset.md`](./dataset.md))
é uma coleção **curada** para treinamento/avaliação, alimentada por fontes
com proveniência conhecida (datasets públicos, geração própria via API do
Gemini) — não pela captura de uploads de visitantes do site. Caso o projeto
evolua para permitir que usuários contribuam voluntariamente com imagens
para o dataset, isso exigirá um fluxo de consentimento explícito
(opt-in, termo de uso, finalidade declarada) antes de qualquer persistência.
