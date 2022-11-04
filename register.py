import argparse
import asyncio
import logging

from environs import Env

from chat import get_connection


def create_args_parser():
    description = (
        'The script registers the chat user: '
        'it creates a token file, that contains your nickname and account hash'
    )
    parser = argparse.ArgumentParser(description=description)

    parser.add_argument(
        '--nickname',
        metavar='{nickname}',
        help='Your nickname in the chat (obligatory)',
        required=True,
    )

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
        help='The chat port, 5050 by default',
        type=int,
    )

    parser.add_argument(
        '--token_path',
        metavar='{token path}',
        help='A path to a file to be created, token.json by default',
    )

    return parser


async def register(reader, writer, token_path, nickname):
    response = await reader.readline()
    logging.debug('response: %s', response.decode().strip())

    writer.write('\n'.encode())
    await writer.drain()
    logging.debug('submit: the token request')

    response = await reader.readline()
    logging.debug('response: %s', response.decode().strip())

    clear_nickname = nickname.replace('\n', '')
    writer.write(f'{clear_nickname}\n'.encode('utf-8'))
    await writer.drain()
    logging.debug('submit: the nickname: %s', clear_nickname)

    response = await reader.readline()
    decoded_response = response.decode().strip()
    logging.debug('response: %s', decoded_response)

    with open(token_path, "w", encoding="UTF-8") as token_file:
        token_file.write(decoded_response)


async def main():
    env = Env()
    env.read_env()
    args_parser = create_args_parser()
    args = args_parser.parse_args()
    if args.host:
        host = args.host
    else:
        host = env('CHAT_HOST', 'minechat.dvmn.org')

    if isinstance(args.port, int):
        port = args.port
    else:
        port = env.int('SEND_PORT', 5050)

    debug_mode = args.debug_mode or env.bool('DEBUG_MODE', False)
    if debug_mode:
        logging.basicConfig(
            level=logging.DEBUG,
            format='%(levelname)s [%(asctime)s]  %(message)s'
        )

    if args.token_path:
        token_path = args.token_path
    else:
        token_path = env('TOKEN_PATH', 'token.json')

    async with get_connection(host, port) as connection:
        reader, writer = connection
        await register(reader, writer, token_path, args.nickname)


if __name__ == '__main__':
    asyncio.run(main())
