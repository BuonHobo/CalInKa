import sys
from pathlib import Path

from common.packet.Sender import Role
from common.packet.Sender import Sender
import common.config.Settings as common_settings


class Settings(common_settings.Settings):

    timeout = 0.1
    sender = Sender("provisioner", Role.PROVISIONER)
    pipe_in_path = "/pipe/in"
    pipe_out_path = "/pipe/out"
    calinka_agent_command = "python3 /calinka/agent.py"
