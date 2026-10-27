from typing import Any, Dict, List

from pescador.http import ClienteHttp
from pescador.models import Vaga
from pescador.sources.datas import parse_iso

URL = 'https://trampos.co/api/v2/opportunities?page={pagina}'
LINK_VAGA = 'https://trampos.co/oportunidades/{id}'
HEADERS = {'User-Agent': 'Mozilla/5.0 (pescador-de-vagas)', 'Accept': 'application/json'}
PAGINAS_PADRAO = 2  # feed vem do mais novo ao mais antigo, 12 por página; polling de 5 min só precisa do topo


class TramposFonte:
    """Trampos.co (BR). A API ignora filtros de busca: o filtro por perfil é feito localmente.

    Endpoint não documentado oficialmente (robots.txt permite); pode mudar sem aviso.
    """
    nome = 'trampos'

    def __init__(self, http: ClienteHttp, paginas: int = PAGINAS_PADRAO) -> None:
        self._http = http
        self._paginas = paginas

    def buscar(self) -> List[Vaga]:
        vagas: List[Vaga] = []
        for pagina in range(1, self._paginas + 1):
            resposta = self._http.get_json(URL.format(pagina=pagina), headers=HEADERS)
            vagas.extend(_para_vaga(item) for item in _itens(resposta))
        return vagas


def _itens(resposta: Any) -> List[Dict[str, Any]]:
    if not isinstance(resposta, dict) or not isinstance(resposta.get('opportunities'), list):
        raise ValueError(f"Trampos: esperado objeto JSON com lista 'opportunities', recebido {type(resposta).__name__}")
    return [o for o in resposta['opportunities'] if isinstance(o, dict) and 'id' in o]


def _para_vaga(item: Dict[str, Any]) -> Vaga:
    empresa = item.get('custom_company_name') or (item.get('company') or {}).get('name') or 'N/A'
    return Vaga(
        id=f"trampos_{item['id']}",
        fonte='trampos',
        titulo=str(item.get('name', '')),
        empresa=str(empresa),
        local='Brasil (híbrido)' if item.get('hybrid') else 'Brasil',
        remoto=bool(item.get('home_office')),
        link=LINK_VAGA.format(id=item['id']),
        publicada_em=parse_iso(item.get('published_at')),
        contexto=str(item.get('category_name') or ''),
    )
