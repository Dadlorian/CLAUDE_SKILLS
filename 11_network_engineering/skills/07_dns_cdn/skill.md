# DNS & CDN Engineering Subskill

## Overview
Mastery of Domain Name System (DNS) and Content Delivery Networks (CDN) infrastructure for reliable, performant global services. Covers authoritative DNS, recursive resolvers, DNSSEC security, DNS load balancing, and advanced CDN optimization techniques. This skill enables architects and engineers to design resilient global content delivery systems, optimize performance across geographic regions, and implement enterprise-grade DNS security.

## Core Competencies

### 1. DNS Infrastructure
- **Authoritative DNS Servers**: Multi-master DNS configurations, zone delegation strategies, SOA/NS record management
- **Recursive DNS Resolvers**: Public resolver deployments (Google, Cloudflare, Quad9), resolver performance optimization, query caching
- **DNSSEC Implementation**: DNSSEC signing workflows, validation chains, key rotation procedures, chain of trust verification
- **DNS Load Balancing**: Weighted DNS routing, geo-based intelligent routing, health checking mechanisms, automatic failover
- **Anycast DNS**: Anycast network routing principles, global DNS distribution architectures, BGP failover strategies
- **Split Horizon DNS**: Internal vs. external DNS views, hybrid DNS architectures for dual-view deployments

### 2. CDN Architecture & Design
- **Cache Strategies**: Time-to-live (TTL) optimization, cache busting techniques, partial object caching, purge strategies
- **Origin Shield**: Origin server protection, request aggregation, reduced origin load, DDoS mitigation at origin
- **Edge Computing**: Serverless functions at edge (Lambda@Edge, Workers), request transformation, regional business logic execution
- **Cache Invalidation**: Soft vs. hard purges, selective purging, cache control headers (Cache-Control, ETag, Last-Modified)
- **Performance Optimization**: HTTP/2 multiplexing, gzip/brotli compression, image optimization, adaptive bitrate streaming
- **Multi-Tier Caching**: Regional cache layers, intelligent cache hierarchy, cache coherency management

### 3. Security & Reliability

#### DNSSEC (DNS Security Extensions)
- **Cryptographic Signing**: DNSSEC signing processes, DNSKEY and RRSIG records, algorithm selection (RSA, ECDSA)
- **Key Management**: KSK (Key Signing Key) and ZSK (Zone Signing Key) hierarchy, DS records, key rotation strategies
- **Validation Workflows**: DNSSEC validation chain, trust anchors, NSEC and NSEC3 record handling
- **Monitoring & Troubleshooting**: DNSSEC status monitoring, signature expiration tracking, validation failure analysis

#### DNS Security
- **Attack Mitigation**: DNS amplification attack prevention, DNS redirection attack detection, DNS cache poisoning prevention
- **Rate Limiting**: Per-client rate limits, recursive query rate limiting, DDoS detection thresholds
- **Access Controls**: Query access lists, recursive resolver restrictions, zone transfer controls

#### CDN Security
- **DDoS Protection**: Layer 3/4 DDoS mitigation, Layer 7 attack detection, automatic traffic scrubbing
- **WAF Integration**: Web application firewall rules at edge, OWASP protection, custom rule implementation
- **Bot Management**: Bot detection and blocking, good bot allowlisting, challenge-based verification
- **SSL/TLS Termination**: Client-facing SSL/TLS, origin SSL/TLS, certificate management automation

### 4. DNS Server Implementations

#### BIND 9
- **Authoritative Configuration**: Zone file management, DNSSEC signing setup, view-based configurations
- **Recursive Resolver Setup**: Forwarding rules, conditional forwarding, response rate limiting
- **Advanced Features**: TSIG for secure transfers, ACL management, logging configurations

#### PowerDNS
- **API-Driven Management**: Modern API for zone management, backend database integration
- **Master-Slave Replication**: Efficient zone replication, change-driven notification
- **Flexible Backends**: SQL-based backends, API backends, pipe backends for custom logic

#### Unbound
- **High-Performance Caching**: Optimized caching algorithms, memory efficiency
- **DNSSEC Validation**: Built-in DNSSEC validation, trust anchor management
- **Custom Configuration**: Access lists, forwarding policies, logging options

#### CoreDNS
- **Kubernetes-Native DNS**: ServiceDiscovery, headless services, external DNS integration
- **Extensible Plugin Architecture**: Custom DNS logic via plugins, middleware chains
- **Cloud-Native Deployments**: Container-based deployment, load balancing across replicas

### 5. CDN Provider Strategies

#### Cloudflare CDN
- **Performance Features**: Argo Smart Routing, Tiered Cache, Smart Cache
- **Security**: DDoS protection, WAF, Bot Management
- **Edge Computing**: Cloudflare Workers for serverless computing, request transformation

#### Fastly CDN
- **VCL (Varnish Configuration Language)**: Custom edge logic programming, request/response modification
- **Real-Time Analytics**: Detailed traffic metrics, performance insights, log streaming
- **API-First Architecture**: Programmatic cache control, configuration management

#### AWS CloudFront
- **AWS Integration**: Seamless integration with S3, ELB, EC2, API Gateway
- **Origin Shield**: Additional cache layer before origin servers, DDoS mitigation
- **Lambda@Edge**: CloudFront-triggered Lambda for request/response processing

#### Akamai CDN
- **Enterprise Features**: Advanced security, predictive prefetch, bandwidth optimization
- **Media Delivery**: Optimized streaming for video/large files, protocol optimization
- **DDoS & Security**: Enterprise-grade DDoS protection, advanced threat detection

### 6. Advanced DNS Concepts

#### Anycast Implementation
- **Network Topology**: Anycast routing principles, BGP advertisement from multiple locations
- **Distributed Authority**: Multiple authoritative servers announcing same prefix
- **Failover Mechanisms**: Automatic routing to nearest healthy anycast node

#### GeoDNS (Geographic DNS)
- **Location-Based Routing**: IP geolocation databases, geographic routing policies
- **Latency-Based Routing**: Measuring latency to multiple endpoints, steering to optimal location
- **Health-Aware Routing**: Combining geolocation with health checks for intelligent failover

#### DNS Performance Optimization
- **Query Response Time**: Minimizing response latency, optimizing TTL values
- **Caching Strategies**: Cache hit ratio optimization, cache warming techniques
- **Recursive Query Optimization**: Forwarding strategies, cache validation

### 7. CDN Optimization Techniques

#### Cache Key Optimization
- **Dynamic Content**: Cache key construction for dynamic content, query parameter handling
- **Cache Segmentation**: User-specific caching, device-specific content variants
- **Cache Collision**: Avoiding cache collisions, cache key uniqueness strategies

#### Origin Request Reduction
- **Intelligent Caching**: Predictive prefetching, cache warming at off-peak hours
- **Compression**: Gzip/Brotli compression strategies, compression level tuning
- **Image Optimization**: Responsive images, format negotiation (WebP, HEIC), quality optimization

#### Regional Cache Strategy
- **Cache Warm-up**: Pre-populating edge caches with popular content
- **Regional Hotspots**: Identifying and optimizing for high-traffic regions
- **Cache Coherency**: Invalidation propagation, eventual consistency handling

### 8. Integration Patterns

#### Multi-CDN Strategy
- **Primary/Secondary CDN**: Failover between CDN providers, traffic steering
- **Content Distribution**: Splitting content across CDNs for optimization
- **Cost Optimization**: Using multiple CDNs for bandwidth arbitrage

#### DNS & Load Balancer Integration
- **Global Load Balancing**: Combining DNS routing with application load balancers
- **Session Affinity**: Maintaining user sessions across global deployment
- **Disaster Recovery**: Failover between data centers via DNS changes

#### Cloud Provider Integration
- **AWS Route 53**: Health checks, failover routing, geolocation routing
- **Azure Traffic Manager**: Endpoint monitoring, priority and weighted routing
- **GCP Cloud DNS**: Managed authoritative DNS, integration with GCP services

### 9. Monitoring & Troubleshooting

#### DNS Monitoring
- **Query Monitoring**: Query volume tracking, query type distribution analysis
- **Response Time Monitoring**: Latency SLIs, end-user perceived latency
- **DNSSEC Validation**: DNSSEC signature expiration tracking, validation failure rates

#### CDN Monitoring
- **Cache Metrics**: Cache hit ratio, cache size utilization, eviction rates
- **Performance Metrics**: Time to first byte (TTFB), content delivery time, bandwidth utilization
- **Origin Health**: Origin response times, origin error rates, origin availability

#### Troubleshooting Tools
- **DNS Tools**: dig, nslookup, dnstrace, DNS query logging and analysis
- **CDN Tools**: CDN provider analytics dashboards, real-time traffic visualization
- **Network Tools**: tcpdump for packet capture, Wireshark for protocol analysis

### 10. Deployment & Operations

#### Authoritative DNS Deployment
- **Redundancy**: Multi-region DNS server deployment, anycast distribution
- **High Availability**: DNS server failover, automated replica synchronization
- **Capacity Planning**: Query load forecasting, server capacity sizing

#### CDN Deployment
- **Content Distribution**: Automated content synchronization to edge locations
- **Configuration Management**: Infrastructure as code for CDN configuration (Terraform)
- **Change Management**: Blue-green deployment, gradual rollout of CDN changes

#### Disaster Recovery
- **DNS Failover**: Automated failover between data centers via DNS changes
- **CDN Redundancy**: Multiple origin servers, cross-CDN failover
- **Recovery Time Objective (RTO)**: Minimizing downtime during outages

## Technology Stack

### DNS Servers
- BIND 9, PowerDNS, Unbound, CoreDNS, Amazon Route 53, Azure DNS, Google Cloud DNS

### CDN Providers
- Cloudflare, Fastly, AWS CloudFront, Akamai, Vimeo, Bunnycdn, Sucuri CDN

### Protocols
- DNS, DNSSEC, HTTP/2, QUIC, UDP, TCP

### Development & Automation
- Terraform, Ansible for infrastructure automation
- Python, Go for custom DNS/CDN tooling
- Docker/Kubernetes for containerized DNS servers

### Tools
- Dig, nslookup, host (DNS diagnostics)
- tcpdump, tshark (packet capture)
- Wireshark (protocol analysis)
- curl, wget (content delivery testing)

## Key Knowledge Areas

### DNS Architecture Patterns
1. Hierarchical DNS structure (root → TLD → authoritative)
2. Recursive resolver architecture and query flow
3. DNS caching hierarchy and TTL management principles
4. Anycast network implementation for global distribution
5. Geo-DNS routing strategies and implementation
6. Split-horizon DNS for internal/external resolution separation

### DNSSEC Implementation
1. DNSSEC signing and validation workflow end-to-end
2. Key hierarchy (KSK, ZSK, DS records) management
3. Zone signing tools and automation (dnssec-signzone, ldns-signzone)
4. DNSSEC monitoring and troubleshooting techniques
5. Key rotation strategies and best practices
6. NSEC/NSEC3 record handling and zone enumeration prevention

### CDN Optimization
1. Cache key computation and optimization strategies
2. Origin request reduction through intelligent caching
3. Regional cache warming and prefetch strategies
4. Bandwidth optimization and compression techniques
5. Real-time analytics and performance monitoring
6. Edge-side scripting and request transformation

### DNS Load Balancing
1. Round-robin DNS basics and limitations
2. Weighted DNS routing for capacity-based distribution
3. Geolocation-based routing implementation
4. Health check based failover mechanisms
5. Sticky sessions with DNS using response codes
6. Multi-region failover orchestration

## Practical Applications

- Designing and deploying authoritative DNS infrastructure with redundancy
- Implementing DNSSEC for domain protection and validation
- Building DNS-based geographic load balancing for global applications
- Optimizing CDN caching for static and dynamic content delivery
- Configuring origin shields for DDoS protection and origin offloading
- Deploying edge functions for request transformation and personalization
- Implementing multi-region CDN strategies for global availability
- Designing DNS failover and disaster recovery architectures

## Real-World Use Cases

### E-commerce & Retail
- Global CDN for fast product catalog delivery
- Geo-routed checkout systems for reduced latency
- DDoS protection during peak shopping periods

### Media & Streaming
- Video CDN for adaptive bitrate streaming
- Global DNS load balancing for content distribution
- Origin shield for protection against traffic spikes

### SaaS Applications
- Multi-region application deployment with DNS steering
- API gateway protection with DDoS mitigation
- DNSSEC for domain authenticity and security

### Enterprise & Corporate
- Hybrid DNS for internal/external service resolution
- Secure DNS with DNSSEC for compliance requirements
- Global CDN for internal content distribution

## Related Skills
- Advanced Networking (Layer 2-3 protocols)
- Cloud Infrastructure (AWS, GCP, Azure)
- Network Security & Firewalls
- Load Balancing & Traffic Engineering
- DDoS Mitigation & Security
- Performance Optimization & Tuning
- DevOps & Infrastructure as Code

## Tools & Technologies
- BIND 9, PowerDNS, Unbound, CoreDNS
- Cloudflare, Fastly, AWS CloudFront, Akamai, Vimeo CDN
- Terraform, Ansible for Infrastructure as Code
- tcpdump, dig, nslookup, host for DNS troubleshooting
- HAProxy, NGINX for proxy/caching
- Elasticsearch/Kibana for CDN analytics
- Prometheus/Grafana for monitoring

## Learning Path
1. **Fundamentals**: DNS record types, DNS resolution process, basic DNS servers
2. **Authoritative DNS**: Zone files, SOA/NS records, master-slave replication, zone transfers
3. **Recursive Resolvers**: Caching strategies, performance optimization, security
4. **DNSSEC**: Signing, validation, key management, troubleshooting, monitoring
5. **Advanced DNS**: Anycast, geo-DNS, load balancing, split-horizon configurations
6. **CDN Basics**: Cache strategies, TTL optimization, origin configuration
7. **CDN Advanced**: Origin shields, edge computing, request transformation, security
8. **Integration**: Multi-CDN strategies, failover, analytics, disaster recovery

## Skill Validation
- Deploy multi-region authoritative DNS with health checking and failover
- Implement DNSSEC end-to-end with proper key rotation and monitoring
- Configure DNS-based load balancing with geolocation and health-aware routing
- Optimize CDN cache hit ratio and reduce origin server load by 50%+
- Troubleshoot DNS resolution issues and trace query paths through all DNS layers
- Design and implement global CDN strategies for multi-region applications
- Implement DNSSEC validation and monitoring with alerting
- Configure and manage origin shields for DDoS protection

## Performance Targets
- DNS Query Response Time: <50ms (p99) globally
- CDN Cache Hit Ratio: >80% for static content
- Origin Shield Efficiency: >90% request aggregation
- DNSSEC Validation: 99.99% validation success rate
