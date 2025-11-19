# SNMP Deployment Guide

## Pre-Deployment Planning

### Requirements Assessment
```
1. Identify devices to monitor
   - Operating systems and versions
   - SNMP capability verification
   - Network accessibility confirmation

2. Assess current monitoring
   - Existing SNMP infrastructure
   - Community string policies
   - Credential management procedures

3. Plan security approach
   - SNMPv1/v2c (legacy only)
   - SNMPv3 (recommended)
   - Network segmentation for SNMP

4. Size management station
   - Device count
   - Polling frequency
   - Data retention requirements
```

### Network Design
```
Recommended Architecture:

Out-of-Band Management Network:
  Devices -----> SNMP Agent (port 161)
                    ↓
            Secure Management LAN
                    ↓
            SNMP Manager (NMS)
                (Port 161/162)

Alternative (In-Band):
  Production Network -----> SNMP Manager
                    (Separate VLAN recommended)
```

## SNMP Manager Setup

### Installation (Linux)

#### Net-SNMP Installation
```bash
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install snmp snmp-mibs-downloader snmptrapd

# RHEL/CentOS
sudo yum install net-snmp net-snmp-utils

# Verify installation
snmpget --version
snmptrapd --version

# Download MIBs
sudo download-mibs
# Update /etc/snmp/snmp.conf
# mibs : /usr/share/snmp/mibs
```

#### SNMP Configuration
```bash
# /etc/snmp/snmp.conf
# SNMP configuration

# MIB paths
mibs ALL
mibdirs /usr/share/snmp/mibs:/usr/share/snmp/mibs/iana:/usr/share/snmp/mibs/ietf
```

### Management Station Software

#### Monitoring Platform Integration
```
Option 1: Prometheus + SNMP Exporter
  - Lightweight
  - Flexible
  - Good for container environments

Option 2: Zabbix
  - Native SNMP support
  - Integrated alerting
  - Good for traditional datacenters

Option 3: Nagios/Icinga
  - Plugin-based
  - Mature ecosystem
  - Custom check capability

Option 4: Commercial (Solarwinds, Splunk)
  - Turnkey solution
  - High cost
  - Good support
```

## Device Configuration

### Cisco IOS SNMPv3

#### Step 1: Create User
```
router(config)# snmp-server group MONITORING v3 auth read MONITORING-VIEW write MONITORING-WRITE

router(config)# snmp-server user monitoring MONITORING v3 auth sha Monitoring123! priv aes 128 Monitoring456!

router(config)# snmp-server user monitoring MONITORING v3 auth sha Monitoring123! priv aes Monitoring456!
```

#### Step 2: Create Views
```
router(config)# snmp-server view MONITORING-VIEW system included
router(config)# snmp-server view MONITORING-VIEW interfaces included
router(config)# snmp-server view MONITORING-VIEW ip included
router(config)# snmp-server view MONITORING-VIEW bgp included
router(config)# snmp-server view MONITORING-VIEW snmp included

router(config)# snmp-server view MONITORING-WRITE system included
router(config)# snmp-server view MONITORING-WRITE interfaces included
```

#### Step 3: Enable Traps
```
router(config)# snmp-server enable traps
router(config)# snmp-server host 10.0.0.100 version 3 auth monitoring
router(config)# snmp-server host 10.0.0.100 version 3 priv monitoring
router(config)# snmp-server host 10.0.0.100 version 3 auth-priv monitoring

router(config)# snmp-server trap-source GigabitEthernet0/0
```

#### Step 4: Verify Configuration
```
router# show snmp
router# show snmp community
router# show snmp group
router# show snmp user
router# show snmp engineID
```

### Juniper Junos SNMPv3

#### Configuration
```
system {
    snmp {
        engine-id "8000070904" { ... }
        usm {
            local-engine {
                user monitoring {
                    authentication-protocol sha;
                    authentication-password "$9$aB..." encrypted;
                    privacy-protocol aes128;
                    privacy-password "$9$bC..." encrypted;
                }
            }
        }
        vacm {
            security-model usm {
                security-level privacy {
                    read-view MONITORING-VIEW;
                }
            }
        }
        view MONITORING-VIEW {
            oid 1.3.6.1.2.1.1 include;
            oid 1.3.6.1.2.1.2 include;
            oid 1.3.6.1.2.1.25 include;
        }
        trap-group traps {
            targets {
                10.0.0.100;
            }
            version v3;
            security-model usm;
            security-level privacy;
            user monitoring;
            source-address 192.168.1.1;
        }
    }
}
```

### Arista EOS SNMPv3

#### Configuration
```
router(config)# snmp-server local-engineid 800007E58F5EFB
router(config)# snmp-server group MONITORING v3 auth
router(config)# snmp-server user monitoring MONITORING v3 auth sha authpass priv aes privpass
router(config)# snmp-server host 10.0.0.100 version 3 auth monitoring
router(config)# snmp-server view MONITORING system included
router(config)# snmp-server view MONITORING interfaces included
```

## Manager Configuration

### Prometheus SNMP Exporter Setup

#### Download and Configure
```bash
# Install
cd /opt
sudo wget https://github.com/prometheus/snmp_exporter/releases/download/v0.24.0/snmp_exporter-0.24.0.linux-amd64.tar.gz
sudo tar xzf snmp_exporter-0.24.0.linux-amd64.tar.gz
sudo mv snmp_exporter-0.24.0.linux-amd64 snmp_exporter
cd snmp_exporter

# Generate config from MIB files
./generator/generator generate
# Output: snmp.yml
```

#### Create SNMPv3 Module
```yaml
# snmp.yml - Add custom SNMPv3 module
modules:
  if_mib_v3:
    version: 3
    max_repetitions: 25
    retries: 3
    timeout: 10s
    security_level: authPriv
    username: monitoring
    auth_protocol: SHA
    auth_password: "${SNMP_AUTH_PASS}"
    priv_protocol: AES
    priv_password: "${SNMP_PRIV_PASS}"
    get:
      - sysDescr.0
      - sysUptime.0
      - sysName.0
    walk:
      - sysDescr
      - sysUptime
      - ifName
      - ifType
      - ifSpeed
      - ifOperStatus
      - ifInOctets
      - ifOutOctets
      - ifInErrors
      - ifOutErrors
    metrics:
      - name: sysUptime
        oid: .1.3.6.1.2.1.1.3
        type: gauge
        help: System uptime in centiseconds
      - name: ifOperStatus
        oid: .1.3.6.1.2.1.2.2.1.8
        type: gauge
        indexes:
          - labelname: ifIndex
            type: gauge
        help: Interface operational status
      - name: ifInOctets
        oid: .1.3.6.1.2.1.2.2.1.10
        type: counter
        indexes:
          - labelname: ifIndex
            type: gauge
        help: Inbound octets
```

#### Run Exporter
```bash
# With environment variables
export SNMP_AUTH_PASS="Monitoring123!"
export SNMP_PRIV_PASS="Monitoring456!"

./snmp_exporter --config.file=snmp.yml

# Verify
curl http://localhost:9116/snmp?module=if_mib_v3&target=192.168.1.1
```

### Prometheus Scrape Configuration

#### Create scrape_configs
```yaml
# prometheus.yml
scrape_configs:
  - job_name: 'snmp_routers'
    static_configs:
      - targets:
          - 192.168.1.1
          - 192.168.1.2
          - 192.168.1.3
        labels:
          device_type: 'router'
          site: 'primary'
    metrics_path: /snmp
    params:
      module: [if_mib_v3]
    relabel_configs:
      - source_labels: [__address__]
        target_label: __param_target
      - source_labels: [__param_target]
        target_label: instance
      - target_label: __address__
        replacement: localhost:9116
    scrape_interval: 2m
    scrape_timeout: 30s
```

#### Test Configuration
```bash
# Verify metrics are being scraped
curl http://localhost:9090/api/v1/query?query=up{job="snmp_routers"}

# Check specific metric
curl http://localhost:9090/api/v1/query?query=sysUptime{instance="192.168.1.1"}
```

## Testing & Validation

### Manual SNMP Test

#### Get Request
```bash
snmpget -v 3 \
  -u monitoring \
  -l authPriv \
  -a SHA \
  -A "Monitoring123!" \
  -x AES \
  -X "Monitoring456!" \
  192.168.1.1 \
  sysDescr.0
```

#### Walk Request
```bash
snmpwalk -v 3 \
  -u monitoring \
  -l authPriv \
  -a SHA \
  -A "Monitoring123!" \
  -x AES \
  -X "Monitoring456!" \
  192.168.1.1 \
  ifName
```

#### Test from Manager
```bash
# From Prometheus host
snmpget -v 3 \
  -u monitoring \
  -l authPriv \
  -a SHA -A "${SNMP_AUTH_PASS}" \
  -x AES -X "${SNMP_PRIV_PASS}" \
  <device_ip> \
  1.3.6.1.2.1.1.1.0  # sysDescr

# Expected output:
# iso.org.dod.internet.mgmt.mib-2.system.sysDescr.0 = ...
```

### Metric Validation

#### Verify in Prometheus
```
1. Go to http://localhost:9090
2. Navigate to Status → Targets
3. Look for SNMP job
4. Verify "Last Scrape" is recent
5. Check "Scrape Duration" is reasonable

If failing:
  - Check target reachability: ping <device>
  - Verify credentials: snmpget command
  - Check firewall rules (UDP 161)
  - Review exporter logs
```

## Trap Configuration

### Trap Server Setup

#### snmptrapd Configuration
```bash
# /etc/snmp/snmptrapd.conf

# Authentication
authCommunity execute,net public
disableAuthorization no

# Log incoming traps
logOption f /var/log/snmp/traps.log

# Execute scripts on specific traps
traphandle default /usr/bin/logger "SNMP TRAP: %A (%B) %C %D"
traphandle .1.3.6.1.6.3.1.1.4.1.0.1.3.6.1.2.1.2.3.0 /usr/local/bin/handle_link_down.sh
```

#### Start Trap Receiver
```bash
# Start as daemon
sudo snmptrapd -c /etc/snmp/snmptrapd.conf -f -l f /var/log/snmp/traps.log

# Enable on boot
sudo systemctl enable snmptrapd
sudo systemctl start snmptrapd

# Monitor traps
sudo tail -f /var/log/snmp/traps.log
```

## Performance Tuning

### Polling Strategy

#### Baseline Configuration
```
Interface statistics: 2-5 minute polling
System metrics: 5-10 minute polling
BGP status: 5 minute polling
CPU/Memory: 1-2 minute polling
```

#### Optimize for Scale
```
If managing 100+ devices:
  1. Increase base polling interval to 5 minutes
  2. Use bulk walk (GetBulk) for efficiency
  3. Separate critical vs non-critical metrics
  4. Implement per-device polling delays
  5. Monitor exporter CPU usage
```

### Device Load

#### Verify SNMP Agent CPU
```
! Cisco IOS
show processes cpu | include snmp

! Monitor for high CPU
# If >10% CPU on SNMP agent:
  - Increase polling interval
  - Reduce number of polled OIDs
  - Enable SNMP rate limiting

snmp-server packetsize 4096
snmp-server max-ifindexes 100
```

## Monitoring & Maintenance

### Health Checks

#### Daily Checks
```bash
# 1. Verify all targets are reachable
for device in 192.168.1.1 192.168.1.2; do
  ping -c 1 $device || echo "Device $device unreachable"
done

# 2. Check for failed scrapes
grep "error" /var/log/prometheus/*.log

# 3. Verify metrics are recent
snmpget -v 3 -u monitoring -l authPriv \
  -a SHA -A <pass> -x AES -X <pass> \
  <device> sysUptime.0
```

#### Monthly Verification
```
1. Review alert logs
2. Audit SNMP access logs
3. Verify credential rotation schedule
4. Check data storage trends
5. Review performance baselines
```

### Credential Management

#### Rotation Schedule
```
SNMPv3 credentials:
  Initial setup: Change from defaults
  Rotation interval: Annually
  Emergency change: When personnel changes

Procedure:
  1. Create new credentials
  2. Distribute to NMS
  3. Configure on devices
  4. Verify functionality
  5. Remove old credentials
  6. Audit trails
```

## Implementation Checklist

- [ ] Assess device SNMP support
- [ ] Plan SNMPv3 security model
- [ ] Design MIB tree for monitoring
- [ ] Configure NMS software
- [ ] Install SNMP agents/exporters
- [ ] Configure device SNMP (SNMPv3)
- [ ] Set up trap receivers
- [ ] Test SNMP connectivity
- [ ] Validate metrics collection
- [ ] Configure monitoring/alerting
- [ ] Document procedures
- [ ] Train operations team
- [ ] Plan credential rotation
- [ ] Establish SLA for monitoring

---

**Guide Type**: Implementation
**Devices**: Cisco IOS, Juniper Junos, Arista EOS
**Security**: SNMPv3 recommended
**Typical Timeline**: 2-4 weeks
**Last Updated**: 2025-11-19
