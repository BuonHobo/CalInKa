from collections import defaultdict
from typing import Awaitable, Callable, Coroutine, Self
from agent.packet.messages import IMessage, Packet
from agent.socket.PipeWriter import PipeWriter
from agent.socket.ISocket import ISocket


class Dispatcher:

    def __init__(self, pipeWriter: PipeWriter):
        self.pipeWriter = pipeWriter
        self.handlers: defaultdict[
            type[IMessage], list[Callable[[Packet, Self], Awaitable[None]]]
        ] = defaultdict(list)

    async def handle(self, data: str):
        try:
            packet = Packet.from_json(data)
            assert isinstance(packet, Packet)
        except Exception as e:
            print(f"Error: {e}")
            return
        if handlers := self.handlers.get(type(packet.message)):
            for handler in handlers:
                await handler(packet, self)

    async def register(
        self,
        message_type: type[IMessage],
        handler: Callable[[Packet, Self], Awaitable[None]],
    ):
        self.handlers[message_type].append(handler)

    async def send(self, packet: Packet):
        self.pipeWriter.write(packet.to_json())
