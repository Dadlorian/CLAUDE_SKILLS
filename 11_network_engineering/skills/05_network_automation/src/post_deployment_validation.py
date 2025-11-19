#!/usr/bin/env python3
"""Post-deployment validation script"""

from napalm import get_network_driver
import sys

def validate_deployment(device_params):
    """Validate deployment on device"""
    try:
        driver = get_network_driver(device_params['os'])
        device = driver(device_params['host'], device_params['user'], device_params['pass'])
        device.open()
        
        checks = {
            'Interfaces Up': 0,
            'BGP Neighbors': 0,
            'Routes Learned': 0
        }
        
        # Check interfaces
        interfaces = device.get_interfaces()
        checks['Interfaces Up'] = sum(1 for i in interfaces.values() if i['is_up'])
        
        # Check BGP
        try:
            bgp = device.get_bgp_neighbors_detail()
            neighbors = bgp['default']['peers']
            checks['BGP Neighbors'] = len([n for n, d in neighbors.items() if d['session_state'] == 'Established'])
        except:
            pass
        
        # Check routes
        try:
            routes = device.get_route_to('0.0.0.0')
            checks['Routes Learned'] = len(routes)
        except:
            pass
        
        device.close()
        
        return checks
    except Exception as e:
        return {'Error': str(e)}

def main():
    device = {
        'host': '192.168.1.1',
        'user': 'admin',
        'pass': 'password',
        'os': 'ios'
    }
    
    print("Running post-deployment validation...")
    checks = validate_deployment(device)
    
    for check, result in checks.items():
        print(f"  {check}: {result}")
    
    return 0

if __name__ == '__main__':
    sys.exit(main())
