import sys
from pathlib import Path

from common.packet.Sender import Role
from common.packet.Sender import Sender
import common.config.Settings as common_settings


class Settings(common_settings.Settings):

    sender = Sender("provisioner", Role.PROVISIONER)

    def init(self, *args, **kwds):
        super().init(*args, **kwds)
