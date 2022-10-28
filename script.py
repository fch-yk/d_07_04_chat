import asyncio


async def read_chat():
    reader, writer = await asyncio.open_connection(
        host='minechat.dvmn.org',
        port=5000
    )

    while True:
        message = await reader.readline()
        if reader.at_eof():
            break
        print(message.decode().strip())

    writer.close()

if __name__ == '__main__':
    asyncio.run(read_chat())
