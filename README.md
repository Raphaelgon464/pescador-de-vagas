# 🎣 Pescador de Vagas

Bot que busca vagas e avisa no Telegram:

- **Alerta quase instantâneo** (a cada ~5 min) quando surge uma vaga que bate com o perfil.
- **Resumo diário às 08:00 (Brasília)** com as vagas compatíveis das últimas 24h.

Roda de graça no GitHub Actions. Fontes: Trampos.co, RemoteOK e Jooble (opcional, precisa de chave).

## Configuração

Em *Settings → Secrets and variables → Actions* do repositório:

| Secret | Obrigatório | O que é |
|---|---|---|
| `TELEGRAM_TOKEN` | sim | token do bot (BotFather) |
| `CHAT_ID` | sim | seu ID no Telegram; antes, envie `/start` ao bot |
| `JOOBLE_API_KEY` | não | chave grátis em jooble.org/api/about; ativa a fonte Jooble |

Nunca coloque esses valores em arquivos do repositório (ele é público).

## Perfil de busca

Edite `src/pescador/config.py`: `KEYWORDS_INCLUSAO` (título + descrição/tags) e `KEYWORDS_EXCLUSAO` (só o título).

## Rodar localmente

```
cd src
pip install -r requirements.txt
python main.py alerta --dry-run    # imprime no console, não envia
python main.py resumo --dry-run
```

Sem `--dry-run`, defina `TELEGRAM_TOKEN` e `CHAT_ID` no ambiente. O estado local fica em `estado.json` (ignorado pelo git).

## Documentação

Comece por `docs/INDEX.md`.
