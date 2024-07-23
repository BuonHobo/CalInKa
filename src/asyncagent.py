import asyncio
import socket
import os


class PipeProtocol(asyncio.Protocol):
    def connection_made(self, transport: asyncio.BaseTransport) -> None:
        print("Connection made")

    def data_received(self, data):
        print("Received:", data)

    def eof_received(self):
        print("EOF received")

    def connection_lost(self, exc):
        print("Connection closed")


def reader(fd: int):
    data = os.read(fd, 1024)
    if not data:
        return
    print(data)


async def main():
    loop = asyncio.get_running_loop()
    p = PipeProtocol()
    fd = os.open("in", os.O_RDONLY)
    loop.add_reader(fd, reader, fd)


if __name__ == "__main__":
    loop = asyncio.new_event_loop()
    loop.create_task(main())
    loop.run_forever()
    # loop.run_until_complete(main())
