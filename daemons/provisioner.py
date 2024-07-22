from typing import Iterable
from Kathara.model.Machine import Machine
from Kathara.model.Lab import Lab
from Kathara.manager.Kathara import Kathara
import threading


class MachineConnection:
    def __init__(self, machine: Machine):
        self.machine = machine


class Provisioner:
    def __init__(self, lab: Lab):
        self.connections: dict[str, MachineConnection] = {}
        self.lab = lab

    def deploy(self):
        pass

    def new_device(self, ):



def main():
    lab = Lab("calinka")

    red = lab.new_machine(
        "red",
        image="ghcr.io/buonhobo/agent:latest",
    )
    blue = lab.new_machine(
        "blue",
        image="ghcr.io/buonhobo/agent:latest",
    )
    controller = lab.new_machine(
        "controller",
        image="ghcr.io/buonhobo/controller:latest",
        bridged=True,
        ports=["8888:8888"],
    )

    lab.connect_machine_to_link(red.name, "A")
    lab.connect_machine_to_link(blue.name, "A")
    lab.connect_machine_to_link(controller.name, "A")

    lab.create_file_from_string(
        """
        ip a add 10.10.10.11/24 dev eth0
        """,
        dst_path="red.startup",
    )

    lab.create_file_from_string(
        """
        ip a add 10.10.10.12/24 dev eth0
        """,
        dst_path="blue.startup",
    )

    lab.create_file_from_string(
        """
        ip a add 10.10.10.10/24 dev eth0
        """,
        dst_path="controller.startup",
    )

    red.create_file_from_path("../agent/agent.py", "/agent/agent.py")

    Kathara.get_instance().deploy_lab(lab)

    Kathara.get_instance().exec(
        machine_name="red",
        command="bash -c 'python3 /agent/agent.py < /agent/in > /agent/out &'",
        lab=lab,
        wait=True,
    )

    print("started tailing", flush=True)
    out = Kathara.get_instance().exec(
        machine_name="red",
        command="cat /agent/out",
        lab=lab,
        stream=True,
    )

    p = '{"src": "controller", "dest": "agent", "type": "Handshake", "payload": {"role": "agent"}}'
    s = f"bash -c 'cat <<EOF > /agent/in\n{p}\nEOF\n'"

    Kathara.get_instance().exec(
        "red",
        s,
        None,
        None,
        lab,
    )

    # threading.Thread(
    #     target=lambda: Kathara.get_instance().connect_tty(machine_name="red", lab=lab)
    # ).start()

    for a, _ in out:
        print("out", a, flush=True)

    # Kathara.get_instance().connect_tty(machine_name="red", lab=lab)
    # Kathara.get_instance().wipe()


if __name__ == "__main__":
    main()
