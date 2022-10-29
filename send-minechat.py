import argparse
import asyncio

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
    print(response.decode().strip())

    writer.write(f'{send_hash}\n\n'.encode())
    await writer.drain()

    response = await reader.readline()
    print(response.decode().strip())

    writer.write(f'{message}\n\n'.encode())
    await writer.drain()

    writer.close()
    await writer.wait_closed()


if __name__ == '__main__':
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

    asyncio.run(submit_message(host, port, send_hash, args.message))
