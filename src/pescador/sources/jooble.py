from typing import Any, Dict, List, Sequence, Tuple

from pescador.http import ClienteHttp
from pescador.models import Vaga
from pescador.sources.datas import parse_iso

URL_BASE = 'https://jooble.org/api/'
Consulta = Tuple[str, str]  # (palavras-chave, local)


class JoobleFonte:
    nome = 'jooble'

    def __init__(self, http: ClienteHttp, api_key: str, consultas: Sequence[Consulta]) -> None:
        self._http = http
        self._url = URL_BASE + api_key
        self._consultas = consultas

    def buscar(self) -> List[Vaga]:
        vagas: List[Vaga] = []
        for palavras, local in self._consultas:
            resposta = self._http.post_json(self._url, {'keywords': palavras, 'location': local})
            vagas.extend(_para_vaga(item) for item in _itens(resposta))
        return vagas


def _itens(resposta: Any) -> List[Dict[str, Any]]:
    if not isinstance(resposta, dict):
        raise ValueError(f"Jooble: esperado objeto JSON com 'jobs', recebido {type(resposta).__name__}")
    return [j for j in resposta.get('jobs') or [] if isinstance(j, dict)]


def _para_vaga(item: Dict[str, Any]) -> Vaga:
    titulo = str(item.get('title', ''))
    local = str(item.get('location') or 'Brasil')
    link = str(item.get('link') or item.get('url') or '')
    contexto = str(item.get('snippet') or item.get('description') or '')
    return Vaga(
        id=f"jooble_{item.get('id') or link}",
        fonte='jooble',
        titulo=titulo,
        empresa=str(item.get('company') or 'N/A'),
        local=local,
        remoto='remot' in f"{local} {titulo} {contexto}".lower(),
        link=link,
        publicada_em=parse_iso(item.get('updated')),
        contexto=contexto,
    )
