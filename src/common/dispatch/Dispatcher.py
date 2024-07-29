from __future__ import annotations

import asyncio
from collections import defaultdict
from typing import Callable, Coroutine, Self, Optional, Union

from marshmallow.utils import is_instance_or_subclass
from common.dispatch.SingletonLauncher import SingletonLauncher
from common.dispatch.IPacketLauncher import IPacketLauncher
from common.packet.messages import IMessage, Packet

from common.dispatch.IHandler import IHandler

Handler = Union[IHandler, Callable[[Packet], Coroutine[None, None, None]]]


def handler_for(kind: type[IMessage]):
    def handler(method: Handler) -> Handler:
        Dispatcher.get_instance().register(kind, method)
        return method

    return handler


class Dispatcher(IHandler):
    __instance: Optional[Dispatcher] = None

    @staticmethod
    def get_instance() -> Dispatcher:
        if Dispatcher.__instance is None:
            return Dispatcher()
        return Dispatcher.__instance

    def __init__(self):
        if self.__instance is not None:
            raise Exception("Dispatcher is a singleton")
        self.__handlers: defaultdict[type[IMessage], list[Handler]] = defaultdict(list)
        Dispatcher.__instance = self

    async def handle(self, packet: Packet):
        if handlers := self.__handlers.get(type(packet.message)):
            for handler in handlers:
                if is_instance_or_subclass(handler, IHandler):
                    await asyncio.get_event_loop().create_task(handler.handle(packet))
                elif isinstance(handler, Callable):
                    await asyncio.get_event_loop().create_task(handler(packet))

    def register(
        self,
        message_type: type[IMessage],
        handler: Handler,
    ):
        self.__handlers[message_type].append(handler)
