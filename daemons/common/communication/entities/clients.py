from ..messaging.messages import HandshakeResponse, IMessage
import common.communication.session.Session as session
from queue import Queue


class Client:
    def __init__(self, name: str, role: str):
        self.name = name
        self.session = session.Session(self)
        self.queue: Queue[IMessage] = Queue()
        ClientRegistry().add(self)

    def send(self, data: IMessage):
        self.session.send(data)

    def recv(self) -> IMessage:
        return self.queue.get()

    def handle(self, msg: IMessage):
        self.queue.put(msg)

        self.send(HandshakeResponse(True))  # TODO togliere


class ClientRegistry:
    instance = None

    def __init__(self) -> None:
        self.instance = self
        self.clients = []

    def add(self, client: Client):
        self.clients.append(client)

    def __new__(cls):
        if not cls.instance:
            return super().__new__(cls)
        return cls.instance
