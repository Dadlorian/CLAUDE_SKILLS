#!/usr/bin/env python3
"""Bandwidth Utilization Monitoring"""

import time
from collections import deque

class BandwidthMonitor:
    def __init__(self, interface, window_size=300):
        self.interface = interface
        self.window_size = window_size
        self.samples = deque(maxlen=window_size)
        self.thresholds = {
            'warning': 0.70,
            'critical': 0.85
        }
    
    def add_sample(self, in_bytes, out_bytes, link_speed):
        """Add utilization sample"""
        total_bits = (in_bytes + out_bytes) * 8
        utilization = total_bits / link_speed if link_speed > 0 else 0
        
        self.samples.append({
            'timestamp': time.time(),
            'utilization': utilization,
            'in_bytes': in_bytes,
            'out_bytes': out_bytes
        })
    
    def get_current_utilization(self):
        """Get current utilization percentage"""
        if not self.samples:
            return 0
        return self.samples[-1]['utilization'] * 100
    
    def get_average_utilization(self):
        """Get average utilization over window"""
        if not self.samples:
            return 0
        avg = sum(s['utilization'] for s in self.samples) / len(self.samples)
        return avg * 100
    
    def get_peak_utilization(self):
        """Get peak utilization over window"""
        if not self.samples:
            return 0
        peak = max(s['utilization'] for s in self.samples)
        return peak * 100
    
    def check_thresholds(self):
        """Check if thresholds exceeded"""
        current = self.get_current_utilization() / 100
        average = self.get_average_utilization() / 100
        
        alerts = []
        if current > self.thresholds['critical']:
            alerts.append('CRITICAL')
        elif current > self.thresholds['warning']:
            alerts.append('WARNING')
        
        if average > self.thresholds['critical']:
            alerts.append('SUSTAINED_CRITICAL')
        
        return alerts

if __name__ == '__main__':
    monitor = BandwidthMonitor('eth0', link_speed=1e9)
    print("Bandwidth Monitor Ready")
