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
AS=$(grep -m1 "^router bgp" /etc/frr/frr.conf | awk '{print $3}')
echo "Detected AS: $AS"
if [ "$AS" = "100" ]; then
	ip addr add 10.0.99.1/24 dev wg0
	ip route add 10.200.30.0/24 via 10.100.30.3 && echo "Route to Branch WAN added" || echo "WARNING: route to Branch WAN failed"
	chmod +x /usr/local/bin/traffic-receiver.sh
	/usr/local/bin/traffic-receiver.sh &
elif [ "$AS" = "200" ]; then
	ip addr add 10.0.99.2/24 dev wg0
	ip route add 10.100.30.0/24 via 10.200.30.3 && echo "Route to Main WAN added" || echo "WARNING: route to Main WAN failed"
	chmod +x /usr/local/bin/traffic-sender.sh
	/usr/local/bin/traffic-sender.sh &
fi
echo "Routing table at WireGuard startup:"
ip route show

# 4. Bring interface up
ip link set up dev wg0

# Execute original FRR entrypoint
echo "Launching FRR..."
exec /usr/lib/frr/docker-start