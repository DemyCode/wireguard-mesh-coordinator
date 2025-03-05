import os
from pydantic import BaseModel
from typing import List

class Interface(BaseModel):
    private_key: str
    listen_port: int
    address: str


class Peer(BaseModel):
    public_key: str
    allowed_ips: str
    endpoint: str
    persistent_keepalive: int


class WireGuardConfig(BaseModel):
    interface: Interface
    peers: List[Peer]


def wg_quick_parser(wg_quick_config: str) -> WireGuardConfig:
    lines = wg_quick_config.splitlines()
    peers = []
    public_key = None
    allowed_ips = None
    endpoint = None
    persistent_keepalive = None
    private_key = None
    listen_port = None
    address = None
    for line in lines:
        if line.startswith("PrivateKey"):
            private_key = line.split(" = ")[1].strip()
        elif line.startswith("ListenPort"):
            listen_port = int(line.split(" = ")[1].strip())
        elif line.startswith("Address"):
            address = line.split(" = ")[1].strip()
        elif line.startswith("PublicKey"):
            public_key = line.split(" = ")[1].strip()
        elif line.startswith("AllowedIPs"):
            allowed_ips = line.split(" = ")[1].strip()
        elif line.startswith("Endpoint"):
            endpoint = line.split(" = ")[1].strip()
        elif line.startswith("PersistentKeepalive"):
            persistent_keepalive = int(line.split(" = ")[1].strip())
        if (
            line.startswith("[Peer]")
            and public_key is not None
            and allowed_ips is not None
            and endpoint is not None
            and persistent_keepalive is not None
        ):
            peers.append(
                Peer(
                    public_key=public_key,
                    allowed_ips=allowed_ips,
                    endpoint=endpoint,
                    persistent_keepalive=persistent_keepalive,
                )
            )
    if (
        public_key is not None
        and allowed_ips is not None
        and endpoint is not None
        and persistent_keepalive is not None
    ):
        peers.append(
            Peer(
                public_key=public_key,
                allowed_ips=allowed_ips,
                endpoint=endpoint,
                persistent_keepalive=persistent_keepalive,
            )
        )
    if private_key is None or listen_port is None or address is None:
        raise ValueError
    return WireGuardConfig(
        interface=Interface(
            private_key=private_key, listen_port=listen_port, address=address
        ),
        peers=peers,
    )


def wg_quick_dump(wireguard_config: WireGuardConfig) -> str:
    wg_quick_config = "[Interface]\n"
    wg_quick_config += f"PrivateKey = {wireguard_config.interface.private_key}\n"
    wg_quick_config += f"ListenPort = {wireguard_config.interface.listen_port}\n"
    wg_quick_config += f"Address = {wireguard_config.interface.address}\n"
    for peer in wireguard_config.peers:
        wg_quick_config += "[Peer]\n"
        wg_quick_config += f"PublicKey = {peer.public_key}\n"
        wg_quick_config += f"AllowedIPs = {peer.allowed_ips}\n"
        wg_quick_config += f"Endpoint = {peer.endpoint}\n"
        wg_quick_config += f"PersistentKeepalive = {peer.persistent_keepalive}\n"
    return wg_quick_config

class NewPeer(BaseModel):
    public_key: str
    allowed_ips: str
    endpoint: str

def add_peer(new_peer: NewPeer):
    wireguard_config = None
    with open("/etc/wireguard/wg0.conf", "r") as file:
        wireguard_config = wg_quick_parser(file.read())
    updated_wireguard_config = WireGuardConfig(
        interface=wireguard_config.interface,
        peers=wireguard_config.peers
        + [
            Peer(
                public_key=new_peer.public_key,
                allowed_ips=new_peer.allowed_ips,
                endpoint=new_peer.endpoint,
                persistent_keepalive=25,
            )
        ],
    )
    with open("/etc/wireguard/wg0.conf", "w") as file:
        file.write(wg_quick_dump(updated_wireguard_config))
    os.system("wg-quick down wg0")
    os.system("wg-quick up /etc/wireguard/wg0.conf")
