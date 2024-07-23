import multiprocessing.connection
import os

from agent.socket.ISocket import ISocket


class FdSocket(ISocket):
    bufsize = 256

    def __init__(self):
        self.incoming = 0
        self.outgoing = 1
        self.buffer = ""

    def send(self, data: str):
        os.write(self.outgoing, bytes(data, "utf-8"))

    def __unbuffered_read(self, size: int) -> str:
        return str(os.read(self.incoming, size), "utf-8")

    def recv(self, size: int) -> str:
        if len(self.buffer) >= size:
            res = self.buffer[:size]
            self.buffer = self.buffer[size:]
            return res
        else:
            reading = max(size - len(self.buffer), self.bufsize)
            self.buffer += self.__unbuffered_read(reading)
            res = self.buffer[:size]
            self.buffer = self.buffer[size:]
            return res
