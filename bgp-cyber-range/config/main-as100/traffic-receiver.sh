#!/bin/sh
# Minimal HTTP server bound to the Main internal IP.
# Accepts POST requests from Branch and replies 200 OK.
# Logs each received payload to stdout for visibility.

# Wait for FRR to bring up the loopback IP before listening
until ip addr show lo | grep -q "192.168.10.1"; do sleep 1; done
echo "Starting traffic receiver on 192.168.10.1:8080..."
while true; do
    PAYLOAD=$(printf 'HTTP/1.1 200 OK\r\nContent-Length: 2\r\nConnection: close\r\n\r\nOK' \
        | nc -l 192.168.10.1 8080)
    echo "[receiver] $(date -Iseconds) payload: $(echo "$PAYLOAD" | tail -1)"
done
