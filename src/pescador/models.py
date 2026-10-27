from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass(frozen=True)
class Vaga:
    """Vaga normalizada, independente da fonte.

    `contexto` guarda descrição/tags: serve só para ajudar a incluir (spec 001),
    nunca para excluir. `publicada_em` é None quando a fonte não informa data.
    """
    id: str
    fonte: str
    titulo: str
    empresa: str
    local: str
    remoto: bool
    link: str
    publicada_em: Optional[datetime]
    contexto: str = ''
