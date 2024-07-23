import sys
from pathlib import Path

from agent.packet.Sender import Role


class Settings(object):
    def __new__(cls, *args, **kwds):
        it = cls.__dict__.get("__it__")
        if it is not None:
            return it
        cls.__it__ = it = object.__new__(cls)
        it.init(*args, **kwds)
        return it

    def init(self, *args, **kwds):
        try:
            self.input_pipe_path = Path(sys.argv[1])
            self.output_pipe_path = Path(sys.argv[2])
            self.hostname = sys.argv[3]
            self.role = Role(sys.argv[4].upper())
        except IndexError:
            if len(sys.argv) == 2 and sys.argv[1] == "--check":
                print("Calinka is available.")
                sys.exit(0)
            print(
                f"Usage: {sys.argv[0]} <input_pipe_path> <output_pipe_path> <hostname> <role>"
            )
            sys.exit(1)
