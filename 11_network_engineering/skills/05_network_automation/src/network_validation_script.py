#!/usr/bin/env python3
"""Network configuration validation script"""

import yaml
from netmiko import ConnectHandler

def validate_interface_config(device_params, expected_interfaces):
    """Validate interface configuration"""
    try:
        net_connect = ConnectHandler(**device_params)
        
        output = net_connect.send_command('show ip interface brief')
        
        for interface in expected_interfaces:
            if interface in output:
                print(f"✓ Interface {interface} found")
            else:
                print(f"✗ Interface {interface} not found")
        
        net_connect.disconnect()
        return True
    except Exception as e:
        print(f"Error: {e}")
        return False

def validate_routing_config(device_params):
    """Validate routing configuration"""
    try:
        net_connect = ConnectHandler(**device_params)
        
        # Check BGP
        bgp = net_connect.send_command('show bgp ipv4 unicast summary')
        if 'Established' in bgp:
            print("✓ BGP neighbors established")
        else:
            print("✗ BGP neighbors not established")
        
        # Check OSPF
        ospf = net_connect.send_command('show ip ospf neighbors')
        if 'FULL' in ospf:
            print("✓ OSPF neighbors in FULL state")
        else:
            print("✗ OSPF neighbors not in FULL state")
        
        net_connect.disconnect()
        return True
    except Exception as e:
        print(f"Error: {e}")
        return False

def main():
    device = {
        'device_type': 'cisco_ios',
        'host': '192.168.1.1',
        'username': 'admin',
        'password': 'password'
    }
    
    print("Network Validation")
    print("=" * 40)
    
    validate_interface_config(device, ['Ethernet0/0', 'Ethernet0/1'])
    validate_routing_config(device)

if __name__ == '__main__':
    main()
