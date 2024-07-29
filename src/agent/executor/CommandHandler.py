from typing import Optional
from common.dispatch import Dispatcher
from common.dispatch.Dispatcher import Dispatcher
from common.dispatch.IHandler import IHandler
from common.dispatch.IPacketLauncher import IPacketLauncher
from common.dispatch.SingletonLauncher import SingletonLauncher
from common.packet.Sender import Role
from common.packet.messages import Command, CommandResponse, Packet
import subprocess

from agent.config.Settings import Settings


class CommandHandler(IHandler):

    def __init__(self) -> None:
        Dispatcher.get_instance().register(Command, self)

    async def handle(self, packet):
        if packet.src.role != Role.CONTROLLER:
            await SingletonLauncher.get_instance().send(
                Packet.from_message(
                    CommandResponse(False, "Unauthorized"),
                    Settings().sender,
                    packet.src.name,
                )
            )
            return

        assert type(packet.message) == Command
        res = subprocess.run(packet.message.cmd, shell=True, capture_output=True)
        await SingletonLauncher.get_instance().send(
            Packet.from_message(
                CommandResponse(True, res.stdout.decode()),
                Settings().sender,
                packet.src.name,
            )
        )
