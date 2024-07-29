from __future__ import annotations

from common.dispatch.IPacketLauncher import IPacketLauncher
from typing import Optional, Self
from common.packet.messages import Packet, IMessage


class SingletonLauncher(IPacketLauncher):
    __instance: Optional[SingletonLauncher] = None

    @staticmethod
    def get_instance() -> SingletonLauncher:
        if SingletonLauncher.__instance is None:
            raise Exception("SingletonLauncher is not initialized")
        return SingletonLauncher.__instance

    def __init__(self, packet_launcher: IPacketLauncher):
        if self.__instance is not None:
            raise Exception("SingletonLauncher is a singleton")
        self.__launcher = packet_launcher
        SingletonLauncher.__instance = self

    async def send(self, packet: Packet):
        await self.__launcher.send(packet)
