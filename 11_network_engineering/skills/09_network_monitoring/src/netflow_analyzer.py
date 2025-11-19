#!/usr/bin/env python3
"""NetFlow Data Analyzer"""

import json
from collections import defaultdict, Counter
from datetime import datetime

class NetFlowAnalyzer:
    def __init__(self):
        self.flows = []
        self.stats = {
            'total_bytes': 0,
            'total_packets': 0,
            'top_talkers': Counter(),
            'protocol_dist': Counter(),
            'port_dist': Counter()
        }
    
    def add_flow(self, flow_record):
        """Add a flow record for analysis"""
        self.flows.append(flow_record)
        
        src_ip = flow_record.get('src_ip')
        dst_ip = flow_record.get('dst_ip')
        bytes_count = flow_record.get('bytes', 0)
        packets_count = flow_record.get('packets', 0)
        protocol = flow_record.get('protocol')
        dst_port = flow_record.get('dst_port')
        
        # Update statistics
        self.stats['total_bytes'] += bytes_count
        self.stats['total_packets'] += packets_count
        self.stats['top_talkers'][(src_ip, dst_ip)] += bytes_count
        self.stats['protocol_dist'][protocol] += 1
        self.stats['port_dist'][dst_port] += 1
    
    def get_top_talkers(self, n=10):
        """Get top N talker pairs"""
        return self.stats['top_talkers'].most_common(n)
    
    def get_protocol_distribution(self):
        """Get protocol breakdown"""
        total = sum(self.stats['protocol_dist'].values())
        dist = {}
        for protocol, count in self.stats['protocol_dist'].items():
            dist[protocol] = {
                'count': count,
                'percentage': (count / total * 100) if total > 0 else 0
            }
        return dist
    
    def get_summary(self):
        """Generate summary report"""
        return {
            'timestamp': datetime.now().isoformat(),
            'total_flows': len(self.flows),
            'total_bytes': self.stats['total_bytes'],
            'total_packets': self.stats['total_packets'],
            'avg_bytes_per_flow': self.stats['total_bytes'] / len(self.flows) if self.flows else 0,
            'top_talkers': self.get_top_talkers(10),
            'protocol_dist': self.get_protocol_distribution()
        }

if __name__ == '__main__':
    import sys
    analyzer = NetFlowAnalyzer()
    # Load and analyze flows
    print(json.dumps(analyzer.get_summary(), indent=2, default=str))
