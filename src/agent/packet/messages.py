from __future__ import annotations

import os
from abc import ABC, abstractmethod

from marshmallow import post_load, fields, Schema, pre_load

from agent.packet.Role import Role
from agent.packet.Sender import SenderSchema, Sender


class IMessage(ABC):

    @classmethod
    def schema(cls) -> IMessageSchema:
        clazz = cls.__name__
        return globals()[clazz + "Schema"]()

    def to_json(self) -> str:
        return self.schema().dumps(self)

    @classmethod
    def from_json(cls, data: str) -> IMessage:
        return cls.schema().loads(data)


class IMessageSchema(Schema):
    @post_load
    def make_packet(self, data, **kwargs):
        clazz = self.__class__.__name__.removesuffix("Schema")
        return globals()[clazz](**data)


class Command(IMessage):
    def __init__(self, cmd: str):
        self.cmd = cmd


class CommandSchema(IMessageSchema):
    cmd = fields.Str(required=True)


class Poke(IMessage):
    def __init__(self, num: int):
        self.num = num


class PokeSchema(IMessageSchema):
    num = fields.Int(required=True)


class Packet(IMessage):
    sender = Sender(
        os.environ.get("HOSTNAME", "daemon"),
        Role(os.environ.get("DAEMON_ROLE", "AGENT")),
    )

    def __init__(self, src: Sender, dst: str, kind: str, message: IMessage):
        self.src = src
        self.dst = dst
        self.kind = kind
        self.message = message

    @staticmethod
    def from_message(message: IMessage, destination: str):
        return Packet(Packet.sender, destination, message.__class__.__name__, message)


class PacketSchema(IMessageSchema):
    src = fields.Nested(SenderSchema(), required=True)
    dst = fields.Str(required=True)
    kind = fields.Str(required=True)
    message = fields.Method(
        serialize="serialize_message", deserialize="deserialize_message", required=True
    )

    @staticmethod
    def serialize_message(obj: Packet):
        return obj.message.schema().dump(obj.message)

    def deserialize_message(self, obj: dict):
        clazz = self.context["kind"]
        return globals()[clazz + "Schema"]().load(obj)

    @pre_load
    def add_type(self, data, **kwargs):
        self.context["kind"] = data.get("kind")
        return data
