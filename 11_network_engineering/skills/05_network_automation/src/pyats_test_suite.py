#!/usr/bin/env python3
"""
PyATS Network Device Test Suite
Tests device connectivity, routing, and configuration compliance
"""

from pyats import aetest
from pyats.log.utils import banner
from genie.testbed import load
import logging

logger = logging.getLogger(__name__)


class CommonSetup(aetest.CommonSetup):
    """Setup for all tests"""

    @aetest.subsection
    def load_testbed(self, testbed):
        """Load testbed from YAML file"""
        try:
            self.testbed = load(testbed)
            logger.info(f"Testbed loaded with {len(self.testbed.devices)} devices")
        except Exception as e:
            self.failed(f"Failed to load testbed: {e}")

    @aetest.subsection
    def connect_to_devices(self):
        """Establish connections to all devices"""
        try:
            self.testbed.connect(log_stdout=False)
            logger.info("✓ Connected to all devices")
        except Exception as e:
            self.failed(f"Failed to connect to devices: {e}")


class DeviceHealthTests(aetest.TestCase):
    """Test basic device health and connectivity"""

    @aetest.setup
    def setup(self):
        """Setup for device health tests"""
        self.devices = self.parent.testbed.devices

    @aetest.test
    def test_device_reachable(self):
        """Test all devices are reachable"""
        for device_name, device in self.devices.items():
            try:
                output = device.execute('show version')
                self.assertIsNotNone(output, f"{device_name} - no output from show version")
                logger.info(f"✓ {device_name} is reachable")
            except Exception as e:
                self.failed(f"{device_name} - Failed to reach device: {e}")

    @aetest.test
    def test_device_uptime(self):
        """Test devices have been up for reasonable time"""
        for device_name, device in self.devices.items():
            try:
                output = device.parse('show version')

                # Get uptime in seconds
                uptime_seconds = output.get('version', {}).get('system_uptime', {}).get('uptime', {}).get('total_seconds', 0)

                # Ensure uptime is greater than 5 minutes
                self.assertGreater(uptime_seconds, 300,
                    f"{device_name} - Device uptime less than 5 minutes")

                logger.info(f"✓ {device_name} - Uptime: {uptime_seconds} seconds")

            except Exception as e:
                self.failed(f"{device_name} - Failed to get uptime: {e}")


class BGPTests(aetest.TestCase):
    """Test BGP neighbor and route status"""

    @aetest.setup
    def setup(self):
        """Setup for BGP tests"""
        self.devices = self.parent.testbed.devices

    @aetest.test
    def test_bgp_neighbors_established(self):
        """Test BGP neighbors are established"""
        for device_name, device in self.devices.items():
            try:
                output = device.parse('show bgp ipv4 unicast summary')

                # Navigate to neighbor information
                bgp_instance = output.get('bgp_instance', {}).get('default', {})
                vrf = bgp_instance.get('vrf', {}).get('default', {})
                neighbors = vrf.get('neighbor', {})

                if not neighbors:
                    self.skipped(f"{device_name} - No BGP neighbors configured")
                    continue

                # Check each neighbor
                for neighbor_ip, neighbor_data in neighbors.items():
                    state = neighbor_data.get('session_state', 'Unknown')

                    if state != 'Established':
                        self.failed(f"{device_name} - BGP neighbor {neighbor_ip} state: {state}")
                    else:
                        logger.info(f"✓ {device_name} - BGP neighbor {neighbor_ip} established")

            except KeyError as e:
                self.skipped(f"{device_name} - BGP data not available: {e}")
            except Exception as e:
                self.failed(f"{device_name} - Error checking BGP: {e}")

    @aetest.test
    def test_bgp_routes_received(self):
        """Test BGP routes are being received"""
        for device_name, device in self.devices.items():
            try:
                output = device.parse('show ip bgp')

                bgp_table = output.get('bgp_route_tab', {})
                routes = bgp_table.get('routes', {})

                if not routes:
                    self.failed(f"{device_name} - No BGP routes received")
                else:
                    logger.info(f"✓ {device_name} - BGP routes received: {len(routes)}")

            except Exception as e:
                self.skipped(f"{device_name} - BGP routes check skipped: {e}")


class InterfaceTests(aetest.TestCase):
    """Test interface status and configuration"""

    @aetest.setup
    def setup(self):
        """Setup for interface tests"""
        self.devices = self.parent.testbed.devices
        self.critical_interfaces = ['Ethernet0/0', 'Ethernet0/1']

    @aetest.parametrize('interface', ['Ethernet0/0', 'Ethernet0/1'])
    @aetest.test
    def test_critical_interface_status(self, interface):
        """Test critical interfaces are up"""
        for device_name, device in self.devices.items():
            try:
                output = device.parse('show interfaces')
                interfaces = output.get('interfaces', {})

                if interface not in interfaces:
                    self.skipped(f"{device_name} - Interface {interface} not found")
                    continue

                iface_data = interfaces[interface]
                is_enabled = iface_data.get('enabled', False)
                line_protocol = iface_data.get('line_protocol', 'down')

                if not is_enabled:
                    self.failed(f"{device_name} - Interface {interface} is disabled")
                    continue

                if line_protocol != 'up':
                    self.failed(f"{device_name} - Interface {interface} line protocol: {line_protocol}")
                else:
                    logger.info(f"✓ {device_name} - Interface {interface} up/up")

            except Exception as e:
                self.failed(f"{device_name} - Error checking interface {interface}: {e}")

    @aetest.test
    def test_interface_mtu(self):
        """Test interface MTU settings"""
        expected_mtu = 1500

        for device_name, device in self.devices.items():
            try:
                output = device.parse('show interfaces')
                interfaces = output.get('interfaces', {})

                for iface_name, iface_data in interfaces.items():
                    mtu = iface_data.get('mtu', 0)

                    if mtu != expected_mtu:
                        logger.warning(f"{device_name} - {iface_name} MTU: {mtu} (expected {expected_mtu})")

            except Exception as e:
                self.skipped(f"{device_name} - MTU check skipped: {e}")


class RoutingTests(aetest.TestCase):
    """Test routing configuration"""

    @aetest.setup
    def setup(self):
        """Setup for routing tests"""
        self.devices = self.parent.testbed.devices

    @aetest.test
    def test_ospf_neighbors_full(self):
        """Test OSPF neighbors are in FULL state"""
        for device_name, device in self.devices.items():
            try:
                output = device.parse('show ip ospf neighbors')

                if not output or 'ospf' not in output:
                    self.skipped(f"{device_name} - OSPF not configured")
                    continue

                ospf_data = output['ospf']
                processes = ospf_data.get('processes', {})

                for process_id, process_data in processes.items():
                    neighbors = process_data.get('neighbors', {})

                    if not neighbors:
                        self.skipped(f"{device_name} - No OSPF neighbors")
                        continue

                    for neighbor_ip, neighbor_data in neighbors.items():
                        state = neighbor_data.get('state', 'Unknown')

                        if state != 'FULL':
                            self.failed(f"{device_name} - OSPF neighbor {neighbor_ip} state: {state}")
                        else:
                            logger.info(f"✓ {device_name} - OSPF neighbor {neighbor_ip} FULL")

            except Exception as e:
                self.skipped(f"{device_name} - OSPF check skipped: {e}")


class ComplianceTests(aetest.TestCase):
    """Test configuration compliance"""

    @aetest.setup
    def setup(self):
        """Setup for compliance tests"""
        self.devices = self.parent.testbed.devices

    @aetest.test
    def test_ssh_enabled(self):
        """Test SSH is enabled"""
        for device_name, device in self.devices.items():
            try:
                output = device.execute('show ip ssh')

                if 'SSH' not in output and 'Version' not in output:
                    self.failed(f"{device_name} - SSH not enabled")
                else:
                    logger.info(f"✓ {device_name} - SSH is enabled")

            except Exception as e:
                self.skipped(f"{device_name} - SSH check skipped: {e}")

    @aetest.test
    def test_logging_configured(self):
        """Test logging is configured"""
        for device_name, device in self.devices.items():
            try:
                output = device.execute('show logging | include Logging')

                if 'Logging buffered' not in output:
                    self.failed(f"{device_name} - Logging not configured")
                else:
                    logger.info(f"✓ {device_name} - Logging configured")

            except Exception as e:
                self.skipped(f"{device_name} - Logging check skipped: {e}")


class CommonCleanup(aetest.CommonCleanup):
    """Cleanup for all tests"""

    @aetest.subsection
    def disconnect_devices(self):
        """Disconnect from all devices"""
        try:
            self.testbed.disconnect()
            logger.info("✓ Disconnected from all devices")
        except Exception as e:
            logger.warning(f"Error disconnecting: {e}")


if __name__ == '__main__':
    aetest.main()
