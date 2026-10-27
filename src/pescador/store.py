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

    def __init__(
        self, registros: Optional[Dict[str, Registro]] = None, consultas: Optional[Dict[str, datetime]] = None,
    ) -> None:
        self._registros: Dict[str, Registro] = {} if registros is None else registros
        self._consultas: Dict[str, datetime] = {} if consultas is None else consultas

    def ultima_consulta(self, fonte: str) -> Optional[datetime]:
        return self._consultas.get(fonte)

    def registrar_consulta(self, fonte: str, quando: datetime) -> None:
        self._consultas[fonte] = quando

    def consultas(self) -> Dict[str, datetime]:
        return dict(self._consultas)

    def registrar(self, vaga: Vaga, agora: datetime) -> bool:
        if vaga.id in self._registros:
            return False
        self._registros[vaga.id] = Registro(vaga, agora)
        return True

    def registrar_todas(self, vagas: Iterable[Vaga], agora: datetime) -> None:
        for vaga in vagas:
            self.registrar(vaga, agora)

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


def _data_obrigatoria(texto: Any) -> datetime:
    data = parse_iso(texto)
    if data is None:
        raise ValueError(f"data inválida: {texto!r}; esperado ISO-8601")
    return data


def _registro_de_dict(dados: Dict[str, Any]) -> Registro:
    return Registro(_vaga_de_dict(dados['vaga']), _data_obrigatoria(dados['vista_em']), bool(dados['alertada']))


def carregar_estado(caminho: Path) -> Estado:
    """Lê o estado; arquivo ausente = vazio. Arquivo corrompido falha alto: ignorar reenviaria tudo."""
    if not caminho.exists():
        return Estado()
    try:
        bruto = json.loads(caminho.read_text(encoding='utf-8'))
        registros = [_registro_de_dict(item) for item in bruto['registros']]
        consultas = {nome: _data_obrigatoria(valor) for nome, valor in bruto.get('consultas', {}).items()}
    except (OSError, ValueError, KeyError, TypeError, AttributeError) as erro:
        raise ValueError(f"Estado ilegível em {caminho}: esperado JSON {{'registros': [...]}} ({erro!r})") from erro
    return Estado({r.vaga.id: r for r in registros}, consultas)


def salvar_estado(estado: Estado, caminho: Path) -> None:
    itens = [
        {'vaga': _vaga_para_dict(r.vaga), 'vista_em': r.vista_em.isoformat(), 'alertada': r.alertada}
        for r in estado.registros()
    ]
    temporario = caminho.with_suffix('.tmp')
    consultas = {nome: quando.isoformat() for nome, quando in estado.consultas().items()}
    temporario.write_text(json.dumps({'registros': itens, 'consultas': consultas}, ensure_ascii=False), encoding='utf-8')
    temporario.replace(caminho)
