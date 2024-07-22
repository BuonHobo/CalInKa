from __future__ import annotations
from abc import ABC, abstractmethod
from marshmallow import Schema, post_load, fields


class IMessage(ABC):

    @property
    @abstractmethod
    def schema(self) -> type[IMessageSchema]:
        pass


class IMessageSchema(Schema):

    @post_load
    def make_packet(self, data, **kwargs):
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

    def __init__(self, role: str) -> None:
        self.role = role


class HandshakeSchema(IMessageSchema):
    role = fields.Str(required=True)


class HandshakeResponse(IResponse):

    @property
    def schema(self) -> type[IMessageSchema]:
        return HandshakeResponseSchema

    def __init__(self, success: bool) -> None:
        self.success = success


class HandshakeResponseSchema(IMessageSchema):
    success = fields.Bool(required=True)


class Command(ICommand):

    @property
    def schema(self) -> type[IMessageSchema]:
        return HandshakeResponseSchema

    def __init__(self, command: str) -> None:
        self.command = command


class CommandSchema(Schema):
    command = fields.Str()
