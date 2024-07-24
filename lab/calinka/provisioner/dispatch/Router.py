from common.dispatch.Dispatcher import Dispatcher
from common.packet.messages import Packet
from provisioner.config.Settings import Settings
import asyncio


class Router:
    def __init__(self, dispatcher: Dispatcher):
        self.__dispatcher = dispatcher

    async def route(self, packet: Packet):
        print(f"PROVISIONER: routing packet {packet.to_json()}")
        if packet.dst == Settings.sender.name:
            asyncio.get_event_loop().create_task(self.__dispatcher.dispatch(packet))
            return
        else:
            await self.__dispatcher.send(packet)
