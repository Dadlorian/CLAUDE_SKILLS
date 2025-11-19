# Streaming Architecture Style Guide

**Professional standards for designing scalable, resilient streaming platforms**

---

## Overview

This guide establishes architectural patterns and best practices for building production-grade streaming platforms, based on patterns used by Netflix, YouTube, Disney+, and other industry leaders.

---

## Architecture Principles

### 1. Separation of Concerns

**Origin vs Edge**
```
┌─────────────┐
│   Origin    │  - Source of truth for content
│  (Storage)  │  - Long-term content storage
│             │  - Metadata management
└──────┬──────┘
       │
┌──────▼──────┐
│  Packaging  │  - Manifest generation
│   Service   │  - Segment creation
│             │  - DRM integration
└──────┬──────┘
       │
┌──────▼──────┐
│     CDN     │  - Global distribution
│    (Edge)   │  - Caching layer
│             │  - User-facing endpoint
└─────────────┘
```

### 2. Scalability by Design

**Horizontal Scaling Pattern**
- Stateless services for easy horizontal scaling
- Distributed state in external stores (Redis, DynamoDB)
- Auto-scaling based on metrics (concurrent viewers, throughput)
- Regional isolation for blast radius containment

**Example Architecture**:
```yaml
services:
  origin:
    replicas: auto  # Scale 10-1000 based on load
    stateless: true
    storage: s3

  packager:
    replicas: auto  # Scale based on encoding queue
    state: redis-cluster

  cdn-edge:
    replicas: global  # PoPs in 100+ cities
    cache: distributed
```

### 3. Resilience & Fault Tolerance

**Multi-Region Active-Active**
```
Region A (us-east-1)          Region B (eu-west-1)
┌──────────────┐              ┌──────────────┐
│ Origin (S3)  │◄────sync────►│ Origin (S3)  │
└──────┬───────┘              └──────┬───────┘
       │                             │
┌──────▼───────┐              ┌──────▼───────┐
│  Packaging   │              │  Packaging   │
└──────┬───────┘              └──────┬───────┘
       │                             │
       └────────► CDN Global ◄───────┘
             (Anycast routing)
```

**Fallback Patterns**:
1. **CDN Fallback**: Primary CDN → Secondary CDN → Origin
2. **Quality Fallback**: 4K → 1080p → 720p → 480p
3. **Protocol Fallback**: DASH → HLS → Progressive download

### 4. Performance Optimization

**Metric-Driven Design**
```
Target SLAs:
├─ Video Start Time: < 2 seconds (p95)
├─ Rebuffer Ratio: < 0.5% of playtime
├─ Bitrate: Maximize within user bandwidth
├─ CDN Cache Hit: > 90%
└─ License Acquisition: < 200ms
```

**Optimization Techniques**:
- Parallel manifest and segment requests
- Predictive prefetching (next 2-3 segments)
- Segment size optimization (2-10 seconds)
- Aggressive edge caching with long TTLs
- Origin shield to reduce origin load

---

## Component Architectures

### Video Origin Architecture

**Pattern: Multi-Tier Storage**
```
┌─────────────────────────────────────────┐
│         HOT TIER (S3 Standard)          │
│  - Recent content (< 30 days)           │
│  - High-demand titles                   │
│  - < 1ms first-byte latency             │
└────────────┬────────────────────────────┘
             │
┌────────────▼────────────────────────────┐
│      WARM TIER (S3 Intelligent)         │
│  - Catalog content (30-365 days)        │
│  - Medium demand titles                 │
│  - Auto-tiering based on access         │
└────────────┬────────────────────────────┘
             │
┌────────────▼────────────────────────────┐
│       COLD TIER (S3 Glacier)            │
│  - Archive content (> 1 year)           │
│  - Low-demand titles                    │
│  - Cost: $0.004/GB/month                │
└─────────────────────────────────────────┘
```

**Implementation**:
```python
# S3 lifecycle policy
{
  "Rules": [
    {
      "Id": "Archive old content",
      "Status": "Enabled",
      "Transitions": [
        {"Days": 30, "StorageClass": "INTELLIGENT_TIERING"},
        {"Days": 365, "StorageClass": "GLACIER_IR"}
      ]
    }
  ]
}
```

### Packaging Service Architecture

**Pattern: Just-in-Time Packaging**
```
┌─────────────┐
│   Request   │
│  manifest   │
└──────┬──────┘
       │
┌──────▼────────────────────────────────┐
│  Packaging Service (Stateless)        │
│  ┌──────────────┐  ┌────────────┐    │
│  │ Manifest Gen │  │ Encryption │    │
│  └──────────────┘  └────────────┘    │
│  ┌──────────────┐  ┌────────────┐    │
│  │ Segmentation │  │ DRM Keys   │    │
│  └──────────────┘  └────────────┘    │
└──────┬────────────────────────────────┘
       │
┌──────▼──────┐
│ Cache (CDN) │  TTL: 3600s
└─────────────┘
```

**Best Practices**:
1. **Cache manifests aggressively**: 1-hour TTL for VOD
2. **Generate on-demand**: Don't pre-package all variants
3. **Stateless design**: Store state in DynamoDB/Redis
4. **Parallel processing**: Generate multiple bitrates concurrently

### CDN Architecture

**Pattern: Multi-CDN with Intelligent Routing**
```
┌──────────────┐
│     User     │
└──────┬───────┘
       │
┌──────▼──────────────────────────┐
│  DNS / Traffic Manager          │
│  - Geo-based routing            │
│  - Health checks                │
│  - Cost optimization            │
└──────┬──────────────────────────┘
       │
   ┌───┴────┬────────┬──────────┐
   │        │        │          │
┌──▼──┐ ┌──▼──┐ ┌───▼──┐ ┌────▼─────┐
│CDN A│ │CDN B│ │CDN C │ │ Origin   │
│90%  │ │8%   │ │2%    │ │ Shield   │
└─────┘ └─────┘ └──────┘ └──────────┘
```

**CDN Selection Criteria**:
```
Primary CDN (90%):
- Lowest latency for region
- Best cache hit ratio
- Cost-effective for volume

Secondary CDN (8%):
- Failover for primary outages
- Geographic coverage gaps
- Peak traffic overflow

Tertiary CDN (2%):
- Specialized content (live, UGC)
- Testing new providers
- Cost arbitrage opportunities
```

### DRM Architecture

**Pattern: Multi-DRM with License Server**
```
┌─────────────┐
│   Player    │
└──────┬──────┘
       │
  ┌────┴─────────────────────────┐
  │                              │
┌─▼────────┐            ┌────────▼──┐
│ Manifest │            │ License   │
│ (CENC)   │            │ Request   │
└──────────┘            └────────┬──┘
                                 │
                        ┌────────▼────────┐
                        │ License Server  │
                        │ ┌─────────────┐ │
                        │ │Auth/Entitle │ │
                        │ └─────────────┘ │
                        │ ┌─────────────┐ │
                        │ │ Key Store   │ │
                        │ └─────────────┘ │
                        │ ┌─────────────┐ │
                        │ │Multi-DRM Gen│ │
                        │ └─────────────┘ │
                        └────────┬────────┘
                                 │
                   ┌─────────────┼─────────────┐
                   │             │             │
              ┌────▼────┐  ┌─────▼────┐  ┌────▼─────┐
              │Widevine │  │ FairPlay │  │PlayReady │
              │ License │  │ License  │  │ License  │
              └─────────┘  └──────────┘  └──────────┘
```

**Implementation Considerations**:
1. **License caching**: Cache licenses client-side for offline
2. **High availability**: Multi-region license server deployment
3. **Performance**: License acquisition < 200ms (p95)
4. **Security**: Rotate encryption keys every 4-24 hours
5. **Monitoring**: Track license failures, track piracy attempts

---

## Live Streaming Architecture

### Low-Latency Live Pattern

**Target: < 3 second glass-to-glass latency**
```
┌───────────┐
│  Encoder  │  (OBS, hardware encoder)
└─────┬─────┘
      │ RTMP/SRT
┌─────▼──────────────────────────┐
│  Ingest Server                 │
│  - Accept RTMP/SRT/WebRTC      │
│  - Validate stream health      │
│  - Backup ingest endpoints     │
└─────┬──────────────────────────┘
      │
┌─────▼──────────────────────────┐
│  Real-time Transcoder          │
│  - GPU encoding (NVIDIA)       │
│  - Multiple bitrates           │
│  - Low latency mode            │
│  - Chunk size: 0.5-1s          │
└─────┬──────────────────────────┘
      │
┌─────▼──────────────────────────┐
│  Live Packager                 │
│  - LL-HLS / LL-DASH            │
│  - Chunked transfer encoding   │
│  - Manifest updates: 500ms     │
└─────┬──────────────────────────┘
      │
┌─────▼──────────────────────────┐
│  CDN Edge                      │
│  - Minimal caching (1-2 chunks)│
│  - HTTP/2 push                 │
│  - Edge origin close to users  │
└────────────────────────────────┘
```

**Key Parameters**:
```yaml
low_latency_config:
  segment_duration: 1.0s  # vs 6s for standard
  part_duration: 0.33s    # LL-HLS partial segments
  manifest_update: 0.5s   # Frequent manifest updates
  cache_ttl: 2s           # Minimal edge caching
  prefetch: 2 segments    # Reduce prefetch buffer

encoder_settings:
  preset: ultrafast       # Lower latency over quality
  tune: zerolatency      # x264 zero-latency mode
  keyframe_interval: 2s   # Frequent keyframes for ABR
  b_frames: 0            # No B-frames in low-latency
```

---

## Adaptive Bitrate Logic

### Bitrate Ladder Design

**Content-Based Approach (Netflix Pattern)**
```
Content Complexity Analysis:
┌─────────────────────────────────────┐
│ High Complexity (action, sports)    │
│ ┌─────────────────────────────────┐ │
│ │ 320p  - 400 kbps                │ │
│ │ 480p  - 900 kbps                │ │
│ │ 720p  - 2,500 kbps              │ │
│ │ 1080p - 5,000 kbps              │ │
│ │ 4K    - 16,000 kbps             │ │
│ └─────────────────────────────────┘ │
└─────────────────────────────────────┘

┌─────────────────────────────────────┐
│ Low Complexity (talking head)       │
│ ┌─────────────────────────────────┐ │
│ │ 320p  - 235 kbps                │ │
│ │ 480p  - 560 kbps                │ │
│ │ 720p  - 1,200 kbps              │ │
│ │ 1080p - 2,300 kbps              │ │
│ │ 4K    - 8,000 kbps              │ │
│ └─────────────────────────────────┘ │
└─────────────────────────────────────┘
```

**Implementation**:
```python
def generate_bitrate_ladder(content_complexity_score):
    """
    Generate per-title bitrate ladder based on content analysis.

    Args:
        content_complexity_score: 0-100 (from VMAF or ML model)

    Returns:
        List of (resolution, bitrate_kbps) tuples
    """
    base_ladder = [
        (320, 180, 300),   # (width, height, base_bitrate)
        (640, 360, 600),
        (960, 540, 1200),
        (1280, 720, 2500),
        (1920, 1080, 5000),
        (3840, 2160, 16000),
    ]

    # Adjust bitrates based on complexity
    complexity_multiplier = 0.5 + (complexity_score / 100)

    ladder = []
    for width, height, base_br in base_ladder:
        adjusted_br = int(base_br * complexity_multiplier)
        ladder.append({
            'width': width,
            'height': height,
            'bitrate': adjusted_br,
            'codec': 'h264' if height <= 1080 else 'hevc'
        })

    return ladder
```

### ABR Algorithm (Player-side)

**Throughput-Based Algorithm**
```javascript
class AdaptiveBitrateController {
  constructor(player) {
    this.player = player;
    this.throughputEstimate = null;
    this.bufferLevel = 0;
    this.currentBitrate = null;
    this.switchHistory = [];
  }

  selectBitrate(availableBitrates, downloadedBytes, downloadTime, bufferLevel) {
    // Update throughput estimate (EWMA)
    const instantThroughput = (downloadedBytes * 8) / downloadTime; // bps
    this.throughputEstimate = this.throughputEstimate
      ? 0.8 * this.throughputEstimate + 0.2 * instantThroughput
      : instantThroughput;

    this.bufferLevel = bufferLevel;

    // Conservative: Use 80% of estimated throughput
    const safeThroughput = this.throughputEstimate * 0.8;

    // Buffer-based adjustment
    let targetBitrate;
    if (bufferLevel < 10) {
      // Low buffer: aggressive downshift
      targetBitrate = safeThroughput * 0.7;
    } else if (bufferLevel > 30) {
      // High buffer: can upshift
      targetBitrate = safeThroughput * 1.0;
    } else {
      // Medium buffer: maintain
      targetBitrate = safeThroughput * 0.85;
    }

    // Find best matching bitrate
    const selectedBitrate = availableBitrates
      .filter(br => br <= targetBitrate)
      .sort((a, b) => b - a)[0] || availableBitrates[0];

    // Prevent rapid switching (debounce)
    if (this.shouldSwitch(selectedBitrate)) {
      this.currentBitrate = selectedBitrate;
      this.switchHistory.push({
        timestamp: Date.now(),
        from: this.currentBitrate,
        to: selectedBitrate,
        reason: this.getReasonCode(bufferLevel, safeThroughput)
      });
    }

    return this.currentBitrate;
  }

  shouldSwitch(newBitrate) {
    // Don't switch too frequently (min 3 seconds between switches)
    const lastSwitch = this.switchHistory[this.switchHistory.length - 1];
    if (lastSwitch && (Date.now() - lastSwitch.timestamp < 3000)) {
      return false;
    }

    // Require significant difference for upshift (reduce oscillation)
    if (newBitrate > this.currentBitrate) {
      return newBitrate / this.currentBitrate > 1.3; // 30% improvement
    }

    // Always allow downshift (prevent rebuffering)
    return true;
  }
}
```

---

## Monitoring & Observability

### Key Metrics to Track

**Video Quality of Experience (QoE)**
```
Startup Metrics:
├─ Video Start Time (VST): Time from play to first frame
├─ Time to First Byte (TTFB): Network latency
└─ Player Initialization: Player load time

Playback Metrics:
├─ Rebuffer Ratio: % of playback time spent buffering
├─ Rebuffer Count: Number of rebuffer events
├─ Rebuffer Duration: Total buffering time
├─ Average Bitrate: Mean bitrate during session
├─ Bitrate Switches: Frequency and direction
└─ Frame Drop Rate: Rendering performance

Completion Metrics:
├─ Completion Rate: % who finish content
├─ Abandonment Time: When users stop watching
└─ Exit Before Start: Play button failures
```

**Infrastructure Metrics**
```
Origin Metrics:
├─ Request Rate: Requests per second
├─ Error Rate: 4xx/5xx responses
├─ Latency: p50, p95, p99
└─ Storage Costs: $/GB/month

CDN Metrics:
├─ Cache Hit Ratio: % of requests served from cache
├─ Origin Offload: % reduction in origin requests
├─ Edge Latency: Response time at edge
├─ Bandwidth Costs: $/GB delivered
└─ Geographic Distribution: Traffic by region

Encoding Metrics:
├─ Encoding Time: Real-time factor (RTF)
├─ Queue Depth: Pending encoding jobs
├─ Quality Score: VMAF per encode
├─ Cost per Minute: Encoding costs
└─ Throughput: Hours encoded per hour
```

**Business Metrics**
```
Engagement:
├─ Watch Time: Total hours watched
├─ Concurrent Viewers: Peak and average
├─ Session Duration: Average watch time
└─ Retention: Day 1, Day 7, Day 30

Conversion:
├─ Trial to Paid: Conversion rate
├─ Churn Rate: Monthly subscription cancellations
└─ Revenue per User: ARPU

Content Performance:
├─ Top Content: Most watched titles
├─ Content Discovery: How users find content
└─ Recommendation CTR: Click-through rate
```

---

## Security Architecture

### Content Protection Layers

**Defense in Depth**
```
Layer 1: Network Security
├─ DDoS Protection (CloudFlare, AWS Shield)
├─ WAF Rules (Bot detection, rate limiting)
├─ Geographic Restrictions (IP geofencing)
└─ TLS 1.3 (Encrypted transport)

Layer 2: Authentication & Authorization
├─ Token-based Auth (JWT, OAuth)
├─ Short-lived Tokens (15-60 min expiry)
├─ Device Registration (Device limits)
└─ Session Management (Concurrent stream limits)

Layer 3: Encryption
├─ AES-128 or AES-256 Encryption
├─ Key Rotation (4-24 hour intervals)
├─ Secure Key Delivery (HTTPS only)
└─ CENC (Common Encryption)

Layer 4: DRM
├─ Widevine L1/L3
├─ FairPlay Streaming
├─ PlayReady
└─ License Policies (Rental, Subscription)

Layer 5: Forensic Watermarking
├─ Session-based Watermarking
├─ User/Device Identification
├─ Piracy Tracking
└─ Legal Evidence Collection

Layer 6: Monitoring & Response
├─ Anomaly Detection (Unusual playback patterns)
├─ Piracy Monitoring (Pirate site scanning)
├─ Device Revocation (Compromised devices)
└─ Incident Response (Takedown procedures)
```

---

## Cost Optimization Strategies

### Encoding Cost Optimization

**Intelligent Encoding**
```
Strategy 1: Per-Title Encoding
- Analyze content complexity (VMAF)
- Generate optimal bitrate ladder
- Savings: 20-50% bandwidth

Strategy 2: Codec Selection
- H.264 for compatibility (older devices)
- H.265 for bandwidth savings (50% reduction)
- AV1 for future-proofing (30% over HEVC)
- Cost trade-off: Encoding time vs bandwidth savings

Strategy 3: Resolution Optimization
- Analyze viewing patterns (80% watch on mobile)
- Prioritize 720p/1080p over 4K
- On-demand 4K encoding for popular content

Strategy 4: Storage Tiering
- Hot tier (30 days): Recent/popular content
- Warm tier (365 days): Catalog content
- Cold tier (long-term): Archive content
- Savings: 70-90% on storage costs
```

**CDN Cost Optimization**
```
Strategy 1: Multi-CDN Arbitrage
- Route to cheapest CDN per region
- Negotiate volume discounts
- Use reserved capacity for predictable traffic

Strategy 2: Origin Shield
- Reduce origin requests by 90%
- Lower origin bandwidth costs
- Improved cache hit ratios

Strategy 3: Cache Optimization
- Long TTLs for VOD content (24+ hours)
- Aggressive manifest caching
- Prefetch popular content to edge

Strategy 4: Compression
- Brotli/Gzip for manifests and APIs
- Efficient video codecs (HEVC, AV1)
- Thumbnail optimization (WebP, AVIF)
```

---

## Best Practices Checklist

### Pre-Production
- [ ] Define target QoE metrics (startup, rebuffer, quality)
- [ ] Select streaming protocol (HLS, DASH, both)
- [ ] Design bitrate ladder (fixed or per-title)
- [ ] Choose DRM system (Widevine, FairPlay, PlayReady, multi-DRM)
- [ ] Select CDN providers (primary, secondary, tertiary)
- [ ] Plan monitoring and analytics (Conviva, Mux, custom)
- [ ] Design architecture for target scale (10k, 100k, 1M CCU)

### Encoding & Packaging
- [ ] Implement per-title encoding or content-aware encoding
- [ ] Use VMAF for quality validation (target > 85)
- [ ] Generate multiple codecs (H.264, H.265, AV1)
- [ ] Create HDR versions for premium content (HDR10, Dolby Vision)
- [ ] Package with CMAF for unified format
- [ ] Implement key rotation for DRM (4-24 hours)
- [ ] Validate manifests (HLS validator, DASH validator)

### CDN & Delivery
- [ ] Configure origin shield to reduce origin load
- [ ] Set appropriate cache TTLs (manifests, segments)
- [ ] Enable HTTP/2 or HTTP/3 for performance
- [ ] Implement multi-CDN with failover
- [ ] Configure geographic routing for optimal latency
- [ ] Enable DDoS protection and WAF
- [ ] Monitor cache hit ratios (target > 90%)

### Player & Client
- [ ] Implement ABR algorithm (throughput-based or hybrid)
- [ ] Add prefetching for smooth playback
- [ ] Handle network changes gracefully
- [ ] Implement DRM integration (EME API)
- [ ] Add quality selector for user override
- [ ] Support accessibility (captions, audio description)
- [ ] Implement analytics/telemetry
- [ ] Test on device matrix (iOS, Android, Web, TV, console)

### Monitoring & Optimization
- [ ] Track QoE metrics (VST, rebuffer ratio, bitrate)
- [ ] Monitor infrastructure (CDN, origin, encoding)
- [ ] Set up alerting for critical failures
- [ ] Implement A/B testing framework
- [ ] Conduct regular load testing
- [ ] Review and optimize costs monthly
- [ ] Analyze user feedback and behavior

### Security & Compliance
- [ ] Implement token-based authentication
- [ ] Configure DRM policies correctly
- [ ] Enable forensic watermarking (optional)
- [ ] Restrict concurrent streams per account
- [ ] Implement device limits
- [ ] Monitor for piracy and abuse
- [ ] Ensure GDPR/privacy compliance
- [ ] Conduct security audits quarterly

---

## References

1. **Netflix Tech Blog**: "Per-Title Encode Optimization" (2015-2023 series)
2. **Apple**: "HLS Authoring Specification for Apple Devices" (2023)
3. **Google**: "Shaka Player Best Practices" (2023)
4. **Bitmovin**: "Video Developer Report" (Annual, 2023)
5. **Conviva**: "State of Streaming Q4 2023"
6. **AWS**: "Media Services Best Practices Guide" (2023)
7. **MPEG**: "DASH Industry Forum Implementation Guidelines"

---

**Version**: 1.0
**Last Updated**: 2025-11-19
**Maintained By**: Media & Entertainment Technology Domain
