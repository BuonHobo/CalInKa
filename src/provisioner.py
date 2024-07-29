import asyncio

from Kathara.parser.netkit.LabParser import LabParser

from common.dispatch.SingletonLauncher import SingletonLauncher
from common.dispatch.Dispatcher import Dispatcher, handler_for
from common.dispatch.IPacketLauncher import IPacketLauncher
from common.packet.Sender import Role, Sender
from common.packet.messages import Command, Packet, Poke
from provisioner.config.Settings import Settings
from provisioner.deployment.Provisioner import Provisioner
from provisioner.dispatch.Router import Router


@handler_for(Poke)
async def handle_poke(packet: Packet):
    poke = packet.message
    assert isinstance(poke, Poke)
    poke.num += 1
    p = Packet.from_message(poke, Settings.sender, packet.src.name)
    await SingletonLauncher.get_instance().send(p)


async def main(p: Provisioner):
    await p.deploy()
    await p.start_routing()
    await p.send(
        Packet.from_message(Poke(0), Sender("provisioner", Role.PROVISIONER), "blue")
    )


if __name__ == "__main__":
    lab = LabParser().parse("./lab")
    p = Provisioner(lab)
    p.add_machine(lab.get_machine("red"), Role.AGENT)
    p.add_machine(lab.get_machine("blue"), Role.AGENT)
    p.add_machine(lab.get_machine("controller"), Role.CONTROLLER)

    loop = asyncio.new_event_loop()
    loop.create_task(main(p))
    loop.run_forever()
