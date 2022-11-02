import argparse
import asyncio
import datetime
import logging
import socket


import aiofiles
from environs import Env


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
    reader = writer = None
    date_format = '%d.%m.%y %H:%M'
    error_delay = 1
    history_file = await aiofiles.open(file_path, mode='a', encoding='utf-8')

    while True:
        try:
            if not reader:
                reader, writer = await asyncio.open_connection(
                    host=host,
                    port=port
                )

                now = datetime.datetime.now()
                history_line = f'[{now.strftime(date_format)}] Connected'
                logging.debug('listener: %s', history_line)
                await history_file.write(f'{history_line}\n')

            message = await reader.readline()
            if reader.at_eof():
                break
            now = datetime.datetime.now()
            history_line = f'[{now.strftime(date_format)}] {message.decode()}'
            logging.debug('listener: %s', history_line.strip())
            await history_file.write(history_line)

            error_delay = 1

        except (ConnectionAbortedError, socket.gaierror) as fail:
            history_line = f'Unable to connect: {fail}'
            logging.debug('listener: Unable to connect: %s', fail)
            await history_file.write(f'{history_line}\n')
            await asyncio.sleep(error_delay)
            reader = None
            error_delay = 15

    await history_file.close()
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
