import sys
from pathlib import Path
from typing import Any

from common.packet.Sender import Role
from common.utils.Singleton import Singleton


class Settings(Singleton):
    check_phrase = "Calinka is available."
