from __future__ import annotations

import asyncio
from collections import defaultdict
from typing import Callable, Coroutine, Self, Optional, Union
from common.dispatch.SingletonLauncher import SingletonLauncher
from common.dispatch.IPacketLauncher import IPacketLauncher
from common.packet.messages import IMessage, Packet

from common.dispatch.IHandler import IHandler


class Dispatcher(IHandler):
    Handler = Union[IHandler, Callable[[Packet], Coroutine[None, None, None]]]
    instance: Optional[Dispatcher] = None

    @staticmethod
    def get_instance() -> Dispatcher:
        if Dispatcher.instance is None:
            return Dispatcher()
        return Dispatcher.instance

    def __init__(self):
        if self.instance is not None:
            raise Exception("Dispatcher is a singleton")
        self.__handlers: defaultdict[type[IMessage], list[Dispatcher.Handler]] = (
            defaultdict(list)
        )
        Dispatcher.instance = self

    async def handle(self, packet: Packet):
        if handlers := self.__handlers.get(type(packet.message)):
            for handler in handlers:
                if isinstance(handler, IHandler):
                    await asyncio.get_event_loop().create_task(handler.handle(packet))
                elif isinstance(handler, Callable):
                    await asyncio.get_event_loop().create_task(handler(packet))

    def register(
        self,
        message_type: type[IMessage],
        handler: Dispatcher.Handler,
    ):
        self.__handlers[message_type].append(handler)
