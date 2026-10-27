from datetime import datetime
from html import escape
from typing import List, Optional, Sequence, Tuple

from pescador.models import Vaga

LIMITE_TELEGRAM = 4096
Lote = Tuple[str, List[str]]  # (texto da mensagem, ids das vagas nela)


def _cortar(texto: str, maximo: int) -> str:
    return texto if len(texto) <= maximo else texto[: maximo - 1] + '…'


def _idade(publicada_em: Optional[datetime], agora: datetime) -> str:
    if publicada_em is None:
        return ''
    horas = int((agora - publicada_em).total_seconds() // 3600)
    if horas < 1:
        return 'publicada há menos de 1h'
    return f'publicada há {horas}h' if horas < 48 else f'publicada há {horas // 24}d'


def formatar_vaga(vaga: Vaga, agora: datetime) -> str:
    tipo = '🏠 Remoto' if vaga.remoto else '🏙️ Híbrido/Presencial'
    linhas = [
        f"💼 <b>{escape(_cortar(vaga.titulo, 200))}</b>",
        f"🏢 {escape(_cortar(vaga.empresa, 100))}",
        f"📍 {escape(_cortar(vaga.local, 100))} | {tipo}",
    ]
    idade = _idade(vaga.publicada_em, agora)
    if idade:
        linhas.append(f"🕒 {idade}")
    if vaga.link:
        linhas.append(f'🔗 <a href="{escape(_cortar(vaga.link, 500), quote=True)}">Aplicar</a>')
    return '\n'.join(linhas)


def dividir_em_mensagens(cabecalho: str, itens: Sequence[Tuple[str, str]], limite: int = LIMITE_TELEGRAM) -> List[Lote]:
    """Agrupa blocos (id, texto) em mensagens <= limite, sem perder nenhum.

    Exemplo: dividir_em_mensagens('<b>Vagas</b>', [('a', 'bloco A')]) -> [('<b>Vagas</b>\\n\\nbloco A', ['a'])]
    """
    lotes: List[Lote] = []
    texto, ids = cabecalho, []
    for id_, bloco in itens:
        candidato = f"{texto}\n\n{bloco}"
        if ids and len(candidato) > limite:
            lotes.append((texto, ids))
            texto, ids = f"{cabecalho} (cont.)\n\n{bloco}", [id_]
        else:
            texto, ids = candidato, ids + [id_]
    lotes.append((texto, ids))
    return lotes


def mensagens_de_resumo(vagas: Sequence[Tuple[Vaga, bool]], agora: datetime) -> List[Lote]:
    """Resumo diário; cada item é (vaga, já_alertada). Sem vagas, ainda avisa que o bot está vivo."""
    if not vagas:
        return [('📋 <b>RESUMO DAS ÚLTIMAS 24H</b>\n\nNenhuma vaga compatível com o perfil.', [])]
    cabecalho = f"📋 <b>RESUMO DAS ÚLTIMAS 24H</b> — {len(vagas)} vaga(s)"
    itens = [
        (v.id, formatar_vaga(v, agora) + ('\n✅ já alertada' if alertada else ''))
        for v, alertada in vagas
    ]
    return dividir_em_mensagens(cabecalho, itens)


def mensagens_de_alerta(vagas: Sequence[Vaga], agora: datetime) -> List[Lote]:
    cabecalho = f"🚨 <b>ALERTA DE VAGAS</b> — {len(vagas)} nova(s)"
    itens = [(v.id, formatar_vaga(v, agora)) for v in vagas]
    return dividir_em_mensagens(cabecalho, itens)
