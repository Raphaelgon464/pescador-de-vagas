import os
from dataclasses import dataclass
from typing import List, Mapping, Optional

# Perfil de busca (spec 001). Sem segredos: este arquivo é versionado em repo público.
KEYWORDS_INCLUSAO: List[str] = [
    'c#', '.net', 'python', 'power bi', 'suporte', 'analista',
    'full stack', 'api', 'jr', 'júnior', 'junior', 'assistente',
    'ti', 'tecnologia', 'desenvolvedor', 'programador', 'estágio',
    'administrativo', 'auxiliar',
]

KEYWORDS_EXCLUSAO: List[str] = [
    'senior', 'sênior', 'sr', 'lead', 'gerente', 'head',
    'diretor', 'vp',
]

CACHE_FILE = 'vagas_cache.json'
MAX_CACHE_SIZE = 500
MAX_VAGAS_POR_MENSAGEM = 10


@dataclass(frozen=True)
class Segredos:
    telegram_token: str
    chat_id: str
    jooble_api_key: Optional[str]


def _exigir(env: Mapping[str, str], nome: str) -> str:
    valor = env.get(nome, '').strip()
    if not valor:
        raise ValueError(
            f"Variável de ambiente {nome} ausente ou vazia (esperado: texto não vazio, "
            f"valor atual: {env.get(nome)!r}). Defina-a nos Secrets do GitHub ou no shell."
        )
    return valor


def carregar_segredos(env: Mapping[str, str] = os.environ) -> Segredos:
    """Lê segredos do ambiente; Jooble é opcional.

    Exemplo: carregar_segredos({'TELEGRAM_TOKEN': 't', 'CHAT_ID': '1'}).chat_id == '1'
    """
    return Segredos(
        telegram_token=_exigir(env, 'TELEGRAM_TOKEN'),
        chat_id=_exigir(env, 'CHAT_ID'),
        jooble_api_key=env.get('JOOBLE_API_KEY', '').strip() or None,
    )
