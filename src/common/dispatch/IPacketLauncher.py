from abc import ABC, abstractmethod

from common.packet.messages import Packet


class IPacketLauncher(ABC):
    @abstractmethod
    async def send(self, packet: Packet):
        pass
