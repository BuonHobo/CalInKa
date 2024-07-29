from typing import Optional
from common.dispatch.IHandler import IHandler
from common.dispatch.IPacketLauncher import IPacketLauncher
from common.dispatch.SingletonLauncher import SingletonLauncher
from common.packet.Sender import Role
from common.packet.messages import Command
import subprocess


class CommandHandler(IHandler):

    def __init__(self, launcher: Optional[IPacketLauncher] = None):
        self.__launcher = launcher or SingletonLauncher.get_instance()

    async def handle(self, packet):
        if packet.src.role != Role.CONTROLLER:
            return

        assert type(packet.message) == Command
        print(subprocess.run(packet.message.cmd, shell=True, capture_output=True))
