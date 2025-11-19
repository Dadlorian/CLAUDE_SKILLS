#!/usr/bin/env python3
"""Network Latency Monitoring"""

import subprocess
import statistics
from collections import deque

class LatencyMonitor:
    def __init__(self, target, window_size=100):
        self.target = target
        self.window_size = window_size
        self.measurements = deque(maxlen=window_size)
    
    def measure_latency(self):
        """Measure RTT using ping"""
        try:
            result = subprocess.run(['ping', '-c', '1', self.target],
                                  capture_output=True, timeout=5, text=True)
            if result.returncode == 0:
                # Extract latency from output
                for line in result.stdout.split('\n'):
                    if 'time=' in line:
                        time_str = line.split('time=')[1].split(' ')[0]
                        return float(time_str)
        except:
            pass
        return None
    
    def add_measurement(self, latency):
        """Add latency measurement"""
        if latency is not None:
            self.measurements.append(latency)
    
    def get_statistics(self):
        """Get latency statistics"""
        if not self.measurements:
            return None
        
        measurements_list = list(self.measurements)
        return {
            'min': min(measurements_list),
            'max': max(measurements_list),
            'avg': statistics.mean(measurements_list),
            'median': statistics.median(measurements_list),
            'stdev': statistics.stdev(measurements_list) if len(measurements_list) > 1 else 0,
            'p95': sorted(measurements_list)[int(len(measurements_list) * 0.95)],
            'p99': sorted(measurements_list)[int(len(measurements_list) * 0.99)]
        }

if __name__ == '__main__':
    monitor = LatencyMonitor('8.8.8.8')
    print("Latency Monitor Ready")
