from __future__ import annotations

import asyncio
from collections import defaultdict
from typing import Callable, Coroutine, Self
from common.dispatch.IPacketLauncher import IPacketLauncher
from common.packet.messages import IMessage, Packet

from common.dispatch.IHandler import IHandler


class Dispatcher(IHandler):
    Handler = type[
        IHandler | Callable[[Packet, IPacketLauncher], Coroutine[None, None, None]]
    ]

    def __init__(self, packet_launcher: IPacketLauncher):
        self.__packetLauncher = packet_launcher
        self.__handlers: defaultdict[type[IMessage], list[Dispatcher.Handler]] = (
            defaultdict(list)
        )

    async def handle(self, packet: Packet):
        if handlers := self.__handlers.get(type(packet.message)):
            for handler in handlers:
                if isinstance(handler, IHandler):
                    await asyncio.get_event_loop().create_task(handler.handle(packet))
                elif isinstance(handler, Callable):
                    await asyncio.get_event_loop().create_task(
                        handler(packet, self.__packetLauncher)
                    )

    def register(
        self,
        message_type: type[IMessage],
        handler: Dispatcher.Handler,
    ):
        self.__handlers[message_type].append(handler)
