# Network Automation with SDN

## Automation Foundation

### Automation Hierarchy

```
Level 1: Scripts (Basic)
├─ SSH automation (expect scripts)
├─ Device CLI scripts
└─ Manual triggers

Level 2: Frameworks (Intermediate)
├─ Ansible playbooks
├─ Terraform configurations
├─ Python scripts
└─ Scheduled execution

Level 3: Orchestration (Advanced)
├─ Multi-step workflows
├─ API-driven integration
├─ Event-driven automation
└─ Self-healing

Level 4: Intelligent Automation (AI/ML)
├─ ML-driven decisions
├─ Predictive actions
├─ Self-optimizing
└─ Autonomous operation
```

## Ansible for SDN

### Basic Playbook Structure

```yaml
---
- name: Deploy SDN Network Policy
  hosts: sdn_controllers
  gather_facts: yes
  vars:
    tenant: "production"
    vni: 1001
    subnet: "10.100.0.0/24"

  tasks:
    - name: Create Tenant
      community.network.onos_app:
        url: "{{ controller_url }}"
        username: "{{ username }}"
        password: "{{ password }}"
        app_name: "org.onlab.app.{{ tenant }}"
        state: present

    - name: Create Logical Network
      uri:
        url: "{{ controller_url }}/api/networks"
        method: POST
        user: "{{ username }}"
        password: "{{ password }}"
        body_format: json
        body:
          name: "{{ tenant }}-net"
          type: "VXLAN"
          vni: "{{ vni }}"
          subnet: "{{ subnet }}"
        status_code: 201
      register: network_result

    - name: Deploy Policy
      uri:
        url: "{{ controller_url }}/api/policies"
        method: POST
        user: "{{ username }}"
        password: "{{ password }}"
        body_format: json
        body:
          name: "allow-web-to-db"
          tenant: "{{ tenant }}"
          rules:
            - source: "web-tier"
              destination: "db-tier"
              protocol: "tcp"
              port: 3306
              action: "allow"
      register: policy_result

    - name: Verify Deployment
      uri:
        url: "{{ controller_url }}/api/networks/{{ network_result.json.id }}"
        method: GET
        user: "{{ username }}"
        password: "{{ password }}"
      register: verify_result
      until: verify_result.json.status == "active"
      retries: 10
      delay: 5
```

### Ansible Advantages
- Agentless (SSH-based)
- YAML syntax (human-readable)
- Idempotent (run multiple times safely)
- Multi-step workflows
- Error handling and rollback

## Terraform for SDN

### Terraform Configuration

```hcl
# Provider configuration
terraform {
  required_providers {
    onos = {
      source  = "onosproject/onos"
      version = "~> 0.3"
    }
  }
}

provider "onos" {
  url      = var.controller_url
  username = var.username
  password = var.password
}

# Variables
variable "controller_url" {
  type = string
}

variable "tenant_name" {
  type = string
}

variable "vni_id" {
  type = number
}

# Resources
resource "onos_logical_network" "tenant_network" {
  name           = var.tenant_name
  type           = "VXLAN"
  vni            = var.vni_id
  subnet         = "10.100.0.0/24"
  gateway        = "10.100.0.1"
  mtu            = 1600
}

resource "onos_security_policy" "allow_web_to_db" {
  name            = "allow-web-to-db"
  source_epg      = "web-tier"
  dest_epg        = "db-tier"
  protocol        = "tcp"
  destination_port = 3306
  action          = "allow"
  logging         = true
}

# Outputs
output "network_id" {
  value = onos_logical_network.tenant_network.id
}
```

### Terraform Advantages
- Infrastructure as Code (version controlled)
- State management
- Plan before apply
- Idempotent and reproducible
- Complex resource dependencies

## Python for SDN

### Python SDN Automation

```python
import requests
import json
from datetime import datetime

class SDNController:
    def __init__(self, url, username, password):
        self.url = url
        self.auth = (username, password)
        self.session = requests.Session()
        self.session.auth = self.auth

    def create_logical_network(self, name, vni, subnet):
        """Create a VXLAN logical network"""

        network_config = {
            "name": name,
            "type": "VXLAN",
            "vni": vni,
            "subnet": subnet,
            "gateway": str(subnet.network_address + 1)
        }

        response = self.session.post(
            f"{self.url}/api/networks",
            json=network_config
        )

        if response.status_code == 201:
            return response.json()
        else:
            raise Exception(f"Failed to create network: {response.text}")

    def deploy_security_policy(self, policy_config):
        """Deploy security policies"""

        response = self.session.post(
            f"{self.url}/api/policies",
            json=policy_config
        )

        return response.status_code == 201

    def monitor_network(self, interval=60):
        """Continuously monitor network health"""

        while True:
            try:
                # Get device status
                devices = self.session.get(f"{self.url}/api/devices").json()
                healthy = sum(1 for d in devices if d['available'])

                # Get flow statistics
                flows = self.session.get(f"{self.url}/api/flows").json()
                total_flows = len(flows)

                # Log metrics
                timestamp = datetime.now().isoformat()
                print(f"{timestamp} - Devices: {healthy}/{len(devices)}, "
                      f"Flows: {total_flows}")

                # Check for anomalies
                if healthy < len(devices) * 0.8:
                    self.alert_degraded_network()

            except Exception as e:
                print(f"Monitoring error: {e}")

            time.sleep(interval)

    def alert_degraded_network(self):
        """Send alert for degraded network"""
        # Integration with monitoring system
        # Could send to PagerDuty, Slack, Splunk, etc.
        pass

# Usage
controller = SDNController(
    url="http://10.0.0.1:8181",
    username="onos",
    password="rocks"
)

# Create network
net = controller.create_logical_network(
    name="production-net",
    vni=1001,
    subnet="10.100.0.0/24"
)

# Monitor
controller.monitor_network()
```

## API-Driven Automation

### RESTful API Workflow

```python
import requests
import json

class NetworkAutomationWorkflow:
    def __init__(self, controller_url):
        self.controller_url = controller_url
        self.session = requests.Session()

    def deploy_application_network(self, app_config):
        """Deploy complete application network"""

        steps = [
            self.create_tenant,
            self.create_networks,
            self.deploy_policies,
            self.verify_deployment
        ]

        for step in steps:
            result = step(app_config)
            if not result:
                self.rollback(app_config)
                raise Exception(f"Step {step.__name__} failed")

        return True

    def create_tenant(self, config):
        """Create tenant namespace"""
        try:
            response = self.session.post(
                f"{self.controller_url}/api/tenants",
                json={"name": config['tenant_name']}
            )
            return response.status_code == 201
        except Exception as e:
            print(f"Tenant creation failed: {e}")
            return False

    def create_networks(self, config):
        """Create logical networks for tenants"""
        for network in config['networks']:
            response = self.session.post(
                f"{self.controller_url}/api/networks",
                json=network
            )
            if response.status_code != 201:
                return False
        return True

    def deploy_policies(self, config):
        """Deploy security and QoS policies"""
        for policy in config['policies']:
            response = self.session.post(
                f"{self.controller_url}/api/policies",
                json=policy
            )
            if response.status_code != 201:
                return False
        return True

    def verify_deployment(self, config):
        """Verify all components are deployed"""
        # Check networks exist
        networks = self.session.get(
            f"{self.controller_url}/api/networks"
        ).json()

        # Check policies enforced
        policies = self.session.get(
            f"{self.controller_url}/api/policies"
        ).json()

        return len(networks) > 0 and len(policies) > 0

    def rollback(self, config):
        """Rollback on failure"""
        print(f"Rolling back {config['tenant_name']}")
        # Delete created resources
        pass

# Usage
workflow = NetworkAutomationWorkflow("http://10.0.0.1:8181")

app_config = {
    "tenant_name": "e-commerce",
    "networks": [
        {"name": "web-tier", "vni": 1001, "subnet": "10.100.0.0/24"},
        {"name": "app-tier", "vni": 1002, "subnet": "10.101.0.0/24"},
        {"name": "db-tier", "vni": 1003, "subnet": "10.102.0.0/24"}
    ],
    "policies": [
        {"source": "web", "dest": "app", "protocol": "tcp", "port": 8080},
        {"source": "app", "dest": "db", "protocol": "tcp", "port": 3306}
    ]
}

workflow.deploy_application_network(app_config)
```

## GitOps for SDN

### Git-Based Workflow

```yaml
# Directory structure
networking/
├─ base/
│  ├─ networks.yaml
│  ├─ policies.yaml
│  └─ qos.yaml
├─ tenants/
│  ├─ production/
│  │  ├─ networks.yaml
│  │  └─ policies.yaml
│  └─ development/
│     ├─ networks.yaml
│     └─ policies.yaml
└─ ci/
   └─ validate.sh

# Example: kustomization.yaml
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization

commonLabels:
  network: sdn

resources:
- base/networks.yaml
- base/policies.yaml

# Patches for specific environments
patchesStrategicMerge:
- tenant-prod-patch.yaml
```

### GitHub Actions Automation

```yaml
# .github/workflows/sdn-deploy.yml
name: SDN Deployment

on:
  push:
    branches: [main]
    paths: ['networking/**']
  pull_request:
    branches: [main]

jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2

      - name: Validate YAML
        run: |
          python -m pip install pyyaml
          python ci/validate.py networking/

  deploy:
    needs: validate
    if: github.ref == 'refs/heads/main'
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2

      - name: Deploy to SDN Controller
        env:
          CONTROLLER_URL: ${{ secrets.CONTROLLER_URL }}
          CONTROLLER_USER: ${{ secrets.CONTROLLER_USER }}
          CONTROLLER_PASS: ${{ secrets.CONTROLLER_PASS }}
        run: |
          python ci/deploy.py networking/

      - name: Run Integration Tests
        run: |
          python tests/integration_test.py
```

## Event-Driven Automation

### Event-Based Remediation

```python
import asyncio
from kafka import KafkaConsumer
import json

class EventDrivenAutomation:
    def __init__(self, broker_url, topic):
        self.consumer = KafkaConsumer(
            topic,
            bootstrap_servers=broker_url,
            value_deserializer=lambda m: json.loads(m.decode())
        )

    async def handle_events(self):
        """Process network events and take action"""

        for message in self.consumer:
            event = message.value

            if event['type'] == 'link-down':
                await self.handle_link_failure(event)
            elif event['type'] == 'device-unhealthy':
                await self.handle_device_failure(event)
            elif event['type'] == 'sla-breach':
                await self.handle_sla_breach(event)
            elif event['type'] == 'security-threat':
                await self.handle_security_threat(event)

    async def handle_link_failure(self, event):
        """Automatic failover for failed link"""
        print(f"Link down: {event['link_id']}")

        # Get alternate paths
        alt_paths = self.get_alternate_paths(event['link_id'])

        # Reroute affected flows
        for flow in event['affected_flows']:
            await self.reroute_flow(flow, alt_paths[0])

        # Alert operations
        await self.alert_operations(f"Link failure: {event['link_id']}")

    async def handle_device_failure(self, event):
        """Isolate failed device"""
        print(f"Device unhealthy: {event['device_id']}")

        # Failover to backup device
        await self.failover_to_backup(event['device_id'])

        # Migrate workloads
        await self.migrate_workloads(event['device_id'])

    async def handle_sla_breach(self, event):
        """Remediate SLA breaches"""
        print(f"SLA breach: {event['application']}")

        # Increase bandwidth
        await self.increase_bandwidth(event['application'])

        # Lower latency threshold
        await self.optimize_path(event['application'])

    async def handle_security_threat(self, event):
        """Respond to security events"""
        print(f"Security threat detected: {event['threat_type']}")

        # Block source
        await self.block_source(event['source_ip'])

        # Rate limit
        await self.rate_limit(event['source_ip'])
```

## Monitoring Integration

### Integration with Monitoring Systems

```python
class MonitoringIntegration:
    def push_to_prometheus(self, metrics):
        """Push metrics to Prometheus"""
        from prometheus_client import Gauge, start_http_server

        network_health = Gauge('sdn_network_health', 'Overall network health')
        active_flows = Gauge('sdn_active_flows', 'Number of active flows')

        network_health.set(metrics['health_score'])
        active_flows.set(metrics['flow_count'])

    def push_to_elasticsearch(self, logs):
        """Send logs to ELK stack"""
        from elasticsearch import Elasticsearch

        es = Elasticsearch(['localhost:9200'])
        for log in logs:
            es.index(index='sdn-logs', document=log)

    def create_alerts(self, alertmanager_url):
        """Configure alerts"""
        alerts = {
            'groups': [{
                'name': 'sdn',
                'rules': [
                    {
                        'alert': 'SDNControllerDown',
                        'expr': 'up{job="sdn-controller"} == 0',
                        'for': '1m'
                    },
                    {
                        'alert': 'HighFlowCount',
                        'expr': 'sdn_active_flows > 1000000',
                        'for': '5m'
                    }
                ]
            }]
        }
        return alerts
```

## Best Practices

### Automation Design
- **Start simple**: Basic playbooks before complex workflows
- **Idempotent**: Can run multiple times safely
- **Error handling**: Graceful failures with rollback
- **Logging**: Detailed logs for troubleshooting
- **Testing**: Test in lab before production

### Version Control
- Keep all configs in Git
- Code review before deployment
- Track all changes
- Audit trail maintained
- Easy rollback capability

### Scalability
- Distribute automation across controllers
- Load balance API requests
- Parallel execution where possible
- Monitor automation tool performance
- Plan for growth

---

## Tools & Frameworks Summary

| Tool | Best For | Complexity |
|------|----------|-----------|
| Ansible | Multi-step workflows | Low |
| Terraform | IaC | Medium |
| Python | Custom logic | Medium-High |
| GitOps | Version control | Medium |
| Event-driven | Real-time response | High |
