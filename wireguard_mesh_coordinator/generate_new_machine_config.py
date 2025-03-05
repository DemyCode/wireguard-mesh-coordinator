import os

from wireguard_mesh_coordinator.utils import Interface, Peer, WireGuardConfig


def generate_config(
    peer_wire_guard_config: WireGuardConfig, peer_ip: str, next_internal_ip: str
) -> WireGuardConfig:
    public_key = os.popen(f'echo {peer_wire_guard_config.interface.private_key} | wg pubkey').read().strip()
    peer_from_interface = Peer(
        public_key=public_key,
        allowed_ips=f"{next_internal_ip}/32",
        endpoint=peer_ip,
        persistent_keepalive=25,
    )
    private_key = os.popen("wg genkey").read().strip()
    new_interface = Interface(
        private_key=private_key,
        listen_port=51820,
        address=f"{next_internal_ip}/24",
    )
    return WireGuardConfig(
        interface=new_interface,
        peers=peer_wire_guard_config.peers + [peer_from_interface],
    )
