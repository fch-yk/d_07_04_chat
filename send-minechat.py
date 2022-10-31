import argparse
import asyncio
import json
import logging

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
        help='The chat port, 5050 by default',
        type=int,
    )

    parser.add_argument(
        '--send_hash',
        metavar='{send_hash}',
        help='Your personal chat hash',
    )

    parser.add_argument(
        '--message',
        metavar='{message}',
        help='Your message to the chat',
        default='My test message'
    )

    return parser


async def register():
    pass


async def authorise():
    pass


async def submit_message(host, port, send_hash, message):
    reader, writer = await asyncio.open_connection(
        host=host,
        port=port
    )
    response = await reader.readline()
    logging.debug('response: %s', response.decode().strip())

    writer.write(f'{send_hash}\n\n'.encode())
    await writer.drain()
    logging.debug('submit: %s', send_hash)

    response = await reader.readline()
    decoded_response = response.decode().strip()
    logging.debug('response: %s', decoded_response)
    if json.loads(decoded_response) is None:
        writer.close()
        await writer.wait_closed()
        logging.debug(
            'Unknown token: %s. Check it or register again.',
            send_hash
        )
        return

    writer.write(f'{message}\n\n'.encode())
    await writer.drain()
    logging.debug('submit: %s', message)

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

    if args.send_hash:
        send_hash = args.send_hash
    else:
        send_hash = env('SEND_HASH', 'no hash')

    debug_mode = args.debug_mode or env.bool('DEBUG_MODE', False)
    if debug_mode:
        logging.basicConfig(
            level=logging.DEBUG,
            format='%(levelname)s [%(asctime)s]  %(message)s'
        )

    asyncio.run(submit_message(host, port, send_hash, args.message))


if __name__ == '__main__':
    main()
