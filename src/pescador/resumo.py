from datetime import datetime, timedelta
from typing import List, Sequence

from pescador.matcher import Perfil
from pescador.mensagens import mensagens_de_resumo
from pescador.notifier import Notificador
from pescador.sources.base import FonteDeVagas, coletar_vagas
from pescador.store import Estado, Registro

JANELA_RESUMO = timedelta(hours=24)


def _referencia(registro: Registro) -> datetime:
    # sem data de publicação, vale quando o bot viu a vaga (spec 001, A4)
    return registro.vaga.publicada_em or registro.vista_em


def _das_ultimas_24h(estado: Estado, perfil: Perfil, agora: datetime) -> List[Registro]:
    selecionados = [
        r for r in estado.registros()
        if perfil.aceita(r.vaga) and agora - _referencia(r) <= JANELA_RESUMO
    ]
    return sorted(selecionados, key=_referencia, reverse=True)


def executar_resumo(
    fontes: Sequence[FonteDeVagas], perfil: Perfil, estado: Estado, notificador: Notificador, agora: datetime,
) -> int:
    """Envia as vagas compatíveis das últimas 24h; devolve quantas listou.

    Vagas ainda não alertadas ficam marcadas como alertadas, para o alerta
    instantâneo não repeti-las depois (spec 001, U3).
    """
    estado.registrar_todas(coletar_vagas(fontes), agora)
    registros = _das_ultimas_24h(estado, perfil, agora)
    itens = [(r.vaga, r.alertada) for r in registros]
    for texto, ids in mensagens_de_resumo(itens, agora):
        notificador.enviar(texto)
        estado.marcar_alertadas(ids)
    return len(registros)
