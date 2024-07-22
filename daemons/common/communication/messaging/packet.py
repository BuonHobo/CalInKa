from marshmallow import Schema, fields, post_load, pre_load
from .messages import *


class Packet:
    def __init__(self, src: str, dest: str, type: str, payload: IMessage):
        self.src = src
        self.dest = dest
        self.type = type
        self.payload = payload


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
        cls = globals()[self.context["type"] + "Schema"]
        return cls().load(obj)

    @pre_load
    def add_type(self, data, **kwargs):
        self.context["type"] = data.get("type")
        return data

    @post_load
    def make_packet(self, data, **kwargs) -> Packet:
        return Packet(**data)
