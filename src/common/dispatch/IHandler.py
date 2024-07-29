from abc import ABC, abstractmethod
from typing import Callable, Awaitable

from src.common.packet.messages import Packet


class IHandler(ABC):
    @abstractmethod
    async def handle(self, packet: Packet | Callable[[Packet], Awaitable[None]]):
        pass