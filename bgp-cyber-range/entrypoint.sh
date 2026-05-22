#!/bin/bash

# Start StrongSwan IPsec daemon in the background
echo "Starting StrongSwan IPsec..."
ipsec start

# Configure WireGuard
echo "Configuring WireGuard Lane..."
# 1. Create WireGuard network interface
ip link add dev wg0 type wireguard
# 2. Apply configuration
wg setconf wg0 /etc/wireguard/wg0.conf

# 3. Assign tunnel IP defined in wg0.conf
if [ "$(hostname)" = "router-main-as100" ]; then
	ip addr add 10.0.99.1/24 dev wg0
elif [ "$(hostname)" = "router-branch-as200" ]; then
	ip addr add 10.0.99.2/24 dev wg0
fi

# 4. Bring interface up
ip link set up dev wg0


# Execute original FRR entrypoint
echo "Launching FRR..."
exec /usr/lib/frr/docker-start