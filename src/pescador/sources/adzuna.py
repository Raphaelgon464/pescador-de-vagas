import html
import re
from typing import Any, Dict, List, Sequence
from urllib.parse import urlencode

from pescador.http import ClienteHttp
from pescador.models import Vaga
from pescador.sources.datas import parse_iso

URL = 'https://api.adzuna.com/v1/api/jobs/{pais}/search/1?{params}'
_TAGS_HTML = re.compile(r'<[^>]+>')


class AdzunaFonte:
    """Adzuna, uma única chamada por busca (cota grátis é pequena: use com FonteLimitada).

    `what_or` casa vagas com QUALQUER das palavras; `sort_by=date` traz as mais novas primeiro.
    """
    nome = 'adzuna'

    def __init__(
        self, http: ClienteHttp, app_id: str, app_key: str, palavras: Sequence[str],
        pais: str = 'br', por_pagina: int = 50, max_dias: int = 2,
    ) -> None:
        self._http = http
        self._pais = pais
        self._params = {
            'app_id': app_id, 'app_key': app_key, 'what_or': ' '.join(palavras),
            'sort_by': 'date', 'max_days_old': max_dias, 'results_per_page': por_pagina,
        }

    def buscar(self) -> List[Vaga]:
        resposta = self._http.get_json(URL.format(pais=self._pais, params=urlencode(self._params)))
        return [_para_vaga(item) for item in _itens(resposta)]


def _itens(resposta: Any) -> List[Dict[str, Any]]:
    if not isinstance(resposta, dict) or not isinstance(resposta.get('results'), list):
        raise ValueError(f"Adzuna: esperado objeto JSON com lista 'results', recebido {type(resposta).__name__}")
    return [r for r in resposta['results'] if isinstance(r, dict) and 'id' in r]


def _limpar(texto: Any) -> str:
    # a Adzuna destaca termos buscados com <strong>; some no Telegram e atrapalha o matcher
    return html.unescape(_TAGS_HTML.sub('', str(texto or ''))).strip()


def _nome(objeto: Any, padrao: str) -> str:
    return _limpar(objeto.get('display_name')) if isinstance(objeto, dict) else padrao


def _para_vaga(item: Dict[str, Any]) -> Vaga:
    titulo = _limpar(item.get('title'))
    local = _nome(item.get('location'), 'Brasil') or 'Brasil'
    contexto = _limpar(item.get('description'))
    return Vaga(
        id=f"adzuna_{item['id']}",
        fonte='adzuna',
        titulo=titulo,
        empresa=_nome(item.get('company'), 'N/A') or 'N/A',
        local=local,
        remoto='remot' in f"{local} {titulo} {contexto}".lower() or 'home office' in contexto.lower(),
        link=str(item.get('redirect_url') or ''),
        publicada_em=parse_iso(item.get('created')),
        contexto=contexto,
    )
