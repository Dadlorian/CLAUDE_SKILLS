#!/usr/bin/env python3
"""Network Health Check Script"""

import subprocess
import sys
import json
from datetime import datetime

def check_connectivity(host):
    """Check if host is reachable"""
    try:
        result = subprocess.run(['ping', '-c', '1', host], 
                              capture_output=True, timeout=2)
        return result.returncode == 0
    except:
        return False

def check_port(host, port):
    """Check if port is open"""
    try:
        result = subprocess.run(['nc', '-zv', '-w', '2', host, str(port)],
                              capture_output=True, timeout=3)
        return result.returncode == 0
    except:
        return False

def main():
    health_report = {
        "timestamp": datetime.now().isoformat(),
        "checks": []
    }
    
    # Define checks
    checks = [
        ("Internet Gateway", "8.8.8.8", 0),
        ("DNS Server", "8.8.8.8", 53),
        ("Router", "192.168.1.1", 0),
        ("Collector", "10.0.0.100", 9090),
    ]
    
    all_passed = True
    for name, host, port in checks:
        if port == 0:
            result = check_connectivity(host)
        else:
            result = check_port(host, port)
        
        health_report["checks"].append({
            "name": name,
            "host": host,
            "port": port,
            "status": "PASS" if result else "FAIL"
        })
        
        if not result:
            all_passed = False
    
    print(json.dumps(health_report, indent=2))
    return 0 if all_passed else 1

if __name__ == '__main__':
    sys.exit(main())
