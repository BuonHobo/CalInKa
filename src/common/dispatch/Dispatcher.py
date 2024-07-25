from collections import defaultdict
from typing import Awaitable, Callable, Coroutine, Self
from common.dispatch.IPacketLauncher import IPacketLauncher
from common.packet.messages import IMessage, Packet
import asyncio


class Dispatcher:

    def __init__(self, packet_launcher: IPacketLauncher):
        self.__packetLauncher = packet_launcher
        self.__handlers: defaultdict[
            type[IMessage], list[Callable[[Packet, IPacketLauncher], Coroutine]]
        ] = defaultdict(list)

    async def dispatch(self, packet: Packet):
        if handlers := self.__handlers.get(type(packet.message)):
            for handler in handlers:
                asyncio.get_event_loop().create_task(
                    handler(packet, self.__packetLauncher)
                )

    def register(
        self,
        message_type: type[IMessage],
        handler: Callable[[Packet, IPacketLauncher], Coroutine],
    ):
        self.__handlers[message_type].append(handler)
