from collections import defaultdict
from typing import Awaitable, Callable, Coroutine, Self
from common.dispatch.IPacketLauncher import IPacketLauncher
from common.packet.messages import IMessage, Packet


class Dispatcher:

    def __init__(self, packet_launcher: IPacketLauncher):
        self.__packetLauncher = packet_launcher
        self.__handlers: defaultdict[
            type[IMessage], list[Callable[[Packet, IPacketLauncher], Awaitable]]
        ] = defaultdict(list)

    async def dispatch(self, packet: Packet):
        if handlers := self.__handlers.get(type(packet.message)):
            for handler in handlers:
                await handler(packet, self.__packetLauncher)

    def register(
        self,
        message_type: type[IMessage],
        handler: Callable[[Packet, IPacketLauncher], Awaitable],
    ):
        self.__handlers[message_type].append(handler)

    async def send(self, packet: Packet):
        await self.__packetLauncher.send(packet)
