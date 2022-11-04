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


async def read_chat(host, port, file_path):
    date_format = '%d.%m.%y %H:%M'
    error_delay = 1
    history_file = await aiofiles.open(file_path, mode='a', encoding='utf-8')
    connection_fail = False
    writer = None

    while True:
        try:
            async with get_connection(host, port) as connection:
                reader, writer = connection

                now = datetime.datetime.now().strftime(date_format)
                history_line = f'[{now}] Connected'
                logging.debug('listener: %s', history_line)
                await history_file.write(f'{history_line}\n')

                while True:
                    message = await reader.readline()
                    now = datetime.datetime.now().strftime(date_format)
                    history_line = f'[{now}] {message.decode()}'
                    logging.debug('listener: %s', history_line.strip())
                    await history_file.write(history_line)

                    error_delay = 1
                    connection_fail = False

        except (ConnectionError, socket.gaierror) as fail:
            history_line = f'Unable to connect: {fail}'
            logging.debug('listener: Unable to connect: %s', fail)
            await history_file.write(f'{history_line}\n')
            connection_fail = True

        finally:
            await asyncio.sleep(error_delay)
            error_delay = 15
            if connection_fail:
                continue

            await history_file.close()
            if writer:
                writer.close()
                await writer.wait_closed()


def main():
    env = Env()
    env.read_env()
    args_parser = create_args_parser()
    args = args_parser.parse_args()

    if args.host:
        host = args.host
    else:
        host = env('CHAT_HOST', 'minechat.dvmn.org')

    with env.prefixed('LISTEN_'):
        if isinstance(args.port, int):
            port = args.port
        else:
            port = env.int('PORT', 5000)

        if args.file_path:
            file_path = args.file_path
        else:
            file_path = env('FILE', 'history.txt')

    debug_mode = args.debug_mode or env.bool('DEBUG_MODE', False)
    if debug_mode:
        logging.basicConfig(
            level=logging.DEBUG,
            format='%(levelname)s [%(asctime)s]  %(message)s'
        )

    asyncio.run(read_chat(host, port, file_path))


if __name__ == '__main__':
    main()
