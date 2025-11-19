#!/usr/bin/env python3
"""
NETCONF-based configuration retrieval and management
Supports devices with NETCONF interface (IOS-XE, IOS-XR, Junos, etc.)
"""

from ncclient import manager
from lxml import etree
import yaml
import os
from datetime import datetime


def connect_netconf(device_params):
    """Establish NETCONF connection to device"""
    try:
        m = manager.connect(
            host=device_params['host'],
            port=device_params.get('port', 830),
            username=device_params['username'],
            password=device_params['password'],
            hostkey_verify=False,
            device_params={'name': device_params.get('netconf_type', 'default')},
            timeout=30
        )
        return m
    except Exception as e:
        print(f"✗ Failed to connect to {device_params['host']}: {e}")
        return None


def get_running_config(m, device_name):
    """Retrieve running configuration via NETCONF"""
    try:
        config_reply = m.get_config(source='running')

        # Parse XML and pretty print
        config_xml = etree.tostring(config_reply.xml, pretty_print=True).decode()

        return config_xml

    except Exception as e:
        print(f"✗ Failed to get running config: {e}")
        return None


def get_config_with_filter(m, filter_spec):
    """Retrieve configuration with subtree filter"""
    try:
        config_reply = m.get_config(
            source='running',
            filter=('subtree', filter_spec)
        )

        config_xml = etree.tostring(config_reply.xml, pretty_print=True).decode()

        return config_xml

    except Exception as e:
        print(f"✗ Failed to get filtered config: {e}")
        return None


def load_config(m, config_xml):
    """Load configuration to candidate datastore"""
    try:
        edit_reply = m.edit_config(
            target='candidate',
            config=config_xml
        )

        print("✓ Configuration loaded to candidate datastore")

        # Compare configurations
        try:
            diff = m.dispatch("""
            <rpc xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
              <request-shell-execute>
                <command>show diff</command>
              </request-shell-execute>
            </rpc>
            """)
            print("Configuration diff:")
            print(etree.tostring(diff, pretty_print=True).decode())
        except:
            pass

        return True

    except Exception as e:
        print(f"✗ Failed to load config: {e}")
        m.discard_changes()
        return False


def commit_config(m):
    """Commit configuration from candidate to running"""
    try:
        m.commit()
        print("✓ Configuration committed")
        return True

    except Exception as e:
        print(f"✗ Failed to commit: {e}")
        m.discard_changes()
        return False


def backup_device_netconf(inventory_file, backup_dir='backups'):
    """Backup all devices via NETCONF"""

    with open(inventory_file) as f:
        inventory = yaml.safe_load(f)

    os.makedirs(backup_dir, exist_ok=True)

    for device_name, device_info in inventory['devices'].items():
        print(f"\nBacking up {device_name}...")

        m = connect_netconf(device_info)
        if not m:
            continue

        try:
            # Get configuration
            config = get_running_config(m, device_name)

            if config:
                # Save to file
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                backup_file = f"{backup_dir}/{device_name}_netconf_{timestamp}.xml"

                with open(backup_file, 'w') as f:
                    f.write(config)

                print(f"✓ Backed up {device_name} to {backup_file}")

        except Exception as e:
            print(f"✗ Error backing up {device_name}: {e}")

        finally:
            m.close_session()


def netconf_workflow(device_params, config_file):
    """Complete NETCONF configuration workflow"""

    print(f"NETCONF Configuration Workflow for {device_params['host']}")
    print("=" * 60)

    # Connect
    m = connect_netconf(device_params)
    if not m:
        return False

    try:
        # Step 1: Backup current configuration
        print("\nStep 1: Backing up current configuration...")
        backup = get_running_config(m, device_params['host'])

        with open('pre_config_backup.xml', 'w') as f:
            f.write(backup)

        print("✓ Backup saved to pre_config_backup.xml")

        # Step 2: Load new configuration
        print("\nStep 2: Loading new configuration...")
        with open(config_file) as f:
            new_config = f.read()

        if not load_config(m, new_config):
            return False

        # Step 3: Validate
        print("\nStep 3: Validating configuration...")
        try:
            m.validate(source='candidate')
            print("✓ Configuration is valid")
        except Exception as e:
            print(f"✗ Validation failed: {e}")
            m.discard_changes()
            return False

        # Step 4: Confirm and commit
        print("\nStep 4: Committing configuration...")
        confirm = input("Commit configuration? (yes/no): ")

        if confirm.lower() == 'yes':
            if commit_config(m):
                print("\n✓ Configuration workflow completed successfully")
                return True
            else:
                print("\n✗ Configuration workflow failed")
                return False
        else:
            m.discard_changes()
            print("\n- Configuration discarded")
            return False

    finally:
        m.close_session()


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='NETCONF Configuration Management Tool')
    parser.add_argument('-i', '--inventory', help='Inventory YAML file')
    parser.add_argument('-d', '--device', help='Device to configure')
    parser.add_argument('-c', '--config', help='Configuration file')
    parser.add_argument('-b', '--backup', action='store_true', help='Backup devices')
    parser.add_argument('--backup-dir', default='backups', help='Backup directory')

    args = parser.parse_args()

    if args.backup and args.inventory:
        backup_device_netconf(args.inventory, args.backup_dir)

    elif args.device and args.config:
        # Simplified device params for demonstration
        device_params = {
            'host': args.device,
            'username': 'admin',
            'password': 'password',
            'port': 830,
            'netconf_type': 'default'
        }

        netconf_workflow(device_params, args.config)
