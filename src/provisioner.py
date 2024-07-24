from typing import Any, Callable, Generator
from Kathara.model.Lab import Lab
from Kathara.model.Machine import Machine
from Kathara.manager.Kathara import Kathara

from common.config.Settings import Settings
from common.packet.Sender import Role, Sender
from common.packet.messages import IMessage, Packet, Poke


class MachineConnection:

    pipe_in_path = "/pipe/in"
    pipe_out_path = "/pipe/out"
    calinka_agent_command = "python3 /calinka/agent.py"

    def __init__(self, machine: Machine, role: Role):
        self.output: None | Callable[[], Generator[Packet, Any, None]] = None
        self.__machine = machine
        self.__role = role

    def connect(self):
        self.check_machine()

        Kathara.get_instance().exec(
            machine_name=self.__machine.name,
            command=f"bash -c 'python3 /calinka/agent.py /pipe/in /pipe/out {self.__machine.name} {self.__role.name} &'",
            lab=self.__machine.lab,
        )

        output = Kathara.get_instance().exec(
            machine_name=self.__machine.name,
            command=f"bash -c 'while true; do cat /pipe/out; done'",
            lab=self.__machine.lab,
            stream=True,
        )

        def __output_generator():
            for stdout, _ in output:  # type: ignore
                if stdout:
                    assert isinstance(stdout, bytes)
                    res = Packet.from_json(stdout.decode())
                    assert isinstance(res, Packet)
                    yield res

        self.output = __output_generator

    def check_machine(self):
        try:
            stdout, _, _ = Kathara.get_instance().exec(
                self.__machine.name,
                f"{self.calinka_agent_command} --check",
                lab=self.__machine.lab,
                wait=True,
                stream=False,
            )
        except Exception as e:
            e.add_note("Did you forget to deploy the lab?")
            raise e

        assert isinstance(stdout, bytes)
        if stdout.decode().strip() != Settings.check_phrase:
            raise ValueError(
                f"Machine: '{self.__machine.name}' running on image '{self.__machine.get_image()}' does not support Calinka"
            )

    def send_message(self, message: IMessage, sender: Sender):
        p = Packet.from_message(message, sender, self.__machine.name)

        Kathara.get_instance().exec(
            self.__machine.name,
            f"bash -c 'cat <<EOF > {self.pipe_in_path}\n{p.to_json()}\nEOF\n'",
            lab=self.__machine.lab,
        )


class Provisioner:

    sender = Sender("provisioner", Role.PROVISIONER)

    def __init__(self, lab: Lab):
        self.__connections: dict[str, MachineConnection] = {}
        self.__lab = lab

    def add_machine(self, machine: Machine, role: Role):
        self.__connections[machine.name] = MachineConnection(machine, role)

    def get_output(self, machine_name: str):
        return self.__connections[machine_name].output()

    def deploy(self):
        for connection in self.__connections.values():
            connection.connect()

    def send_message(self, machine_name: str, message: IMessage):
        self.__connections[machine_name].send_message(message, self.sender)


def main():
    lab = Lab("calinka")

    red = lab.new_machine(
        "red",
        image="ghcr.io/buonhobo/agent:latest",
    )
    blue = lab.new_machine(
        "blue",
        image="ghcr.io/buonhobo/agent:latest",
    )
    controller = lab.new_machine(
        "controller",
        image="ghcr.io/buonhobo/agent:latest",
    )

    lab.connect_machine_to_link(red.name, "A")
    lab.connect_machine_to_link(blue.name, "A")
    lab.connect_machine_to_link(controller.name, "A")

    lab.create_file_from_string(
        """
        ip a add 10.10.10.11/24 dev eth0
        """,
        dst_path="red.startup",
    )

    lab.create_file_from_string(
        """
        ip a add 10.10.10.12/24 dev eth0
        """,
        dst_path="blue.startup",
    )

    lab.create_file_from_string(
        """
        ip a add 10.10.10.10/24 dev eth0
        """,
        dst_path="controller.startup",
    )

    p = Provisioner(lab)
    p.add_machine(red, Role.AGENT)
    p.add_machine(blue, Role.AGENT)
    p.add_machine(controller, Role.CONTROLLER)
    Kathara.get_instance().deploy_lab(lab)
    p.deploy()
    p.send_message("red", Poke(0))
    for o in p.get_output("red"):
        print(o.to_json())


if __name__ == "__main__":
    main()
