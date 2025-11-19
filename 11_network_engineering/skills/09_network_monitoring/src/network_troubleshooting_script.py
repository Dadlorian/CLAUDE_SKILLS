#!/usr/bin/env python3
"""Network Troubleshooting Automation"""

import subprocess
import socket
import sys

class NetworkTroubleshooter:
    @staticmethod
    def ping_host(host):
        """Test connectivity with ping"""
        try:
            result = subprocess.run(['ping', '-c', '1', host],
                                  capture_output=True, timeout=2)
            return result.returncode == 0
        except:
            return False
    
    @staticmethod
    def traceroute(host):
        """Trace route to destination"""
        try:
            result = subprocess.run(['traceroute', host],
                                  capture_output=True, timeout=10, text=True)
            return result.stdout
        except:
            return None
    
    @staticmethod
    def check_dns(hostname):
        """Check DNS resolution"""
        try:
            ip = socket.gethostbyname(hostname)
            return ip
        except:
            return None
    
    @staticmethod
    def check_port(host, port):
        """Check if port is open"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(2)
            result = sock.connect_ex((host, port))
            sock.close()
            return result == 0
        except:
            return False
    
    def run_diagnostics(self, target_host):
        """Run full diagnostics"""
        results = {}
        
        # Ping
        results['ping'] = self.ping_host(target_host)
        
        # DNS
        results['dns'] = self.check_dns(target_host)
        
        # Traceroute
        results['traceroute'] = self.traceroute(target_host)
        
        # Port checks
        for port in [22, 80, 443]:
            results[f'port_{port}'] = self.check_port(target_host, port)
        
        return results

if __name__ == '__main__':
    ts = NetworkTroubleshooter()
    if len(sys.argv) > 1:
        target = sys.argv[1]
        results = ts.run_diagnostics(target)
        import json
        print(json.dumps(results, indent=2, default=str))
