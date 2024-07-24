from provisioner.connection.MachineConnection import MachineConnection
from provisioner.dispatch.Router import Router
import asyncio


class MachineListener:
    def __init__(self, machine_connection: MachineConnection, router: Router):
        self.__connection = machine_connection
        self.__router = router

    async def listen(self):
        for packet in self.__connection.recv():
            asyncio.get_event_loop().create_task(self.__router.route(packet))
