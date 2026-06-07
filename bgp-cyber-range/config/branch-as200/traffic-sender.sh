#!/bin/bash

echo "Starting traffic sender..."
while true; do
    curl -X POST -H "Content-Type: application/json" -d '{"test":"traffic"}' http://192.168.10.1:8080 1>/dev/null 2>&1
    echo "[sender] request sent..."
    sleep 5
done