from typing import Any, Dict, List

from pescador.http import ClienteHttp
from pescador.models import Vaga
from pescador.sources.datas import de_epoch, parse_iso

URL = 'https://remoteok.com/api'
HEADERS = {'User-Agent': 'Mozilla/5.0 (pescador-de-vagas)'}


class RemoteOkFonte:
    nome = 'remoteok'

    def __init__(self, http: ClienteHttp) -> None:
        self._http = http

    def buscar(self) -> List[Vaga]:
        itens = self._http.get_json(URL, headers=HEADERS)
        if not isinstance(itens, list):
            raise ValueError(f"RemoteOK: esperado list JSON, recebido {type(itens).__name__}")
        return [_para_vaga(item) for item in itens if _eh_vaga(item)]


def _eh_vaga(item: Any) -> bool:
    # o 1º elemento da API é um aviso legal, sem 'position'
    return isinstance(item, dict) and 'id' in item and 'position' in item


def _tags(item: Dict[str, Any]) -> str:
    tags = item.get('tags') or []
    return ' '.join(t.get('tag', '') if isinstance(t, dict) else str(t) for t in tags)


def _para_vaga(item: Dict[str, Any]) -> Vaga:
    return Vaga(
        id=f"rok_{item['id']}",
        fonte='remoteok',
        titulo=str(item.get('position', '')),
        empresa=str(item.get('company') or 'N/A'),
        local=str(item.get('location') or 'Global'),
        remoto=True,
        link=str(item.get('url') or item.get('apply_url') or ''),
        publicada_em=de_epoch(item.get('epoch')) or parse_iso(item.get('date')),
        contexto=_tags(item),
    )
