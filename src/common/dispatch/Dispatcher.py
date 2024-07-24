from collections import defaultdict
from typing import Awaitable, Callable, Coroutine, Self
from common.dispatch.IPacketLauncher import IPacketLauncher
from common.packet.messages import IMessage, Packet


class Dispatcher:

    def __init__(self, packet_launcher: IPacketLauncher):
        self.__packetLauncher = packet_launcher
        self.__handlers: defaultdict[
            type[IMessage], list[Callable[[Packet, Self], Awaitable[None]]]
        ] = defaultdict(list)

    async def handle(self, data: str):
        try:
            packet = Packet.from_json(data)
            assert isinstance(packet, Packet)
        except Exception as e:
            print(f"Error: {e}")
            return
        if handlers := self.__handlers.get(type(packet.message)):
            for handler in handlers:
                await handler(packet, self)

    async def register(
        self,
        message_type: type[IMessage],
        handler: Callable[[Packet, Self], Awaitable[None]],
    ):
        self.__handlers[message_type].append(handler)

    async def send(self, packet: Packet):
        self.__packetLauncher.send(packet)
