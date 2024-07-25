from multiprocessing.connection import Connection
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
import os
import multiprocessing


async def main(p: Provisioner):

    d = Dispatcher(p)
    r = Router(d, p)


if __name__ == "__main__":

    lab = LabParser().parse("./lab")
    p = Provisioner(lab)
    p.add_machine(lab.get_machine("red"), Role.AGENT)
    p.add_machine(lab.get_machine("blue"), Role.AGENT)
    p.add_machine(lab.get_machine("controller"), Role.CONTROLLER)
    Kathara.get_instance().deploy_lab(lab)
    par, c = os.pipe()
    os.set_inheritable(c, True)
    os.set_inheritable(par, True)
    child = os.fork()
    if child != 0:
        o = Kathara.get_instance().exec(
            "red",
            "bash -c 'while true; do echo ciao; sleep 1; done'",
            lab=lab,
            stream=True,
        )
        d = open(c, "wb")
        for a, _ in o:
            if a:
                d.write(a)
                d.flush()
        exit(0)
    child = os.fork()
    if child != 0:
        o = Kathara.get_instance().exec(
            "blue",
            "bash -c 'while true; do echo blue; sleep 1; done'",
            lab=lab,
            stream=True,
        )
        d = open(c, "wb")
        for a, _ in o:
            if a:
                d.write(a)
                d.flush()
        exit(0)
    else:
        d = open(par, "r")
        while True:
            print(d.read(5))
