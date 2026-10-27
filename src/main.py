import argparse
import logging
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Optional

from pescador.alerta import executar_alerta
from pescador.config import (
    CONSULTAS_JOOBLE, ESTADO_PADRAO, KEYWORDS_EXCLUSAO, KEYWORDS_INCLUSAO, carregar_segredos,
)
from pescador.http import ClienteHttp, ClienteRequests
from pescador.matcher import Perfil
from pescador.notifier import ConsoleNotificador, Notificador, TelegramNotificador
from pescador.resumo import executar_resumo
from pescador.sources.base import FonteDeVagas
from pescador.sources.jooble import JoobleFonte
from pescador.sources.remoteok import RemoteOkFonte
from pescador.store import carregar_estado, salvar_estado


_EXECUTORES = {'alerta': executar_alerta, 'resumo': executar_resumo}


def _ler_args(argv: Optional[List[str]]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description='Pescador de vagas')
    parser.add_argument('modo', choices=sorted(_EXECUTORES), help='alerta: vagas novas agora; resumo: últimas 24h')
    parser.add_argument('--dry-run', action='store_true', help='imprime no console em vez de enviar ao Telegram')
    parser.add_argument('--estado', type=Path, default=Path(os.environ.get('ESTADO_PATH', ESTADO_PADRAO)))
    return parser.parse_args(argv)


def _montar_fontes(http: ClienteHttp) -> List[FonteDeVagas]:
    fontes: List[FonteDeVagas] = [RemoteOkFonte(http)]
    chave_jooble = os.environ.get('JOOBLE_API_KEY', '').strip()
    if chave_jooble:
        fontes.append(JoobleFonte(http, chave_jooble, CONSULTAS_JOOBLE))
    return fontes


def _montar_notificador(dry_run: bool, http: ClienteHttp) -> Notificador:
    if dry_run:
        return ConsoleNotificador()
    segredos = carregar_segredos()
    return TelegramNotificador(http, segredos.telegram_token, segredos.chat_id)


def main(argv: Optional[List[str]] = None) -> int:
    args = _ler_args(argv)
    sys.stdout.reconfigure(encoding='utf-8')
    logging.basicConfig(level=logging.INFO, format='%(levelname)s %(message)s')
    http = ClienteRequests()
    notificador = _montar_notificador(args.dry_run, http)
    estado = carregar_estado(args.estado)
    agora = datetime.now(timezone.utc)
    try:
        perfil = Perfil(KEYWORDS_INCLUSAO, KEYWORDS_EXCLUSAO)
        total = _EXECUTORES[args.modo](_montar_fontes(http), perfil, estado, notificador, agora)
    finally:
        estado.podar(agora)
        salvar_estado(estado, args.estado)
    print(f"{args.modo}: {total} vaga(s) enviada(s)")
    return 0


if __name__ == '__main__':
    sys.exit(main())
