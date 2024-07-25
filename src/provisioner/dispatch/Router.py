from common.dispatch.Dispatcher import Dispatcher
from common.packet.messages import Packet
from common.dispatch.IPacketLauncher import IPacketLauncher
from provisioner.config.Settings import Settings
import asyncio


class Router(Dispatcher):
    def __init__(self, dispatcher: Dispatcher, launcher: IPacketLauncher):
        self.__dispatcher = dispatcher
        self.__launcher = launcher

    async def dispatch(self, packet: Packet):
        print("received", packet.to_json())
        if packet.dst == Settings.sender.name:
            asyncio.get_event_loop().create_task(self.__dispatcher.dispatch(packet))
            return
        else:
            asyncio.get_event_loop().create_task(self.__launcher.send(packet))
