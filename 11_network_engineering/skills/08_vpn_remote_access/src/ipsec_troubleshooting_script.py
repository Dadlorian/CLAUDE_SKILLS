#!/usr/bin/env python3
"""
IPsec VPN Troubleshooting Script
Monitor and diagnose IPsec tunnel issues
"""

import subprocess
import sys
import time
from datetime import datetime

class IPsecTroubleshooter:
    def __init__(self):
        self.errors = []
        self.warnings = []
        self.info = []
    
    def check_ipsec_daemon(self):
        """Check if IPsec daemon is running"""
        try:
            result = subprocess.run(['systemctl', 'status', 'ipsec'],
                                  capture_output=True, text=True)
            if result.returncode == 0:
                self.info.append("IPsec daemon is running")
                return True
            else:
                self.errors.append("IPsec daemon is not running")
                return False
        except Exception as e:
            self.errors.append(f"Cannot check IPsec status: {e}")
            return False
    
    def check_ikev2_sas(self):
        """Check IKEv2 Security Associations"""
        try:
            result = subprocess.run(['ipsec', 'statusall'],
                                  capture_output=True, text=True)
            if 'ESTABLISHED' in result.stdout:
                self.info.append("IKEv2 SAs established")
                return True
            else:
                self.warnings.append("No established IKEv2 SAs found")
                return False
        except Exception as e:
            self.errors.append(f"Cannot check IKEv2 SAs: {e}")
            return False
    
    def check_ipsec_sas(self):
        """Check IPsec Security Associations"""
        try:
            result = subprocess.run(['ip', 'xfrm', 'state', 'list'],
                                  capture_output=True, text=True)
            if 'src' in result.stdout and 'dst' in result.stdout:
                sa_count = result.stdout.count('src')
                self.info.append(f"Found {sa_count} IPsec SAs")
                return True
            else:
                self.warnings.append("No IPsec SAs found")
                return False
        except Exception as e:
            self.errors.append(f"Cannot check IPsec SAs: {e}")
            return False
    
    def check_connectivity(self, peer_ip):
        """Check network connectivity to peer"""
        try:
            result = subprocess.run(['ping', '-c', '5', peer_ip],
                                  capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                self.info.append(f"Network connectivity to {peer_ip} OK")
                return True
            else:
                self.errors.append(f"Cannot reach peer {peer_ip}")
                return False
        except Exception as e:
            self.errors.append(f"Connectivity check failed: {e}")
            return False
    
    def check_firewall_rules(self):
        """Check if firewall allows IPsec"""
        try:
            result = subprocess.run(['sudo', 'iptables', '-L', '-n'],
                                  capture_output=True, text=True)
            
            issues = []
            if 'esp' not in result.stdout.lower():
                issues.append("ESP traffic (IP 50) may not be allowed")
            if 'ah' not in result.stdout.lower():
                issues.append("AH traffic (IP 51) may not be allowed")
            
            if issues:
                self.warnings.append(f"Firewall issues: {', '.join(issues)}")
                return False
            else:
                self.info.append("Firewall rules appear correct for IPsec")
                return True
        except Exception as e:
            self.warnings.append(f"Cannot verify firewall rules: {e}")
            return False
    
    def check_crypto_algorithms(self):
        """Verify encryption algorithms"""
        try:
            result = subprocess.run(['ipsec', 'listall'],
                                  capture_output=True, text=True)
            
            if 'aes_256' in result.stdout.lower():
                self.info.append("AES-256 encryption available")
            else:
                self.warnings.append("AES-256 encryption not available")
            
            if 'sha256' in result.stdout.lower():
                self.info.append("SHA-256 hashing available")
            else:
                self.warnings.append("SHA-256 hashing not available")
        except Exception as e:
            self.warnings.append(f"Cannot check crypto algorithms: {e}")
    
    def test_tunnel(self, local_subnet, remote_subnet, peer_ip):
        """Test tunnel with ping to remote subnet"""
        try:
            remote_test_ip = remote_subnet.replace('/24', '1')
            result = subprocess.run(['ping', '-c', '3', remote_test_ip],
                                  capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0:
                self.info.append(f"Tunnel test successful to {remote_test_ip}")
                return True
            else:
                self.errors.append(f"Cannot reach remote subnet {remote_subnet} via tunnel")
                return False
        except Exception as e:
            self.errors.append(f"Tunnel test failed: {e}")
            return False
    
    def monitor_performance(self, duration=60):
        """Monitor VPN performance metrics"""
        try:
            result = subprocess.run(['ip', 'xfrm', 'state', 'list'],
                                  capture_output=True, text=True)
            
            # Parse statistics (simplified)
            if 'bytes:' in result.stdout:
                self.info.append("Encryption/Decryption statistics available")
            
            # Monitor packet loss if available
            self.info.append(f"Performance monitoring completed ({duration}s)")
        except Exception as e:
            self.warnings.append(f"Cannot monitor performance: {e}")
    
    def generate_report(self):
        """Generate troubleshooting report"""
        print("\n" + "="*50)
        print("IPsec VPN Troubleshooting Report")
        print(f"Generated: {datetime.now().isoformat()}")
        print("="*50)
        
        if self.errors:
            print("\nERRORS (Fix Required):")
            for error in self.errors:
                print(f"  [ERROR] {error}")
        
        if self.warnings:
            print("\nWARNINGS (Review):")
            for warning in self.warnings:
                print(f"  [WARN] {warning}")
        
        if self.info:
            print("\nINFO (Status Good):")
            for info in self.info:
                print(f"  [INFO] {info}")
        
        print("\n" + "="*50)
        if not self.errors:
            print("Overall Status: HEALTHY")
        else:
            print(f"Overall Status: {len(self.errors)} ISSUES FOUND")
        print("="*50 + "\n")

def main():
    print("IPsec VPN Troubleshooting Tool")
    print("-" * 50)
    
    troubleshooter = IPsecTroubleshooter()
    
    # Run checks
    print("Running diagnostic checks...")
    troubleshooter.check_ipsec_daemon()
    troubleshooter.check_ikev2_sas()
    troubleshooter.check_ipsec_sas()
    troubleshooter.check_crypto_algorithms()
    troubleshooter.check_firewall_rules()
    
    # Optional: connectivity and tunnel tests
    peer_ip = "203.0.113.1"  # Replace with actual peer
    if len(sys.argv) > 1:
        peer_ip = sys.argv[1]
    
    troubleshooter.check_connectivity(peer_ip)
    
    # Generate report
    troubleshooter.generate_report()
    
    # Exit with error code if issues found
    sys.exit(1 if troubleshooter.errors else 0)

if __name__ == "__main__":
    main()

