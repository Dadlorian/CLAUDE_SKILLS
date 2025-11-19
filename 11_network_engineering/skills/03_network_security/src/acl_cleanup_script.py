#!/usr/bin/env python3
"""
ACL Cleanup Script
Remove unused and obsolete access control list entries
"""

import re
import sys
from datetime import datetime, timedelta

class ACLAnalyzer:
    def __init__(self, acl_config):
        self.config = acl_config
        self.hit_counts = {}
        self.obsolete_rules = []
        
    def parse_acl(self):
        """Parse ACL configuration"""
        rules = []
        for line in self.config.split('\n'):
            if 'access-list' in line:
                rules.append(line.strip())
        return rules
    
    def analyze_hits(self, acl_name):
        """Analyze rule hit counts"""
        # This would parse "show access-lists" output
        # Look for (0 match(es)) - no hits in X days
        pass
    
    def identify_obsolete(self, days_threshold=90):
        """Identify obsolete rules (no hits in X days)"""
        obsolete = []
        # Check rules with zero hits for more than X days
        for rule in self.parse_acl():
            if rule not in self.hit_counts or self.hit_counts[rule] == 0:
                obsolete.append(rule)
        return obsolete
    
    def generate_removal_commands(self, obsolete_rules):
        """Generate removal commands"""
        commands = []
        for rule in obsolete_rules:
            match = re.search(r'access-list\s+(\S+)', rule)
            if match:
                acl_name = match.group(1)
                commands.append(f"no {rule}")
        return commands
    
    def generate_report(self):
        """Generate cleanup report"""
        obsolete = self.identify_obsolete()
        
        report = f"""
ACL Cleanup Report
Generated: {datetime.now().isoformat()}

Total Rules: {len(self.parse_acl())}
Obsolete Rules: {len(obsolete)}

Obsolete Rules:
"""
        for rule in obsolete:
            report += f"  {rule}\n"
        
        report += f"\nRemoval Commands:\n"
        for cmd in self.generate_removal_commands(obsolete):
            report += f"  {cmd}\n"
        
        return report

def main():
    sample_config = """
access-list 101 permit tcp any any eq 80 log
access-list 101 permit tcp any any eq 443 log
access-list 101 deny ip any any log
"""
    
    analyzer = ACLAnalyzer(sample_config)
    print(analyzer.generate_report())

if __name__ == "__main__":
    main()
