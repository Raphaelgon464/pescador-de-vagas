2026-10-27 | Hospedagem: GitHub Actions a cada 5 min | grátis, sem servidor; aceita atraso | migrar p/ VPS se atraso incomodar | -
2026-10-27 | Perfil: TI + administrativo, remoto BR + SP | escopo original do usuário, filtros mais precisos | - | -
2026-10-27 | Resumo 24h: 1x/dia às 08:00 BRT | escolha do usuário | - | -
2026-10-27 | Exclusão de nível aplicada só ao título | descrição citando "seniors" não deve descartar vaga júnior | - | -
2026-10-27 | Estado em branch órfã `estado`, não actions/cache | cache imutável gera churn a cada 5 min | - | -
2026-10-27 | Repo público; segredos só em GitHub Secrets, branch estado guarda só dados públicos das vagas | minutos ilimitados no Actions | - | -
2026-10-27 | Jooble: campos reais são 'snippet'\/'link'\/'updated' (código legado lia 'description'\/'url'); RemoteOK 'tags' é lista de strings | achado na T2 | - | -
2026-10-27 | Matcher normaliza acentos e usa fronteira de palavra; exclusão ampliada (pleno, especialista, coordenador, principal, staff, manager, III, analista de suporte n1/nível 1) | spec pede "pleno+" e N1; interpretação mais ampla de "pleno+" | - | -
2026-10-27 | Alerta só para vagas publicadas há ≤ 48h (ou sem data); mais velhas são registradas sem alertar | 1ª execução inundaria o chat com vagas antigas (RemoteOK traz até 70 dias) | - | -
2026-10-27 | Marca "alertada" por mensagem enviada, não no fim | falha no meio não duplica nem perde vagas | - | -
2026-10-27 | ErroHttp.corpo fora da mensagem; só o Telegram o exibe | URL/corpo de Jooble podem carregar chave; logs do Actions são públicos | - | -
2026-10-27 | Resumo usa publicada_em, ou vista_em se não houver data; marca as listadas como alertadas | evita repetir no alerta (U3); resumo vazio ainda envia aviso de que o bot está vivo | - | -
2026-10-27 | Fonte BR: Trampos.co (API v2 sem chave, 2 primeiras páginas, filtro local) | única fonte BR viável sem chave; robots.txt permite; API não documentada, pode mudar | - | -
2026-10-27 | Gupy descartada | sem API documentada; portal.api.gupy.io e employability-portal.gupy.io deram 404 | - | -
2026-10-27 | Jooble: consultas só em inglês com local 'Brazil' (3); removida 'Sao Paulo' | medido: pt-BR/'São Paulo'/'Brasil' retornam 0; br.jooble.org não serve a API; das 27 vagas únicas, 4 batem e todas têm 25–55 dias | - | -
2026-10-27 | Exclusões em inglês: specialist, architect, arquiteto | 'IT Specialist' passou pelo filtro | - | -
2026-10-27 | Adzuna: 1 chamada `what_or` a cada 30 min via FonteLimitada; última consulta guardada no estado | cota grátis 250/dia e 2500/mês (termos oficiais) vs 288 execuções/dia | - | -
