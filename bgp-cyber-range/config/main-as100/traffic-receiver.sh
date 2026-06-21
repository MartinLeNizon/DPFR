#!/bin/sh

# Wait for FRR to bring up the loopback IP before listening
until ip addr show lo | grep -q "192.168.10.1"; do sleep 1; done
echo "Starting traffic receiver on 192.168.10.1:8080..."
while true; do
    PAYLOAD=$(printf 'HTTP/1.1 200 OK\r\nContent-Length: 2\r\nConnection: close\r\n\r\nOK' \
        | nc -l 192.168.10.1 8080)
    echo "[receiver] $(date -Iseconds) payload: $(echo "$PAYLOAD" | tail -1)"
done
