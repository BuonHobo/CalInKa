from .ISocket import ISocket
from ..session.SessionHandler import SessionHandler


class SocketListener:

    bufsize = 1024

    def __init__(self, socket: ISocket):
        self.socket = socket
        self.buffer = ""
        SessionHandler.get_instance().add_socket(socket)

    def buffered_read(self, size: int = bufsize):
        if len(self.buffer) >= size:
            res = self.buffer[:size]
            self.buffer = self.buffer[size:]
            return res
        else:
            reading = max(size - len(self.buffer), self.bufsize)
            self.buffer += self.socket.recv(reading)
            res = self.buffer[:size]
            self.buffer = self.buffer[size:]
            return res

    def accept_packet(self):
        buf = "{"
        depth = 1
        while True:
            c = self.buffered_read(1)
            if c == "{":
                depth += 1
            elif c == "}":
                depth -= 1
            buf += c
            if depth == 0:
                SessionHandler.get_instance().handle(buf)
                return

    def listen(self):
        while True:
            c = self.buffered_read(1)
            if c == "{":
                self.accept_packet()
