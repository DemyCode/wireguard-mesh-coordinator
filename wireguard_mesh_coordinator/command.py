import os
import requests

from wireguard_mesh_coordinator.api import NewPeer
from wireguard_mesh_coordinator.utils import (
    Interface,
    Peer,
    WireGuardConfig,
    add_peer,
    wg_quick_parser,
)


def add_to_all_peers(new_peer: NewPeer):
    with open("/etc/wireguard/wg0.conf", "r") as file:
        wireguard_config = wg_quick_parser(file.read())
        for peer in wireguard_config.peers:
            requests.post(f"http://{peer.endpoint}/add_peer", json=new_peer.json())
    add_peer(new_peer)


def generate_next_ip(wireguard_config: WireGuardConfig) -> str:
    taken_ips = [False] * 255
    for peer in wireguard_config.peers:
        ip = int(peer.allowed_ips.split("/")[0].split(".")[3])
        taken_ips[ip] = True
    for i, taken in enumerate(taken_ips):
        if not taken:
            return f"10.0.0.{i + 1}"
    raise ValueError


def generate_config(
    peer_wire_guard_config: WireGuardConfig, peer_ip: str, next_internal_ip: str
) -> WireGuardConfig:
    os.system(
        f"wg pubkey < {peer_wire_guard_config.interface.private_key} > public_key"
    )
    with open("public_key", "r") as file:
        public_key = file.read().strip()
    peer_from_interface = Peer(
        public_key=public_key,
        allowed_ips=f"{next_internal_ip}/32",
        endpoint=peer_ip,
        persistent_keepalive=25,
    )
    os.system("wg genkey")
    with open("private_key", "r") as file:
        private_key = file.read().strip()
    new_interface = Interface(
        private_key=private_key,
        listen_port=51820,
        address=f"{next_internal_ip}/24",
    )
    return WireGuardConfig(
        interface=new_interface,
        peers=peer_wire_guard_config.peers + [peer_from_interface],
    )
