from typing import Any, Callable, Dict, Optional, Protocol
from urllib.parse import urlsplit

import requests

TIMEOUT_PADRAO_S = 15


class ErroHttp(Exception):
    """Falha de rede/HTTP. A mensagem nunca contém a URL completa: ela pode carregar chaves."""


class ClienteHttp(Protocol):
    def get_json(self, url: str, headers: Optional[Dict[str, str]] = None) -> Any: ...

    def post_json(self, url: str, payload: Dict[str, Any]) -> Any: ...


class ClienteRequests:
    """Implementação de ClienteHttp sobre `requests` (única fronteira com a lib)."""

    def get_json(self, url: str, headers: Optional[Dict[str, str]] = None) -> Any:
        enviar = lambda: requests.get(url, headers=headers, timeout=TIMEOUT_PADRAO_S)
        return self._json(enviar, 'GET', url)

    def post_json(self, url: str, payload: Dict[str, Any]) -> Any:
        enviar = lambda: requests.post(url, json=payload, timeout=TIMEOUT_PADRAO_S)
        return self._json(enviar, 'POST', url)

    def _json(self, enviar: Callable[[], Any], metodo: str, url: str) -> Any:
        host = urlsplit(url).netloc
        try:
            resposta = enviar()
            resposta.raise_for_status()
            return resposta.json()
        except requests.RequestException as erro:
            status = getattr(getattr(erro, 'response', None), 'status_code', None)
            raise ErroHttp(
                f"{metodo} {host} falhou (status={status}, erro={type(erro).__name__}); esperado 200 com JSON"
            ) from None
        except ValueError:
            raise ErroHttp(f"{metodo} {host} respondeu corpo que não é JSON; esperado JSON") from None
