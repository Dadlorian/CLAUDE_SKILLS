# CDN Configuration Guide

**Professional standards for configuring and optimizing content delivery networks for streaming**

---

## Overview

This guide provides production-grade CDN configuration patterns based on architectures from Netflix Open Connect, Cloudflare Stream, Fastly, and Akamai. Proper CDN configuration is critical for delivering high-quality streaming experiences globally.

---

## Multi-CDN Architecture

### Primary/Secondary/Tertiary Strategy

**Recommended Setup**:
```
Traffic Distribution:
├─ Primary CDN (Cloudflare): 70% - Best global coverage
├─ Secondary CDN (Fastly): 20% - Specialized regions
├─ Tertiary CDN (AWS CloudFront): 9% - Failover
└─ Direct Origin: 1% - Testing, fallback
```

**Benefits**:
- Redundancy and failover
- Cost optimization (use cheapest per region)
- Performance optimization (best latency per geo)
- Load distribution during traffic spikes

---

## Cache Configuration

### TTL Settings

**VOD Content**:
```
Asset Type          TTL           Rationale
──────────────────────────────────────────────────────
Video Segments      7 days        Immutable content
HLS Manifests       30 seconds    Allow updates
DASH Manifests      30 seconds    Allow updates
Master Playlist     10 seconds    Bitrate changes
DRM Licenses        No cache      Security
Subtitles/Captions  7 days        Immutable
Thumbnails          30 days       Rarely change
```

**Live Content**:
```
Asset Type          TTL           Rationale
──────────────────────────────────────────────────────
Live Segments       2-6 seconds   Recent content only
Live Manifest       1 second      Frequent updates
DVR Segments        1 hour        Time-shifted viewing
```

### Cache Keys

**Optimize cache hit ratio**:
```
# Include in cache key:
- URL path
- Quality variant
- DRM type (widevine/fairplay/playready)

# Exclude from cache key:
- Session IDs
- User authentication tokens
- Analytics parameters
- Timestamp parameters
```

**Cloudflare Example**:
```javascript
// Cloudflare Worker - normalize cache keys
addEventListener('fetch', event => {
  event.respondWith(handleRequest(event.request))
})

async function handleRequest(request) {
  const url = new URL(request.url)

  // Remove query params that don't affect content
  const paramsToRemove = ['session_id', 'user_id', '_ts', 'utm_source']
  paramsToRemove.forEach(param => url.searchParams.delete(param))

  // Create cache key
  const cacheKey = new Request(url.toString(), request)

  const cache = caches.default
  let response = await cache.match(cacheKey)

  if (!response) {
    response = await fetch(request)
    event.waitUntil(cache.put(cacheKey, response.clone()))
  }

  return response
}
```

---

## Origin Shield

**Purpose**: Reduce origin load by adding a cache layer between edge and origin.

**Architecture**:
```
User Request → Edge PoP (Miss) → Origin Shield (Hit) → Response
                  ↓ (Hit)
               Cached Response
```

**Benefits**:
- 90%+ reduction in origin requests
- Improved cache hit ratio
- Lower origin bandwidth costs
- Reduced origin infrastructure needs

**Configuration** (AWS CloudFront):
```javascript
{
  "OriginShield": {
    "Enabled": true,
    "OriginShieldRegion": "us-east-1"  // Closest to origin
  }
}
```

---

## Geographic Optimization

### Regional CDN Selection

**Intelligent routing based on latency**:
```
Region              Primary CDN       Secondary CDN
────────────────────────────────────────────────────
North America       Cloudflare        Fastly
Europe              Fastly            Cloudflare
Asia-Pacific        AWS CloudFront    Cloudflare
Latin America       Cloudflare        AWS CloudFront
Middle East         Cloudflare        Akamai
Africa              Cloudflare        AWS CloudFront
```

---

## Performance Optimizations

### HTTP/2 & HTTP/3

**Enable modern protocols**:
```
Protocol Benefits:
├─ HTTP/2: Multiplexing, header compression, server push
├─ HTTP/3: QUIC, reduced latency, better mobile performance
└─ TLS 1.3: Faster handshakes, improved security
```

### Compression

**Compress text-based assets**:
```
Asset Type          Compression    Savings
──────────────────────────────────────────
M3U8 Manifests      Gzip/Brotli    70-80%
MPD Manifests       Gzip/Brotli    70-80%
JSON APIs           Gzip/Brotli    80-90%
Subtitles (VTT)     Gzip/Brotli    70-85%
Video (MP4/TS)      None           Already compressed
```

---

## Security Configuration

### DDoS Protection

**Cloudflare**:
```
- Layer 3/4 DDoS: Automatic mitigation
- Layer 7 DDoS: Rate limiting, challenge pages
- Bot protection: Identify and block malicious bots
```

### Rate Limiting

```
Resource            Limit           Action
─────────────────────────────────────────────────
License Requests    10/min/IP       Challenge
Manifest Requests   100/min/IP      Monitor
Segment Requests    1000/min/IP     Normal
API Calls           50/min/user     Block
```

### Token Authentication

**Signed URLs for content protection**:
```javascript
// Generate signed URL (AWS CloudFront)
const crypto = require('crypto');

function signUrl(url, keyPairId, privateKey, expiration) {
  const policy = JSON.stringify({
    Statement: [{
      Resource: url,
      Condition: {
        DateLessThan: { 'AWS:EpochTime': expiration }
      }
    }]
  });

  const signature = crypto
    .createSign('RSA-SHA1')
    .update(policy)
    .sign(privateKey, 'base64')
    .replace(/\+/g, '-')
    .replace(/=/g, '_')
    .replace(/\//g, '~');

  return `${url}?Policy=${encodeURIComponent(policy)}&Signature=${signature}&Key-Pair-Id=${keyPairId}`;
}
```

---

## Monitoring & Metrics

### Key CDN Metrics

```
Metric                    Target        Alert
──────────────────────────────────────────────────
Cache Hit Ratio           > 90%         < 85%
Edge Latency (p95)        < 50ms        > 100ms
Origin Requests           < 10%         > 15%
4xx Error Rate            < 1%          > 2%
5xx Error Rate            < 0.1%        > 0.5%
Bandwidth (Egress)        Monitor       Spike
```

---

**Version**: 1.0
**Last Updated**: 2025-11-19
**Maintained By**: Media & Entertainment Technology Domain
