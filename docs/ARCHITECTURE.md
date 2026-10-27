# Arquitetura

Fluxo: `fontes → coletar_vagas → Estado.registrar_todas → Perfil.aceita → mensagens → Notificador → marcar_alertadas → salvar_estado`.

## Módulos (src/pescador/)
- `config.py` — segredos via env (`carregar_segredos`), keywords do perfil, consultas Jooble.
- `models.py` — `Vaga` (fonte-agnóstica; `publicada_em` pode ser None; `contexto` só ajuda a incluir).
- `http.py` — `ClienteHttp` (Protocol) + `ClienteRequests`. `ErroHttp` nunca leva a URL (chaves) na mensagem.
- `sources/` — `FonteDeVagas` (Protocol), `coletar_vagas` (dedup + isola falha por fonte), `trampos.py`, `remoteok.py`, `jooble.py`, `adzuna.py`, `datas.py`; `limitada.py` (`FonteLimitada`: 1 consulta por intervalo, última consulta guardada no `Estado` — cota de API).
- `matcher.py` — `Perfil.aceita`: fronteira de palavra, sem acento; exclusão só no título.
- `store.py` — `Estado` (vagas vistas/alertadas, poda 7 dias) + JSON. Arquivo corrompido falha alto.
- `mensagens.py` — formatação HTML escapada; `dividir_em_mensagens` ≤ 4096 chars, devolve (texto, ids).
- `notifier.py` — `Notificador` (Protocol): `TelegramNotificador`, `ConsoleNotificador` (dry-run).
- `alerta.py` / `resumo.py` — casos de uso. Alerta: janela 48h. Resumo: janela 24h.
- `src/main.py` — composição: `python main.py alerta|resumo [--dry-run] [--estado caminho]`.

## Regras que não são óbvias
- "Alertada" é marcada por mensagem enviada: falha no meio não duplica nem perde vagas.
- Resumo marca as listadas como alertadas (alerta não repete — spec U3).
- Vaga sem data conta como vista agora (`vista_em`).

## Execução (`.github/workflows/vagas.yml`)
- Dois crons: `*/5 * * * *` (alerta) e `0 11 * * *` (resumo, 08:00 BRT). `workflow_dispatch` aceita `modo`.
- Concorrência serializada (grupo `estado-vagas`): todos escrevem o mesmo estado.
- Estado em `estado.json` na branch órfã `estado`: commit único, `--amend` + force push (sem histórico crescente).
- Repo público: segredos só em GitHub Secrets; logs públicos, então nada sensível pode ser impresso.
