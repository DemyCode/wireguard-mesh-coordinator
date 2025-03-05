set -e

KNOWN_PEER="existing-peer-ip"
WG_INTERFACE="wg0"
USERNAME="root"

scp $USERNAME@$KNOWN_PEER:/etc/wireguard/$WG_INTERFACE.conf remote.conf

NEXT_IP=$(wireguard-mesh-coordinator generate-next-ip)
wireguard-mesh-coordinator generate-new-machine-config $KNOWN_PEER $NEXT_IP remote.conf /etc/wireguard/$WG_INTERFACE.conf

wg-quick down $WG_INTERFACE || echo "No existing interface to bring down"
wg-quick up $WG_INTERFACE

echo "New machine added to network"

ssh $USERNAME@$KNOWN_PEER "wireguard-mesh-coordinator register-and-propagate-new-machine $NEXT_IP $NEXT_IP $(curl -4 ifconfig.me)"

