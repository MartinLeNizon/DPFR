#!/bin/bash

# Start StrongSwan IPsec daemon in the background
echo "Starting StrongSwan IPsec..."
ipsec start

# Execute original FRR entrypoint
echo "Launching FRR..."
exec /usr/lib/frr/docker-start