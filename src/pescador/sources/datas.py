import re
from datetime import datetime, timezone
from typing import Optional

_FRACAO = re.compile(r'(\.\d{6})\d+')


def parse_iso(texto: object) -> Optional[datetime]:
    """Converte ISO-8601 em datetime UTC; None se ausente/ilegível.

    Exemplo: parse_iso('2026-10-27T10:00:00Z') -> 2026-10-27 10:00 UTC.
    Sem fuso na origem, assume UTC (Jooble não informa).
    """
    if not isinstance(texto, str) or not texto:
        return None
    limpo = _FRACAO.sub(r'\1', texto.strip().replace('Z', '+00:00'))
    try:
        data = datetime.fromisoformat(limpo)
    except ValueError:
        return None
    return data if data.tzinfo else data.replace(tzinfo=timezone.utc)


def de_epoch(segundos: object) -> Optional[datetime]:
    if isinstance(segundos, bool) or not isinstance(segundos, (int, float)) or segundos <= 0:
        return None
    return datetime.fromtimestamp(segundos, tz=timezone.utc)
