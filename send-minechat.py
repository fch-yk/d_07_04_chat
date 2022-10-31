import argparse
import asyncio
import json
import logging
from pathlib import Path

from environs import Env


def create_args_parser():
    description = ('Listen to Minecraft chat.')
    parser = argparse.ArgumentParser(description=description)

    parser.add_argument(
        '--message',
        metavar='{message}',
        help='Your message to the chat',
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
        help='A path to your token file (a token is your account hash)',
    )

    return parser


async def authorise(host, port, token):
    reader, writer = await asyncio.open_connection(
        host=host,
        port=port
    )
    response = await reader.readline()
    logging.debug('response: %s', response.decode().strip())

    writer.write(f'{token}\n\n'.encode())
    await writer.drain()
    logging.debug('submit: %s', token)

    authorized = True
    response = await reader.readline()
    decoded_response = response.decode().strip()
    logging.debug('response: %s', decoded_response)
    if json.loads(decoded_response) is None:
        logging.debug(
            'Unknown token: %s. Check it or register again.',
            token
        )
        authorized = False

    return authorized, writer


async def submit_message(writer, message):
    clear_message = message.replace('\n', '')
    writer.write(f'{clear_message}\n\n'.encode())
    await writer.drain()
    logging.debug('submit: %s', clear_message)


async def send_message_to_chat(host, port, token, message):
    authorized, writer = await authorise(host, port, token)
    if authorized:
        await submit_message(writer, message)
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
        token_path = env('TOKEN_PATH', 'token.txt')

    if not Path(token_path).exists():
        logging.debug('Invalid token file path: %s', token_path)
        return

    with open(token_path, 'r', encoding="UTF-8") as token_file:
        token_text = token_file.read()

    token = json.loads(token_text)['account_hash']
    asyncio.run(send_message_to_chat(host, port, token, args.message))


if __name__ == '__main__':
    main()
