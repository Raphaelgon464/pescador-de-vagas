import re
import unicodedata
from typing import Iterable, List, Pattern

from pescador.models import Vaga


def normalizar(texto: str) -> str:
    """Minúsculas e sem acentos, para 'sênior' e 'senior' serem a mesma palavra."""
    decomposto = unicodedata.normalize('NFKD', texto.casefold())
    return ''.join(c for c in decomposto if not unicodedata.combining(c))


def _padrao(palavra: str) -> str:
    # Só exige fronteira onde a ponta é letra/dígito: '.net' casa em 'asp.net'; 'ti' não casa em 'analista'.
    chave = normalizar(palavra)
    antes = r'(?<!\w)' if chave[0].isalnum() else ''
    depois = r'(?!\w)' if chave[-1].isalnum() else ''
    return antes + re.escape(chave) + depois


def _compilar(palavras: Iterable[str]) -> Pattern[str]:
    return re.compile('|'.join(_padrao(p) for p in palavras))


class Perfil:
    """Decide se uma vaga interessa. Inclusão olha título+contexto; exclusão só o título.

    Exemplo: Perfil(['python'], ['senior']).aceita(vaga) -> True para 'Dev Python Jr'.
    """

    def __init__(self, inclusao: List[str], exclusao: List[str]) -> None:
        self._inclusao = _compilar(inclusao)
        self._exclusao = _compilar(exclusao)

    def aceita(self, vaga: Vaga) -> bool:
        if self._exclusao.search(normalizar(vaga.titulo)):
            return False
        return bool(self._inclusao.search(normalizar(f"{vaga.titulo} {vaga.contexto}")))
