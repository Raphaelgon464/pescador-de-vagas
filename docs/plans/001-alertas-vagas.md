# Plano 001 — Alertas de vagas
Spec: docs/specs/001-alertas-vagas.md | Status: APROVADO (2026-10-27) — repo público; exclusão de nível só no título

## Delta de arquitetura
`src/main.py` (script único) vira pacote `src/pescador/`, um módulo por responsabilidade:
- `config.py` — lê env (segredos) + perfil (keywords).
- `models.py` — `Vaga` (id, titulo, empresa, local, remoto, link, publicada_em|None, fonte).
- `matcher.py` — regex por palavra inteira; exclusão aplicada ao título.
- `store.py` — estado JSON `{id: {vaga, vista_em, alertada}}`; poda > 7 dias.
- `sources/` — `FonteDeVagas` (Protocol: `buscar() -> list[Vaga]`) + `jooble.py`, `remoteok.py`, `adzuna.py`, `gupy.py`. Lib HTTP atrás de `http.py` fino, injetado.
- `notifier.py` + `mensagens.py` — `Notificador` (Protocol); `TelegramNotificador` (escape HTML, quebra ≤ 4096) e `ConsoleNotificador` (dry-run).
- `alerta.py` / `resumo.py` — casos de uso; `main.py` escolhe modo via argumento (`alerta` | `resumo`).

Estado persistido numa branch órfã `estado` (arquivo `estado.json`), commitada pelo workflow só quando muda. `actions/cache` descartado: chaves imutáveis geram churn a cada 5 min.

Workflows: `alerta.yml` (cron */5) e `resumo.yml` (cron `0 11 * * *` = 08:00 BRT), ambos com `concurrency` para não sobrepor escrita do estado.

## Riscos
- **Custo do Actions (decisão sua):** cron de 5 min = ~288 execuções/dia (~6–8 mil min/mês). Repo **público** = minutos ilimitados; repo **privado** = 2000 min/mês, estoura. Ver OPEN.md. Sem decisão, T9 assume repo público (segredos ficam nos Secrets; só o código e as vagas ficam visíveis).
- Cron do Actions atrasa/pula execuções; e é desativado após 60 dias sem atividade no repo (commits do estado devem contar; validar).
- Fontes BR (Gupy API não oficial; Adzuna exige chave grátis) podem mudar/limitar. T8 começa com spike e só inclui o que passar.
- Irreversível: nenhuma. Token antigo exposto: revogar no BotFather (ação sua).
- Premissa registrada: exclusão (sênior, pleno, especialista, III, "analista de suporte n1" etc.) só no título; descrição só ajuda a incluir. Evita descartar "trabalhará com seniors".

## Tarefas (1 tarefa = 1 commit)
- [x] T1 Segredos por env. Goal: A7. Files: `src/pescador/config.py`, remover `src/config.py`, `.gitignore`, `src/main.py` (só o import, legado até T6). Done-check: busca pelo token e chat id antigos no repo retorna vazio; falta de env lança erro com nome da variável. Depois `git init` + commit inicial (sem segredos).
- [x] T2 Modelo `Vaga` + Protocol de fonte + migrar Jooble/RemoteOK com `publicada_em`. Goal: A4, A8 (parcial). Files: `models.py`, `http.py`, `sources/{base,jooble,remoteok}.py`. Done-check: execução local lista vagas normalizadas; falha de uma fonte loga e segue.
- [x] T3 Matcher por palavra inteira. Goal: A3, U4. Files: `matcher.py`, `config.py` (keywords). Done-check: script de verificação manual com 8 títulos (analista/Israel/sênior/pleno/suporte N1/…) imprime resultado esperado.
- [x] T4 Store persistente. Goal: A1, A2. Files: `store.py`. Done-check: duas gravações/leituras seguidas; segunda rodada vê tudo como já visto; poda funciona.
- [x] T5 Notificador (Telegram + Console). Goal: A5. Files: `notifier.py`. Done-check: 60 vagas fictícias geram N mensagens ≤ 4096 caracteres, nenhuma perdida, `<`/`&` escapados.
- [x] T6 Modo `alerta`. Goal: U1, U3, A1. Files: `alerta.py`, `main.py`. Done-check: dry-run duas vezes: 1ª lista novas, 2ª nada. Marca `alertada` só após envio com sucesso.
- [x] T7 Modo `resumo`. Goal: U2, A6. Files: `resumo.py`, `main.py`. Done-check: dry-run lista só `publicada_em` ≤ 24h; marca as já alertadas.
- [x] T8 Fontes BR: spike (Gupy, Adzuna, Programathor/Remotar: API existe? ToS? data de publicação?) → implementar as aprovadas. Goal: A8. Files: `sources/adzuna.py`, `sources/gupy.py`, `docs/decisions/LOG.md`. Done-check: ≥ 2 fontes com cobertura BR retornam vagas reais em execução local.
- [x] T9 Workflows + branch `estado` + Secrets. Goal: U1, U2, A2. Files: `.github/workflows/{alerta,resumo}.yml`, remover `buscar-vagas.yml`, `src/requirements.txt`. Done-check: `workflow_dispatch` manual envia alerta real no Telegram; 2º disparo não reenvia.
- [ ] T10 README + reconciliação. Files: `README.md`, `docs/ARCHITECTURE.md`, `docs/INDEX.md`, spec se divergiu. Done-check: INDEX lista todos os docs.

## Verificação final
Critérios A1–A8 marcados um a um; sem testes automatizados (não solicitados), done-checks acima são manuais.
