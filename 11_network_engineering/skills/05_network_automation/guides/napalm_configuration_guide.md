# NAPALM Configuration Guide

## Configuration Management Workflow

### Multi-Vendor Deployment
```python
from napalm import get_network_driver
import yaml

# Load inventory
with open('inventory.yaml') as f:
    devices = yaml.safe_load(f)

# Deploy configuration to each device
for device_name, device_params in devices.items():
    print(f"\n{'='*60}")
    print(f"Configuring {device_name}")
    print(f"{'='*60}")

    # Get correct driver for vendor
    vendor = device_params['vendor']
    driver = get_network_driver(vendor)

    # Create connection
    device = driver(
        device_params['host'],
        device_params['username'],
        device_params['password']
    )

    device.open()

    # Load new configuration
    config_file = f"configs/{device_name}.conf"
    with open(config_file) as f:
        new_config = f.read()

    device.load_candidate_config(config=new_config)

    # Compare configurations
    diff = device.compare_config()
    if diff:
        print(f"\nChanges to be applied:\n{diff}")

        # Ask for confirmation
        confirm = input("\nApply changes? (yes/no): ")
        if confirm.lower() == 'yes':
            device.commit_config()
            print("✓ Configuration committed")
        else:
            device.discard_config()
            print("✗ Configuration discarded")
    else:
        print("✓ No changes needed")

    device.close()
```

## Configuration Backup and Restoration

### Automated Backup
```python
from napalm import get_network_driver
from datetime import datetime
import os

def backup_network_configs(inventory_file, backup_dir='backups'):
    """Backup configurations from all devices"""

    with open(inventory_file) as f:
        devices = yaml.safe_load(f)

    os.makedirs(backup_dir, exist_ok=True)

    backup_manifest = {}

    for device_name, device_params in devices.items():
        print(f"Backing up {device_name}...")

        driver = get_network_driver(device_params['vendor'])
        device = driver(
            device_params['host'],
            device_params['username'],
            device_params['password']
        )

        device.open()

        try:
            # Get running configuration
            config = device.get_config(retrieve='running')
            running_config = config['running']

            # Get startup configuration
            startup_config = config.get('startup', '')

            # Save files
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            running_file = f"{backup_dir}/{device_name}_running_{timestamp}.conf"
            startup_file = f"{backup_dir}/{device_name}_startup_{timestamp}.conf"

            with open(running_file, 'w') as f:
                f.write(running_config)

            with open(startup_file, 'w') as f:
                f.write(startup_config)

            backup_manifest[device_name] = {
                'running': running_file,
                'startup': startup_file,
                'timestamp': timestamp
            }

            print(f"✓ Backed up {device_name}")

        except Exception as e:
            print(f"✗ Failed to backup {device_name}: {e}")

        finally:
            device.close()

    # Save manifest
    with open(f"{backup_dir}/manifest.json", 'w') as f:
        json.dump(backup_manifest, f, indent=2)

    print(f"\n✓ All configurations backed up to {backup_dir}")

# Run backup
backup_network_configs('inventory.yaml')
```

### Restoration
```python
def restore_configuration(device_params, config_file):
    """Restore configuration from file"""

    driver = get_network_driver(device_params['vendor'])
    device = driver(
        device_params['host'],
        device_params['username'],
        device_params['password']
    )

    device.open()

    # Load configuration file
    with open(config_file) as f:
        config = f.read()

    # Load to candidate
    device.load_candidate_config(config=config)

    # Show what will change
    diff = device.compare_config()
    print(f"Configuration diff:\n{diff}")

    # Restore
    device.commit_config()
    print("✓ Configuration restored")

    device.close()
```

## Multi-Vendor Configuration

### Handling Vendor Differences
```python
def get_facts_multivendor(device_list):
    """Get facts from devices of different vendors"""

    facts_summary = {}

    for device_info in device_list:
        print(f"Getting facts from {device_info['host']} ({device_info['os']})")

        driver = get_network_driver(device_info['os'])
        device = driver(
            device_info['host'],
            device_info['username'],
            device_info['password']
        )

        device.open()

        facts = device.get_facts()

        facts_summary[device_info['host']] = {
            'vendor': facts['vendor'],
            'model': facts['model'],
            'os_version': facts['os_version'],
            'serial_number': facts['serial_number'],
            'uptime': facts['uptime'],
            'interfaces': len(facts['interface_list'])
        }

        device.close()

    # Display results
    for host, info in facts_summary.items():
        print(f"\n{host}:")
        for key, value in info.items():
            print(f"  {key}: {value}")

    return facts_summary
```

## Configuration Validation

### Pre-Commit Validation
```python
def validate_config_before_commit(device_params, config_file):
    """Validate configuration before committing"""

    driver = get_network_driver(device_params['vendor'])
    device = driver(
        device_params['host'],
        device_params['username'],
        device_params['password']
    )

    device.open()

    # Load configuration
    with open(config_file) as f:
        config = f.read()

    device.load_candidate_config(config=config)

    # Validate
    print("Validating configuration...")

    checks = {
        'Has BGP config': lambda: 'router bgp' in config,
        'Has NTP config': lambda: 'ntp server' in config,
        'Has logging config': lambda: 'logging' in config,
        'Has hostname': lambda: 'hostname' in config,
    }

    all_valid = True
    for check_name, check_func in checks.items():
        try:
            result = check_func()
            status = "✓" if result else "✗"
            print(f"{status} {check_name}")
            if not result:
                all_valid = False
        except Exception as e:
            print(f"✗ {check_name}: {e}")
            all_valid = False

    if all_valid:
        print("\n✓ Configuration is valid")
        # Commit if approved
        user_input = input("Commit configuration? (yes/no): ")
        if user_input.lower() == 'yes':
            device.commit_config()
            print("✓ Configuration committed")
        else:
            device.discard_config()
    else:
        print("\n✗ Configuration validation failed")
        device.discard_config()

    device.close()
```

## Compliance Checking

### Configuration Compliance
```python
def check_compliance(device_params):
    """Check device configuration compliance"""

    driver = get_network_driver(device_params['vendor'])
    device = driver(
        device_params['host'],
        device_params['username'],
        device_params['password']
    )

    device.open()

    # Get configuration
    config = device.get_config(retrieve='running')
    running_config = config['running']

    # Define compliance rules
    compliance_rules = {
        'SSH enabled': 'ssh' in running_config.lower() or 'ip ssh' in running_config,
        'AAA configured': 'aaa new-model' in running_config,
        'Logging configured': 'logging' in running_config,
        'NTP configured': 'ntp server' in running_config,
        'SNMP configured': 'snmp-server' in running_config,
        'ACL configured': 'access-list' in running_config,
        'Enable password set': 'enable password' in running_config,
    }

    # Check compliance
    print(f"Compliance check for {device_params['host']}:")
    compliant_count = 0

    for rule_name, rule_check in compliance_rules.items():
        status = "✓" if rule_check else "✗"
        print(f"{status} {rule_name}")
        if rule_check:
            compliant_count += 1

    print(f"\nCompliance: {compliant_count}/{len(compliance_rules)} ({100*compliant_count//len(compliance_rules)}%)")

    device.close()

    return compliant_count == len(compliance_rules)
```

## Integration with Version Control

### Git-Based Configuration Management
```python
import subprocess
from datetime import datetime

def deploy_config_from_git(device_params, git_repo, branch='main'):
    """Deploy configuration from Git repository"""

    # Clone/update Git repo
    repo_dir = 'network_configs'
    if not os.path.exists(repo_dir):
        subprocess.run(['git', 'clone', git_repo, repo_dir])
    else:
        os.chdir(repo_dir)
        subprocess.run(['git', 'checkout', branch])
        subprocess.run(['git', 'pull'])
        os.chdir('..')

    # Get device config file
    config_file = f"{repo_dir}/configs/{device_params['host']}.conf"

    if not os.path.exists(config_file):
        print(f"✗ Configuration file not found: {config_file}")
        return False

    # Deploy configuration
    driver = get_network_driver(device_params['vendor'])
    device = driver(
        device_params['host'],
        device_params['username'],
        device_params['password']
    )

    device.open()

    with open(config_file) as f:
        config = f.read()

    device.load_candidate_config(config=config)

    # Compare
    diff = device.compare_config()
    print(f"Configuration diff:\n{diff}")

    # Commit
    device.commit_config()
    print(f"✓ Configuration deployed from Git ({branch})")

    # Create Git commit to track deployment
    os.chdir(repo_dir)
    subprocess.run(['git', 'add', f"configs/{device_params['host']}.conf"])
    subprocess.run([
        'git', 'commit',
        '-m', f"deployment: deployed to {device_params['host']} at {datetime.now()}"
    ])
    subprocess.run(['git', 'push'])
    os.chdir('..')

    device.close()
    return True
```

---

**Last Updated**: 2025-11-19
**Reference**: napalm.readthedocs.io
