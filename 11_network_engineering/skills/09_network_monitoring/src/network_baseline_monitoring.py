#!/usr/bin/env python3
"""Network Baseline Establishment and Monitoring"""

import json
import statistics
from datetime import datetime, timedelta

class NetworkBaseline:
    def __init__(self):
        self.baseline = {}
        self.current_period = []
    
    def add_measurement(self, metric_name, value):
        """Add measurement for baseline"""
        if metric_name not in self.baseline:
            self.baseline[metric_name] = []
        self.baseline[metric_name].append(value)
    
    def calculate_baseline(self):
        """Calculate baseline statistics"""
        stats = {}
        for metric, values in self.baseline.items():
            if len(values) > 1:
                stats[metric] = {
                    'min': min(values),
                    'max': max(values),
                    'avg': statistics.mean(values),
                    'median': statistics.median(values),
                    'stdev': statistics.stdev(values),
                    'p95': sorted(values)[int(len(values) * 0.95)],
                    'p99': sorted(values)[int(len(values) * 0.99)]
                }
        return stats
    
    def check_anomaly(self, metric_name, value, threshold_std_dev=2):
        """Check if value is anomalous"""
        if metric_name not in self.baseline or len(self.baseline[metric_name]) < 2:
            return False
        
        values = self.baseline[metric_name]
        mean = statistics.mean(values)
        stdev = statistics.stdev(values)
        
        z_score = abs((value - mean) / stdev) if stdev > 0 else 0
        return z_score > threshold_std_dev

if __name__ == '__main__':
    baseline = NetworkBaseline()
    print("Network Baseline Monitor Ready")
