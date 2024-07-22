import common.communication.entities.clients as client
from ..socket.ISocket import ISocket
from ..messaging.messages import IMessage
from ..messaging.packet import Packet, PacketSchema
from ..entities.Daemon import Daemon
import common.communication.session.SessionHandler as sessionHandler


class Session:
    def __init__(self, client):
        self.client = client

    def handle(self, data: Packet):
        self.client.handle(data.payload)

    def send(self, payload: IMessage):
        data = PacketSchema().dumps(
            Packet(
                Daemon().name,
                self.client.name,
                payload.__class__.__name__,
                payload,
            )
        )

        sessionHandler.SessionHandler.get_instance().send(data)
