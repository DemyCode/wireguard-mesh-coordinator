import re
import requests

from wireguard_mesh_coordinator.api import NewPeer
from wireguard_mesh_coordinator.utils import (
    WireGuardConfig,
    add_peer,
    wg_quick_parser,
)


def add_to_all_peers_and_myself(new_peer: NewPeer):
    with open("/etc/wireguard/wg0.conf", "r") as file:
        wireguard_config = wg_quick_parser(file.read())
        for peer in wireguard_config.peers:
            requests.post(f"http://{peer.endpoint}/add_peer", json=new_peer.json())
    add_peer(new_peer)


def generate_next_ip_func(wireguard_config: WireGuardConfig) -> str:
    taken_ips = {i: False for i in range(1, 255)}
    ip = re.sub(r"10\.0\.0\.(\d+)/.*", r"\1", wireguard_config.interface.address)
    taken_ips[int(ip)] = True
    for peer in wireguard_config.peers:
        ip = re.sub(r"10\.0\.0\.(\d+)/.*", r"\1", peer.allowed_ips)
        taken_ips[int(ip)] = True
    for i, taken in taken_ips.items():
        if not taken:
            return i
    raise ValueError
