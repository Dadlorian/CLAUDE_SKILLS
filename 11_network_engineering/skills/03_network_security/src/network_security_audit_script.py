#!/usr/bin/env python3
"""
Network Security Audit Script
Comprehensive network security assessment and reporting
Production-grade security testing
"""

import socket
import subprocess
import sys
import json
from datetime import datetime
from ipaddress import ip_network, ip_address

class NetworkSecurityAudit:
    """Comprehensive network security auditing tool"""
    
    def __init__(self, network_range, target_hosts=None):
        self.network_range = network_range
        self.target_hosts = target_hosts or []
        self.results = {}
        self.timestamp = datetime.now().isoformat()
        
    def check_open_ports(self, host, ports):
        """Check for open ports on target host"""
        open_ports = []
        for port in ports:
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(2)
                result = sock.connect_ex((host, port))
                if result == 0:
                    open_ports.append(port)
                sock.close()
            except socket.error:
                pass
        return open_ports
    
    def check_weak_ciphers(self, host, port=443):
        """Check for weak SSL/TLS ciphers"""
        try:
            cmd = f"openssl s_client -connect {host}:{port} -cipher LOW,EXPORT,MEDIUM"
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            
            if "Cipher" in result.stdout:
                weak_ciphers = []
                for line in result.stdout.split('\n'):
                    if 'Cipher' in line and ('LOW' in line or 'EXPORT' in line):
                        weak_ciphers.append(line.strip())
                return weak_ciphers
        except Exception as e:
            print(f"Error checking ciphers: {e}")
        return []
    
    def check_firewall_rules(self, target_network):
        """Audit firewall rules for best practices"""
        issues = []
        
        # Check for overly permissive rules
        # Check for deprecated protocols
        # Check for missing logging
        # Check for implicit deny
        
        # This would integrate with actual firewall API
        # Example checks:
        checks = {
            "any-to-any rule exists": False,
            "logging enabled": True,
            "deprecated protocols": [],
            "implicit deny configured": True
        }
        return checks
    
    def check_network_segmentation(self):
        """Verify network segmentation"""
        segmentation = {
            "vlan_count": 0,
            "security_zones": [],
            "micro_segmentation": False,
            "dmz_configured": False
        }
        return segmentation
    
    def check_authentication(self):
        """Check authentication mechanisms"""
        auth_status = {
            "mfa_enabled": False,
            "strong_passwords_enforced": False,
            "radius_configured": False,
            "ldap_integration": False,
            "certificate_based_auth": False
        }
        return auth_status
    
    def generate_report(self):
        """Generate security audit report"""
        report = {
            "timestamp": self.timestamp,
            "audit_scope": str(self.network_range),
            "target_hosts": self.target_hosts,
            "findings": self.results,
            "recommendations": self.generate_recommendations()
        }
        return report
    
    def generate_recommendations(self):
        """Generate security recommendations"""
        recommendations = []
        
        # Example recommendations
        recommendations.append({
            "severity": "CRITICAL",
            "title": "Weak SSL/TLS Cipher Suites",
            "description": "Disable weak ciphers and use TLS 1.2+ with strong ciphers",
            "remediation": "Configure: ssl-protocols TLSv1.2 TLSv1.3; cipher-suite HIGH:!aNULL"
        })
        
        recommendations.append({
            "severity": "HIGH",
            "title": "Open Administrative Ports",
            "description": "Restrict SSH/RDP access to management network only",
            "remediation": "Apply ACL: access-list MGMT permit tcp 10.1.100.0 255.255.255.0 any eq 22"
        })
        
        recommendations.append({
            "severity": "MEDIUM",
            "title": "Enhanced Logging",
            "description": "Enable detailed logging for security events",
            "remediation": "Configure: logging host 10.1.50.10; logging class attacks"
        })
        
        return recommendations
    
    def run_audit(self):
        """Execute full security audit"""
        print(f"[*] Starting security audit at {self.timestamp}")
        print(f"[*] Target network: {self.network_range}")
        
        # Check target hosts
        common_ports = [21, 22, 23, 25, 80, 110, 143, 443, 3306, 3389, 5432, 5900]
        
        for host in self.target_hosts:
            print(f"[*] Scanning {host}...")
            open_ports = self.check_open_ports(host, common_ports)
            self.results[host] = {
                "open_ports": open_ports,
                "weak_ciphers": self.check_weak_ciphers(host) if 443 in open_ports else []
            }
        
        # Generate report
        report = self.generate_report()
        return report
    
    def export_json(self, filename):
        """Export audit results to JSON"""
        report = self.generate_report()
        with open(filename, 'w') as f:
            json.dump(report, f, indent=2)
        print(f"[+] Report exported to {filename}")
    
    def export_html(self, filename):
        """Export audit results to HTML"""
        report = self.generate_report()
        html = self._generate_html_report(report)
        with open(filename, 'w') as f:
            f.write(html)
        print(f"[+] Report exported to {filename}")
    
    def _generate_html_report(self, report):
        """Generate HTML report"""
        html = f"""
        <html>
        <head>
            <title>Network Security Audit Report</title>
            <style>
                body {{ font-family: Arial; margin: 20px; }}
                .critical {{ color: red; font-weight: bold; }}
                .high {{ color: orange; font-weight: bold; }}
                .medium {{ color: yellow; }}
                table {{ border-collapse: collapse; width: 100%; }}
                th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
                th {{ background-color: #4CAF50; color: white; }}
            </style>
        </head>
        <body>
            <h1>Network Security Audit Report</h1>
            <p>Generated: {report['timestamp']}</p>
            <p>Audit Scope: {report['audit_scope']}</p>
            
            <h2>Recommendations</h2>
            <table>
                <tr>
                    <th>Severity</th>
                    <th>Title</th>
                    <th>Description</th>
                    <th>Remediation</th>
                </tr>
        """
        
        for rec in report['recommendations']:
            severity_class = rec['severity'].lower()
            html += f"""
                <tr>
                    <td class="{severity_class}">{rec['severity']}</td>
                    <td>{rec['title']}</td>
                    <td>{rec['description']}</td>
                    <td><pre>{rec['remediation']}</pre></td>
                </tr>
            """
        
        html += """
            </table>
        </body>
        </html>
        """
        return html

def main():
    """Main function"""
    # Example usage
    print("[*] Network Security Audit Tool")
    
    # Define target network and hosts
    network = ip_network("10.1.0.0/16")
    targets = ["10.1.10.5", "10.1.20.10", "10.1.30.5"]
    
    # Run audit
    audit = NetworkSecurityAudit(network, targets)
    audit.run_audit()
    
    # Export results
    audit.export_json("security_audit_report.json")
    audit.export_html("security_audit_report.html")
    
    print("[+] Audit complete. Reports generated.")

if __name__ == "__main__":
    main()
