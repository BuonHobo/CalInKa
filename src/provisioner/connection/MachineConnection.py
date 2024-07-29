import asyncio
import os

import common.config.Settings as common_settings
from Kathara.manager.Kathara import Kathara
from Kathara.model.Machine import Machine
from common.dispatch.IPacketLauncher import IPacketLauncher
from common.packet.Sender import Role
from common.packet.messages import Packet
from provisioner.config.Settings import Settings


class MachineConnection(IPacketLauncher):

    def __init__(self, machine: Machine, role: Role):
        self.__machine = machine
        self.__role = role

    async def start_agent(self):

        print(f"Connecting to '{self.__machine.name}'...")

        log = Kathara.get_instance().exec(
            machine_name=self.__machine.name,
            command=f"{Settings.calinka_agent_command} {Settings.pipe_in_path} {Settings.pipe_out_path} {self.__machine.name} {self.__role.name}",
            lab=self.__machine.lab,
            wait=True,
            stream=True,
        )
        asyncio.get_event_loop().create_task(self.wait_for_connection(log))

    async def wait_for_connection(self, log):
        for stdout, stderr in log:
            out, err = None, None
            if stdout:
                out = stdout.decode().strip()  # type:ignore
                print(f"'{self.__machine.name}' says: {out}")
                if out == common_settings.Settings.check_phrase:
                    break
            if stderr:
                err = stderr.decode().strip()  # type:ignore
                print(f"'{self.__machine.name}' showed an error: {err}")

    async def fork_and_listen(self, write_pipe: int):
        pid = os.fork()
        if pid <= 0:
            output = Kathara.get_instance().exec(
                machine_name=self.__machine.name,
                command=f"bash -c 'while true; do cat {Settings.pipe_out_path}; done'",
                # command=f"tail -f {Settings.pipe_out_path}",
                lab=self.__machine.lab,
                stream=True,
            )
            pipe = open(write_pipe, "wb")
            for o, _ in output:  # type:ignore
                if o:
                    pipe.write(o)  # type:ignore
                    pipe.flush()
            exit(0)

    async def send(self, packet: Packet):
        print("sent", packet.to_json())
        Kathara.get_instance().exec(
            self.__machine.name,
            f"bash -c 'cat <<EOF > {Settings.pipe_in_path}\n{packet.to_json()}\nEOF\n'",
            lab=self.__machine.lab,
        )
