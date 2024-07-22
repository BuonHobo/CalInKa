from __future__ import annotations
from typing import Self
from abc import ABC, abstractmethod
from os import environ, read, sync, write, fsync
from queue import Queue
from enum import Enum
import threading
from marshmallow import Schema, ValidationError, fields, pre_dump, pre_load, post_load


class Daemon:
    instance = None
    default_name = environ.get("DAEMON_NAME", "daemon")

    def __init__(self) -> None:
        self.instance = self
        self.name = self.default_name

    def __new__(cls):
        if not cls.instance:
            return super().__new__(cls)
        return cls.instance


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


class ISocket(ABC):
    @abstractmethod
    def send(self, data: str):
        pass

    @abstractmethod
    def recv(self, size: int) -> str:
        pass


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
        write(self.stdout, bytes(data + "\n", encoding="utf-8"))

    def recv(self, size: int) -> str:
        return str(read(self.stdin, size), encoding="utf-8")


class IMessage(ABC):

    @property
    @abstractmethod
    def schema(self) -> type[IMessageSchema]:
        pass


class IMessageSchema(Schema):

    @post_load
    def make_packet(self, data, **kwargs) -> Packet:
        clazz = self.__class__.__name__.removesuffix("Schema")
        return globals()[clazz](**data)


class IEvent(IMessage):
    pass


class ICommand(IMessage):
    pass


class IResponse(IMessage):
    pass


class Handshake(IEvent):

    @property
    def schema(self) -> type[IMessageSchema]:
        return HandshakeSchema

    def __init__(self, role: Role) -> None:
        self.role = role


class Role(Enum):
    controller = 0
    agent = 1
    provisioner = 2


class HandshakeSchema(IMessageSchema):
    role = fields.Enum(Role, required=True)


class HandshakeResponseSchema(IMessageSchema):
    success = fields.Bool(required=True)


class HandshakeResponse(IResponse):

    @property
    def schema(self) -> type[IMessageSchema]:
        return HandshakeResponseSchema

    def __init__(self, success: bool) -> None:
        self.success = success


class Client:
    def __init__(self, name: str, role: Role):
        self.name = name
        self.session = Session(self)
        self.queue: Queue[IMessage] = Queue()
        ClientRegistry().add(self)

    def send(self, data: IMessage):
        self.session.send(data)

    def recv(self) -> IMessage:
        return self.queue.get()

    def handle(self, msg: IMessage):
        self.queue.put(msg)

        ###########

        self.send(HandshakeResponse(True))


class Session:
    def __init__(self, client: Client):
        self.socket: ISocket = FileDescriptorSocket()
        self.client = client

    def send(self, payload: IMessage):
        data = PacketSchema().dumps(
            Packet(
                Daemon().name,
                self.client.name,
                payload.__class__.__name__,
                payload,
            )
        )

        self.socket.send(data)

    def handle(self, data: Packet):

        self.client.handle(data.payload)


class SocketListener:
    def __init__(self, socket: ISocket):
        self.socket = socket

    def accept_packet(self):
        buffer = "{"
        depth = 1
        while True:
            c = self.socket.recv(1)
            if c == "{":
                depth += 1
            elif c == "}":
                depth -= 1

            buffer += c
            if depth == 0:
                SessionHandler().handle(buffer)
                return

    def listen(self):
        while True:
            c = self.socket.recv(1)
            if c == "{":
                self.accept_packet()


class SessionHandler:

    instance = None

    def __init__(self):
        self.instance = self
        self.sessions = {}

    def __new__(cls):
        if not cls.instance:
            return super().__new__(cls)
        return cls.instance

    def add_session(self, session: Session):
        self.sessions[session.client] = session

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
            client = Client(packet.src, packet.payload.role)
            self.sessions[packet.src] = client.session
        self.sessions[packet.src].handle(packet)


class CommandSchema(Schema):
    command = fields.Str()


class PacketSchema(Schema):
    src = fields.Str(required=True)
    dest = fields.Str(required=True)
    type = fields.Str(required=True)
    payload = fields.Method(
        required=True, serialize="serialize_payload", deserialize="deserialize_payload"
    )

    def serialize_payload(self, obj):
        return obj.payload.schema().dump(obj.payload)

    def deserialize_payload(self, obj):
        return globals()[self.context["type"] + "Schema"]().load(obj)

    @pre_load
    def add_type(self, data, **kwargs):
        self.context["type"] = data.get("type")
        return data

    @post_load
    def make_packet(self, data, **kwargs) -> Packet:
        return Packet(**data)


class Packet:
    def __init__(self, src: str, dest: str, type: str, payload: IMessage):
        self.src = src
        self.dest = dest
        self.type = type
        self.payload = payload


if __name__ == "__main__":
    t = threading.Thread(
        target=SocketListener(FileDescriptorSocket()).listen, daemon=False
    )
    t.start()
