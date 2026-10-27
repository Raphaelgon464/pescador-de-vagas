from typing import Any, Dict, Protocol

from pescador.http import ClienteHttp, ErroHttp

API_TELEGRAM = 'https://api.telegram.org/bot'


class Notificador(Protocol):
    def enviar(self, texto: str) -> None: ...


class TelegramNotificador:
    """Envia HTML ao chat configurado. O token vai na URL; ClienteHttp nunca a expõe em erros."""

    def __init__(self, http: ClienteHttp, token: str, chat_id: str) -> None:
        self._http = http
        self._url = f"{API_TELEGRAM}{token}/sendMessage"
        self._chat_id = chat_id

    def enviar(self, texto: str) -> None:
        try:
            resposta = self._http.post_json(self._url, self._payload(texto))
        except ErroHttp as erro:
            # a descrição do Telegram (ex.: 'chat not found') nunca contém o token
            raise ValueError(f"Telegram recusou a mensagem: {erro}; resposta={erro.corpo!r}") from None
        if not (isinstance(resposta, dict) and resposta.get('ok')):
            raise ValueError(f"Telegram recusou a mensagem: esperado {{'ok': true}}, recebido {resposta!r}")

    def _payload(self, texto: str) -> Dict[str, Any]:
        return {
            'chat_id': self._chat_id,
            'text': texto,
            'parse_mode': 'HTML',
            'disable_web_page_preview': True,
        }


class ConsoleNotificador:
    """Dry-run: imprime em vez de enviar."""

    def enviar(self, texto: str) -> None:
        print(texto)
        print('-' * 30)
