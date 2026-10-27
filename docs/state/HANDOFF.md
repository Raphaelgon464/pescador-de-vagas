DONE: T1–T10 do plano 001. Bot em produção no GitHub Actions (alerta */5, resumo 11:00 UTC); testado: A1/A2 (2ª execução enviou 0), resumo e Telegram OK.
NEXT: usuário cria ADZUNA_APP_ID e ADZUNA_APP_KEY (developer.adzuna.com/signup) -> gravar Secrets, rodar 1x, conferir se país `br` retorna vagas (T11).
RISKS: cron do Actions atrasa/pula; Actions desativa agendamento após 60 dias sem atividade no repo; Trampos.co é API não documentada; RemoteOK global/inglês gera ruído.
CONTEXT: docs/ARCHITECTURE.md; estado em branch `estado`; segredos em GitHub Secrets.
