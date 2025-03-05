set -e

KNOWN_PEER="existing-peer-ip"
WG_INTERFACE="wg0"
USERNAME="root"

scp $USERNAME@$KNOWN_PEER:/etc/wireguard/$WG_INTERFACE.conf remote.conf

NEXT_IP=generate_next_ip.py | tail -n 1
./generate_new_machine_config.py --peer-wire-guard-config remote.conf --peer-ip $KNOWN_PEER --next-internal-ip $NEXT_IP --output-file new.conf
mv new.conf /etc/wireguard/$WG_INTERFACE.conf

wg-quick down $WG_INTERFACE || echo "No existing interface to bring down"
wg-quick up $WG_INTERFACE

echo "New machine added to network"

ssh $USERNAME@$KNOWN_PEER "python add_to_all_peer.py $NEXT_IP"
