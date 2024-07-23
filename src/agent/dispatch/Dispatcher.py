from agent.packet.messages import Packet
from agent.socket.ISocket import ISocket


class Dispatcher:

    def __init__(self, socket: ISocket):
        self.socket = socket

    def handle(self, data: str):
        p = Packet.from_json(data)
        packet = Packet.from_message(p, p.sender.name)
        self.socket.send(packet.to_json())
