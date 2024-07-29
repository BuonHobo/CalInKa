import sys
from pathlib import Path

import common.config.Settings as common_settings
from common.packet.Sender import Role
from common.packet.Sender import Sender


class Settings(common_settings.Settings):

    def init(self, *args, **kwds):
        super().init(*args, **kwds)
        try:
            self.input_pipe_path = Path(sys.argv[1])
            self.output_pipe_path = Path(sys.argv[2])
            self.hostname = sys.argv[3]
            self.role = Role(sys.argv[4].upper())
            self.sender = Sender(self.hostname, self.role)

        except IndexError:

            print(
                f"Usage: {sys.argv[0]} <input_pipe_path> <output_pipe_path> <hostname> <role>"
            )
            sys.exit(1)
