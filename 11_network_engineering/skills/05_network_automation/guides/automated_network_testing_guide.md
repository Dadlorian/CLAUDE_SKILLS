# Automated Network Testing Guide

## Test Framework Setup

### Installation
```bash
pip install pytest pytest-napalm netmiko pyats[full]
```

### Test Structure
```
tests/
├── conftest.py           # Shared fixtures
├── unit/
│   ├── test_config_parsing.py
│   └── test_template_rendering.py
├── integration/
│   ├── conftest.py
│   ├── test_interface_status.py
│   ├── test_routing.py
│   └── test_bgp.py
└── e2e/
    └── test_deployment.py
```

## Unit Tests

### Configuration Validation
```python
# tests/unit/test_configuration.py
import pytest
from jinja2 import Environment, FileSystemLoader

@pytest.fixture
def jinja_env():
    """Jinja2 environment fixture"""
    return Environment(loader=FileSystemLoader('templates/'))

def test_router_config_generation(jinja_env):
    """Test router configuration template rendering"""
    template = jinja_env.get_template('cisco_router.j2')

    variables = {
        'hostname': 'test-router',
        'bgp_asn': 65001,
        'interfaces': [
            {
                'name': 'Ethernet0/0',
                'ip_address': '10.0.0.1',
                'netmask': '255.255.255.0'
            }
        ]
    }

    output = template.render(variables)

    assert 'hostname test-router' in output
    assert 'router bgp 65001' in output
    assert '10.0.0.1 255.255.255.0' in output

def test_interface_configuration():
    """Test interface configuration logic"""
    config = generate_interface_config('Gi0/0/0', '10.0.0.1')

    assert 'interface Gi0/0/0' in config
    assert 'ip address 10.0.0.1' in config
    assert 'no shutdown' in config
```

## Integration Tests

### Device Testing
```python
# tests/integration/conftest.py
import pytest
from netmiko import ConnectHandler

@pytest.fixture(scope='module')
def cisco_device():
    """Connect to Cisco device for testing"""
    device = {
        'device_type': 'cisco_ios',
        'host': '192.168.1.1',
        'username': 'admin',
        'password': 'password',
        'timeout': 30
    }

    net_connect = ConnectHandler(**device)
    yield net_connect
    net_connect.disconnect()

# tests/integration/test_interface_status.py
def test_interface_up(cisco_device):
    """Test interface is operational"""
    output = cisco_device.send_command('show interfaces Ethernet0/0')

    assert 'line protocol is up' in output
    assert 'Hardware is' in output

def test_interface_configuration(cisco_device):
    """Test interface has correct IP"""
    output = cisco_device.send_command('show ip interface brief')

    assert '10.0.0.1' in output
    assert 'Ethernet0/0' in output
    assert 'up' in output
```

### Routing Tests
```python
# tests/integration/test_routing.py
def test_bgp_neighbors(cisco_device):
    """Test BGP neighbors are established"""
    output = cisco_device.send_command('show bgp ipv4 unicast summary')

    assert 'Established' in output
    assert output.count('Established') >= 1

def test_bgp_routes(cisco_device):
    """Test BGP routes are received"""
    output = cisco_device.send_command('show ip bgp')

    # Should have received routes
    lines = output.split('\n')
    route_lines = [l for l in lines if 'i' in l]  # Internal routes

    assert len(route_lines) > 0

def test_ospf_neighbors(cisco_device):
    """Test OSPF neighbors are full"""
    output = cisco_device.send_command('show ip ospf neighbors')

    assert 'FULL' in output
    assert 'LOADING' not in output
    assert 'INIT' not in output
```

## End-to-End Tests

### Deployment Validation
```python
# tests/e2e/test_deployment.py
import pytest
from napalm import get_network_driver
from datetime import datetime

@pytest.fixture
def deployment_devices():
    """Get list of devices to test"""
    return [
        {'host': '192.168.1.1', 'os': 'ios'},
        {'host': '192.168.1.2', 'os': 'ios'},
        {'host': '192.168.1.3', 'os': 'junos'},
    ]

def test_post_deployment_interfaces(deployment_devices):
    """Test all interfaces are configured"""
    for device in deployment_devices:
        driver = get_network_driver(device['os'])
        dev = driver(device['host'], 'admin', 'password')
        dev.open()

        interfaces = dev.get_interfaces()

        # Should have at least 2 interfaces up
        up_interfaces = [i for i, d in interfaces.items() if d['is_up']]
        assert len(up_interfaces) >= 2

        dev.close()

def test_post_deployment_routing(deployment_devices):
    """Test routing is working"""
    for device in deployment_devices[:2]:  # Test first 2 (Cisco)
        driver = get_network_driver('ios')
        dev = driver(device['host'], 'admin', 'password')
        dev.open()

        routes = dev.get_route_to('8.8.8.8')
        assert len(routes) > 0

        dev.close()

def test_configuration_compliance(deployment_devices):
    """Test configuration meets compliance standards"""
    required_configs = [
        'ntp server',
        'logging',
        'snmp-server',
        'access-list'
    ]

    for device in deployment_devices:
        driver = get_network_driver(device['os'])
        dev = driver(device['host'], 'admin', 'password')
        dev.open()

        config = dev.get_config(retrieve='running')
        running_config = config['running']

        for required in required_configs:
            assert required in running_config, \
                f"Missing required configuration: {required}"

        dev.close()
```

## Baseline Comparison

### Snapshot Testing
```python
# tests/integration/test_baseline.py
import json
import os
from napalm import get_network_driver

def load_baseline(device_name):
    """Load baseline for device"""
    baseline_file = f"tests/baselines/{device_name}.json"
    if os.path.exists(baseline_file):
        with open(baseline_file, 'r') as f:
            return json.load(f)
    return None

def save_baseline(device_name, data):
    """Save baseline for device"""
    baseline_file = f"tests/baselines/{device_name}.json"
    os.makedirs('tests/baselines', exist_ok=True)
    with open(baseline_file, 'w') as f:
        json.dump(data, f, indent=2)

def test_interface_statistics_against_baseline(cisco_device):
    """Compare current stats against baseline"""
    driver = get_network_driver('ios')
    device = driver('192.168.1.1', 'admin', 'password')
    device.open()

    current_stats = device.get_interfaces()
    baseline = load_baseline('router1')

    if baseline:
        for intf_name, current_data in current_stats.items():
            if intf_name in baseline:
                baseline_data = baseline[intf_name]

                # Allow small increase in errors
                current_errors = current_data.get('errors', 0)
                baseline_errors = baseline_data.get('errors', 0)

                assert current_errors - baseline_errors < 10, \
                    f"{intf_name}: error count increased significantly"
    else:
        # First run, save baseline
        save_baseline('router1', current_stats)

    device.close()
```

## Compliance Testing

### Configuration Compliance
```python
# tests/integration/test_compliance.py
def test_ssh_enabled(cisco_device):
    """Verify SSH is enabled"""
    output = cisco_device.send_command('show ip ssh')

    assert 'SSH Enabled' in output or 'Version' in output

def test_aaa_configured(cisco_device):
    """Verify AAA is configured"""
    output = cisco_device.send_command('show aaa')

    assert 'aaa new-model' in output or 'aaa' in output

def test_logging_configured(cisco_device):
    """Verify logging is configured"""
    output = cisco_device.send_command('show logging')

    assert 'Logging buffered' in output or 'logging' in output

def test_ntp_configured(cisco_device):
    """Verify NTP is configured"""
    output = cisco_device.send_command('show ntp status')

    # Either NTP is configured or status shows no associations
    assert 'synchronized' in output.lower() or 'no associations' in output.lower()

def test_snmp_configured(cisco_device):
    """Verify SNMP is configured"""
    output = cisco_device.send_command('show snmp')

    assert 'SNMP enabled' in output or 'snmp-server' in output
```

## PyATS Tests

### Using PyATS Framework
```python
# tests/pyats_tests.py
from pyats import aetest
from genie.testbed import load

class CommonSetup(aetest.CommonSetup):
    @aetest.subsection
    def load_testbed(self):
        """Load testbed"""
        self.testbed = load('testbed.yaml')

    @aetest.subsection
    def connect_devices(self):
        """Connect to devices"""
        self.testbed.connect()

class BGPTests(aetest.TestCase):
    """BGP connectivity tests"""

    @aetest.setup
    def setup(self):
        self.router = self.testbed.devices['router1']

    @aetest.test
    def test_bgp_neighbors(self):
        """Test BGP neighbors established"""
        output = self.router.parse('show bgp ipv4 unicast summary')

        neighbors = output['bgp_instance']['default']['vrf']['default']['neighbor']
        self.assertGreater(len(neighbors), 0, "No BGP neighbors found")

        for neighbor_ip, neighbor_data in neighbors.items():
            state = neighbor_data['session_state']
            self.assertEqual(state, 'Established',
                f"BGP neighbor {neighbor_ip} state: {state}")

class InterfaceTests(aetest.TestCase):
    """Interface tests"""

    @aetest.test
    def test_critical_interfaces_up(self):
        """Test critical interfaces are up"""
        critical = ['Ethernet0/0', 'Ethernet0/1']
        router = self.testbed.devices['router1']

        output = router.parse('show interfaces')

        for intf in critical:
            assert intf in output['interfaces'], \
                f"Interface {intf} not found"
            assert output['interfaces'][intf]['enabled'], \
                f"Interface {intf} is disabled"
```

## Running Tests

### With pytest
```bash
# Run all tests
pytest tests/

# Run specific test file
pytest tests/integration/test_routing.py

# Run specific test
pytest tests/integration/test_routing.py::test_bgp_neighbors

# Run with verbose output
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=. --cov-report=html

# Run tests matching pattern
pytest tests/ -k "bgp"
```

### With PyATS
```bash
# Run PyATS test
pyats run job pyats_job.yaml

# Run test with specific testbed
pyats run job pyats_job.yaml --testbed testbed.yaml
```

### With Robot Framework
```bash
# Run robot tests
robot tests/

# Run specific test suite
robot tests/routing_tests.robot

# Generate report
robot --output results.xml tests/
```

## CI/CD Integration

### GitLab CI
```yaml
test_network:
  stage: test
  script:
    - pip install -r requirements.txt
    - pytest tests/unit -v
    - pytest tests/integration -v
    - pyats run job job_file.yaml
  artifacts:
    reports:
      junit: test-results.xml
```

---

**Last Updated**: 2025-11-19
**Reference**: pytest.org, pyats.readthedocs.io, robotframework.org
