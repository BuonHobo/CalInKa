import asyncio
import os
import signal
from pathlib import Path

from agent.executor.CommandHandler import CommandHandler
import common.config.Settings as common_settings
from agent.config.Settings import Settings
from agent.socket.PipeWriter import PipeWriter
from common.dispatch.SingletonLauncher import SingletonLauncher
from common.dispatch.Dispatcher import Dispatcher
from common.dispatch.IPacketLauncher import IPacketLauncher
from common.packet.messages import Command, Poke, Packet
from common.socket.PipeReadProtocol import PipeReadProtocol


async def return_poke(packet: Packet, launcher: IPacketLauncher):
    poke = packet.message
    assert isinstance(poke, Poke)
    poke.num += 1
    p = Packet.from_message(poke, Settings().sender, packet.src.name)
    await launcher.send(p)


async def main():
    SingletonLauncher(PipeWriter(Settings().output_pipe_path))
    dispatcher = Dispatcher()
    dispatcher.register(Poke, return_poke)
    dispatcher.register(Command, CommandHandler())

    Settings().input_pipe_path.parent.mkdir(parents=True, exist_ok=True, mode=0o600)
    Settings().input_pipe_path.unlink(missing_ok=True)
    os.mkfifo(Settings().input_pipe_path, 0o600)

    pipeReader = PipeReadProtocol(dispatcher, Settings().input_pipe_path)

    asyncio.get_event_loop().call_soon(pipeReader.listen)
    print(common_settings.Settings.check_phrase, flush=True)


def shutdown(input_pipe_path: Path, output_pipe_path: Path):
    print("\nDeleting Pipes before shutting down...")
    os.close(2)
    os.remove(input_pipe_path)
    os.remove(output_pipe_path)
    exit(0)


if __name__ == "__main__":
    loop = asyncio.new_event_loop()
    loop.create_task(main())

    signal.signal(
        signal.SIGINT,
        lambda s, f: shutdown(Settings().input_pipe_path, Settings().output_pipe_path),
    )

    loop.run_forever()
