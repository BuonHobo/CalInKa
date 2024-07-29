import asyncio

from src.common.dispatch.Dispatcher import Dispatcher
from src.common.dispatch.IHandler import IHandler
from src.common.dispatch.IPacketLauncher import IPacketLauncher
from src.common.packet.messages import Packet
from src.provisioner.config.Settings import Settings


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
