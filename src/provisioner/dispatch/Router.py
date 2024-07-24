from common.dispatch.Dispatcher import Dispatcher
from common.packet.messages import Packet
from common.dispatch.IPacketLauncher import IPacketLauncher
from provisioner.config.Settings import Settings
import asyncio


class Router:
    def __init__(self, dispatcher: Dispatcher, launcher: IPacketLauncher):
        self.__dispatcher = dispatcher
        self.__launcher = launcher

    async def route(self, packet: Packet):
        if packet.dst == Settings.sender.name:
            asyncio.get_event_loop().create_task(self.__dispatcher.dispatch(packet))
            return
        else:
            await self.__launcher.send(packet)
