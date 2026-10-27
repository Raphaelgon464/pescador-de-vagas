import json
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional

from pescador.models import Vaga
from pescador.sources.datas import parse_iso

RETENCAO = timedelta(days=7)


@dataclass
class Registro:
    vaga: Vaga
    vista_em: datetime
    alertada: bool = False


class Estado:
    """Vagas já vistas e se já foram alertadas. Persistido em JSON entre execuções.

    Exemplo: estado.registrar(vaga, agora) -> True na 1ª vez, False depois.
    """

    def __init__(self, registros: Optional[Dict[str, Registro]] = None) -> None:
        self._registros: Dict[str, Registro] = {} if registros is None else registros

    def registrar(self, vaga: Vaga, agora: datetime) -> bool:
        if vaga.id in self._registros:
            return False
        self._registros[vaga.id] = Registro(vaga, agora)
        return True

    def registros(self) -> List[Registro]:
        return list(self._registros.values())

    def marcar_alertadas(self, ids: Iterable[str]) -> None:
        for id_ in ids:
            self._registros[id_].alertada = True

    def podar(self, agora: datetime) -> None:
        validos = {i: r for i, r in self._registros.items() if agora - r.vista_em <= RETENCAO}
        self._registros = validos


def _vaga_para_dict(vaga: Vaga) -> Dict[str, Any]:
    dados = asdict(vaga)
    dados['publicada_em'] = vaga.publicada_em.isoformat() if vaga.publicada_em else None
    return dados


def _vaga_de_dict(dados: Dict[str, Any]) -> Vaga:
    return Vaga(**{**dados, 'publicada_em': parse_iso(dados.get('publicada_em'))})


def _registro_de_dict(dados: Dict[str, Any]) -> Registro:
    vista_em = parse_iso(dados['vista_em'])
    if vista_em is None:
        raise ValueError(f"vista_em inválido: {dados['vista_em']!r}")
    return Registro(_vaga_de_dict(dados['vaga']), vista_em, bool(dados['alertada']))


def carregar_estado(caminho: Path) -> Estado:
    """Lê o estado; arquivo ausente = vazio. Arquivo corrompido falha alto: ignorar reenviaria tudo."""
    if not caminho.exists():
        return Estado()
    try:
        itens = json.loads(caminho.read_text(encoding='utf-8'))['registros']
        registros = [_registro_de_dict(item) for item in itens]
    except (OSError, ValueError, KeyError, TypeError) as erro:
        raise ValueError(f"Estado ilegível em {caminho}: esperado JSON {{'registros': [...]}} ({erro!r})") from erro
    return Estado({r.vaga.id: r for r in registros})


def salvar_estado(estado: Estado, caminho: Path) -> None:
    itens = [
        {'vaga': _vaga_para_dict(r.vaga), 'vista_em': r.vista_em.isoformat(), 'alertada': r.alertada}
        for r in estado.registros()
    ]
    temporario = caminho.with_suffix('.tmp')
    temporario.write_text(json.dumps({'registros': itens}, ensure_ascii=False), encoding='utf-8')
    temporario.replace(caminho)
