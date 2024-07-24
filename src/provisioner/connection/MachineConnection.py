from concurrent.futures import ProcessPoolExecutor

from marshmallow import pprint
from common.dispatch.IPacketLauncher import IPacketLauncher
from Kathara.model.Machine import Machine
from Kathara.manager.Kathara import Kathara
from typing import Callable, Generator, Any, AsyncGenerator
from common.packet.Sender import Role, Sender
from common.packet.messages import Packet, IMessage
import common.config.Settings as common_settings
from provisioner.config.Settings import Settings
from typing import Tuple
import asyncio


class MachineConnection(IPacketLauncher):

    def __init__(self, machine: Machine, role: Role):
        self.__machine = machine
        self.__role = role

    def connect(self):

        print(f"Connecting to '{self.__machine.name}'...")

        log = Kathara.get_instance().exec(
            machine_name=self.__machine.name,
            command=f"{Settings.calinka_agent_command} {Settings.pipe_in_path} {Settings.pipe_out_path} {self.__machine.name} {self.__role.name}",
            lab=self.__machine.lab,
            wait=True,
            stream=True,
        )

        def output_generator() -> Generator[Tuple[str | None, str | None], None, None]:
            for stdout, stderr in log:  # type:ignore
                out, err = None, None
                if stdout:
                    out = stdout.decode().strip()  # type:ignore
                if stderr:
                    err = stderr.decode().strip()  # type:ignore
                yield out, err

        for out, err in output_generator():
            if out:
                print(f"'{self.__machine.name}' says: {out}")
                if out.strip() == common_settings.Settings.check_phrase:
                    break
            if err:
                print(f"'{self.__machine.name}' showed an error: {err}")

    async def send(self, packet: Packet):
        print("sent", packet.to_json())
        Kathara.get_instance().exec(
            self.__machine.name,
            f"bash -c 'cat <<EOF > {Settings.pipe_in_path}\n{packet.to_json()}\nEOF\n'",
            lab=self.__machine.lab,
        )

    async def get_packet(self) -> Packet | None:

        o, _, _ = Kathara.get_instance().exec(
            machine_name=self.__machine.name,
            command=f"timeout {Settings.timeout} cat {Settings.pipe_out_path}",
            lab=self.__machine.lab,
            stream=False,
        )

        if o:
            assert isinstance(o, bytes)
            res = Packet.from_json(o.decode())
            print("received", res.to_json())
            assert isinstance(res, Packet)
            return res
