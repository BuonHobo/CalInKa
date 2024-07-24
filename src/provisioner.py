from Kathara.model.Lab import Lab
from Kathara.manager.Kathara import Kathara
from Kathara.parser.netkit.LabParser import LabParser

from common.packet.Sender import Role, Sender
from common.packet.messages import IMessage, Packet, Poke
from provisioner.deployment.Provisioner import Provisioner


def main():
    lab = LabParser().parse("./lab")
    p = Provisioner(lab)
    p.add_machine(lab.get_machine("red"), Role.AGENT)
    p.add_machine(lab.get_machine("blue"), Role.AGENT)
    p.add_machine(lab.get_machine("controller"), Role.CONTROLLER)
    p.deploy()
    p.send_message("red", Poke(0))
    for o in p.get_output("red"):
        print(o.to_json())
        break
    Kathara.get_instance().wipe()


if __name__ == "__main__":
    main()
