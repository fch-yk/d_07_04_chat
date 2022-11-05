import asyncio
from contextlib import asynccontextmanager


@asynccontextmanager
async def get_connection(host, port):
    reader, writer = await asyncio.open_connection(
        host=host,
        port=port
    )
    try:
        yield reader, writer
    finally:
        writer.close()
        await writer.wait_closed()


async def submit_message(writer, message, new_lines_number):
    message_to_submit = message.replace('\n', '')
    message_to_submit += '\n'*new_lines_number
    message_to_submit = message_to_submit.encode()
    writer.write(message_to_submit)
    await writer.drain()
