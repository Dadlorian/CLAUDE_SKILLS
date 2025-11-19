# Network Testing Frameworks Reference

## PyATS (Python Automated Test System)

### Installation and Setup
```bash
pip install pyats[full]
pyats --version
```

### Test Structure
```python
import unittest
from pyats import aetest
from pyats.log.utils import banner
from genie.testbed import load

class CommonSetup(aetest.CommonSetup):
    """Common setup for all tests"""

    @aetest.subsection
    def load_testbed(self, testbed):
        """Load testbed from file"""
        self.testbed = load(testbed)

    @aetest.subsection
    def connect_devices(self):
        """Connect to all devices in testbed"""
        self.testbed.connect()

class BGPTests(aetest.TestCase):
    """Test BGP neighbor states"""

    @aetest.setup
    def setup(self):
        """Setup BGP test"""
        self.intf = self.testbed.devices['router1']

    @aetest.test
    def test_bgp_neighbors_established(self):
        """Verify BGP neighbors are established"""
        output = self.intf.parse('show bgp ipv4 unicast summary')

        # Get neighbor count
        neighbor_count = len(output['bgp_instance']['default']['vrf']['default']['neighbor'])

        self.assertGreater(neighbor_count, 0, "No BGP neighbors found")

        # Check all neighbors are established
        for neighbor_ip, neighbor_data in output['bgp_instance']['default']['vrf']['default']['neighbor'].items():
            state = neighbor_data.get('session_state', 'Unknown')
            self.assertEqual(state, 'Established', f"Neighbor {neighbor_ip} state: {state}")

    @aetest.test
    def test_bgp_routes(self):
        """Verify BGP routes are received"""
        output = self.intf.parse('show ip bgp')

        routes = len(output.get('bgp_route_tab', {}).get('routes', {}))
        self.assertGreater(routes, 0, "No BGP routes received")

class InterfaceTests(aetest.TestCase):
    """Test interface states"""

    @aetest.setup
    def setup(self):
        """Setup interface test"""
        self.intf = self.testbed.devices['router1']

    @aetest.test
    def test_interface_up(self):
        """Verify critical interfaces are up"""
        critical_interfaces = ['GigabitEthernet0/0/0', 'GigabitEthernet0/0/1']

        output = self.intf.parse('show interfaces')

        for intf_name in critical_interfaces:
            intf_data = output['interfaces'].get(intf_name)
            self.assertIsNotNone(intf_data, f"Interface {intf_name} not found")

            enabled = intf_data.get('enabled', False)
            line_protocol = intf_data.get('line_protocol', 'down')

            self.assertTrue(enabled, f"Interface {intf_name} is disabled")
            self.assertEqual(line_protocol, 'up', f"Interface {intf_name} line protocol: {line_protocol}")

class CommonCleanup(aetest.CommonCleanup):
    """Common cleanup for all tests"""

    @aetest.subsection
    def disconnect_devices(self):
        """Disconnect from all devices"""
        self.testbed.disconnect()

if __name__ == '__main__':
    aetest.main()
```

### Testbed YAML File
```yaml
testbed:
  name: production_testbed

devices:
  router1:
    type: router
    os: iosxe
    platform: asr1001-x
    connections:
      cli:
        protocol: ssh
        ip: 192.168.1.1
        port: 22
        username: admin
        password: password

  switch1:
    type: switch
    os: iosxe
    platform: c9300
    connections:
      cli:
        protocol: ssh
        ip: 192.168.1.2
        username: admin
        password: password

  firewall1:
    type: firewall
    os: asa
    platform: asa5525
    connections:
      cli:
        protocol: ssh
        ip: 192.168.1.3
        username: admin
        password: password
```

### Advanced Testing

#### Baseline Comparison
```python
@aetest.test
def test_interface_statistics(self):
    """Compare current statistics against baseline"""
    baseline = {
        'GigabitEthernet0/0/0': {
            'in_discards': 0,
            'out_discards': 0,
            'in_errors': 0,
            'out_errors': 0
        }
    }

    device = self.testbed.devices['router1']
    output = device.parse('show interfaces')

    for intf_name, baseline_stats in baseline.items():
        intf_stats = output['interfaces'][intf_name]

        for stat_name, baseline_val in baseline_stats.items():
            current_val = intf_stats.get(stat_name, 0)

            # Allow small increase but flag large changes
            if current_val > baseline_val + 10:
                self.failed(f"{intf_name}: {stat_name} increased from {baseline_val} to {current_val}")
```

## Robot Framework

### Installation
```bash
pip install robotframework
pip install robotframework-sshlibrary
```

### Test Suite
```robot
*** Settings ***
Library    SSHLibrary
Library    Collections

*** Variables ***
${ROUTER_IP}      192.168.1.1
${USERNAME}       admin
${PASSWORD}       password

*** Test Cases ***
Test BGP Neighbor Status
    [Documentation]    Verify all BGP neighbors are established
    Connect To Router
    ${output}=    Execute Command    show bgp ipv4 unicast summary
    Should Contain    ${output}    Established
    [Teardown]    Close Connection

Test Interface Availability
    [Documentation]    Check critical interfaces are up
    Connect To Router
    ${output}=    Execute Command    show interfaces brief
    Should Contain    ${output}    GigabitEthernet0/0/0    up
    Should Contain    ${output}    GigabitEthernet0/0/1    up
    [Teardown]    Close Connection

*** Keywords ***
Connect To Router
    Open Connection    ${ROUTER_IP}
    Login    ${USERNAME}    ${PASSWORD}

Close Connection
    Close All Connections
```

## Pytest for Network Testing

### Installation
```bash
pip install pytest pytest-xfail
```

### Test Suite
```python
import pytest
from netmiko import ConnectHandler

@pytest.fixture
def device():
    """Fixture for device connection"""
    device = {
        'device_type': 'cisco_ios',
        'host': '192.168.1.1',
        'username': 'admin',
        'password': 'password'
    }
    connection = ConnectHandler(**device)
    yield connection
    connection.disconnect()

def test_interface_count(device):
    """Test interface count"""
    output = device.send_command('show interfaces brief')
    lines = [l for l in output.split('\n') if l and 'Ethernet' in l]
    assert len(lines) >= 2, "Expected at least 2 interfaces"

def test_bgp_session(device):
    """Test BGP session establishment"""
    output = device.send_command('show ip bgp summary')
    assert 'Established' in output, "BGP session not established"

@pytest.mark.parametrize("interface", ["Ethernet0/0", "Ethernet0/1"])
def test_interface_up(device, interface):
    """Test multiple interfaces are up"""
    output = device.send_command(f'show interface {interface}')
    assert 'up' in output.lower(), f"Interface {interface} is not up"
```

## NAPALM Validation

### Configuration Validation
```python
from napalm import get_network_driver
from netmiko import ConnectHandler

def validate_ospf_neighbors(device):
    """Validate OSPF neighbors using NAPALM"""
    driver = get_network_driver('ios')
    device = driver('192.168.1.1', 'admin', 'password')
    device.open()

    # Get routing neighbors
    neighbors = device.get_bgp_neighbors_detail()

    # Validate neighbor count
    assert len(neighbors['default']['peers']) >= 2, "Not enough OSPF neighbors"

    # Validate neighbor states
    for neighbor_ip, neighbor_data in neighbors['default']['peers'].items():
        assert neighbor_data['state'] == 'Established', \
            f"Neighbor {neighbor_ip} not established"

    device.close()

def validate_configuration_compliance(device):
    """Validate configuration meets compliance standards"""
    driver = get_network_driver('ios')
    device = driver('192.168.1.1', 'admin', 'password')
    device.open()

    # Get running config
    config = device.get_config(retrieve='running')

    # Check for required configurations
    required_configs = [
        'aaa new-model',
        'line vty 0 15',
        'transport input ssh'
    ]

    for required in required_configs:
        assert required in config['running'], f"Missing: {required}"

    device.close()
```

## Network Compliance Testing

### Pre-Deployment Validation
```python
def pre_deployment_checks(device_ip, device_type):
    """Run pre-deployment validation"""
    device = {
        'device_type': device_type,
        'host': device_ip,
        'username': 'admin',
        'password': 'password'
    }

    net_connect = ConnectHandler(**device)

    checks = {
        'Memory Available': lambda: int(get_memory_free(net_connect)) > 100000,
        'Reachable NTP Server': lambda: is_ntp_reachable(net_connect),
        'Logging Configured': lambda: 'logging' in net_connect.send_command('show logging'),
        'SSH Enabled': lambda: 'ssh' in net_connect.send_command('show ip ssh'),
    }

    results = {}
    for check_name, check_func in checks.items():
        try:
            results[check_name] = check_func()
        except Exception as e:
            results[check_name] = False

    net_connect.disconnect()
    return results

def post_deployment_validation(device_ip, device_type):
    """Run post-deployment validation"""
    device = {
        'device_type': device_type,
        'host': device_ip,
        'username': 'admin',
        'password': 'password'
    }

    net_connect = ConnectHandler(**device)

    checks = {
        'Config Saved': lambda: 'startup-config' in net_connect.send_command('show startup-config'),
        'All Interfaces Up': lambda: 'up' in net_connect.send_command('show interfaces summary'),
        'OSPF Neighbors': lambda: 'FULL' in net_connect.send_command('show ip ospf neighbors'),
    }

    results = {}
    for check_name, check_func in checks.items():
        try:
            results[check_name] = check_func()
        except Exception as e:
            results[check_name] = False

    net_connect.disconnect()
    return results
```

## Continuous Testing

### CI/CD Integration
```yaml
# .gitlab-ci.yml
test_network_changes:
  stage: test
  script:
    # Pre-deployment checks
    - python scripts/pre_deployment_checks.py $DEVICE_IP

    # Run PyATS tests
    - pyats run job job_file.yaml

    # Run robot framework tests
    - robot --variable DEVICE_IP:$DEVICE_IP tests/

    # Run pytest tests
    - pytest tests/network_tests.py -v

  artifacts:
    reports:
      junit: results.xml
    paths:
      - results/
      - logs/
```

---

**Last Updated**: 2025-11-19
**Reference**: pyats.readthedocs.io, robotframework.org, pytest.org
