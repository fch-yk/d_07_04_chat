import asyncio
import datetime
import socket
import sys

import aiofiles


async def read_chat():
    file_path = 'history.txt'
    host = 'minechat.dvmn.org'
    port = 5000
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
    asyncio.run(read_chat())
