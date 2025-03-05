from wireguard_mesh_coordinator.api import serve
from wireguard_mesh_coordinator.generate_new_machine_config import generate_config
from wireguard_mesh_coordinator.command import (
    add_to_all_peers_and_myself,
    generate_next_ip_func,
)
from typer import Typer
from wireguard_mesh_coordinator.utils import NewPeer, wg_quick_parser

app = Typer()


@app.command()
def api():
    serve()


@app.command()
def generate_new_machine_config(peer_ip: str, next_internal_ip: str, remote_config: str, output: str):
    with open(remote_config, "r") as file:
        peer_wire_guard_config = wg_quick_parser(file.read())
    new_config = generate_config(peer_wire_guard_config, peer_ip, next_internal_ip)
    with open(output, "w") as file:
        file.write(str(new_config))

@app.command()
def generate_next_ip():
    with open("/etc/wireguard/wg0.conf", "r") as file:
        wireguard_config = wg_quick_parser(file.read())
    print(generate_next_ip_func(wireguard_config), end="")


@app.command()
def register_and_propagate_new_machine(public_key: str, allowed_ips: str, endpoint: str):
    add_to_all_peers_and_myself(NewPeer(public_key=public_key, allowed_ips=allowed_ips, endpoint=endpoint))

