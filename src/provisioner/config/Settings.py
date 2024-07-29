import src.common.config.Settings as common_settings
from src.common.packet.Sender import Role
from src.common.packet.Sender import Sender


class Settings(common_settings.Settings):
    sender = Sender("provisioner", Role.PROVISIONER)
    pipe_in_path = "/pipe/in"
    pipe_out_path = "/pipe/out"
    calinka_agent_command = "python3 /calinka/agent.py"
