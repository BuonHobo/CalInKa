from agent.socket.ISocket import ISocket
from agent.dispatch.Dispatcher import Dispatcher


class SocketListener:
    def __init__(self, socket: ISocket, dispatcher: Dispatcher):
        self.socket = socket
        self.dispatcher = dispatcher

    def accept_packet(self):
        buf = "{"
        depth = 1
        while True:
            c = self.socket.recv(1)
            if c == "{":
                depth += 1
            elif c == "}":
                depth -= 1
            buf += c
            if depth == 0:
                self.dispatcher.handle(buf)
                return

    def listen(self):
        while True:
            c = self.socket.recv(1)
            if c == "{":
                self.accept_packet()

    def stop(self):
        pass
