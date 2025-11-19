# Load Balancer Comparison Reference

## Platform Comparison Matrix

### Feature Comparison

| Feature | NGINX OSS | NGINX Plus | HAProxy | F5 BIG-IP | Citrix ADC | AWS ALB | AWS NLB |
|---------|-----------|-----------|---------|-----------|-----------|---------|---------|
| **Licensing** | Free | Paid | Free | Paid | Paid | Pay-per-use | Pay-per-use |
| **Architecture** | Software | Software | Software | Hardware/Software | Hardware/Software | Cloud Managed | Cloud Managed |

### Load Balancing Capabilities

| Feature | NGINX OSS | NGINX Plus | HAProxy | F5 BIG-IP | Citrix ADC | AWS ALB | AWS NLB |
|---------|-----------|-----------|---------|-----------|-----------|---------|---------|
| Round Robin | Yes | Yes | Yes | Yes | Yes | Yes | Yes |
| Least Connections | No | Yes | Yes | Yes | Yes | Yes | Yes |
| IP Hash | Yes | Yes | Yes | Yes | Yes | No | No |
| Weighted Routing | Yes | Yes | Yes | Yes | Yes | Yes | Yes |
| Response Time Based | No | Yes | Limited | Yes | Yes | No | No |
| Random | Yes | Yes | Yes | Yes | Yes | No | No |
| URI Hash | No | Yes | Yes | Yes | Yes | No | No |

### Protocol Support

| Protocol | NGINX OSS | NGINX Plus | HAProxy | F5 BIG-IP | Citrix ADC | AWS ALB | AWS NLB |
|----------|-----------|-----------|---------|-----------|-----------|---------|---------|
| HTTP | Yes | Yes | Yes | Yes | Yes | Yes | No |
| HTTPS | Yes | Yes | Yes | Yes | Yes | Yes | No |
| TCP | Limited | Yes | Yes | Yes | Yes | No | Yes |
| UDP | No | Yes | Yes | Yes | Yes | No | Yes |
| HTTP/2 | Yes | Yes | Yes | Yes | Yes | Yes | No |
| gRPC | Yes | Yes | Limited | Yes | Limited | No | No |
| WebSocket | Yes | Yes | Yes | Yes | Yes | Yes | No |
| QUIC | Experimental | Experimental | No | Yes | Yes | Experimental | No |

### Session Persistence

| Method | NGINX OSS | NGINX Plus | HAProxy | F5 BIG-IP | Citrix ADC | AWS ALB | AWS NLB |
|--------|-----------|-----------|---------|-----------|-----------|---------|---------|
| IP Hash | Yes | Yes | Yes | Yes | Yes | No | No |
| Cookie Insert | No | Yes | Yes | Yes | Yes | Yes | Yes |
| Source IP | Yes | Yes | Yes | Yes | Yes | Limited | No |
| SSL Session ID | Limited | Yes | Limited | Yes | Yes | No | No |
| Custom Hash | No | Yes | Yes | Yes | Yes | No | No |

### Advanced Features

| Feature | NGINX OSS | NGINX Plus | HAProxy | F5 BIG-IP | Citrix ADC | AWS ALB | AWS NLB |
|---------|-----------|-----------|---------|-----------|-----------|---------|---------|
| SSL Offloading | Yes | Yes | Yes | Yes | Yes | Yes | Yes |
| WAF Integration | No | Module | No | Native | Native | AWS WAF | No |
| DDoS Protection | No | Module | No | Native | Native | AWS Shield | AWS Shield |
| Compression | Yes | Yes | Yes | Yes | Yes | No | No |
| Caching | Limited | Yes | Limited | Yes | Yes | No | No |
| URL Rewriting | Basic | Yes | Yes | Yes | Yes | Limited | No |
| Health Checks | Limited | Advanced | Advanced | Advanced | Advanced | Basic | Basic |
| GSLB | No | No | No | GTM | Yes | Route53 | Route53 |
| Rate Limiting | Limited | Yes | Yes | Yes | Yes | Limited | No |

## Performance Comparison

### Throughput (Mbps)
```
AWS NLB:        1,000,000+ Mbps (1+ Tbps)
AWS ALB:        1,000+ Mbps (1 Gbps)
F5 BIG-IP:      100,000+ Mbps (100+ Gbps)
Citrix ADC:     50,000 Mbps (50+ Gbps)
A10 Thunder:    40,000+ Mbps
NGINX Plus:     50,000+ Mbps (software, auto-scaling)
NGINX OSS:      50,000+ Mbps (software, auto-scaling)
HAProxy:        40,000+ Mbps (software)
```

### Concurrent Connections
```
AWS NLB:        100,000,000+
F5 BIG-IP:      10,000,000+
AWS ALB:        1,000,000+
Citrix ADC:     10,000,000+
NGINX Plus:     1,000,000+ (per instance, auto-scale)
HAProxy:        1,000,000+ (per instance, auto-scale)
NGINX OSS:      1,000,000+ (per instance, auto-scale)
```

### SSL/TLS Transactions Per Second (TPS)
```
AWS ALB:        1,000,000+ TPS
AWS NLB:        100,000+ TPS
F5 BIG-IP:      500,000 TPS
A10 Thunder:    400,000 TPS
Citrix ADC:     300,000 TPS
NGINX Plus:     100,000+ TPS (CPU dependent)
HAProxy:        50,000+ TPS (CPU dependent)
NGINX OSS:      50,000+ TPS (CPU dependent)
```

### Latency (Added by Load Balancer)
```
AWS NLB:        <100 microseconds
F5 BIG-IP:      100-500 microseconds
Citrix ADC:     100-500 microseconds
AWS ALB:        1-10 milliseconds
NGINX Plus:     1-10 milliseconds (software)
HAProxy:        1-10 milliseconds (software)
NGINX OSS:      1-10 milliseconds (software)
```

## Cost Comparison (Annual)

### Hardware ADC (Per Appliance)

**F5 BIG-IP**:
```
Entry-level (i5600):    $50,000 - $75,000
Mid-range (i7600):      $100,000 - $150,000
High-end (i9600):       $200,000 - $500,000
Support (per year):     $10,000 - $50,000+
```

**Citrix ADC**:
```
Entry-level:            $30,000 - $50,000
Mid-range:              $75,000 - $150,000
High-end:               $150,000 - $300,000
Support (per year):     $8,000 - $40,000+
```

**A10 Thunder**:
```
Entry-level:            $20,000 - $40,000
Mid-range:              $60,000 - $120,000
High-end:               $150,000 - $250,000
Support (per year):     $5,000 - $30,000+
```

### Software-Based LB (Per Year)

**NGINX Plus**:
```
Per instance/year:      $2,500 - $5,000
Support (enterprise):   $10,000 - $50,000+
Total (10 instances):   $25,000 - $50,000
```

**HAProxy**:
```
Community:              $0
Professional support:   $5,000 - $30,000+
```

**NGINX OSS**:
```
Community:              $0
Professional support:   $5,000 - $50,000+ (third party)
```

### Cloud-Based LB (Monthly/Hourly)

**AWS ALB**:
```
LB charge:              $0.0225 per hour
LCU charge:             $0.006 per LCU-hour
Estimated monthly:      $16 - $100+ (varies by traffic)
Typical (medium app):   $50 - $150/month
```

**AWS NLB**:
```
NLB charge:             $0.0252 per hour
RLCU charge:            $0.006 per RLCU-hour
Estimated monthly:      $18 - $200+ (varies by traffic)
Typical (high performance): $100 - $300+/month
```

**Azure Load Balancer**:
```
LB charge:              $0.025 per hour
Processing charge:      $0.005 per GB
Typical (medium app):   $20 - $80/month
```

### Total Cost of Ownership (3 Years)

**High-Volume E-Commerce (Peak 100k RPS)**

```
Option 1: F5 BIG-IP HA Pair
  Hardware:             $200,000 (2 appliances)
  Support (3 years):    $120,000
  Maintenance/Power:    $30,000
  Total:                $350,000
  Per RPS/year:         $1,167

Option 2: NGINX Plus (10 instances)
  Licenses:             $150,000
  Support:              $90,000
  Infrastructure:       $50,000
  Total:                $290,000
  Per RPS/year:         $967

Option 3: AWS ALB (Auto-scaling)
  LB charges:           $100,000
  Data charges:         $80,000
  Total:                $180,000
  Per RPS/year:         $600
```

## Technology Selection Guide

### Choose NGINX OSS/Plus When:
- **Budget**: Tight (OSS is free)
- **Performance**: Need software flexibility
- **Containers**: Using Docker/Kubernetes
- **Simplicity**: Need straightforward config
- **Customization**: Want modules/flexibility
- **Cloud**: Multi-cloud or hybrid
- **Learning Curve**: Team prefers simpler platforms

**Best For**: Startups, modern apps, microservices, cloud-native

### Choose HAProxy When:
- **Performance**: Need maximum throughput per server
- **Control**: Want fine-grained ACLs and routing
- **Flexibility**: Need extensive customization
- **Learning**: Team strong in networking
- **Free Software**: Committed to open source
- **TCP**: Heavy TCP workload

**Best For**: High-performance computing, cost-conscious enterprise, TCP heavy

### Choose F5 BIG-IP When:
- **Complexity**: Enterprise application diversity
- **Features**: Need complete ADC feature set
- **Support**: Can afford premium support
- **Integration**: Existing F5 ecosystem
- **Security**: Critical security requirements
- **Compliance**: Strict audit/logging needs
- **Performance**: Absolute maximum performance needed

**Best For**: Fortune 500, financial services, telecom, mission-critical

### Choose Citrix ADC When:
- **RemoteAccess**: NetScaler Gateway integration
- **MultiSite**: Distributed data center needs
- **AppAccel**: Content acceleration important
- **Maturity**: Established platform preference
- **Enterprise**: Large organization with DC footprint

**Best For**: Established enterprises, remote work scenarios

### Choose AWS ALB When:
- **AWS**: Heavily AWS-dependent
- **Cost**: Pay-as-you-go acceptable
- **Simplicity**: Need AWS-native integration
- **Auto-scale**: Need auto-scaling
- **Multi-AZ**: Multi-AZ redundancy important
- **No Ops**: Want managed service

**Best For**: AWS-focused organizations, web applications

### Choose AWS NLB When:
- **Performance**: Ultra-low latency critical
- **Throughput**: Extreme throughput requirements
- **UDP**: Need UDP load balancing
- **Gaming**: Real-time applications
- **IoT**: Millions of connections
- **FixedIP**: Need static IP addresses

**Best For**: Gaming, IoT, real-time, extreme performance

## Decision Matrix

| Factor | Weight | OSS | Plus | HAProxy | F5 | Citrix | AWS ALB | AWS NLB |
|--------|--------|-----|------|---------|-----|---------|---------|---------|
| **Cost** | 25% | 10 | 7 | 9 | 2 | 3 | 6 | 6 |
| **Performance** | 20% | 8 | 9 | 9 | 10 | 9 | 7 | 10 |
| **Ease of Use** | 15% | 7 | 8 | 5 | 4 | 4 | 9 | 8 |
| **Features** | 20% | 6 | 8 | 8 | 10 | 10 | 6 | 5 |
| **Support** | 10% | 3 | 8 | 5 | 10 | 9 | 7 | 7 |
| **Cloud Ready** | 10% | 9 | 9 | 7 | 4 | 4 | 10 | 10 |
| **TOTAL** | 100% | 7.6 | 8.1 | 7.7 | 7.4 | 6.8 | 7.7 | 8.0 |

*Scores: 1-10 scale, 10 = best*

## Migration Paths

### From NGINX OSS to NGINX Plus
- Configuration compatible
- Minimal migration effort
- Drop-in replacement
- Same team expertise

### From HAProxy to F5 BIG-IP
- More complex
- Different management model
- Learning curve needed
- Professional services helpful

### From Hardware (F5) to Cloud (AWS ALB)
- Different paradigm
- Potential rewriting
- Scaling model changes
- Cost structure changes

### From AWS ALB to NGINX Plus
- Container deployments
- Better control
- Higher performance per dollar
- Team needs training

---

**Last Updated**: 2025-11-19
**Version**: 2.0
