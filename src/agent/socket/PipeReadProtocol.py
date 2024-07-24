import asyncio
from io import TextIOWrapper
from pathlib import Path
from common.dispatch.Dispatcher import Dispatcher
from common.packet.messages import Packet
import os


class PipeReadProtocol(asyncio.Protocol):
    def __init__(self, dispatcher: Dispatcher, input_pipe_path: Path):
        input_pipe_path.parent.mkdir(parents=True, exist_ok=True, mode=0o600)
        input_pipe_path.unlink(missing_ok=True)
        os.mkfifo(input_pipe_path, 0o600)

        self.__input_pipe_path = input_pipe_path
        self.__buffer = ""
        self.__depth = 0
        self.__is_packet = False
        self.__dispatcher = dispatcher

    def listen(self):
        loop = asyncio.get_event_loop()
        loop.create_task(
            loop.connect_read_pipe(
                lambda: self,
                self.__input_pipe_path.open("r"),
            )
        )

    def data_received(self, data):
        data = data.decode("utf-8")

        for c in data:
            if c == "{":
                self.__depth += 1
                self.__is_packet = True
            elif c == "}":
                self.__depth -= 1

            self.__depth = max(self.__depth, 0)

            if self.__is_packet:
                self.__buffer += c
                if self.__depth == 0:
                    if packet := self.parse_packet(self.__buffer):
                        asyncio.get_event_loop().create_task(
                            self.__dispatcher.dispatch(packet)
                        )
                    self.__buffer = ""
                    self.__is_packet = False

    def parse_packet(self, data: str):
        try:
            packet = Packet.from_json(data)
            assert isinstance(packet, Packet)
        except Exception as e:
            print(f"Couldn't parse packet {data}: {e}")
            return
        return packet

    def connection_lost(self, exc):
        self.listen()
