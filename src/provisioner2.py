from Kathara.model.Machine import Machine
from Kathara.model.Lab import Lab


class MachineConnection:
    def __init__(self, machine: Machine):
        self.machine = machine

    def provision(self):
        self.machine.copy_directory_from_path("src", "/calinka")

    def connect(self):
        pass


class Provisioner:
    def __init__(self, lab: Lab) -> None:
        self.lab = lab
        self.connections: dict[str, MachineConnection] = {}

    def add_device(self, machine: Machine) -> None:
        self.connections[machine.name] = MachineConnection(machine)
