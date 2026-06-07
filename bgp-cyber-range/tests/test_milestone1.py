"""
Milestone 1 — Multi-AS BGP topology and data plane transit.

Control plane: eBGP sessions established, routes propagated correctly.
Data plane:    end-to-end ping routes through Transit (not directly).
"""


def _bgp_peer_established(summary: str, peer_ip: str) -> bool:
    """True if the BGP peer shows an integer (prefix count) in State/PfxRcd."""
    for line in summary.splitlines():
        if line.startswith(peer_ip):
            fields = line.split()
            return len(fields) > 9 and fields[9].isdigit()
    return False


class TestBGPSessions:

    def test_main_peers_with_transit(self, main):
        out = main("vtysh", "-c", "show ip bgp summary")
        assert _bgp_peer_established(out, "10.100.30.3"), (
            "Main (AS100) ↔ Transit (AS300) session not established\n" + out
        )

    def test_main_peers_with_rogue(self, main):
        out = main("vtysh", "-c", "show ip bgp summary")
        assert _bgp_peer_established(out, "10.166.60.66"), (
            "Main (AS100) ↔ Rogue (AS666) session not established\n" + out
        )

    def test_branch_peers_with_transit(self, branch):
        out = branch("vtysh", "-c", "show ip bgp summary")
        assert _bgp_peer_established(out, "10.200.30.3"), (
            "Branch (AS200) ↔ Transit (AS300) session not established\n" + out
        )

    def test_transit_peers_with_main(self, transit):
        out = transit("vtysh", "-c", "show ip bgp summary")
        assert _bgp_peer_established(out, "10.100.30.2"), (
            "Transit (AS300) ↔ Main (AS100) session not established\n" + out
        )

    def test_transit_peers_with_branch(self, transit):
        out = transit("vtysh", "-c", "show ip bgp summary")
        assert _bgp_peer_established(out, "10.200.30.2"), (
            "Transit (AS300) ↔ Branch (AS200) session not established\n" + out
        )


class TestRouteLearning:

    def test_main_learns_branch_prefix_via_transit(self, main):
        out = main("vtysh", "-c", "show ip bgp 192.168.20.0/24")
        assert "300 200" in out, (
            "Main does not have 192.168.20.0/24 with AS-Path '300 200'\n" + out
        )

    def test_branch_learns_main_prefix_via_transit(self, branch):
        out = branch("vtysh", "-c", "show ip bgp 192.168.10.0/24")
        assert "300 100" in out, (
            "Branch does not have 192.168.10.0/24 with AS-Path '300 100'\n" + out
        )


class TestDataPlane:

    def test_ping_main_to_branch(self, main):
        out = main("ping", "-c", "3", "-I", "192.168.10.1", "192.168.20.1")
        assert "0% packet loss" in out, (
            "Ping from Main (192.168.10.1) to Branch (192.168.20.1) failed\n" + out
        )

    def test_traffic_routes_through_transit(self, main):
        out = main("ip", "route", "get", "192.168.20.1")
        assert "via 10.100.30.3" in out, (
            "Kernel routing table does not route 192.168.20.1 through Transit (10.100.30.3)\n" + out
        )
