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
