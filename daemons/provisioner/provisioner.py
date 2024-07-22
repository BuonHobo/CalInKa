from Kathara.model.Lab import Lab
from Kathara.manager.Kathara import Kathara


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

        server="http://10.10.10.10:8888";

        pip install marshmallow --break-system-packages;

        until curl --output /dev/null --silent --fail $server; do
            sleep 1
        done

        curl -s -X POST -H "file:sandcat.go" -H "platform:linux" $server/file/download > splunkd;
        chmod +x splunkd;
        ./splunkd -server $server -group red -v &
        """,
        dst_path="red.startup",
    )

    lab.create_file_from_string(
        """
        ip a add 10.10.10.12/24 dev eth0

        server="http://10.10.10.10:8888";

        until curl --output /dev/null --silent --fail $server; do
            sleep 1
        done

        curl -s -X POST -H "file:sandcat.go" -H "platform:linux" $server/file/download > splunkd;
        chmod +x splunkd;
        ./splunkd -server $server -group blue -v &
        """,
        dst_path="blue.startup",
    )

    lab.create_file_from_string(
        """
        ip a add 10.10.10.10/24 dev eth0

        cd /caldera
        python3 server.py --insecure &
        """,
        dst_path="controller.startup",
    )

    red.create_file_from_path("../agent/agent.py", "/agent/agent.py")

    Kathara.get_instance().deploy_lab(lab)

    out = Kathara.get_instance().exec(
        machine_name="red",
        command="python /agent/agent.py < /agent/in > /agent/out",
        lab=lab,
        wait=True,
        stream=True,
    )

    out = Kathara.get_instance().exec(
        machine_name="red",
        command="tail -f /agent/out",
        lab=lab,
        wait=True,
        stream=True,
    )

    print("started tailing", flush=True)

    for a, _ in out:
        print(a)

    # Kathara.get_instance().connect_tty(machine_name="red", lab=lab)
    Kathara.get_instance().wipe()


if __name__ == "__main__":
    main()
