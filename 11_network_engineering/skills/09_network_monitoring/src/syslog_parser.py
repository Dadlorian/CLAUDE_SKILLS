#!/usr/bin/env python3
"""Syslog Message Parser"""

import re
from datetime import datetime
from collections import defaultdict

class SyslogParser:
    def __init__(self):
        self.messages = []
        self.stats = defaultdict(int)
    
    def parse_message(self, raw_message):
        """Parse syslog message (RFC 5424 format)"""
        pattern = r'<(\d+)>(\S+)\s+(\S+)\s+(\S+)\s+(\S+)\s+(\S+)\s+(\S+)\s+(.*)'
        
        match = re.match(pattern, raw_message)
        if not match:
            return None
        
        priority, timestamp, hostname, app, pid, mid, sd, msg = match.groups()
        
        # Parse priority
        pri = int(priority)
        facility = pri // 8
        severity = pri % 8
        
        # Severity names
        severity_names = ['EMERGENCY', 'ALERT', 'CRITICAL', 'ERROR', 
                         'WARNING', 'NOTICE', 'INFORMATIONAL', 'DEBUG']
        
        parsed = {
            'timestamp': timestamp,
            'hostname': hostname,
            'application': app,
            'pid': pid,
            'facility': facility,
            'severity': severity_names[severity] if severity < len(severity_names) else 'UNKNOWN',
            'message': msg
        }
        
        self.messages.append(parsed)
        self.stats[parsed['severity']] += 1
        
        return parsed
    
    def get_summary(self):
        """Get summary statistics"""
        return {
            'total_messages': len(self.messages),
            'severity_distribution': dict(self.stats),
            'unique_hosts': len(set(m['hostname'] for m in self.messages))
        }

if __name__ == '__main__':
    parser = SyslogParser()
    print("Syslog Parser Ready")
