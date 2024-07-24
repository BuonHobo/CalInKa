from typing import Any, Generator
from common.packet.Sender import Role, Sender
from common.packet.messages import Packet, IMessage
from Kathara.manager.Kathara import Kathara
from Kathara.model.Lab import Lab
from Kathara.model.Machine import Machine
from provisioner.connection.MachineConnection import MachineConnection


class Provisioner:

    sender = Sender("provisioner", Role.PROVISIONER)

    def __init__(self, lab: Lab):
        self.__connections: dict[str, MachineConnection] = {}
        self.__lab = lab

    def add_machine(self, machine: Machine, role: Role):
        self.__connections[machine.name] = MachineConnection(machine, role)

    def get_output(self, machine_name: str) -> Generator[Packet, Any, None]:
        res = self.__connections[machine_name].output
        assert res is not None
        return res()

    def deploy(self):
        Kathara.get_instance().deploy_lab(self.__lab)
        for connection in self.__connections.values():
            connection.connect()

    def send_message(self, machine_name: str, message: IMessage):
        self.__connections[machine_name].send_message(message, self.sender)
