from common.dispatch.IPacketLauncher import IPacketLauncher
from Kathara.model.Machine import Machine
from Kathara.manager.Kathara import Kathara
from typing import Callable, Generator, Any
from common.packet.Sender import Role, Sender
from common.packet.messages import Packet, IMessage
import common.config.Settings as common_settings
from provisioner.config.Settings import Settings
from typing import Tuple


class MachineConnection(IPacketLauncher):

    def __init__(self, machine: Machine, role: Role):
        self.__recv: None | Callable[[], Generator[Packet, Any, None]] = None
        self.__machine = machine
        self.__role = role
        self.__output: (
            None | Callable[[], Generator[Tuple[str | None, str | None], None, None]]
        ) = None

    def recv(self):
        assert self.__recv is not None
        for p in self.__recv():
            yield p

    def connect(self):

        print(f"Connecting to '{self.__machine.name}'...")

        log = Kathara.get_instance().exec(
            machine_name=self.__machine.name,
            command=f"{Settings.calinka_agent_command} {Settings.pipe_in_path} {Settings.pipe_out_path} {self.__machine.name} {self.__role.name}",
            lab=self.__machine.lab,
            wait=True,
            stream=True,
        )

        def __output_generator() -> (
            Generator[Tuple[str | None, str | None], None, None]
        ):
            for stdout, stderr in log:  # type:ignore
                out, err = None, None
                if stdout:
                    out = stdout.decode().strip()  # type:ignore
                if stderr:
                    err = stderr.decode().strip()  # type:ignore
                yield out, err

        self.__output = __output_generator

        for out, err in self.output():
            if out:
                print(f"'{self.__machine.name}' says: {out}")
                if out.strip() == common_settings.Settings.check_phrase:
                    break
            if err:
                print(f"'{self.__machine.name}' showed an error: {err}")

        output = Kathara.get_instance().exec(
            machine_name=self.__machine.name,
            command=f"bash -c 'while true; do cat {Settings.pipe_out_path}; done'",
            lab=self.__machine.lab,
            stream=True,
        )

        def __recv_generator():
            for stdout, _ in output:  # type: ignore
                if stdout:
                    assert isinstance(stdout, bytes)
                    res = Packet.from_json(stdout.decode())
                    assert isinstance(res, Packet)
                    yield res

        self.__recv = __recv_generator

    def output(self):
        assert self.__output is not None
        for p in self.__output():
            yield p

    async def send(self, packet: Packet):
        print("sending", packet.to_json())
        Kathara.get_instance().exec(
            self.__machine.name,
            f"bash -c 'cat <<EOF > {Settings.pipe_in_path}\n{packet.to_json()}\nEOF\n'",
            lab=self.__machine.lab,
        )
