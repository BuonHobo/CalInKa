from __future__ import annotations

from common.dispatch.IPacketLauncher import IPacketLauncher
from typing import Optional, Self
from common.packet.messages import Packet, IMessage


class SingletonLauncher(IPacketLauncher):
    instance: Optional[SingletonLauncher] = None

    @staticmethod
    def get_instance() -> SingletonLauncher:
        if SingletonLauncher.instance is None:
            raise Exception("SingletonLauncher is not initialized")
        return SingletonLauncher.instance

    def __init__(self, packet_launcher: IPacketLauncher):
        if self.instance is not None:
            raise Exception("SingletonLauncher is a singleton")
        self.__launcher = packet_launcher
        SingletonLauncher.instance = self

    async def send(self, packet: Packet):
        await self.__launcher.send(packet)
