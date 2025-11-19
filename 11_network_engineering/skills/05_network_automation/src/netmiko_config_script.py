#!/usr/bin/env python3
"""
Network Configuration Deployment Script using Netmiko
Supports multi-vendor deployments (Cisco IOS, IOS-XR, Juniper)
"""

import argparse
import json
import logging
from datetime import datetime
from netmiko import ConnectHandler
from netmiko.ssh_exception import NetmikoTimeoutException, AuthenticationException
import yaml


# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def load_inventory(inventory_file):
    """Load device inventory from YAML file"""
    with open(inventory_file, 'r') as f:
        return yaml.safe_load(f)


def backup_device(net_connect, device_name, backup_dir='backups'):
    """Backup device running configuration"""
    try:
        output = net_connect.send_command('show running-config')

        # Save to file
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_file = f"{backup_dir}/{device_name}_{timestamp}.cfg"

        with open(backup_file, 'w') as f:
            f.write(output)

        logger.info(f"✓ Backed up {device_name} to {backup_file}")
        return backup_file

    except Exception as e:
        logger.error(f"✗ Failed to backup {device_name}: {e}")
        return None


def deploy_configuration(device_params, config_commands):
    """Deploy configuration to device"""
    try:
        # Connect to device
        net_connect = ConnectHandler(**device_params)
        logger.info(f"✓ Connected to {device_params['host']}")

        # Backup current configuration
        backup_file = backup_device(net_connect, device_params['host'])

        # Send configuration
        logger.info(f"Deploying configuration to {device_params['host']}...")

        output = net_connect.send_config_set(config_commands)
        logger.info("✓ Configuration deployed")

        # Save running config to memory
        if device_params.get('device_type') in ['cisco_ios', 'cisco_xe']:
            net_connect.send_command('write memory')
            logger.info("✓ Configuration saved")

        # Verify deployment
        verify_output = net_connect.send_command('show running-config | include ' + config_commands[0][:20])
        if config_commands[0][:20] in verify_output:
            logger.info("✓ Configuration verified")
            result = {'status': 'success', 'backup': backup_file}
        else:
            logger.warning("⚠ Configuration verification failed")
            result = {'status': 'warning', 'backup': backup_file}

        net_connect.disconnect()
        return result

    except AuthenticationException:
        logger.error(f"✗ Authentication failed for {device_params['host']}")
        return {'status': 'failed', 'reason': 'authentication'}

    except NetmikoTimeoutException:
        logger.error(f"✗ Connection timeout for {device_params['host']}")
        return {'status': 'failed', 'reason': 'timeout'}

    except Exception as e:
        logger.error(f"✗ Error deploying to {device_params['host']}: {e}")
        return {'status': 'failed', 'reason': str(e)}


def main():
    """Main execution function"""
    parser = argparse.ArgumentParser(description='Network Configuration Deployment Tool')
    parser.add_argument('-i', '--inventory', required=True, help='Inventory YAML file')
    parser.add_argument('-c', '--config', required=True, help='Configuration file to deploy')
    parser.add_argument('-d', '--device', help='Specific device to deploy to')
    parser.add_argument('-b', '--backup-dir', default='backups', help='Backup directory')
    parser.add_argument('-v', '--verbose', action='store_true', help='Verbose output')

    args = parser.parse_args()

    # Load inventory
    try:
        inventory = load_inventory(args.inventory)
    except Exception as e:
        logger.error(f"Failed to load inventory: {e}")
        return 1

    # Load configuration
    try:
        with open(args.config, 'r') as f:
            config_lines = f.readlines()
        config_commands = [line.strip() for line in config_lines if line.strip() and not line.startswith('#')]
    except Exception as e:
        logger.error(f"Failed to load configuration: {e}")
        return 1

    # Deploy to devices
    results = {}

    devices_to_deploy = {}
    if args.device:
        # Deploy to specific device
        if args.device in inventory['devices']:
            devices_to_deploy[args.device] = inventory['devices'][args.device]
        else:
            logger.error(f"Device {args.device} not found in inventory")
            return 1
    else:
        # Deploy to all devices
        devices_to_deploy = inventory['devices']

    logger.info(f"Deploying to {len(devices_to_deploy)} device(s)")

    for device_name, device_info in devices_to_deploy.items():
        logger.info(f"\n{'='*60}")
        logger.info(f"Deploying to {device_name}")
        logger.info(f"{'='*60}")

        # Merge defaults with device-specific settings
        device_params = {
            'host': device_info['host'],
            'username': device_info.get('username', inventory['defaults']['username']),
            'password': device_info.get('password', inventory['defaults']['password']),
            'device_type': device_info.get('device_type', inventory['defaults']['device_type']),
            'port': device_info.get('port', 22),
            'timeout': 30
        }

        result = deploy_configuration(device_params, config_commands)
        results[device_name] = result

    # Summary
    logger.info(f"\n{'='*60}")
    logger.info("DEPLOYMENT SUMMARY")
    logger.info(f"{'='*60}")

    success_count = sum(1 for r in results.values() if r['status'] == 'success')
    failed_count = sum(1 for r in results.values() if r['status'] == 'failed')
    warning_count = sum(1 for r in results.values() if r['status'] == 'warning')

    logger.info(f"Success: {success_count}, Warning: {warning_count}, Failed: {failed_count}")

    # Save results
    with open('deployment_results.json', 'w') as f:
        json.dump(results, f, indent=2)

    logger.info("Results saved to deployment_results.json")

    return 0 if failed_count == 0 else 1


if __name__ == '__main__':
    exit(main())
