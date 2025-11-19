#!/usr/bin/env python3
"""Automated network configuration backup script"""

from napalm import get_network_driver
from netmiko import ConnectHandler
import os
import json
from datetime import datetime

def backup_with_napalm(devices, backup_dir='backups'):
    """Backup using NAPALM"""
    os.makedirs(backup_dir, exist_ok=True)
    
    for device in devices:
        print(f"Backing up {device['host']} with NAPALM...")
        
        try:
            driver = get_network_driver(device['os'])
            dev = driver(device['host'], device['user'], device['pass'])
            dev.open()
            
            config = dev.get_config()
            running = config.get('running', '')
            
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filepath = f"{backup_dir}/{device['host']}_{timestamp}.cfg"
            
            with open(filepath, 'w') as f:
                f.write(running)
            
            print(f"✓ Backed up {device['host']}")
            dev.close()
            
        except Exception as e:
            print(f"✗ Failed: {e}")

def main():
    devices = [
        {'host': '192.168.1.1', 'user': 'admin', 'pass': 'pass', 'os': 'ios'},
        {'host': '192.168.1.2', 'user': 'admin', 'pass': 'pass', 'os': 'junos'},
    ]
    
    backup_with_napalm(devices)

if __name__ == '__main__':
    main()
