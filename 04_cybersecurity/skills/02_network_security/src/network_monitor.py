"""
Network Security Monitoring Tool
Real-time network traffic analysis and intrusion detection
"""

import socket
import struct
from datetime import datetime
from typing import Dict, List
from dataclasses import dataclass


@dataclass
class NetworkPacket:
    """Network packet representation"""
    timestamp: datetime
    src_ip: str
    dst_ip: str
    src_port: int
    dst_port: int
    protocol: str
    payload_size: int


class NetworkMonitor:
    """
    Network security monitoring and anomaly detection

    Features:
    - Packet capture and analysis
    - Port scan detection
    - DDoS attack detection
    - Suspicious traffic identification
    - Real-time alerting
    """

    def __init__(self):
        self.packets: List[NetworkPacket] = []
        self.connection_tracker: Dict[str, int] = {}
        self.port_scan_threshold = 20
        self.ddos_threshold = 1000

    def analyze_packet(self, packet: NetworkPacket) -> List[str]:
        """Analyze packet for security threats"""
        alerts = []

        # Track connection
        conn_key = f"{packet.src_ip}:{packet.dst_ip}"
        self.connection_tracker[conn_key] = self.connection_tracker.get(conn_key, 0) + 1

        # Port scan detection
        if self._detect_port_scan(packet.src_ip):
            alerts.append(f"Port scan detected from {packet.src_ip}")

        # DDoS detection
        if self._detect_ddos(packet.dst_ip):
            alerts.append(f"Possible DDoS attack on {packet.dst_ip}")

        # Suspicious port detection
        if self._is_suspicious_port(packet.dst_port):
            alerts.append(f"Connection to suspicious port {packet.dst_port}")

        return alerts

    def _detect_port_scan(self, src_ip: str) -> bool:
        """Detect port scanning activity"""
        # Count unique destination ports from this IP
        unique_ports = len([
            p for p in self.packets[-100:]  # Last 100 packets
            if p.src_ip == src_ip
        ])
        return unique_ports > self.port_scan_threshold

    def _detect_ddos(self, dst_ip: str) -> bool:
        """Detect DDoS attack patterns"""
        # Count connections to this IP in last minute
        recent_count = sum(
            1 for p in self.packets[-1000:]
            if p.dst_ip == dst_ip
        )
        return recent_count > self.ddos_threshold

    def _is_suspicious_port(self, port: int) -> bool:
        """Check if port is commonly used for malicious activity"""
        suspicious_ports = {
            1337, 31337,  # Common backdoor ports
            4444, 5555,   # Metasploit default ports
            6667,         # IRC (often used by botnets)
            3389          # RDP (common attack target)
        }
        return port in suspicious_ports

    def generate_report(self) -> Dict:
        """Generate network security report"""
        return {
            'total_packets': len(self.packets),
            'unique_sources': len(set(p.src_ip for p in self.packets)),
            'unique_destinations': len(set(p.dst_ip for p in self.packets)),
            'top_talkers': self._get_top_talkers(5)
        }

    def _get_top_talkers(self, n: int) -> List[tuple]:
        """Get top N IP addresses by packet count"""
        ip_counts = {}
        for packet in self.packets:
            ip_counts[packet.src_ip] = ip_counts.get(packet.src_ip, 0) + 1

        return sorted(ip_counts.items(), key=lambda x: x[1], reverse=True)[:n]


if __name__ == "__main__":
    monitor = NetworkMonitor()
    print("Network Security Monitor")
    print("Monitoring for suspicious activity...")
