from argparse import ArgumentParser

from wireguard_mesh_coordinator.command import add_to_all_peers
from wireguard_mesh_coordinator.utils import NewPeer

if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("public-key", type=str)
    parser.add_argument("allowed-ips", type=str)
    parser.add_argument("endpoint", type=str)
    args = parser.parse_args()
    new_peer = NewPeer(
        public_key=args.public_key, allowed_ips=args.allowed_ips, endpoint=args.endpoint
    )
    add_to_all_peers(new_peer)
