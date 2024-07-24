import os
import signal
from Kathara.model.Lab import Lab
from Kathara.manager.Kathara import Kathara
from Kathara.parser.netkit.LabParser import LabParser

from common.dispatch.IPacketLauncher import IPacketLauncher
from common.dispatch.Dispatcher import Dispatcher
from common.packet.Sender import Role, Sender
from common.packet.messages import IMessage, Packet, Poke
from provisioner.config.Settings import Settings
from provisioner.deployment.Provisioner import Provisioner
from provisioner.dispatch.Router import Router
import asyncio


async def handle_poke(packet: Packet, launcher: IPacketLauncher):
    poke = packet.message
    assert isinstance(poke, Poke)
    poke.num += 1
    p = Packet.from_message(poke, Settings.sender, packet.src.name)
    await launcher.send(p)


async def main(p: Provisioner):

    d = Dispatcher(p)
    r = Router(d, p)
    d.register(Poke, handle_poke)

    await p.start_routing(r)
    await p.send(Packet.from_message(Poke(0), Sender("blue", Role.AGENT), "red"))
    await p.send(Packet.from_message(Poke(0), Settings.sender, "controller"))


if __name__ == "__main__":

    lab = LabParser().parse("./lab")
    p = Provisioner(lab)
    p.add_machine(lab.get_machine("red"), Role.AGENT)
    p.add_machine(lab.get_machine("blue"), Role.AGENT)
    p.add_machine(lab.get_machine("controller"), Role.CONTROLLER)
    p.deploy()

    loop = asyncio.new_event_loop()
    loop.create_task(main(p))
    loop.run_forever()
