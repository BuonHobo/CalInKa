from abc import ABC, abstractmethod


class ISocket(ABC):
    @abstractmethod
    def send(self, data: str):
        pass

    @abstractmethod
    def recv(self, size: int) -> str:
        pass
