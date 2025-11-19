#!/usr/bin/env python3
"""
NAPALM-based multi-vendor configuration retrieval and backup
"""

from napalm import get_network_driver
import json
import yaml
import os
from datetime import datetime


def backup_configs(inventory_file, backup_dir='backups'):
    """Backup configurations from all devices in inventory"""

    # Load inventory
    with open(inventory_file) as f:
        inventory = yaml.safe_load(f)

    os.makedirs(backup_dir, exist_ok=True)

    backup_manifest = {
        'timestamp': datetime.now().isoformat(),
        'devices': {}
    }

    for device_name, device_info in inventory['devices'].items():
        print(f"Backing up {device_name}...")

        try:
            # Get driver
            driver_class = get_network_driver(device_info['os'])

            # Create connection
            device = driver_class(
                hostname=device_info['host'],
                username=device_info['username'],
                password=device_info['password'],
                timeout=30
            )

            device.open()

            # Get configurations
            configs = device.get_config()

            # Save running configuration
            running_config = configs.get('running', '')
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            running_file = f"{backup_dir}/{device_name}_running_{timestamp}.cfg"

            with open(running_file, 'w') as f:
                f.write(running_config)

            # Save startup configuration
            startup_config = configs.get('startup', '')
            startup_file = f"{backup_dir}/{device_name}_startup_{timestamp}.cfg"

            with open(startup_file, 'w') as f:
                f.write(startup_config)

            # Record in manifest
            backup_manifest['devices'][device_name] = {
                'running': running_file,
                'startup': startup_file,
                'timestamp': timestamp,
                'size': len(running_config)
            }

            device.close()

            print(f"✓ Backed up {device_name}")

        except Exception as e:
            print(f"✗ Failed to backup {device_name}: {e}")
            backup_manifest['devices'][device_name] = {
                'status': 'failed',
                'error': str(e)
            }

    # Save manifest
    manifest_file = f"{backup_dir}/manifest_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(manifest_file, 'w') as f:
        json.dump(backup_manifest, f, indent=2)

    print(f"\n✓ Backup complete. Manifest: {manifest_file}")

    return backup_manifest


def get_device_facts(device_info):
    """Get device facts using NAPALM"""

    driver_class = get_network_driver(device_info['os'])

    device = driver_class(
        hostname=device_info['host'],
        username=device_info['username'],
        password=device_info['password']
    )

    device.open()

    facts = device.get_facts()

    device.close()

    return facts


def compare_configurations(device_info, new_config_file):
    """Load and compare configurations"""

    driver_class = get_network_driver(device_info['os'])

    device = driver_class(
        hostname=device_info['host'],
        username=device_info['username'],
        password=device_info['password']
    )

    device.open()

    # Load new configuration
    with open(new_config_file, 'r') as f:
        new_config = f.read()

    # Load to candidate
    device.load_candidate_config(config=new_config)

    # Get diff
    diff = device.compare_config()

    # Discard changes
    device.discard_config()

    device.close()

    return diff


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='NAPALM Configuration Backup Tool')
    parser.add_argument('-i', '--inventory', required=True, help='Inventory YAML file')
    parser.add_argument('-b', '--backup-dir', default='backups', help='Backup directory')
    parser.add_argument('-d', '--device', help='Specific device')

    args = parser.parse_args()

    # Perform backup
    backup_configs(args.inventory, args.backup_dir)
