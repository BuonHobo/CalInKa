from provisioner.connection.MachineConnection import MachineConnection
from provisioner.dispatch.Router import Router
import asyncio
from asyncio.tasks import Task
from common.packet.messages import Packet
from concurrent.futures.process import ProcessPoolExecutor


class MachineListener:
    def __init__(
        self,
        machine_connection: MachineConnection,
        router: Router,
    ):
        self.__connection = machine_connection
        self.__router = router

    async def listen(self):
        packet = await self.__connection.get_packet()
        if packet:
            asyncio.get_event_loop().create_task(self.__router.route(packet))
        asyncio.get_event_loop().create_task(self.listen())
