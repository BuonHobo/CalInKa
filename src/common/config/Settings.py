import sys
from pathlib import Path
from typing import Any

from common.packet.Sender import Role


class Settings(object):

    check_phrase = "Calinka is available."

    def __new__(cls, *args, **kwds):
        it = cls.__dict__.get("__it__")
        if it is not None:
            return it
        cls.__it__ = it = object.__new__(cls)
        it.init(*args, **kwds)
        return it

    def init(self, *args, **kwds):
        pass
