from marshmallow import ValidationError
import common.communication.entities.clients as client
from common.communication.socket.ISocket import ISocket
from ..messaging.messages import Handshake, IMessage
from ..messaging.packet import Packet, PacketSchema
from ..entities.Daemon import Daemon


class SessionHandler:

    instance = None

    def __init__(self):
        instance = self
        self.sessions = {}
        self.socket: ISocket | None = None

    def add_socket(self, socket: ISocket):
        self.socket = socket

    @staticmethod
    def get_instance():
        if __class__.instance:
            return __class__.instance
        __class__.instance = SessionHandler()
        return __class__.instance

    def add_session(self, session):
        self.sessions[session.client] = session

    def send(self, payload: str):
        if self.socket is None:
            print("no")
            return  # Not good
        self.socket.send(payload)

    def handle(self, data: str):
        try:
            packet: Packet = PacketSchema().loads(data)  # type: ignore
        except ValidationError as e:
            print("Invalid")
            return  # TODO: reply with a message
        if packet.src not in self.sessions:
            if type(packet.payload) != Handshake:
                print("Unknown")
                return  # TODO: reply with a message
            clnt = client.Client(packet.src, packet.payload.role)
            self.sessions[packet.src] = clnt.session
        self.sessions[packet.src].handle(packet)
