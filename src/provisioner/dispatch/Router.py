import asyncio

from common.dispatch.Dispatcher import Dispatcher
from common.dispatch.IHandler import IHandler
from common.dispatch.IPacketLauncher import IPacketLauncher
from common.packet.messages import Packet
from provisioner.config.Settings import Settings


class Router(IHandler):
    def __init__(self, dispatcher: Dispatcher, launcher: IPacketLauncher):
        self.__dispatcher = dispatcher
        self.__launcher = launcher

    async def handle(self, packet: Packet):
        print("received", packet.to_json())
        if packet.dst == Settings.sender.name:
            await asyncio.get_event_loop().create_task(self.__dispatcher.handle(packet))
            return
        else:
            await asyncio.get_event_loop().create_task(self.__launcher.send(packet))
