# Nornir Automation Guide

## Project Setup

### Installation
```bash
pip install nornir nornir_napalm nornir_netmiko
```

### Project Structure
```
nornir_project/
├── config.yaml                # Nornir configuration
├── inventory/
│   ├── hosts.yaml            # Host definitions
│   ├── groups.yaml           # Group definitions
│   └── defaults.yaml         # Default values
├── tasks/
│   ├── __init__.py
│   ├── common_tasks.py
│   ├── monitoring_tasks.py
│   └── config_tasks.py
└── scripts/
    ├── backup_devices.py
    ├── deploy_config.py
    └── validate_devices.py
```

## Configuration

### config.yaml
```yaml
---
core:
  num_workers: 20

inventory:
  plugin: SimpleInventory
  options:
    host_file: "inventory/hosts.yaml"
    group_file: "inventory/groups.yaml"
    defaults_file: "inventory/defaults.yaml"

runner:
  plugin: threaded
```

### Inventory Files

#### hosts.yaml
```yaml
---
router1:
  hostname: 192.168.1.1
  groups:
    - routers
    - cisco
    - production
  data:
    site: dc1
    role: core

router2:
  hostname: 192.168.1.2
  groups:
    - routers
    - cisco
    - production
  data:
    site: dc2
    role: edge

switch1:
  hostname: 192.168.1.3
  groups:
    - switches
    - cisco
    - production
  data:
    site: dc1
```

#### groups.yaml
```yaml
---
routers:
  username: admin
  password: password
  port: 22

switches:
  username: admin
  password: password
  port: 22

cisco:
  platform: ios

juniper:
  platform: junos

production:
  # Can add production-specific settings
```

#### defaults.yaml
```yaml
---
data:
  ntp_servers:
    - 8.8.8.8
    - 8.8.4.4
  dns_servers:
    - 1.1.1.1
    - 8.8.8.8
```

## Task Development

### Basic Tasks
```python
# tasks/common_tasks.py
from nornir.core.task import Task, Result
from nornir_napalm.plugins.tasks import napalm_get

def get_device_info(task: Task) -> Result:
    """Get basic device information"""

    result = task.run(
        name="Get device facts",
        task=napalm_get,
        getters=["facts"]
    )

    facts = result[0].result['facts']

    return Result(
        host=task.host,
        result={
            'hostname': facts['hostname'],
            'vendor': facts['vendor'],
            'model': facts['model'],
            'os_version': facts['os_version'],
            'uptime': facts['uptime']
        }
    )
```

### Task with Subtasks
```python
from nornir_netmiko.tasks import netmiko_commands, netmiko_send_config

def deploy_and_verify(task: Task, commands: list) -> Result:
    """Deploy commands and verify"""

    # Step 1: Backup current config
    backup = task.run(
        name="Backup configuration",
        task=netmiko_commands,
        command_string="show running-config"
    )

    # Step 2: Apply changes
    deploy = task.run(
        name="Deploy configuration",
        task=netmiko_send_config,
        config_commands=commands
    )

    # Step 3: Verify changes
    verify = task.run(
        name="Verify changes",
        task=netmiko_commands,
        command_string="show running-config | include {{ cmd }}"
    )

    return Result(
        host=task.host,
        result={
            'backup': len(backup[0].result),
            'deployed': True,
            'verified': len(verify[0].result) > 0
        }
    )
```

## Execution Examples

### Parallel Execution
```python
# scripts/backup_devices.py
from nornir import InitNornir
from nornir.core.task import Task, Result
from nornir_napalm.plugins.tasks import napalm_get
import os

def backup_configs(task: Task) -> Result:
    """Backup device configurations"""

    # Get configuration
    result = task.run(
        name="Get configuration",
        task=napalm_get,
        getters=["config"]
    )

    config = result[0].result['config']['running']

    # Save to file
    backup_dir = 'backups'
    os.makedirs(backup_dir, exist_ok=True)

    with open(f"{backup_dir}/{task.host.name}.conf", 'w') as f:
        f.write(config)

    return Result(
        host=task.host,
        result=f"Backed up {len(config)} bytes"
    )

def main():
    nr = InitNornir(config_file="config.yaml")

    # Execute on all devices in parallel
    results = nr.run(task=backup_configs)

    # Print results
    for host, result in results.items():
        if result.failed:
            print(f"✗ {host}: {result.exception}")
        else:
            print(f"✓ {host}: {result[0].result}")

if __name__ == '__main__':
    main()
```

### Filtered Execution
```python
# scripts/deploy_config.py
from nornir import InitNornir

def main():
    nr = InitNornir(config_file="config.yaml")

    # Filter to production routers
    prod_routers = nr.filter(group="routers", role="core")

    print(f"Deploying to {len(prod_routers.inventory.hosts)} devices")

    # Deploy configuration
    results = prod_routers.run(task=deploy_and_verify)

    # Show results
    for host, result in results.items():
        if result.failed:
            print(f"✗ {host}: FAILED")
        else:
            print(f"✓ {host}: {result[0].result}")

if __name__ == '__main__':
    main()
```

### Device-Specific Tasks
```python
def task_for_cisco_only(task: Task) -> Result:
    """Run only on Cisco devices"""

    # Check device type
    if task.host.platform != 'ios':
        return Result(host=task.host, skipped=True)

    # Execute task
    return Result(host=task.host, result="Executed on Cisco device")

def main():
    nr = InitNornir(config_file="config.yaml")

    # Execute filtered by platform
    cisco_devices = nr.filter(platform='ios')
    results = cisco_devices.run(task=task_for_cisco_only)

    for host, result in results.items():
        if result.skipped:
            print(f"- {host}: SKIPPED")
        elif result.failed:
            print(f"✗ {host}: FAILED")
        else:
            print(f"✓ {host}: SUCCESS")
```

## Working with Results

### Result Processing
```python
from nornir.plugins.functions.text import print_result

def main():
    nr = InitNornir(config_file="config.yaml")

    results = nr.run(task=my_task)

    # Built-in result printing
    print_result(results)

    # Custom result processing
    summary = {
        'success': 0,
        'failed': 0,
        'skipped': 0
    }

    for host, result in results.items():
        if result.skipped:
            summary['skipped'] += 1
        elif result.failed:
            summary['failed'] += 1
        else:
            summary['success'] += 1

    print(f"\nSummary: {summary['success']} succeeded, {summary['failed']} failed, {summary['skipped']} skipped")
```

## Advanced Features

### Error Handling and Retries
```python
def task_with_retry(task: Task) -> Result:
    """Task with retry logic"""

    max_retries = 3
    retry_count = 0

    while retry_count < max_retries:
        try:
            result = task.run(
                name="Attempt operation",
                task=risky_operation
            )

            return Result(host=task.host, result=result[0].result)

        except Exception as e:
            retry_count += 1
            if retry_count >= max_retries:
                return Result(
                    host=task.host,
                    result=None,
                    failed=True,
                    exception=e
                )
            else:
                print(f"Retry {retry_count}/{max_retries}...")
                time.sleep(5)
```

### Conditional Task Execution
```python
def conditional_task(task: Task) -> Result:
    """Execute based on host data"""

    # Get host data
    environment = task.host.data.get('environment', 'unknown')
    role = task.host.data.get('role', 'unknown')

    if environment != 'production':
        return Result(host=task.host, skipped=True)

    if role == 'core':
        # Execute core-specific task
        return core_operation(task)
    else:
        # Execute default task
        return default_operation(task)
```

### Aggregating Results Across Hosts
```python
def main():
    nr = InitNornir(config_file="config.yaml")

    results = nr.run(task=get_device_info)

    # Aggregate data
    devices_by_site = {}

    for host, result in results.items():
        if not result.failed:
            site = host.data.get('site')
            if site not in devices_by_site:
                devices_by_site[site] = []

            device_info = result[0].result
            devices_by_site[site].append(device_info)

    # Display aggregated data
    for site, devices in devices_by_site.items():
        print(f"\n{site}: {len(devices)} devices")
        for device in devices:
            print(f"  - {device['hostname']}: {device['os_version']}")
```

## Integration with External Systems

### Database Integration
```python
import sqlite3

def save_to_database(task: Task, db_file='devices.db') -> Result:
    """Save device info to SQLite database"""

    result = task.run(
        name="Get facts",
        task=napalm_get,
        getters=["facts"]
    )

    facts = result[0].result['facts']

    # Save to database
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()

    cursor.execute('''
        INSERT OR REPLACE INTO devices
        (hostname, vendor, model, os_version)
        VALUES (?, ?, ?, ?)
    ''', (
        facts['hostname'],
        facts['vendor'],
        facts['model'],
        facts['os_version']
    ))

    conn.commit()
    conn.close()

    return Result(host=task.host, result="Saved to database")
```

### Webhook Integration
```python
import requests

def send_webhook(task: Task, webhook_url: str) -> Result:
    """Send results to webhook"""

    payload = {
        'host': task.host.name,
        'timestamp': datetime.now().isoformat(),
        'status': 'success'
    }

    try:
        response = requests.post(webhook_url, json=payload)
        return Result(host=task.host, result=f"Webhook sent: {response.status_code}")
    except Exception as e:
        return Result(host=task.host, failed=True, exception=e)
```

---

**Last Updated**: 2025-11-19
**Reference**: nornir.readthedocs.io, github.com/nornir-automation/nornir
