from typing import Callable
from agent.packet.messages import IMessage, Packet
from agent.socket.ISocket import ISocket


class Dispatcher:

    def __init__(self, socket: ISocket):
        self.socket = socket
        self.handlers: dict[type[IMessage], Callable[[Packet], Packet]] = {}

    def handle(self, data: str):
        try:
            packet = Packet.from_json(data)
        except Exception as e:
            print(f"Error: {e}")
            return
