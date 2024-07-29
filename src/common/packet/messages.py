from __future__ import annotations

from abc import ABC

from common.packet.Sender import SenderSchema, Sender
from marshmallow import post_load, fields, Schema, pre_load


class IMessage(ABC):

    @classmethod
    def schema(cls) -> IMessageSchema:
        clazz = cls.__name__
        return globals()[clazz + "Schema"]()

    def to_json(self) -> str:
        return self.schema().dumps(self)

    @classmethod
    def from_json(cls, data: str) -> IMessage:
        res = cls.schema().loads(data)
        assert isinstance(res, IMessage)
        return res


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


class CommandResponse(IMessage):
    def __init__(self, ok: bool, body: str):
        self.ok = ok
        self.body: str = body


class CommandResponseSchema(IMessageSchema):
    ok = fields.Boolean(required=True)
    body = fields.String(required=True)


class Poke(IMessage):
    def __init__(self, num: int):
        self.num = num


class PokeSchema(IMessageSchema):
    num = fields.Int(required=True)


class Packet(IMessage):
    def __init__(self, src: Sender, dst: str, kind: str, message: IMessage):
        self.src = src
        self.dst = dst
        self.kind = kind
        self.message = message

    @staticmethod
    def from_message(message: IMessage, sender: Sender, destination: str):
        return Packet(sender, destination, message.__class__.__name__, message)


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
