from wireguard_mesh_coordinator.command import generate_next_ip
from wireguard_mesh_coordinator.utils import WireGuardConfig, wg_quick_parser

if __name__ == "__main__":
    with open("/etc/wireguard/remote.conf", "r") as file:
        wireguard_config = wg_quick_parser(file.read())
    print(generate_next_ip(wireguard_config))
