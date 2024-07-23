import asyncio
from io import TextIOWrapper
from pathlib import Path
from agent.dispatch.Dispatcher import Dispatcher
import os


class PipeReadProtocol(asyncio.Protocol):
    def __init__(self, dispatcher: Dispatcher, input_pipe_path: Path):
        input_pipe_path.parent.mkdir(parents=True, exist_ok=True, mode=0o600)
        input_pipe_path.unlink(missing_ok=True)
        os.mkfifo(input_pipe_path, 0o600)

        self.input_pipe_path = input_pipe_path
        self.buffer = ""
        self.depth = 0
        self.is_packet = False
        self.dispatcher = dispatcher

    def listen(self):
        loop = asyncio.get_event_loop()
        loop.create_task(
            loop.connect_read_pipe(
                lambda: self,
                self.input_pipe_path.open("r"),
            )
        )

    def data_received(self, data):
        data = data.decode("utf-8")

        for c in data:
            if c == "{":
                self.depth += 1
                self.is_packet = True
            elif c == "}":
                self.depth -= 1

            self.depth = max(self.depth, 0)

            if self.is_packet:
                self.buffer += c
                if self.depth == 0:
                    asyncio.get_event_loop().create_task(
                        self.dispatcher.handle(self.buffer)
                    )
                    self.buffer = ""
                    self.is_packet = False

    def connection_lost(self, exc):
        self.listen()
