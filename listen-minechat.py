import argparse
import asyncio
import datetime
import logging
import socket

import aiofiles
from environs import Env

from chat import get_connection


def create_args_parser():
    description = ('Listen to Minecraft chat.')
    parser = argparse.ArgumentParser(description=description)

    parser.add_argument(
        '--debug_mode',
        help='Turn on debug mode',
        action="store_true",
    )

    parser.add_argument(
        '--host',
        metavar='{host}',
        help='The chat host, minechat.dvmn.org by default',
    )

    parser.add_argument(
        '--port',
        metavar='{port}',
        help='The chat port, 5000 by default',
        type=int,
    )

    parser.add_argument(
        '--file_path',
        metavar='{file path}',
        help='A path to history file, history.txt by default',
    )

    return parser


def reconnect(async_function):
    async def wrap():
        error_delay = 1
        while True:
            try:
                error_delay = 1
                await async_function()
            except (ConnectionError, socket.gaierror) as fail:
                logging.debug('listener: Unable to connect: %s', fail)
                await asyncio.sleep(error_delay)
                error_delay = 5

    return wrap


async def read_chat(reader, writer, file_path):
    async with aiofiles.open(file_path, mode='a', encoding='utf-8') as file:
        while True:
            message = await reader.readline()
            if reader.at_eof():
                break
            now = datetime.datetime.now().strftime('%d.%m.%y %H:%M')
            history_line = f'[{now}] {message.decode()}'
            logging.debug('listener: %s', history_line.strip())
            await file.write(history_line)


@reconnect
async def main():
    env = Env()
    env.read_env()
    args_parser = create_args_parser()
    args = args_parser.parse_args()

    host = args.host or env('CHAT_HOST', 'minechat.dvmn.org')
    with env.prefixed('LISTEN_'):
        port = args.port or env.int('PORT', 5000)
        file_path = args.file_path or env('FILE', 'history.txt')

    debug_mode = args.debug_mode or env.bool('DEBUG_MODE', False)
    if debug_mode:
        logging.basicConfig(
            level=logging.DEBUG,
            format='%(levelname)s [%(asctime)s]  %(message)s'
        )

    async with get_connection(host, port) as (reader, writer):
        logging.debug('listener: Connected')
        await read_chat(reader, writer, file_path)


if __name__ == '__main__':
    asyncio.run(main())
