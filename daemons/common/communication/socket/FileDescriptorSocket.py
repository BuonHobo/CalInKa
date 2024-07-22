from os import read, write
from .ISocket import ISocket


class FileDescriptorSocket(ISocket):
    stdin = 0
    stdout = 1
    instance = None

    def __init__(self) -> None:
        self.instance = self

    def __new__(cls):
        if not cls.instance:
            return super().__new__(cls)
        return cls.instance

    def send(self, data: str):
        write(self.stdout, bytes(data, encoding="utf-8"))

    def recv(self, size: int) -> str:
        return str(read(0, size), encoding="utf-8")
