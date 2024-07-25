import asyncio
from concurrent.futures import ProcessPoolExecutor
from concurrent.futures.thread import ThreadPoolExecutor
from typing import Any, AsyncGenerator, Generator, Tuple
from common.dispatch.IPacketLauncher import IPacketLauncher
from common.packet.Sender import Role, Sender
from common.packet.messages import Packet, IMessage
from Kathara.manager.Kathara import Kathara
from Kathara.model.Lab import Lab
from Kathara.model.Machine import Machine
from common.socket.PipeReadProtocol import PipeReadProtocol
from provisioner.config.Settings import Settings
from provisioner.connection.MachineListener import MachineListener
from provisioner.connection.MachineConnection import MachineConnection
from common.utils.Singleton import Singleton
from provisioner.dispatch.Router import Router
import os


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
        asyncio.get_event_loop().create_task(
            self.__connections[machine_name].send(
                Packet.from_message(message, Settings.sender, machine_name)
            )
        )

    async def start_routing(self, router: Router):
        read_pipe, write_pipe = os.pipe()
        os.set_inheritable(read_pipe, True)
        os.set_inheritable(write_pipe, True)
        for connection in self.__connections.values():
            asyncio.get_event_loop().create_task(connection.listen(write_pipe))
        asyncio.get_event_loop().create_task(
            asyncio.get_event_loop().connect_read_pipe(
                lambda: PipeReadProtocol(router, read_pipe), open(read_pipe, "r")
            )
        )

    async def send(self, packet: Packet):
        asyncio.get_event_loop().create_task(
            self.__connections[packet.dst].send(packet)
        )
