import asyncio

from Kathara.parser.netkit.LabParser import LabParser

from src.common.dispatch.Dispatcher import Dispatcher
from src.common.dispatch.IPacketLauncher import IPacketLauncher
from src.common.packet.Sender import Role, Sender
from src.common.packet.messages import Packet, Poke
from src.provisioner.config.Settings import Settings
from src.provisioner.deployment.Provisioner import Provisioner
from src.provisioner.dispatch.Router import Router


async def handle_poke(packet: Packet, launcher: IPacketLauncher):
    poke = packet.message
    assert isinstance(poke, Poke)
    poke.num += 1
    p = Packet.from_message(poke, Settings.sender, packet.src.name)
    await launcher.send(p)


async def main(p: Provisioner):
    await p.deploy()
    d = Dispatcher(p)
    r = Router(d, p)
    d.register(Poke, handle_poke)

    await p.start_routing(r)


if __name__ == "__main__":
    lab = LabParser().parse("./lab")
    p = Provisioner(lab)
    p.add_machine(lab.get_machine("red"), Role.AGENT)
    p.add_machine(lab.get_machine("blue"), Role.AGENT)
    p.add_machine(lab.get_machine("controller"), Role.CONTROLLER)

    loop = asyncio.new_event_loop()
    loop.create_task(main(p))
    loop.run_forever()
