import asyncio
from collections import defaultdict

from src.common.dispatch.IPacketLauncher import IPacketLauncher
from src.common.packet.messages import IMessage, Packet

from src.common.dispatch.IHandler import IHandler


class Dispatcher(IHandler):

    def __init__(self, packet_launcher: IPacketLauncher):
        self.__packetLauncher = packet_launcher
        self.__handlers: defaultdict[
            type[IMessage], list[IHandler]
        ] = defaultdict(list)

    async def handle(self, packet: Packet):
        if handlers := self.__handlers.get(type(packet.message)):
            for handler in handlers:
                await asyncio.get_event_loop().create_task(
                    handler.handle(packet, self.__packetLauncher)
                )

    def register(
            self,
            message_type: type[IMessage],
            handler: IHandler | ,
    ):
        self.__handlers[message_type].append(handler)
