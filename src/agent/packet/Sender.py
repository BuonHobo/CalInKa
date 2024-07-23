from marshmallow import Schema, fields, post_load
from enum import Enum


class Role(Enum):
    AGENT = "AGENT"
    CONTROLLER = "CONTROLLER"
    PROVISIONER = "PROVISIONER"


class Sender:
    def __init__(self, name: str, role: Role):
        self.name = name
        self.role = role


class SenderSchema(Schema):
    name = fields.Str(required=True)
    role = fields.Enum(Role, required=True)

    @post_load
    def make_client(self, data, **kwargs):
        return Sender(**data)
