import argparse
import asyncio
import datetime
import socket
import sys

import aiofiles
from environs import Env


def create_args_parser():
    description = ('Listen to Minecraft chat.')
    parser = argparse.ArgumentParser(description=description)

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

    while True:
        try:
            if not reader:
                reader, writer = await asyncio.open_connection(
                    host=host,
                    port=port
                )

                now = datetime.datetime.now()
                history_line = f'[{now.strftime(date_format)}] Connected\n'
                print(history_line, end='')
                async with aiofiles.open(
                    file_path,
                    mode='a',
                    encoding='utf-8'
                ) as history_file:
                    await history_file.write(history_line)

            message = await reader.readline()
            if reader.at_eof():
                break
            now = datetime.datetime.now()
            history_line = f'[{now.strftime(date_format)}] {message.decode()}'
            print(history_line, end='')

            async with aiofiles.open(
                file_path,
                mode='a',
                encoding='utf-8'
            ) as history_file:
                await history_file.write(history_line)

            error_delay = 1
        except (ConnectionAbortedError, socket.gaierror) as fail:
            print(f'Unable to connect: {fail}', file=sys.stderr)
            await asyncio.sleep(error_delay)
            reader = None
            error_delay = 15

    writer.close()

if __name__ == '__main__':
    env = Env()
    env.read_env()
    args_parser = create_args_parser()
    args = args_parser.parse_args()
    with env.prefixed('LISTEN_'):
        if args.host:
            host = args.host
        else:
            host = env('HOST', 'minechat.dvmn.org')

        if isinstance(args.port, int):
            port = args.port
        else:
            port = env.int('PORT', 5000)

        if args.file_path:
            file_path = args.file_path
        else:
            file_path = env('FILE', 'history.txt')

    asyncio.run(read_chat(host, port, file_path))
