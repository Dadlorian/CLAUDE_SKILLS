# Nornir Reference Guide

## Overview

Nornir is a task execution framework for network automation, offering parallelization, plugin architecture, and flexible inventory management.

## Installation
```bash
pip install nornir
pip install nornir_napalm  # For NAPALM integration
pip install nornir_netmiko  # For Netmiko integration
```

## Configuration

### Config File (config.yaml)
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

logging:
  enabled: true
  level: INFO
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
  data:
    site: DC1
    os: ios

router2:
  hostname: 192.168.1.2
  groups:
    - routers
    - cisco
  data:
    site: DC2
    os: ios

switch1:
  hostname: 192.168.1.3
  groups:
    - switches
    - cisco
  data:
    site: DC1
    os: ios
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
```

#### defaults.yaml
```yaml
---
data:
  dns_servers:
    - 8.8.8.8
    - 8.8.4.4
  ntp_servers:
    - 0.pool.ntp.org
    - 1.pool.ntp.org
```

## Initialization

### Initialize Nornir
```python
from nornir import InitNornir

# Initialize with config file
nr = InitNornir(config_file="config.yaml")

# Initialize with parameters
nr = InitNornir(
    inventory={
        "plugin": "SimpleInventory",
        "options": {
            "host_file": "inventory/hosts.yaml",
            "group_file": "inventory/groups.yaml"
        }
    },
    runner={"plugin": "threaded", "options": {"num_workers": 20}}
)

# Check devices
print(nr.inventory.hosts.keys())
```

## Task Development

### Basic Task
```python
from nornir.core.task import Task, Result

def get_device_info(task: Task) -> Result:
    """Get device information"""
    device_info = {
        'hostname': task.host.name,
        'ip': task.host.hostname,
        'site': task.host.data.get('site'),
    }

    return Result(
        host=task.host,
        result=device_info
    )

# Execute task
nr = InitNornir(config_file="config.yaml")
results = nr.run(task=get_device_info)

# Print results
for host, result in results.items():
    print(f"{host}: {result['device_info'].result}")
```

### Task with Parameters
```python
def send_command(task: Task, commands: list) -> Result:
    """Send commands to device"""
    from nornir_netmiko.tasks import netmiko_commands

    results = {}
    for cmd in commands:
        output = task.run(
            name=f"Execute {cmd}",
            task=netmiko_commands,
            command_string=cmd
        )
        results[cmd] = output[0].result

    return Result(
        host=task.host,
        result=results
    )

# Execute with parameters
commands = ['show ip interface brief', 'show ip route']
results = nr.run(
    task=send_command,
    commands=commands
)
```

### Task Groups
```python
from nornir.core.task import Task, Result
from nornir_netmiko.tasks import netmiko_commands, netmiko_send_config

def backup_and_update(task: Task, new_config: str) -> Result:
    """Backup current config and apply new configuration"""

    # Backup current config
    backup = task.run(
        name="Backup configuration",
        task=netmiko_commands,
        command_string="show running-config"
    )

    # Save backup to file
    with open(f"backups/{task.host.name}_backup.cfg", "w") as f:
        f.write(backup[0].result)

    # Apply new configuration
    config_result = task.run(
        name="Apply configuration",
        task=netmiko_send_config,
        config_commands=new_config.split('\n')
    )

    return Result(
        host=task.host,
        result={
            'backup': backup[0].result[:100],  # First 100 chars
            'config_status': 'applied'
        }
    )
```

## NAPALM Integration

### Using Nornir with NAPALM
```python
from nornir import InitNornir
from nornir_napalm.plugins.tasks import napalm_get, napalm_configure

def get_device_facts(task: Task) -> Result:
    """Get device facts using NAPALM"""
    result = task.run(
        task=napalm_get,
        getters=["facts", "interfaces", "bgp_neighbors_detail"]
    )

    return result

# Execute
nr = InitNornir(config_file="config.yaml")
results = nr.run(task=get_device_facts)

# Print results
for host, result in results.items():
    if result.failed:
        print(f"{host}: FAILED - {result.exception}")
    else:
        facts = result[0].result['facts']
        print(f"{host}: {facts['hostname']} ({facts['os_version']})")
```

### Configuration Management
```python
def deploy_configuration(task: Task, config_file: str) -> Result:
    """Deploy configuration using NAPALM"""

    with open(config_file, 'r') as f:
        new_config = f.read()

    # Load configuration
    task.run(
        task=napalm_configure,
        configuration=new_config,
        action="load"
    )

    # Compare configuration
    comparison = task.run(
        task=napalm_get,
        getters=["config"]
    )

    return Result(
        host=task.host,
        result={'config_loaded': True}
    )
```

## Filtering Devices

### Filter Operations
```python
nr = InitNornir(config_file="config.yaml")

# Filter by group
routers = nr.filter(group="routers")

# Filter by OS
cisco_devices = nr.filter(platform="ios")

# Filter by data
dc1_devices = nr.filter(site="DC1")

# Combined filters
dc1_routers = nr.filter(group="routers", site="DC1")

# Filter with function
critical_devices = nr.filter(lambda h: h.data.get('critical', False))

# Exclusion filter
non_critical = nr.filter(~(lambda h: h.data.get('critical', False)))
```

## Result Handling

### Print Results
```python
from nornir.plugins.functions.text import print_result

results = nr.run(task=some_task)
print_result(results)
```

### Custom Output
```python
def print_custom(results):
    """Custom result printing"""
    for host, result in results.items():
        if result.failed:
            print(f"❌ {host}: FAILED")
            for subtask, error in result.items():
                if isinstance(error, Exception):
                    print(f"   - {error}")
        else:
            print(f"✓ {host}: SUCCESS")
            for subtask, output in result.items():
                if hasattr(output, 'result'):
                    print(f"   - {subtask}: {output.result}")

results = nr.run(task=some_task)
print_custom(results)
```

### Aggregating Results
```python
def aggregate_results(results):
    """Aggregate results from all hosts"""
    aggregated = {
        'success': [],
        'failed': [],
        'data': {}
    }

    for host, result in results.items():
        if result.failed:
            aggregated['failed'].append(host)
        else:
            aggregated['success'].append(host)
            # Extract data from result
            if 'get_device_info' in result:
                aggregated['data'][host] = result['get_device_info'].result

    return aggregated

results = nr.run(task=some_task)
summary = aggregate_results(results)
print(f"Success: {len(summary['success'])}, Failed: {len(summary['failed'])}")
```

## Advanced Features

### Subtasks
```python
def parent_task(task: Task) -> Result:
    """Task with subtasks"""

    # Subtask 1
    r1 = task.run(
        name="Get facts",
        task=napalm_get,
        getters=["facts"]
    )

    # Subtask 2
    r2 = task.run(
        name="Get interfaces",
        task=napalm_get,
        getters=["interfaces"]
    )

    # Subtask 3
    r3 = task.run(
        name="Get routing",
        task=napalm_get,
        getters=["bgp_neighbors"]
    )

    return Result(
        host=task.host,
        result={
            'facts': r1[0].result,
            'interfaces': r2[0].result,
            'routing': r3[0].result
        }
    )
```

### Error Handling
```python
def safe_task(task: Task) -> Result:
    """Task with error handling"""

    try:
        result = task.run(
            task=some_operation,
            some_param="value"
        )

        return Result(
            host=task.host,
            result=result[0].result
        )

    except Exception as e:
        return Result(
            host=task.host,
            result=None,
            failed=True,
            exception=e
        )
```

## Parallel Execution

### Built-in Parallelization
```python
# config.yaml sets num_workers
# Default: 20 concurrent tasks

nr = InitNornir(config_file="config.yaml")

# All devices process in parallel
results = nr.run(
    task=some_task,
    task_params={'param1': 'value'}
)
```

## Complete Example

### Backup and Compliance Check
```python
#!/usr/bin/env python3

from nornir import InitNornir
from nornir.core.task import Task, Result
from nornir_napalm.plugins.tasks import napalm_get, napalm_configure
from nornir.plugins.functions.text import print_result
import os

def backup_device(task: Task) -> Result:
    """Backup device configuration"""

    # Get config
    result = task.run(
        task=napalm_get,
        getters=["config"]
    )

    config = result[0].result['config']['running']

    # Save to file
    backup_dir = "backups"
    os.makedirs(backup_dir, exist_ok=True)

    with open(f"{backup_dir}/{task.host.name}.cfg", "w") as f:
        f.write(config)

    return Result(
        host=task.host,
        result=f"Backed up {len(config)} bytes"
    )

def compliance_check(task: Task) -> Result:
    """Check compliance"""

    result = task.run(
        task=napalm_get,
        getters=["config"]
    )

    config = result[0].result['config']['running']

    # Check for compliance items
    compliance_items = {
        'ntp': 'ntp server' in config,
        'logging': 'logging' in config,
        'snmp': 'snmp-server community' in config,
        'ssh': 'ssh' in config.lower()
    }

    failed_items = [k for k, v in compliance_items.items() if not v]

    return Result(
        host=task.host,
        result={
            'compliant': len(failed_items) == 0,
            'missing': failed_items
        }
    )

def main():
    """Main execution"""

    nr = InitNornir(config_file="config.yaml")

    # Backup all devices
    print("=== Backing up configurations ===")
    backup_results = nr.run(task=backup_device)
    print_result(backup_results)

    # Check compliance
    print("\n=== Checking compliance ===")
    compliance_results = nr.run(task=compliance_check)
    print_result(compliance_results)

    # Summary
    failed_compliance = [
        h for h, r in compliance_results.items()
        if not r[0].result['compliant']
    ]

    if failed_compliance:
        print(f"\n⚠️  {len(failed_compliance)} devices failed compliance:")
        for host in failed_compliance:
            missing = compliance_results[host][0].result['missing']
            print(f"   {host}: missing {', '.join(missing)}")

if __name__ == "__main__":
    main()
```

## Performance Tuning

### Worker Threads
```yaml
# config.yaml
core:
  num_workers: 50  # For I/O-bound tasks

runner:
  plugin: threaded
  options:
    num_workers: 50
```

### Connection Pooling
```python
# Nornir automatically manages connections
# Reuses connections across tasks for efficiency
```

---

**Last Updated**: 2025-11-19
**Reference**: nornir.readthedocs.io, github.com/nornir-automation/nornir
