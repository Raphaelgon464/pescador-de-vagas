import logging
from typing import Dict, List, Protocol, Sequence

from pescador.models import Vaga

log = logging.getLogger('pescador.fontes')


class FonteDeVagas(Protocol):
    nome: str

    def buscar(self) -> List[Vaga]: ...


def coletar_vagas(fontes: Sequence[FonteDeVagas]) -> List[Vaga]:
    """Junta vagas de todas as fontes, sem duplicar por id; fonte com falha vira log.

    Exemplo: coletar_vagas([RemoteOkFonte(http), JoobleFonte(http, chave, consultas)])
    """
    unicas: Dict[str, Vaga] = {}
    for fonte in fontes:
        for vaga in _buscar_isolado(fonte):
            unicas.setdefault(vaga.id, vaga)
    return list(unicas.values())


def _buscar_isolado(fonte: FonteDeVagas) -> List[Vaga]:
    try:
        return fonte.buscar()
    except Exception as erro:  # uma fonte fora do ar não pode derrubar as demais (spec 001, restrições)
        log.error('fonte=%s falhou: %s: %s', fonte.nome, type(erro).__name__, erro)
        return []
