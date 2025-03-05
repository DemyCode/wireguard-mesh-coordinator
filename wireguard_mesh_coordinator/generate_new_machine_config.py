from argparse import ArgumentParser

from wireguard_mesh_coordinator.command import generate_config
from wireguard_mesh_coordinator.utils import wg_quick_dump, wg_quick_parser

if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("peer-wire-guard-config", type=str)
    parser.add_argument("peer-ip", type=str)
    parser.add_argument("next-internal-ip", type=str)
    parser.add_argument("output-file", type=str)
    args = parser.parse_args()
    with open(args.peer_wire_guard_config, "r") as file:
        wireguard_config = wg_quick_parser(file.read())
    new_machine_config = generate_config(
        wireguard_config, args.peer_ip, args.next_internal_ip
    )
    with open(args.output_file, "w") as file:
        file.write(wg_quick_dump(new_machine_config))
