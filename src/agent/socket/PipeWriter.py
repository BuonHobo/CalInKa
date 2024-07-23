import multiprocessing.connection
import os
from pathlib import Path
import asyncio


class PipeWriter:
    def __init__(self, output_pipe_path: Path):
        output_pipe_path.parent.mkdir(parents=True, exist_ok=True, mode=0o600)
        output_pipe_path.unlink(missing_ok=True)
        os.mkfifo(output_pipe_path, 0o600)

        self.__output_pipe_path = output_pipe_path

    def write(self, data: str):
        self.__output_pipe_path.write_text(data, encoding="utf-8", newline="")
