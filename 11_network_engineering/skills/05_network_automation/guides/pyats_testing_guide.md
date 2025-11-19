# PyATS Testing Guide

## Installation and Setup

```bash
pip install pyats[full]
pyats --version
```

## Testbed Configuration

### testbed.yaml
```yaml
devices:
  router1:
    type: router
    os: iosxe
    platform: asr1001x
    connections:
      cli:
        protocol: ssh
        ip: 192.168.1.1
        port: 22
        username: admin
        password: admin
      rest:
        protocol: https
        ip: 192.168.1.1
        port: 443
        username: admin
        password: admin

  router2:
    type: router
    os: iosxe
    connections:
      cli:
        protocol: ssh
        ip: 192.168.1.2
        username: admin
        password: admin

  switch1:
    type: switch
    os: iosxe
    connections:
      cli:
        protocol: ssh
        ip: 192.168.1.3
        username: admin
        password: admin

topology:
  router1:
    interfaces:
      Ethernet0/0:
        link: router1_to_router2
      Ethernet0/1:
        link: router1_to_switch1

  router2:
    interfaces:
      Ethernet0/0:
        link: router1_to_router2

  switch1:
    interfaces:
      GigabitEthernet1/1:
        link: router1_to_switch1
```

## Basic Test Structure

### Minimal Test
```python
# test_basic.py
from pyats import aetest
from genie.testbed import load

class CommonSetup(aetest.CommonSetup):
    """Setup for all tests"""

    @aetest.subsection
    def load_testbed(self, testbed):
        """Load testbed from file"""
        self.testbed = load(testbed)

    @aetest.subsection
    def connect_to_devices(self):
        """Connect to all devices"""
        self.testbed.connect()

class RouterHealthTests(aetest.TestCase):
    """Basic router health tests"""

    @aetest.test
    def test_device_reachable(self):
        """Test device is reachable"""
        device = self.testbed.devices['router1']
        output = device.execute('show version')
        self.assertIn('Cisco IOS XE', output)

    @aetest.test
    def test_uptime_greater_than_zero(self):
        """Test device has been up"""
        device = self.testbed.devices['router1']
        output = device.parse('show version')
        uptime = output['version']['system_uptime']['uptime']['total_seconds']
        self.assertGreater(uptime, 0)

class CommonCleanup(aetest.CommonCleanup):
    """Cleanup for all tests"""

    @aetest.subsection
    def disconnect_devices(self):
        """Disconnect from devices"""
        self.testbed.disconnect()
```

## Intermediate Tests

### BGP Testing
```python
# test_bgp.py
from pyats import aetest

class BGPTests(aetest.TestCase):
    """BGP neighbor and route tests"""

    @aetest.setup
    def setup(self, testbed):
        """Setup for BGP tests"""
        self.router1 = testbed.devices['router1']

    @aetest.test
    def test_bgp_neighbors_established(self):
        """Verify all BGP neighbors are established"""

        # Parse BGP summary
        output = self.router1.parse('show bgp ipv4 unicast summary')

        # Navigate to neighbor data
        bgp_instance = output['bgp_instance']['default']
        vrf = bgp_instance['vrf']['default']
        neighbors = vrf['neighbor']

        # Verify neighbors exist
        self.assertGreater(len(neighbors), 0, "No BGP neighbors configured")

        # Check each neighbor state
        for neighbor_ip, neighbor_data in neighbors.items():
            state = neighbor_data.get('session_state', 'Unknown')
            self.assertEqual(state, 'Established',
                f"Neighbor {neighbor_ip} state is {state}, expected Established")

    @aetest.test
    def test_bgp_routes_received(self):
        """Verify BGP routes are being received"""

        # Get BGP routes
        output = self.router1.parse('show ip bgp')

        # Navigate to routes
        bgp_table = output['bgp_route_tab']
        routes = bgp_table.get('routes', {})

        # Verify routes received
        self.assertGreater(len(routes), 0, "No BGP routes received")

    @aetest.test
    def test_bgp_aggregate_routes(self):
        """Verify aggregate routes are present"""

        output = self.router1.parse('show ip bgp')
        routes = output['bgp_route_tab']['routes']

        # Check for specific aggregate route
        aggregate_found = False
        for route in routes:
            if '10.0.0.0/8' in route:
                aggregate_found = True
                break

        self.assertTrue(aggregate_found, "Aggregate route 10.0.0.0/8 not found")
```

### Interface Testing
```python
# test_interfaces.py
class InterfaceTests(aetest.TestCase):
    """Interface status tests"""

    @aetest.setup
    def setup(self, testbed):
        self.router = testbed.devices['router1']

    @aetest.test
    def test_critical_interfaces_up(self):
        """Test critical interfaces are up"""

        critical_interfaces = ['Ethernet0/0', 'Ethernet0/1']

        output = self.router.parse('show interfaces')
        interfaces = output['interfaces']

        for iface_name in critical_interfaces:
            self.assertIn(iface_name, interfaces,
                f"Interface {iface_name} not found")

            iface_data = interfaces[iface_name]

            # Check enabled
            self.assertTrue(iface_data.get('enabled'),
                f"Interface {iface_name} is not enabled")

            # Check line protocol
            line_protocol = iface_data.get('line_protocol', 'down')
            self.assertEqual(line_protocol, 'up',
                f"Interface {iface_name} line protocol is {line_protocol}")

    @aetest.test
    def test_interface_mtu(self):
        """Test interface MTU settings"""

        output = self.router.parse('show interfaces')
        interfaces = output['interfaces']

        expected_mtu = {
            'Ethernet0/0': 1500,
            'Ethernet0/1': 9000,
        }

        for iface_name, expected in expected_mtu.items():
            actual = interfaces[iface_name]['mtu']
            self.assertEqual(actual, expected,
                f"{iface_name} MTU is {actual}, expected {expected}")
```

## Advanced Features

### Parameterized Testing
```python
# test_parameterized.py
class MultiInterfaceTests(aetest.TestCase):
    """Test multiple interfaces with parameters"""

    @aetest.parametrize('interface', ['Ethernet0/0', 'Ethernet0/1', 'Ethernet0/2'])
    @aetest.test
    def test_interface_configuration(self, interface):
        """Test interface is configured"""

        device = self.testbed.devices['router1']
        output = device.parse('show interfaces')

        self.assertIn(interface, output['interfaces'],
            f"Interface {interface} not found")
```

### Conditional Tests
```python
# test_conditional.py
class ConditionalTests(aetest.TestCase):

    @aetest.test
    def test_ospf_if_enabled(self):
        """Test OSPF only if configured"""

        device = self.testbed.devices['router1']

        # Check if OSPF is configured
        try:
            output = device.execute('show ip ospf')
            if 'not running' in output.lower():
                self.skipped("OSPF not configured")
        except:
            self.skipped("OSPF not available")

        # Run OSPF tests
        ospf_data = device.parse('show ip ospf neighbors')
        self.assertGreater(len(ospf_data), 0, "No OSPF neighbors")
```

## Test Execution

### Running Tests
```bash
# Run all tests
pyats run job test_job.yaml

# Run specific test file
pyats run job test_job.yaml -t test_bgp.py

# Run with specific testbed
pyats run job test_job.yaml --testbed testbed.yaml

# Generate HTML report
pyats run job test_job.yaml --html report.html
```

### Job File
```yaml
# test_job.yaml
---
runtime:
  max_attempts: 1
  memory_limit: 2GB
  timeout: 3600

testbed: testbed.yaml

tests:
  - test_basic.py
  - test_bgp.py
  - test_interfaces.py
```

## Integration Test Example

### Complete Test Suite
```python
# test_network_deployment.py
import time
from pyats import aetest
from pyats.log.utils import banner

class DeploymentTestbed(aetest.CommonSetup):
    """Setup for deployment tests"""

    @aetest.subsection
    def connect_devices(self, testbed):
        self.testbed = testbed
        self.testbed.connect()

    @aetest.subsection
    def collect_pre_deployment_state(self):
        """Capture baseline before deployment"""

        self.pre_deployment = {}

        for device_name in self.testbed.devices:
            device = self.testbed.devices[device_name]

            try:
                facts = device.parse('show version')
                interfaces = device.parse('show interfaces')

                self.pre_deployment[device_name] = {
                    'version': facts,
                    'interfaces': interfaces
                }

                self.logger.info(f"Collected baseline for {device_name}")

            except Exception as e:
                self.logger.error(f"Failed to collect baseline for {device_name}: {e}")

class ConfigurationTests(aetest.TestCase):
    """Test configurations after deployment"""

    @aetest.test
    def test_interfaces_not_broken(self, testbed):
        """Ensure deployment didn't break interfaces"""

        for device_name in testbed.devices:
            device = testbed.devices[device_name]

            pre = self.parent.pre_deployment[device_name]['interfaces']
            post = device.parse('show interfaces')

            # Compare interface counts
            pre_count = len(pre.get('interfaces', {}))
            post_count = len(post.get('interfaces', {}))

            self.assertEqual(pre_count, post_count,
                f"{device_name} interface count changed")

    @aetest.test
    def test_routing_established(self, testbed):
        """Test routing protocols are established"""

        device = testbed.devices['router1']

        # Test BGP
        bgp = device.parse('show bgp ipv4 unicast summary')
        neighbors = bgp['bgp_instance']['default']['vrf']['default']['neighbor']

        for neighbor_ip, data in neighbors.items():
            self.assertEqual(data['session_state'], 'Established',
                f"BGP neighbor {neighbor_ip} not established")

        # Test OSPF
        ospf = device.parse('show ip ospf neighbors')
        for neighbor in ospf.get('ospf', {}).get('processes', {}).values():
            neighbors = neighbor.get('neighbors', {})
            for neighbor_ip, data in neighbors.items():
                self.assertEqual(data['state'], 'FULL',
                    f"OSPF neighbor {neighbor_ip} not full")

class DeploymentCleanup(aetest.CommonCleanup):
    """Cleanup after tests"""

    @aetest.subsection
    def disconnect(self):
        self.testbed.disconnect()

    @aetest.subsection
    def generate_report(self):
        """Generate test summary"""

        self.logger.info(banner("Test Deployment Summary"))

        # Report on what was tested and results
        self.logger.info("Deployment validation completed")
```

## Best Practices

1. **Use Testbed Files**: Keep device configuration external
2. **Organize Tests**: Group related tests in classes
3. **Use Setup/Cleanup**: Establish and teardown properly
4. **Log Effectively**: Use task logging for debugging
5. **Handle Exceptions**: Don't let parsing errors crash tests

```python
# Good error handling
try:
    output = device.parse('show bgp')
except Exception as e:
    self.skipped(f"BGP parsing failed: {e}")
```

---

**Last Updated**: 2025-11-19
**Reference**: pyats.readthedocs.io, developer.cisco.com/docs/genie
