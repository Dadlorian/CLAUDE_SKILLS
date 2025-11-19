#!/usr/bin/env python3
"""
VPN Health Monitoring Script
Monitor VPN tunnel status and performance
"""

import subprocess
import json
import time
from datetime import datetime

class VPNHealthMonitor:
    def __init__(self):
        self.metrics = {}
        self.timestamp = datetime.now().isoformat()
    
    def get_ipsec_status(self):
        """Get IPsec tunnel status"""
        try:
            result = subprocess.run(['ipsec', 'statusall'],
                                  capture_output=True, text=True, timeout=5)
            
            connections = {}
            for line in result.stdout.split('\n'):
                if 'ESTABLISHED' in line or 'FAILED' in line:
                    parts = line.split()
                    if len(parts) > 0:
                        conn_name = parts[0]
                        status = 'up' if 'ESTABLISHED' in line else 'down'
                        connections[conn_name] = status
            
            return connections
        except Exception as e:
            return {"error": str(e)}
    
    def get_tunnel_stats(self):
        """Get tunnel statistics"""
        try:
            # IPsec statistics
            result = subprocess.run(['ip', 'xfrm', 'state', 'list'],
                                  capture_output=True, text=True, timeout=5)
            
            stats = {
                "total_sas": result.stdout.count('src'),
                "timestamp": datetime.now().isoformat()
            }
            return stats
        except Exception as e:
            return {"error": str(e)}
    
    def get_interface_stats(self):
        """Get VPN interface statistics"""
        try:
            interfaces = {}
            
            # Check tun/tap interfaces
            for iface in ['tun0', 'tun1', 'tap0', 'wg0']:
                try:
                    result = subprocess.run(['ip', 'link', 'show', iface],
                                          capture_output=True, text=True, timeout=2)
                    if result.returncode == 0:
                        stats = subprocess.run(['ip', '-s', 'link', 'show', iface],
                                             capture_output=True, text=True, timeout=2)
                        interfaces[iface] = "up"
                except:
                    pass
            
            return interfaces
        except Exception as e:
            return {"error": str(e)}
    
    def check_connectivity(self, test_ips):
        """Check connectivity to test IPs"""
        connectivity = {}
        
        for ip in test_ips:
            try:
                result = subprocess.run(['ping', '-c', '1', '-W', '2', ip],
                                      capture_output=True, text=True, timeout=5)
                connectivity[ip] = "reachable" if result.returncode == 0 else "unreachable"
            except:
                connectivity[ip] = "timeout"
        
        return connectivity
    
    def get_certificate_info(self):
        """Check VPN certificate validity"""
        certs = {}
        try:
            result = subprocess.run(['find', '/etc/ipsec.d/certs', '-name', '*.crt'],
                                  capture_output=True, text=True, timeout=5)
            
            for cert_file in result.stdout.split('\n'):
                if cert_file.strip():
                    try:
                        cert_info = subprocess.run(
                            ['openssl', 'x509', '-in', cert_file.strip(), '-noout', '-dates'],
                            capture_output=True, text=True, timeout=5
                        )
                        certs[cert_file.strip()] = cert_info.stdout
                    except:
                        pass
        except Exception as e:
            certs["error"] = str(e)
        
        return certs
    
    def get_memory_usage(self):
        """Monitor memory usage"""
        try:
            result = subprocess.run(['ps', 'aux'],
                                  capture_output=True, text=True, timeout=5)
            
            memory_usage = {}
            for line in result.stdout.split('\n'):
                if 'openvpn' in line or 'ipsec' in line or 'wireguard' in line:
                    parts = line.split()
                    if len(parts) > 5:
                        process = parts[10] if len(parts) > 10 else 'unknown'
                        mem = parts[5]
                        memory_usage[process] = f"{mem} MB"
            
            return memory_usage
        except Exception as e:
            return {"error": str(e)}
    
    def generate_health_report(self):
        """Generate comprehensive health report"""
        report = {
            "timestamp": self.timestamp,
            "ipsec_connections": self.get_ipsec_status(),
            "tunnel_stats": self.get_tunnel_stats(),
            "interfaces": self.get_interface_stats(),
            "connectivity": self.check_connectivity(["10.0.0.1", "192.168.1.1"]),
            "memory_usage": self.get_memory_usage(),
            "certificates": self.get_certificate_info()
        }
        return report
    
    def print_report(self, report):
        """Pretty print health report"""
        print("\n" + "="*60)
        print("VPN HEALTH MONITORING REPORT")
        print(f"Generated: {report['timestamp']}")
        print("="*60)
        
        print("\nIPSec Connections:")
        for conn, status in report.get("ipsec_connections", {}).items():
            print(f"  {conn}: {status}")
        
        print("\nTunnel Statistics:")
        for stat, value in report.get("tunnel_stats", {}).items():
            print(f"  {stat}: {value}")
        
        print("\nInterfaces:")
        for iface, status in report.get("interfaces", {}).items():
            print(f"  {iface}: {status}")
        
        print("\nConnectivity Test:")
        for ip, status in report.get("connectivity", {}).items():
            print(f"  {ip}: {status}")
        
        print("\nMemory Usage:")
        for process, memory in report.get("memory_usage", {}).items():
            print(f"  {process}: {memory}")
        
        print("\n" + "="*60 + "\n")

def main():
    print("VPN Health Monitoring")
    monitor = VPNHealthMonitor()
    
    report = monitor.generate_health_report()
    monitor.print_report(report)
    
    # Optionally save as JSON
    try:
        with open('/tmp/vpn_health_report.json', 'w') as f:
            json.dump(report, f, indent=2)
        print("Report saved to /tmp/vpn_health_report.json")
    except Exception as e:
        print(f"Could not save report: {e}")

if __name__ == "__main__":
    main()

