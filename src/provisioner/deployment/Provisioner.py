import asyncio
import os

from Kathara.manager.Kathara import Kathara
from Kathara.model.Lab import Lab
from Kathara.model.Machine import Machine
from src.common.dispatch.IPacketLauncher import IPacketLauncher
from src.common.packet.Sender import Role
from src.common.packet.messages import Packet, IMessage
from src.common.socket.PipeReadProtocol import PipeReadProtocol
from src.provisioner.config.Settings import Settings
from src.provisioner.connection.MachineConnection import MachineConnection
from src.provisioner.dispatch.Router import Router


class Provisioner(IPacketLauncher):

    def __init__(self, lab: Lab):
        self.__connections: dict[str, MachineConnection] = {}
        self.__lab = lab

    def add_machine(self, machine: Machine, role: Role):
        self.__connections[machine.name] = MachineConnection(machine, role)

    async def deploy(self):
        print("Remember that all Calinka devices must support the calinka agent.")
        print("Deploying lab...")
        Kathara.get_instance().deploy_lab(self.__lab)

        await asyncio.gather(
            *(connection.start_agent() for connection in self.__connections.values())
        )

    async def send_message(self, machine_name: str, message: IMessage):
        await asyncio.get_event_loop().create_task(
            self.__connections[machine_name].send(
                Packet.from_message(message, Settings.sender, machine_name)
            )
        )

    async def start_routing(self, router: Router):
        read_pipe, write_pipe = os.pipe()
        os.set_inheritable(read_pipe, True)
        os.set_inheritable(write_pipe, True)
        for connection in self.__connections.values():
            await asyncio.get_event_loop().create_task(connection.fork_and_listen(write_pipe))
        PipeReadProtocol(router, read_pipe).listen()

    async def send(self, packet: Packet):
        await asyncio.get_event_loop().create_task(
            self.__connections[packet.dst].send(packet)
        )
