# DNS & CDN Engineering Subskill

## Overview
Mastery of Domain Name System (DNS) and Content Delivery Networks (CDN) infrastructure for reliable, performant global services. Covers authoritative DNS, recursive resolvers, DNSSEC security, DNS load balancing, and advanced CDN optimization techniques.

## Core Competencies

### DNS Infrastructure
- **Authoritative DNS**: Multi-master DNS servers, zone delegation, SOA/NS record management
- **Recursive DNS**: Public recursive resolvers, DNS caching strategies, resolver performance
- **DNSSEC**: DNSSEC signing, validation, key rotation, chain of trust management
- **DNS Load Balancing**: Weighted DNS, geo-based routing, health checking, failover
- **Anycast DNS**: Network layer routing, global DNS distribution, BGP failover
- **Split Horizon DNS**: Internal vs. external DNS views, hybrid DNS architectures

### CDN Architecture
- **Cache Strategies**: Time-to-live (TTL) optimization, cache busting, partial caching
- **Origin Shields**: Origin protection, reduced origin load, DDoS mitigation
- **Edge Computing**: Serverless functions at edge, request transformation, regional logic
- **Cache Invalidation**: Soft vs. hard purges, selective purging, cache control headers
- **Performance**: HTTP/2 multiplexing, gzip/brotli compression, image optimization

### Security & Reliability
- **DNSSEC**: Cryptographic signing, DNSKEY and RRSIG records, KSK/ZSK key management
- **DNS Security**: DNS amplification prevention, DNS redirection attacks, rate limiting
- **CDN Security**: DDoS protection, WAF integration, bot management, SSL/TLS termination
- **Health Checking**: DNS health probes, origin health monitoring, automatic failover

### DNS Server Implementations
- **BIND 9**: Industry standard, authoritative and recursive modes, zone management
- **PowerDNS**: Modern API, master-slave replication, flexible backends
- **Unbound**: High-performance recursive resolver, DNSSEC validation
- **CoreDNS**: Kubernetes-native DNS, extensible plugins, cloud-native deployments

### CDN Provider Strategies
- **Cloudflare**: Performance, DDoS protection, WAF, Argo Smart Routing
- **Fastly**: High-performance edge, VCL customization, real-time analytics
- **AWS CloudFront**: Tight AWS integration, origin shield, Lambda@Edge
- **Akamai**: Enterprise CDN, advanced security, predictive prefetch

## Key Knowledge Areas

### DNS Architecture Patterns
1. Hierarchical DNS structure (root → TLD → authoritative)
2. Recursive resolver architecture
3. DNS caching hierarchy and TTL management
4. Anycast network implementation
5. Geo-DNS routing strategies
6. Split-horizon DNS for internal/external resolution

### DNSSEC Implementation
1. DNSSEC signing and validation workflow
2. Key hierarchy (KSK, ZSK, DS records)
3. Zone signing tools and automation
4. DNSSEC monitoring and troubleshooting
5. Key rotation strategies

### CDN Optimization
1. Cache key computation and optimization
2. Origin request reduction through intelligent caching
3. Regional cache warming and prefetch strategies
4. Bandwidth optimization techniques
5. Real-time analytics and performance monitoring
6. Edge-side scripting and request transformation

### DNS Load Balancing
1. Round-robin DNS
2. Weighted DNS routing
3. Geolocation-based routing
4. Health check based failover
5. Sticky sessions with DNS

## Practical Applications

- Setting up authoritative DNS infrastructure with redundancy
- Deploying DNSSEC for domain protection and validation
- Implementing DNS-based geographic load balancing
- Optimizing CDN caching for static and dynamic content
- Configuring origin shields for DDoS protection
- Edge function deployment for request transformation
- Multi-region CDN strategies for global availability
- DNS failover and disaster recovery architectures

## Related Skills
- Advanced Networking (Layer 2-3 protocols)
- Cloud Infrastructure (AWS, GCP, Azure)
- Network Security & Firewalls
- Load Balancing & Traffic Engineering
- DDoS Mitigation & Security
- Performance Optimization

## Tools & Technologies
- BIND 9, PowerDNS, Unbound, CoreDNS
- Cloudflare, Fastly, AWS CloudFront, Akamai
- Terraform, Ansible for Infrastructure as Code
- tcpdump, dig, nslookup for DNS troubleshooting
- HAProxy, NGINX for proxy/caching

## Learning Path
1. **Fundamentals**: DNS record types, DNS resolution process, basic DNS servers
2. **Authoritative DNS**: Zone files, SOA/NS records, master-slave replication
3. **DNSSEC**: Signing, validation, key management, troubleshooting
4. **Advanced DNS**: Anycast, geo-DNS, load balancing, split-horizon
5. **CDN Basics**: Cache strategies, TTL optimization, origin configuration
6. **CDN Advanced**: Origin shields, edge computing, request transformation
7. **Integration**: Multi-CDN strategies, failover, analytics

## Skill Validation
- Deploy multi-region authoritative DNS with health checking
- Implement DNSSEC end-to-end with proper key rotation
- Configure DNS-based load balancing with geolocation
- Optimize CDN cache hit ratio and reduce origin load
- Troubleshoot DNS resolution issues and query paths
- Design and implement global CDN strategies
