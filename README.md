# Data-Plane Fingerprinting Range (DPFR)

The goal is to build an isolated, multi-Autonomous System (AS) cyber range. Within this range, corporate sites maintain encrypted tunnels. An adversarial AS will execute an active BGP prefix hijacking/interception attack. To detect this attack without relying on traditional BGP routers' control-plane data, you will implement an eBPF-based telemetry sensor that fingerprints physical path variations (such as TCP Round-Trip Time and IP Time-To-Live). A Go daemon will ingest this telemetry, detect the hijack, and execute an active defense response by rerouting traffic.

# Milestone 1

```bash
cd bgp-cyber-range
```

This configuration establishes a containerized, multi-AS virtual internet topology using Docker Compose and FRRouting (FRR) to simulate an enterprise core network, a remote branch, a legitimate transit ISP, and an adversarial network. By establishing authentic eBGP peerings over isolated Layer 2 subnets, it builds an operational data plane capable of exchanging traffic via deterministic, multi-hop AS paths, providing a clean baseline environment for analyzing BGP path routing variations.

## Multi-Autonomous System (AS) Cyber Range

* AS 100: Enterprise Main
* AS 200: Remote Branch
* AS 300: Transit ISP (Connecting Main and Branch)
* AS 666: Rogue ISP

| AS | Role                  | Configured Subnet(s)                     | Router ID  |
|-|-|-|-|
| AS 100 | Main | 192.168.10.0/24 (Internal), 10.100.30.0/24 (WAN to ISP), 10.166.60.0/24 (WAN to Rogue) | 1.1.1.1 |
| AS 200 | Remote Branch | 192.168.20.0/24 (Internal), 10.200.30.0/24 (WAN to ISP) | 2.2.2.2 |
| AS 300 | Transit ISP | 10.100.30.0/24, 10.200.30.0/24            | 3.3.3.3 |
| AS 666 | Rogue ISP   | 10.166.60.0/24                            | 6.6.6.6 |


## Usage

1. Bring the Infrastructure Online: Deploy the network segments, initialize the routing nodes, and establish the eBGP handshakes

(If using `podman`, run `systemctl --user enable --now podman.socket` so that `docker-compose` work)

```bash
docker-compose build
docker-compose up -d
```

<!-- (If using `podman`, run: 
```bash
podman exec -it router-transit-as300 sysctl -w net.ipv4.ip_forward=1
```
) -->

2. Verify Control Plane Status: Ensure the Main Office has formed valid peering relationships with both providers and has integrated the path to the Remote Branch into its routing table

```bash
# Check that neighbor connections are established (look for integers under State/PfxRcd)
docker exec -it router-main-as100 vtysh -c "show ip bgp summary"

# Confirm the path to 192.168.20.0/24 resolves via the AS-Path: 300 200
docker exec -it router-main-as100 vtysh -c "show ip bgp"
```

3. Verify Data Plane Transit: Validate end-to-end user data transit and map the baseline physical path hop count by sourcing traffic from the internal network interface

```bash
# Test connectivity across the backbone
docker exec -it router-main-as100 ping -c 3 -I 192.168.10.1 192.168.20.1

# Trace the route to verify traffic passes explicitly through Transit ISP (10.100.30.3)
docker exec -it router-main-as100 traceroute -n -s 192.168.10.1 192.168.20.1
```

4. Shutdown the Infrastructure

```bash
docker-compose down
```

# Milestone 2

```
                  +-----------------------------------------+
                  |         [Production Lane] IKEv2 IPsec    |
                  |     (Routed normally over Transit AS300) |
                  +-----------------------------------------+
                                    |
+----------------------+            v            +------------------------+
|                      |=========================|                        |
|  router-main-as100   |                         |  router-branch-as200   |
|  (192.168.10.1)      |=========================|  (192.168.20.1)        |
+----------------------+            ^            +------------------------+
                                    |
                  +-----------------------------------------+
                  |         [Remediation Lane] WireGuard     |
                  |     (Dormant / Backup failover link)    |
                  +-----------------------------------------+
```

**The Production Lane (StrongSwan IPsec)**: This represents standard corporate traffic. It runs over the public WAN IPs across AS 300. When the rogue AS 666 eventually hijacks the BGP prefixes in Milestone 3, this IPsec tunnel will get disrupted or intercepted.

**The Remediation Lane (WireGuard)**: This is your out-of-band "emergency lane." It stays dormant until your Go daemon (which you'll build later) detects the hijack via eBPF and forces traffic onto it.

1. Verify StrongSwan connection:
```bash
docker exec -it router-main-as100 ipsec status
```

### Routers

| Role    | Internal     | Main WAN/ISP | Remote WAN/ISP | Rogue WAN | Wireguard
|-|-|-|-|-|-|
| Main    | 192.168.10.1 | 10.100.30.2 |             | 10.166.60.2  | 10.0.99.1 |
| Branch  | 192.168.20.1 |             | 10.200.30.2 |              | 10.0.99.2 |
| Transit |              | 10.100.30.3 | 10.200.30.3 |              | |
| Rogue   |              |             |             | 10.166.60.66 | |
