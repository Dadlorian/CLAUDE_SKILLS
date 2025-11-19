#!/usr/bin/env python3
"""
SNMP Network Monitoring Script
Polls SNMP-enabled devices and stores metrics in Prometheus
"""

import time
import logging
from pysnmp.hlapi import *
from prometheus_client import start_http_server, Gauge, Counter
import yaml

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Prometheus metrics
interface_status = Gauge('network_interface_status', 'Interface up/down',
                         ['device', 'interface', 'index'])
interface_throughput_in = Gauge('network_interface_in_bytes_total', 'Input bytes',
                                ['device', 'interface', 'index'])
interface_throughput_out = Gauge('network_interface_out_bytes_total', 'Output bytes',
                                 ['device', 'interface', 'index'])
interface_errors_in = Gauge('network_interface_in_errors_total', 'Input errors',
                            ['device', 'interface', 'index'])
interface_errors_out = Gauge('network_interface_out_errors_total', 'Output errors',
                             ['device', 'interface', 'index'])
device_uptime = Gauge('network_device_uptime_seconds', 'Device uptime',
                      ['device'])
device_cpu = Gauge('network_device_cpu_percent', 'Device CPU usage',
                   ['device'])
device_memory = Gauge('network_device_memory_percent', 'Device memory usage',
                      ['device'])

def snmp_get(engine, contextEngine, varBinds):
    """Execute SNMP GET request"""
    errorIndication, errorStatus, errorIndex, varBinds = next(
        getCmd(engine, contextEngine, *varBinds)
    )
    if errorIndication:
        logger.error(f"SNMP GET failed: {errorIndication}")
        return None
    return varBinds

def snmp_walk(engine, contextEngine, oid):
    """Execute SNMP WALK request"""
    results = {}
    errorIndication, errorStatus, errorIndex, varBindTable = nextCmd(
        engine, contextEngine, oid, lexicographicMode=False
    )
    if errorIndication:
        logger.error(f"SNMP WALK failed: {errorIndication}")
        return results

    for varBinds in varBindTable:
        for name, val in varBinds:
            results[str(name)] = val
    return results

def collect_device_metrics(device_ip, snmp_user, auth_key, priv_key):
    """Collect metrics from a single device"""
    logger.info(f"Collecting metrics from {device_ip}")

    # Setup SNMP engine
    engine = SnmpEngine()
    contextEngine = ContextEngine(
        SecurityParameters(
            UserBasedSecurityModel(),
            UsmUserEngineID(),
            usmHMACMDAuthentication,
            usmAesCfb128Encryption
        )
    )

    # Get system uptime
    varBinds = snmp_get(
        engine, contextEngine,
        [ObjectType(ObjectIdentity('SNMPv2-MIB', 'sysUpTime', 0))]
    )
    if varBinds:
        uptime = int(varBinds[0][1]) / 100  # Convert centiseconds to seconds
        device_uptime.labels(device=device_ip).set(uptime)

    # Walk interface table
    interface_oids = {
        'ifIndex': '1.3.6.1.2.1.2.2.1.1',
        'ifName': '1.3.6.1.2.1.2.2.1.2',
        'ifOperStatus': '1.3.6.1.2.1.2.2.1.8',
        'ifInOctets': '1.3.6.1.2.1.2.2.1.10',
        'ifOutOctets': '1.3.6.1.2.1.2.2.1.16',
        'ifInErrors': '1.3.6.1.2.1.2.2.1.14',
        'ifOutErrors': '1.3.6.1.2.1.2.2.1.20',
    }

    interface_data = {}
    for oid_name, oid in interface_oids.items():
        results = snmp_walk(engine, contextEngine, oid)
        for full_oid, value in results.items():
            if_index = full_oid.split('.')[-1]
            if if_index not in interface_data:
                interface_data[if_index] = {}
            interface_data[if_index][oid_name] = value

    # Store interface metrics
    for if_index, data in interface_data.items():
        interface_name = data.get('ifName', f'interface_{if_index}')

        # Interface status
        status = int(data.get('ifOperStatus', 0))
        interface_status.labels(device=device_ip, interface=interface_name,
                               index=if_index).set(status)

        # Interface throughput
        in_bytes = int(data.get('ifInOctets', 0))
        out_bytes = int(data.get('ifOutOctets', 0))
        interface_throughput_in.labels(device=device_ip, interface=interface_name,
                                       index=if_index).set(in_bytes)
        interface_throughput_out.labels(device=device_ip, interface=interface_name,
                                        index=if_index).set(out_bytes)

        # Interface errors
        in_errors = int(data.get('ifInErrors', 0))
        out_errors = int(data.get('ifOutErrors', 0))
        interface_errors_in.labels(device=device_ip, interface=interface_name,
                                   index=if_index).set(in_errors)
        interface_errors_out.labels(device=device_ip, interface=interface_name,
                                    index=if_index).set(out_errors)

def main():
    """Main monitoring loop"""
    # Start Prometheus HTTP server
    start_http_server(8000)
    logger.info("Prometheus exporter started on http://0.0.0.0:8000")

    # Load device configuration
    with open('/etc/network-monitoring/devices.yml', 'r') as f:
        config = yaml.safe_load(f)

    # Main polling loop
    poll_interval = config.get('poll_interval', 120)  # seconds

    while True:
        for device in config.get('devices', []):
            try:
                collect_device_metrics(
                    device['ip'],
                    device.get('snmp_user'),
                    device.get('auth_key'),
                    device.get('priv_key')
                )
            except Exception as e:
                logger.error(f"Error collecting from {device['ip']}: {e}")

        time.sleep(poll_interval)

if __name__ == '__main__':
    main()

---

## Device Configuration Example (devices.yml)

poll_interval: 120  # seconds

devices:
  - name: "router-01"
    ip: "192.168.1.1"
    snmp_version: 3
    snmp_user: "monitoring"
    auth_protocol: "SHA"
    auth_key: "Monitoring@Auth123"
    priv_protocol: "AES"
    priv_key: "Monitoring@Priv456"
    tags:
      site: "primary"
      type: "router"

  - name: "switch-01"
    ip: "10.0.1.1"
    snmp_version: 3
    snmp_user: "monitoring"
    auth_key: "Monitoring@Auth123"
    priv_key: "Monitoring@Priv456"
    tags:
      site: "datacenter"
      type: "switch"

---

**Script Type**: Python Network Monitoring
**Purpose**: SNMP metrics collection for Prometheus
**Dependencies**: pysnmp, prometheus-client, pyyaml
**Output**: Prometheus HTTP endpoint on port 8000
