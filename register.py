import argparse
import asyncio
import logging

from environs import Env

from chat import get_connection, submit_message


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

    await submit_message(writer, '', 1)
    logging.debug('submit: the token request')

    response = await reader.readline()
    logging.debug('response: %s', response.decode().strip())

    await submit_message(writer, nickname, 1)
    logging.debug('submit: the nickname: %s', nickname)

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
    host = args.host or env('CHAT_HOST', 'minechat.dvmn.org')
    port = args.port or env.int('SEND_PORT', 5050)
    token_path = args.token_path or env('TOKEN_PATH', 'token.json')
    debug_mode = args.debug_mode or env.bool('DEBUG_MODE', False)
    if debug_mode:
        logging.basicConfig(
            level=logging.DEBUG,
            format='%(levelname)s [%(asctime)s]  %(message)s'
        )

    async with get_connection(host, port) as connection:
        reader, writer = connection
        await register(reader, writer, token_path, args.nickname)


if __name__ == '__main__':
    asyncio.run(main())
