import asyncio

from common.dispatch.SingletonLauncher import SingletonLauncher
from common.dispatch.Dispatcher import Dispatcher
from common.dispatch.IHandler import IHandler
from common.dispatch.IPacketLauncher import IPacketLauncher
from common.packet.messages import Packet
from provisioner.config.Settings import Settings
from typing import Optional


class Router(IHandler):
    def __init__(
        self,
        handler: IHandler,
        launcher: Optional[IPacketLauncher] = None,
    ):
        self.handler = handler
        self.__launcher = launcher or SingletonLauncher.get_instance()

    async def handle(self, packet: Packet):
        print("received", packet.to_json())
        if packet.dst == Settings.sender.name:
            await asyncio.get_event_loop().create_task(self.handler.handle(packet))
            return
        else:
            await asyncio.get_event_loop().create_task(self.__launcher.send(packet))
