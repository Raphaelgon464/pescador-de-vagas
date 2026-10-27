import logging
from datetime import datetime, timedelta
from typing import List

from pescador.models import Vaga
from pescador.sources.base import FonteDeVagas
from pescador.store import Estado

log = logging.getLogger('pescador.fontes')


class FonteLimitada:
    """Consulta a fonte no máximo uma vez por `intervalo`, lembrando a última consulta no Estado.

    Existe por causa de cotas de API (ex.: Adzuna grátis = 250/dia, 2500/mês) incompatíveis
    com o polling de 5 min. Guardar a hora no estado, e não olhar o relógio, tolera os
    atrasos do cron do GitHub. A consulta é registrada antes da chamada: falha também gasta cota.

    Exemplo: FonteLimitada(adzuna, estado, timedelta(minutes=30), agora)
    """

    def __init__(self, fonte: FonteDeVagas, estado: Estado, intervalo: timedelta, agora: datetime) -> None:
        self._fonte = fonte
        self._estado = estado
        self._intervalo = intervalo
        self._agora = agora
        self.nome = fonte.nome

    def buscar(self) -> List[Vaga]:
        ultima = self._estado.ultima_consulta(self.nome)
        if ultima is not None and self._agora - ultima < self._intervalo:
            log.info('fonte=%s pulada: última consulta há %s (intervalo %s)', self.nome, self._agora - ultima, self._intervalo)
            return []
        self._estado.registrar_consulta(self.nome, self._agora)
        return self._fonte.buscar()
