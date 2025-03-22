from typing import Optional
import os
from wireguard_mesh_coordinator.api import serve
from wireguard_mesh_coordinator.generate_new_machine_config import generate_config
from wireguard_mesh_coordinator.command import generate_next_ip_func
from typer import Typer
from wireguard_mesh_coordinator.utils import wg_quick_parser
from wireguard_mesh_coordinator.utils import WireGuardConfig, Interface
from wireguard_mesh_coordinator.command import add_to_all_peers_and_myself
from wireguard_mesh_coordinator.utils import NewPeer

app = Typer()


@app.command()
def api():
    serve()


def generate_new_machine_config(
    peer_ip: str, next_internal_ip: str, remote_config: str, output: str
):
    with open(remote_config, "r") as file:
        peer_wire_guard_config = wg_quick_parser(file.read())
    new_config = generate_config(peer_wire_guard_config, peer_ip, next_internal_ip)
    with open(output, "w") as file:
        file.write(str(new_config))


@app.command()
def solo_network():
    private_key = os.popen("wg genkey").read().strip()
    ip_address = os.popen("curl -4 ifconfig.me").read().strip()
    machine_config = WireGuardConfig(
        interface=Interface(
            private_key=private_key,
            listen_port=51820,
            address=ip_address + "/24",
        ),
        peers=[],
    )
    with open("/etc/wireguard/wg0.conf", "w") as file:
        file.write(str(machine_config))
    os.system("wg-quick down wg0")
    os.system("wg-quick up wg0")


@app.command()
def register_and_propagate_new_machine(
    public_key: str, allowed_ips: str, endpoint: str
):
    add_to_all_peers_and_myself(
        NewPeer(public_key=public_key, allowed_ips=allowed_ips, endpoint=endpoint)
    )


@app.command()
def enter_network(known_peer_ip: str, ssh_private_key: str):
    os.system(f"scp root@{known_peer_ip}:/etc/wireguard/wg0.conf remote.conf")
    with open("remote.conf", "r") as file:
        peer_wire_guard_config = wg_quick_parser(file.read())
    next_ip = generate_next_ip_func(peer_wire_guard_config)
    generate_new_machine_config(
        known_peer_ip, next_ip, "remote.conf", "/etc/wireguard/wg0.conf"
    )

    os.system("wg-quick down wg0")
    os.system("wg-quick up wg0")

    with open("/etc/wireguard/wg0.conf", "r") as file:
        wireguard_config = wg_quick_parser(file.read())
    private_key = wireguard_config.interface.private_key
    public_key = os.popen(f"echo {private_key} | wg pubkey").read().strip()
    os.system(
        f'ssh -i {ssh_private_key} root@{known_peer_ip} "wireguard-mesh-coordinator register-and-propagate-new-machine {public_key} {next_ip} $(curl -4 ifconfig.me)"'
    )
