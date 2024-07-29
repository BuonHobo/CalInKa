import os
from pathlib import Path

from common.dispatch.IPacketLauncher import IPacketLauncher
from common.packet.messages import Packet


class PipeWriter(IPacketLauncher):
    def __init__(self, output_pipe_path: Path):
        output_pipe_path.parent.mkdir(parents=True, exist_ok=True, mode=0o600)
        output_pipe_path.unlink(missing_ok=True)
        os.mkfifo(output_pipe_path, 0o600)

        self.__output_pipe_path = output_pipe_path

    async def send(self, packet: Packet):
        self.__output_pipe_path.write_text(
            packet.to_json(), encoding="utf-8", newline=""
        )
