# 001 — Alertas de vagas (instantâneo + resumo 24h)

Status: APROVADA (2026-10-27)

## Intenção
Receber no Telegram (a) um alerta assim que surgir vaga que bata com o perfil e (b) um resumo diário das vagas das últimas 24h.

## Resultados para o usuário
- U1. Vaga nova compatível chega no Telegram em até ~15 min após aparecer na fonte.
- U2. Todo dia às 08:00 (Brasil/Sao_Paulo) chega um resumo das vagas compatíveis publicadas nas últimas 24h.
- U3. A mesma vaga nunca é enviada duas vezes (nem entre alertas e resumo, que pode listá-la como "já alertada").
- U4. Poucos falsos positivos: vaga sênior/lead/gerência nunca chega.

## Perfil (decidido em 2026-10-27)
- Áreas: TI (dev, C#/.NET, Python, Power BI, suporte, análise, API) + administrativo/auxiliar/assistente.
- Nível: estágio, júnior, assistente, auxiliar. Excluir sênior, pleno+, lead, gerente, head, diretor, VP,Analista de Suporte N1.
- Local: remoto Brasil + São Paulo (presencial/híbrido).

## Restrições
- Roda no GitHub Actions (grátis), sem servidor próprio. "Instantâneo" = polling a cada 5 min, melhor esforço.
- Segredos (token Telegram, chat id, chaves de API) só por variável de ambiente; nunca no repositório.
- Falha de uma fonte não derruba as demais nem o envio.

## Critérios de aceite
- A1. Duas execuções seguidas sem vaga nova não enviam nada na segunda.
- A2. Estado de "vagas já vistas" persiste entre execuções do Actions.
- A3. Casamento por palavra inteira: "analista" não casa 'ti'; "Israel" não casa 'sr'; "sênior" exclui.
- A4. Vaga sem data de publicação confiável é tratada como "vista agora" e não entra no resumo 24h como antiga.
- A5. Nenhuma vaga nova é descartada por limite de mensagem: excedente vai em mensagens adicionais (≤ 4096 caracteres cada, HTML escapado).
- A6. Resumo diário lista só vagas com publicação nas últimas 24h.
- A7. Repositório não contém nenhum token/chave; o token atual do `config.py` foi removido do código.
- A8. Pelo menos 2 fontes com cobertura Brasil ativas (hoje só RemoteOK roda sem chave Jooble).

## Fora de escopo
- Candidatura automática, painel web, múltiplos usuários, banco de dados dedicado.
- Scraping de sites que proíbem em ToS (ex.: LinkedIn).
