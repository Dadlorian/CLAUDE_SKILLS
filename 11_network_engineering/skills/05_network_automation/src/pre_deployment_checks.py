#!/usr/bin/env python3
"""Pre-deployment validation script"""

from netmiko import ConnectHandler
import sys

def check_device_health(device_params):
    """Check device health before deployment"""
    try:
        net_connect = ConnectHandler(**device_params)
        
        checks = {
            'Device Reachable': True,
            'Memory Available': True,
            'NTP Configured': False,
            'Logging Enabled': False,
            'SSH Enabled': False
        }
        
        # Get device info
        version = net_connect.send_command('show version')
        checks['Device Reachable'] = 'Cisco' in version or 'IOS' in version
        
        # Check memory
        memory = net_connect.send_command('show memory | include Processor')
        checks['Memory Available'] = 'free' in memory.lower()
        
        # Check NTP
        ntp = net_connect.send_command('show ntp status')
        checks['NTP Configured'] = 'synchronized' in ntp.lower() or 'synced' in ntp.lower()
        
        # Check logging
        logging = net_connect.send_command('show logging | include Logging')
        checks['Logging Enabled'] = 'buffered' in logging.lower()
        
        # Check SSH
        ssh = net_connect.send_command('show ip ssh')
        checks['SSH Enabled'] = 'SSH' in ssh or 'Version' in ssh
        
        net_connect.disconnect()
        
        return checks
    except Exception as e:
        return {'Error': str(e)}

def main():
    """Run pre-deployment checks"""
    device = {
        'device_type': 'cisco_ios',
        'host': '192.168.1.1',
        'username': 'admin',
        'password': 'password'
    }
    
    print("Running pre-deployment checks...")
    checks = check_device_health(device)
    
    all_pass = True
    for check_name, result in checks.items():
        status = "✓" if result else "✗"
        print(f"{status} {check_name}")
        if not result:
            all_pass = False
    
    return 0 if all_pass else 1

if __name__ == '__main__':
    sys.exit(main())
