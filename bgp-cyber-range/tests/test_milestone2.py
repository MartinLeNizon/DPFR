"""
Milestone 2 — Encrypted tunnels.

Production Lane:    StrongSwan IKEv2 IPsec tunnel between Main and Branch.
Remediation Lane:   WireGuard out-of-band tunnel (dormant failover link).
"""


class TestIPsecProductionLane:

    def test_main_ipsec_established(self, main):
        out = main("ipsec", "status")
        assert "ESTABLISHED" in out, (
            "Main IPsec tunnel is not established\n" + out
        )

    def test_branch_ipsec_established(self, branch):
        out = branch("ipsec", "status")
        assert "ESTABLISHED" in out, (
            "Branch IPsec tunnel is not established\n" + out
        )


class TestWireGuardRemediationLane:

    def test_main_wg_tunnel_ip(self, main):
        out = main("ip", "addr", "show", "wg0")
        assert "10.0.99.1/24" in out, (
            "Main wg0 does not have 10.0.99.1/24 assigned\n" + out
        )

    def test_branch_wg_tunnel_ip(self, branch):
        out = branch("ip", "addr", "show", "wg0")
        assert "10.0.99.2/24" in out, (
            "Branch wg0 does not have 10.0.99.2/24 assigned\n" + out
        )

    def test_wg_handshake_completed(self, main):
        out = main("wg", "show")
        assert "latest handshake" in out, (
            "WireGuard handshake has not been completed\n" + out
        )

    def test_ping_across_wireguard_tunnel(self, main):
        out = main("ping", "-c", "3", "10.0.99.2")
        assert "0% packet loss" in out, (
            "Ping across WireGuard tunnel (10.0.99.1 → 10.0.99.2) failed\n" + out
        )
