# VPC Networking Reference

## Virtual Private Cloud (VPC) Overview

A VPC provides networking functionality for Google Cloud resources. It's a global resource that contains regional subnets, firewall rules, and routes.

## VPC Modes

### Auto Mode VPC
Automatically creates one subnet per region with predefined IP ranges.

**Characteristics**:
- Auto-created subnets: one per region
- Predefined IP ranges (10.128.0.0/9)
- Easy to set up
- Limited control

**Create Auto Mode VPC**:
```bash
gcloud compute networks create auto-vpc \
    --subnet-mode=auto \
    --bgp-routing-mode=regional
```

### Custom Mode VPC
Complete control over subnet creation and IP ranges.

**Characteristics**:
- Manual subnet creation
- Custom IP ranges
- Full control
- Production recommended

**Create Custom VPC**:
```bash
gcloud compute networks create custom-vpc \
    --subnet-mode=custom \
    --bgp-routing-mode=global
```

## Subnets

### Subnet Configuration

**Create Subnet**:
```bash
gcloud compute networks subnets create my-subnet \
    --network=custom-vpc \
    --region=us-central1 \
    --range=10.0.1.0/24 \
    --enable-private-ip-google-access \
    --enable-flow-logs
```

### Secondary IP Ranges
Additional IP ranges for pods/services (GKE) or alias IPs.

```bash
gcloud compute networks subnets create gke-subnet \
    --network=custom-vpc \
    --region=us-central1 \
    --range=10.0.0.0/24 \
    --secondary-range=pods=10.4.0.0/14 \
    --secondary-range=services=10.8.0.0/20
```

### Subnet Expansion
Expand (but not shrink) existing subnets.

```bash
gcloud compute networks subnets expand-ip-range my-subnet \
    --region=us-central1 \
    --prefix-length=20
```

### Private Google Access
Allow VMs without external IPs to reach Google APIs.

```bash
gcloud compute networks subnets update my-subnet \
    --region=us-central1 \
    --enable-private-ip-google-access
```

## IP Addressing

### Internal IP Addresses
- **Primary Range**: Main subnet CIDR (e.g., 10.0.1.0/24)
- **Secondary Ranges**: Additional IP ranges for aliases
- **Ephemeral vs Static**: Auto-assigned vs manually reserved

**Reserve Static Internal IP**:
```bash
gcloud compute addresses create my-internal-ip \
    --region=us-central1 \
    --subnet=my-subnet \
    --addresses=10.0.1.100
```

### External IP Addresses
- **Ephemeral**: Auto-assigned, changes on stop/start
- **Static**: Reserved, persists across restarts
- **Premium vs Standard Tier**: Performance vs cost

**Reserve Static External IP**:
```bash
gcloud compute addresses create my-external-ip \
    --region=us-central1 \
    --network-tier=PREMIUM
```

**Global IP** (for load balancers):
```bash
gcloud compute addresses create my-global-ip \
    --global \
    --ip-version=IPV4
```

### Bring Your Own IP (BYOIP)
Use your own public IP addresses.

```bash
gcloud compute public-advertised-prefixes create my-prefix \
    --range=203.0.113.0/24 \
    --dns-verification-ip=203.0.113.1
```

## Firewall Rules

### Firewall Basics
- **Stateful**: Return traffic automatically allowed
- **Implied Rules**: Allow egress, deny ingress
- **Priority**: 0-65535 (lower = higher priority)
- **Direction**: Ingress (incoming) or Egress (outgoing)

### Firewall Rule Components
- **Action**: Allow or Deny
- **Direction**: Ingress or Egress
- **Priority**: 0-65535
- **Target**: All instances, tags, or service accounts
- **Source/Destination**: IP ranges, tags, service accounts
- **Protocols/Ports**: TCP, UDP, ICMP, etc.

### Ingress Rules

**Allow SSH from specific IP**:
```bash
gcloud compute firewall-rules create allow-ssh \
    --network=custom-vpc \
    --allow=tcp:22 \
    --source-ranges=203.0.113.0/24 \
    --target-tags=ssh-enabled \
    --description="Allow SSH from office"
```

**Allow HTTP/HTTPS**:
```bash
gcloud compute firewall-rules create allow-web \
    --network=custom-vpc \
    --allow=tcp:80,tcp:443 \
    --source-ranges=0.0.0.0/0 \
    --target-tags=web-server
```

**Allow internal traffic**:
```bash
gcloud compute firewall-rules create allow-internal \
    --network=custom-vpc \
    --allow=tcp:0-65535,udp:0-65535,icmp \
    --source-ranges=10.0.0.0/8
```

### Egress Rules

**Deny egress to specific IPs**:
```bash
gcloud compute firewall-rules create deny-egress-malicious \
    --network=custom-vpc \
    --action=DENY \
    --direction=EGRESS \
    --rules=all \
    --destination-ranges=192.0.2.0/24 \
    --priority=100
```

**Allow egress to specific service**:
```bash
gcloud compute firewall-rules create allow-egress-db \
    --network=custom-vpc \
    --action=ALLOW \
    --direction=EGRESS \
    --rules=tcp:5432 \
    --destination-ranges=10.1.0.0/24 \
    --target-service-accounts=app@project.iam.gserviceaccount.com
```

### Hierarchical Firewall Policies
Organization/folder-level firewall rules.

```bash
# Create policy
gcloud compute firewall-policies create my-policy \
    --organization=ORG_ID

# Add rule
gcloud compute firewall-policies rules create 1000 \
    --firewall-policy=my-policy \
    --action=allow \
    --direction=INGRESS \
    --src-ip-ranges=10.0.0.0/8 \
    --layer4-configs=tcp:22
```

### Firewall Insights
Analyze firewall rule usage.

```bash
# Enable Firewall Insights
gcloud compute networks update custom-vpc \
    --enable-firewall-insights

# View shadowed rules
gcloud recommender insights list \
    --insight-type=google.compute.firewall.Insight
```

## Routes

### Route Types
1. **System-Generated**: Default, subnet routes
2. **Custom Static**: Manually created
3. **Dynamic (BGP)**: Via Cloud Router

### Default Routes
- **Default internet gateway**: 0.0.0.0/0 → internet gateway
- **Subnet routes**: Automatic for each subnet

### Custom Static Routes

**Route to next hop instance**:
```bash
gcloud compute routes create route-to-proxy \
    --network=custom-vpc \
    --destination-range=192.168.1.0/24 \
    --next-hop-instance=proxy-vm \
    --next-hop-instance-zone=us-central1-a
```

**Route to next hop IP**:
```bash
gcloud compute routes create route-to-vpn \
    --network=custom-vpc \
    --destination-range=172.16.0.0/12 \
    --next-hop-address=10.0.1.10
```

**Route to VPN tunnel**:
```bash
gcloud compute routes create route-to-on-prem \
    --network=custom-vpc \
    --destination-range=192.168.0.0/16 \
    --next-hop-vpn-tunnel=my-vpn-tunnel \
    --next-hop-vpn-tunnel-region=us-central1
```

### Route Priority
Routes with lower priority (numeric value) are preferred.

```bash
# Priority 100 (high)
gcloud compute routes create primary-route \
    --network=custom-vpc \
    --destination-range=10.1.0.0/16 \
    --next-hop-gateway=default-internet-gateway \
    --priority=100

# Priority 200 (lower)
gcloud compute routes create backup-route \
    --network=custom-vpc \
    --destination-range=10.1.0.0/16 \
    --next-hop-instance=backup-gateway \
    --priority=200
```

## Cloud NAT

### NAT for Private Instances
Allow instances without external IPs to access the internet.

**Create Cloud Router**:
```bash
gcloud compute routers create my-router \
    --network=custom-vpc \
    --region=us-central1
```

**Create NAT Gateway**:
```bash
gcloud compute routers nats create my-nat \
    --router=my-router \
    --region=us-central1 \
    --nat-all-subnet-ip-ranges \
    --auto-allocate-nat-external-ips
```

**NAT with Specific Subnets**:
```bash
gcloud compute routers nats create selective-nat \
    --router=my-router \
    --region=us-central1 \
    --nat-custom-subnet-ip-ranges=my-subnet \
    --auto-allocate-nat-external-ips
```

**NAT with Reserved IPs**:
```bash
# Reserve IPs
gcloud compute addresses create nat-ip-1 nat-ip-2 \
    --region=us-central1

# Create NAT with reserved IPs
gcloud compute routers nats create manual-nat \
    --router=my-router \
    --region=us-central1 \
    --nat-all-subnet-ip-ranges \
    --nat-external-ip-pool=nat-ip-1,nat-ip-2
```

### NAT Logging
```bash
gcloud compute routers nats update my-nat \
    --router=my-router \
    --region=us-central1 \
    --enable-logging \
    --log-filter=ALL
```

## VPC Peering

### Peering Basics
Connect two VPC networks (same or different projects).

**Characteristics**:
- Private RFC 1918 connectivity
- No overlapping IP ranges
- Transitive peering not supported
- Both networks must agree

### Create VPC Peering

**From VPC 1 to VPC 2**:
```bash
gcloud compute networks peerings create peer-vpc1-to-vpc2 \
    --network=vpc-1 \
    --peer-project=project-2 \
    --peer-network=vpc-2 \
    --auto-create-routes
```

**From VPC 2 to VPC 1**:
```bash
gcloud compute networks peerings create peer-vpc2-to-vpc1 \
    --network=vpc-2 \
    --peer-project=project-1 \
    --peer-network=vpc-1 \
    --auto-create-routes
```

### Peering with Custom Routes
```bash
gcloud compute networks peerings update peer-vpc1-to-vpc2 \
    --network=vpc-1 \
    --import-custom-routes \
    --export-custom-routes
```

## Shared VPC

### Shared VPC Architecture
Centralized network administration across multiple projects.

- **Host Project**: Contains shared VPC network
- **Service Projects**: Use host's VPC

### Setup Shared VPC

**Enable Shared VPC**:
```bash
gcloud compute shared-vpc enable HOST_PROJECT_ID
```

**Attach Service Project**:
```bash
gcloud compute shared-vpc associated-projects add SERVICE_PROJECT_ID \
    --host-project=HOST_PROJECT_ID
```

**Grant Permissions**:
```bash
gcloud projects add-iam-policy-binding HOST_PROJECT_ID \
    --member=user:admin@example.com \
    --role=roles/compute.xpnAdmin
```

**Share Specific Subnets**:
```bash
gcloud compute networks subnets set-iam-policy my-subnet \
    --region=us-central1 \
    policy.yaml
```

**policy.yaml**:
```yaml
bindings:
- members:
  - serviceAccount:SERVICE_PROJECT_NUMBER@cloudservices.gserviceaccount.com
  role: roles/compute.networkUser
```

## Private Service Connect

### PSC for Google APIs
Access Google APIs via private IPs.

**Create PSC Endpoint**:
```bash
gcloud compute addresses create psc-endpoint \
    --global \
    --purpose=PRIVATE_SERVICE_CONNECT \
    --addresses=10.0.0.100 \
    --network=custom-vpc
```

**Create Forwarding Rule**:
```bash
gcloud compute forwarding-rules create psc-rule \
    --global \
    --network=custom-vpc \
    --address=psc-endpoint \
    --target-google-apis-bundle=all-apis
```

### PSC for Published Services
Connect to third-party or internal services.

```bash
gcloud compute forwarding-rules create psc-consumer-rule \
    --region=us-central1 \
    --network=custom-vpc \
    --address=10.0.1.100 \
    --target-service-attachment=projects/PRODUCER_PROJECT/regions/us-central1/serviceAttachments/SERVICE_NAME
```

## Cloud VPN

### HA VPN (99.99% SLA)
High availability VPN with automatic failover.

**Create VPN Gateway**:
```bash
gcloud compute vpn-gateways create my-vpn-gateway \
    --network=custom-vpc \
    --region=us-central1
```

**Create Cloud Router**:
```bash
gcloud compute routers create vpn-router \
    --region=us-central1 \
    --network=custom-vpc \
    --asn=65001
```

**Create VPN Tunnel**:
```bash
gcloud compute vpn-tunnels create tunnel-1 \
    --peer-gcp-gateway=peer-vpn-gateway \
    --region=us-central1 \
    --ike-version=2 \
    --shared-secret=SECRET \
    --router=vpn-router \
    --vpn-gateway=my-vpn-gateway \
    --interface=0
```

**Configure BGP**:
```bash
gcloud compute routers add-interface vpn-router \
    --interface-name=if-tunnel-1 \
    --vpn-tunnel=tunnel-1 \
    --region=us-central1

gcloud compute routers add-bgp-peer vpn-router \
    --peer-name=bgp-peer-1 \
    --peer-asn=65002 \
    --interface=if-tunnel-1 \
    --region=us-central1
```

### Classic VPN (99.9% SLA)
Legacy VPN (single tunnel).

```bash
gcloud compute target-vpn-gateways create classic-vpn \
    --network=custom-vpc \
    --region=us-central1

gcloud compute vpn-tunnels create classic-tunnel \
    --target-vpn-gateway=classic-vpn \
    --peer-address=203.0.113.1 \
    --shared-secret=SECRET \
    --region=us-central1
```

## Cloud Interconnect

### Dedicated Interconnect
Direct physical connection (10/100 Gbps).

**Bandwidth**: 10 Gbps or 100 Gbps per connection
**SLA**: 99.9% - 99.99%
**Use Cases**: Large data transfers, hybrid cloud

### Partner Interconnect
Connection via service provider (50 Mbps - 50 Gbps).

**Bandwidth**: 50 Mbps to 50 Gbps
**SLA**: 99.9% - 99.99%
**Use Cases**: Flexible bandwidth, multiple locations

### VLAN Attachments

```bash
gcloud compute interconnects attachments create my-attachment \
    --region=us-central1 \
    --router=interconnect-router \
    --interconnect=my-interconnect \
    --vlan=100
```

## Packet Mirroring

### Mirror Traffic for Analysis
Clone packets for monitoring/security analysis.

**Create Collector Instance**:
```bash
gcloud compute instances create packet-collector \
    --zone=us-central1-a \
    --machine-type=n2-standard-4 \
    --network=custom-vpc
```

**Create Packet Mirroring Policy**:
```bash
gcloud compute packet-mirrorings create my-mirroring \
    --region=us-central1 \
    --network=custom-vpc \
    --collector-ilb=LOAD_BALANCER_URL \
    --mirrored-subnets=my-subnet
```

## VPC Flow Logs

### Enable Flow Logs
Sample and log network traffic.

```bash
gcloud compute networks subnets update my-subnet \
    --region=us-central1 \
    --enable-flow-logs \
    --logging-aggregation-interval=interval-30-sec \
    --logging-flow-sampling=0.5 \
    --logging-metadata=include-all
```

### Query Flow Logs
```sql
SELECT
  jsonPayload.connection.src_ip,
  jsonPayload.connection.dest_ip,
  jsonPayload.connection.dest_port,
  SUM(CAST(jsonPayload.bytes_sent AS INT64)) as total_bytes
FROM `project.dataset.compute_googleapis_com_vpc_flows_*`
WHERE DATE(timestamp) = CURRENT_DATE()
GROUP BY src_ip, dest_ip, dest_port
ORDER BY total_bytes DESC
LIMIT 10
```

## DNS

### Cloud DNS Zones

**Public Zone**:
```bash
gcloud dns managed-zones create public-zone \
    --dns-name=example.com. \
    --description="Public DNS zone"
```

**Private Zone**:
```bash
gcloud dns managed-zones create private-zone \
    --dns-name=internal.example.com. \
    --description="Private DNS zone" \
    --visibility=private \
    --networks=custom-vpc
```

### DNS Records

**Add A Record**:
```bash
gcloud dns record-sets create www.example.com. \
    --zone=public-zone \
    --type=A \
    --ttl=300 \
    --rrdatas=203.0.113.1
```

**Add CNAME**:
```bash
gcloud dns record-sets create alias.example.com. \
    --zone=public-zone \
    --type=CNAME \
    --ttl=300 \
    --rrdatas=www.example.com.
```

### DNSSEC
```bash
gcloud dns managed-zones update public-zone \
    --dnssec-state=on
```

### DNS Forwarding
```bash
gcloud dns policies create forward-to-onprem \
    --networks=custom-vpc \
    --enable-inbound-forwarding \
    --enable-logging
```

## Network Security

### Cloud Armor
DDoS protection and WAF.

**Create Security Policy**:
```bash
gcloud compute security-policies create my-policy

gcloud compute security-policies rules create 1000 \
    --security-policy=my-policy \
    --expression="origin.region_code == 'CN'" \
    --action=deny-403

gcloud compute security-policies rules create 2000 \
    --security-policy=my-policy \
    --expression="true" \
    --action=allow
```

**Attach to Backend Service**:
```bash
gcloud compute backend-services update my-backend \
    --security-policy=my-policy \
    --global
```

### SSL Policies
Control TLS versions and cipher suites.

```bash
gcloud compute ssl-policies create modern-policy \
    --profile=MODERN \
    --min-tls-version=1.2
```

## Best Practices

1. **Use Custom VPCs**: More control than auto mode
2. **Plan IP Ranges**: Avoid overlaps, allow for growth
3. **Enable Private Google Access**: For private instances
4. **Use Firewall Tags**: Instead of IP ranges when possible
5. **Implement Least Privilege**: Restrictive firewall rules
6. **Enable VPC Flow Logs**: For troubleshooting and security
7. **Use Hierarchical Firewall**: For organization-wide policies
8. **Leverage Shared VPC**: For centralized network management
9. **Monitor with Network Intelligence**: Use topology, metrics
10. **Document Network Design**: Maintain network diagrams
11. **Use Cloud NAT**: Instead of external IPs when possible
12. **Regular Audits**: Review firewall rules, routes
13. **Enable Logging**: Flow logs, firewall logs, NAT logs
14. **Use Service Accounts**: Instead of target tags for security
15. **Implement Defense in Depth**: Multiple security layers
