from datetime import datetime, timedelta
from typing import List, Sequence

from pescador.matcher import Perfil
from pescador.mensagens import mensagens_de_alerta
from pescador.models import Vaga
from pescador.notifier import Notificador
from pescador.sources.base import FonteDeVagas, coletar_vagas
from pescador.store import Estado

# Vaga velha vista pela 1ª vez (ex.: 1ª execução) não é "nova": registra sem alertar.
JANELA_ALERTA = timedelta(hours=48)


def _recente(vaga: Vaga, agora: datetime) -> bool:
    return vaga.publicada_em is None or agora - vaga.publicada_em <= JANELA_ALERTA


def _pendentes(estado: Estado, perfil: Perfil, agora: datetime) -> List[Vaga]:
    return [
        r.vaga for r in estado.registros()
        if not r.alertada and perfil.aceita(r.vaga) and _recente(r.vaga, agora)
    ]


def executar_alerta(
    fontes: Sequence[FonteDeVagas], perfil: Perfil, estado: Estado, notificador: Notificador, agora: datetime,
) -> int:
    """Alerta vagas novas que batem com o perfil; devolve quantas foram enviadas.

    Cada mensagem enviada com sucesso marca suas vagas como alertadas na hora: se um envio
    falhar, o que já foi entregue não é repetido e o resto é tentado na próxima execução.
    """
    estado.registrar_todas(coletar_vagas(fontes), agora)
    pendentes = _pendentes(estado, perfil, agora)
    if not pendentes:
        return 0
    for texto, ids in mensagens_de_alerta(pendentes, agora):
        notificador.enviar(texto)
        estado.marcar_alertadas(ids)
    return len(pendentes)
