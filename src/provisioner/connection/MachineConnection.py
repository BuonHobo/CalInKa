from common.dispatch.IPacketLauncher import IPacketLauncher
from Kathara.model.Machine import Machine
from Kathara.manager.Kathara import Kathara
from typing import Callable, Generator, Any
from common.packet.Sender import Role, Sender
from common.packet.messages import Packet, IMessage
from common.config.Settings import Settings


class MachineConnection(IPacketLauncher):

    pipe_in_path = "/pipe/in"
    pipe_out_path = "/pipe/out"
    calinka_agent_command = "python3 /calinka/agent.py"

    def __init__(self, machine: Machine, role: Role):
        self.__output: None | Callable[[], Generator[Packet, Any, None]] = None
        self.__machine = machine
        self.__role = role

    def connect(self):
        self.check_machine()

        Kathara.get_instance().exec(
            machine_name=self.__machine.name,
            command=f"bash -c '{self.calinka_agent_command} {self.pipe_in_path} {self.pipe_out_path} {self.__machine.name} {self.__role.name} &'",
            lab=self.__machine.lab,
        )

        output = Kathara.get_instance().exec(
            machine_name=self.__machine.name,
            command=f"bash -c 'while true; do cat {self.pipe_out_path}; done'",
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

        self.__output = __output_generator

    def output(self):
        assert self.__output is not None
        for p in self.__output():
            yield p

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

    async def send(self, packet: Packet):
        print("sending", packet)
        Kathara.get_instance().exec(
            self.__machine.name,
            f"bash -c 'cat <<EOF > {self.pipe_in_path}\n{packet.to_json()}\nEOF\n'",
            lab=self.__machine.lab,
        )
