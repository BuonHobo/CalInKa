import asyncio
from typing import Any, Generator
from common.dispatch.IPacketLauncher import IPacketLauncher
from common.packet.Sender import Role, Sender
from common.packet.messages import Packet, IMessage
from Kathara.manager.Kathara import Kathara
from Kathara.model.Lab import Lab
from Kathara.model.Machine import Machine
from provisioner.config.Settings import Settings
from provisioner.connection.MachineListener import MachineListener
from provisioner.connection.MachineConnection import MachineConnection
from common.utils.Singleton import Singleton
from provisioner.dispatch.Router import Router


class Provisioner(IPacketLauncher):

    def __init__(self, lab: Lab):
        self.__connections: dict[str, MachineConnection] = {}
        self.__lab = lab

    def add_machine(self, machine: Machine, role: Role):
        self.__connections[machine.name] = MachineConnection(machine, role)

    def get_output(self, machine_name: str) -> Generator[Packet, Any, None]:
        return self.__connections[machine_name].recv()

    def deploy(self):
        print("Remember that all Calinka devices must support the calinka agent.")
        print("Deploying lab...")
        Kathara.get_instance().deploy_lab(self.__lab)
        for connection in self.__connections.values():
            connection.connect()

    async def send_message(self, machine_name: str, message: IMessage):
        await self.__connections[machine_name].send(
            Packet.from_message(message, Settings.sender, machine_name)
        )

    async def start_routing(self, router: Router):
        for connection in self.__connections.values():
            asyncio.get_event_loop().create_task(
                MachineListener(connection, router).listen()
            )

    async def send(self, packet: Packet):
        await self.__connections[packet.dst].send(packet)
