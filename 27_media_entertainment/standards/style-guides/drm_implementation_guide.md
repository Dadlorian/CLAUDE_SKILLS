# DRM Implementation Guide

**Professional standards for implementing digital rights management and content protection**

---

## Overview

This guide provides production-grade patterns for implementing DRM (Digital Rights Management) in streaming platforms, based on implementations from Netflix, Disney+, Apple TV+, and industry best practices. DRM protects premium content from piracy while ensuring seamless playback for legitimate users.

---

## DRM Systems Overview

### Industry-Standard DRM Technologies

**Widevine (Google)**
```
Security Levels:
├─ L1 (Hardware): Secure video path, TEE decryption
│  └─ Max Resolution: 4K, HDR, Dolby Vision
├─ L2 (Software): Software decryption, secure codec
│  └─ Max Resolution: 1080p, SDR only
└─ L3 (Software): Software decryption, no TEE
   └─ Max Resolution: 480p/SD (limited quality)

Supported Platforms:
├─ Android: Native support (MediaDrm API)
├─ Chrome/Chromium: Built-in CDM
├─ Firefox: OpenCDM integration
└─ Edge: Chromium-based support

License Server: Widevine License Server or custom
```

**FairPlay Streaming (Apple)**
```
Security: Hardware-backed DRM (Secure Enclave)
Max Resolution: 4K, HDR10, Dolby Vision

Supported Platforms:
├─ iOS/iPadOS: Native support (AVFoundation)
├─ macOS: Safari, native apps
├─ tvOS: Apple TV devices
└─ Safari (macOS/iOS): HLS + FairPlay

License Server: Custom FairPlay license server
Certificate: Obtained from Apple Developer Portal
```

**PlayReady (Microsoft)**
```
Security Levels:
├─ SL3000: Hardware root of trust
├─ SL2000: Software with restrictions
└─ SL150: Software, limited resolution

Supported Platforms:
├─ Windows: Native support (PlayReady Client)
├─ Xbox: Gaming consoles
├─ Smart TVs: Samsung, LG, many others
└─ Edge (legacy): Pre-Chromium versions

License Server: PlayReady License Server or custom
```

### Multi-DRM Strategy

**Coverage Matrix**
```
Platform          Primary DRM    Fallback       Notes
────────────────────────────────────────────────────────────
Chrome (Desktop)  Widevine      -              Built-in
Chrome (Android)  Widevine L1   Widevine L3    Device-dependent
Firefox           Widevine      -              OpenCDM
Safari (macOS)    FairPlay      -              HLS only
Safari (iOS)      FairPlay      -              Native
Edge (Chromium)   Widevine      PlayReady      Windows 10+
Edge (Legacy)     PlayReady     -              Pre-Chromium
Smart TV          PlayReady     Widevine       Manufacturer
Xbox/PS          PlayReady     -              Gaming consoles
```

**Implementation Decision Tree**
```
Need DRM?
├─ Yes → Need multi-DRM?
│  ├─ Yes (global platform)
│  │  └─ Implement: Widevine + FairPlay + PlayReady
│  └─ No (specific platform)
│     ├─ Apple ecosystem → FairPlay only
│     ├─ Android/Chrome → Widevine only
│     └─ Windows/Xbox → PlayReady only
└─ No → Use AES-128 or unencrypted
```

---

## Encryption Standards

### Common Encryption (CENC)

**CENC (ISO/IEC 23001-7)**

CENC allows a single encrypted file to work with multiple DRM systems, reducing storage and encoding costs.

**Benefits**:
- Single encrypted asset for all DRM systems
- Reduced storage (no per-DRM encoding)
- Faster packaging and encoding

**CENC Container**:
```
MP4 with CENC:
├─ pssh (Protection System Specific Header) boxes
│  ├─ Widevine pssh (UUID: edef8ba9...)
│  ├─ PlayReady pssh (UUID: 9a04f079...)
│  └─ FairPlay (HLS: skd:// URI in manifest)
├─ Encrypted samples (AES-128-CTR mode)
├─ Clear samples (unencrypted, if applicable)
└─ Key ID (identifies encryption key)
```

**FFmpeg CENC Packaging**:
```bash
# Create CENC encrypted MP4 (multi-DRM compatible)
MP4Box -crypt cenc_config.xml \
  -out encrypted.mp4 \
  source.mp4

# cenc_config.xml
<GPACDRM>
  <CrypTrack trackID="1" IsEncrypted="1"
    IV_size="16" saiSavedBox="senc">
    <key KID="0x1234567890abcdef1234567890abcdef"
         value="0xfedcba0987654321fedcba0987654321"/>
  </CrypTrack>
</GPACDRM>
```

### AES-128 Encryption (HLS)

**Simpler Alternative for HLS**

AES-128 is a simpler encryption method for HLS, suitable for moderate content protection.

**When to Use**:
- Non-premium content (free tiers, trailers)
- HLS-only deployments
- Budget-conscious projects
- Internal/corporate video

**HLS Manifest with AES-128**:
```m3u8
#EXTM3U
#EXT-X-VERSION:6
#EXT-X-TARGETDURATION:6
#EXT-X-KEY:METHOD=AES-128,URI="https://license.example.com/key?token=abc123",IV=0x12345678901234567890123456789012
#EXTINF:6.0,
segment_0.ts
#EXTINF:6.0,
segment_1.ts
#EXT-X-KEY:METHOD=AES-128,URI="https://license.example.com/key?token=def456",IV=0x98765432109876543210987654321098
#EXTINF:6.0,
segment_2.ts
```

**Key Rotation**: Change encryption keys periodically (every 4-24 hours) to limit piracy exposure.

---

## Widevine Implementation

### Architecture

```
┌──────────────┐
│  Video Player│
│  (Shaka/EME) │
└──────┬───────┘
       │ 1. Request license
       │
┌──────▼──────────────────────────┐
│  Application Server             │
│  - Authenticate user            │
│  - Validate entitlements        │
│  - Generate auth token          │
└──────┬──────────────────────────┘
       │ 2. Forward license request
       │    + auth token
┌──────▼──────────────────────────┐
│  Widevine License Server        │
│  - Validate token               │
│  - Check device security level  │
│  - Generate license             │
│  - Apply playback restrictions  │
└──────┬──────────────────────────┘
       │ 3. Return license
┌──────▼───────┐
│  CDM (Client)│
│  - Decrypt   │
│  - Playback  │
└──────────────┘
```

### Client Implementation (Shaka Player)

**HTML5 EME with Shaka Player**:
```javascript
// Initialize Shaka Player with Widevine DRM
const video = document.getElementById('video');
const player = new shaka.Player(video);

// Configure Widevine DRM
player.configure({
  drm: {
    servers: {
      'com.widevine.alpha': 'https://license.example.com/widevine'
    },
    advanced: {
      'com.widevine.alpha': {
        'videoRobustness': 'SW_SECURE_CRYPTO',  // or HW_SECURE_ALL for L1
        'audioRobustness': 'SW_SECURE_CRYPTO'
      }
    }
  }
});

// Modify license request (add auth token)
player.getNetworkingEngine().registerRequestFilter((type, request) => {
  if (type === shaka.net.NetworkingEngine.RequestType.LICENSE) {
    // Add authentication token
    request.headers['X-Auth-Token'] = getUserAuthToken();

    // Add custom data
    request.headers['X-User-ID'] = getUserId();
  }
});

// Handle license response
player.getNetworkingEngine().registerResponseFilter((type, response) => {
  if (type === shaka.net.NetworkingEngine.RequestType.LICENSE) {
    console.log('License acquired successfully');
  }
});

// Load manifest
player.load('https://cdn.example.com/manifest.mpd')
  .then(() => {
    console.log('Video loaded');
    video.play();
  })
  .catch((error) => {
    console.error('Error loading video:', error);
  });
```

**Android Native (ExoPlayer)**:
```kotlin
import com.google.android.exoplayer2.ExoPlayer
import com.google.android.exoplayer2.MediaItem
import com.google.android.exoplayer2.drm.DefaultDrmSessionManager
import com.google.android.exoplayer2.drm.HttpMediaDrmCallback
import com.google.android.exoplayer2.drm.DrmSessionManager
import com.google.android.exoplayer2.util.Util

// Build DRM session manager
val drmCallback = HttpMediaDrmCallback(
    "https://license.example.com/widevine",
    DefaultHttpDataSource.Factory()
)

// Add authentication headers
drmCallback.setKeyRequestProperty("X-Auth-Token", authToken)

val drmSessionManager = DefaultDrmSessionManager.Builder()
    .setUuidAndExoMediaDrmProvider(
        C.WIDEVINE_UUID,
        FrameworkMediaDrm.DEFAULT_PROVIDER
    )
    .build(drmCallback)

// Create player with DRM
val player = ExoPlayer.Builder(context)
    .setDrmSessionManager(drmSessionManager)
    .build()

// Create media item with DRM configuration
val mediaItem = MediaItem.Builder()
    .setUri("https://cdn.example.com/manifest.mpd")
    .setDrmConfiguration(
        MediaItem.DrmConfiguration.Builder(C.WIDEVINE_UUID)
            .setLicenseUri("https://license.example.com/widevine")
            .build()
    )
    .build()

player.setMediaItem(mediaItem)
player.prepare()
player.play()
```

### License Server Implementation

**Node.js Widevine License Proxy**:
```javascript
const express = require('express');
const axios = require('axios');
const app = express();

app.post('/widevine', express.raw({type: 'application/octet-stream', limit: '10mb'}), async (req, res) => {
  try {
    // Extract authentication from headers
    const authToken = req.headers['x-auth-token'];
    const userId = req.headers['x-user-id'];

    // Validate user entitlements
    const isEntitled = await checkUserEntitlement(userId, authToken);
    if (!isEntitled) {
      return res.status(403).json({error: 'Not entitled'});
    }

    // Get content ID from license request
    const contentId = extractContentId(req.body);

    // Check user's subscription level for quality limits
    const userTier = await getUserTier(userId);
    const securityLevel = userTier === 'premium' ? 'L1' : 'L3';

    // Forward to actual Widevine license server
    const licenseResponse = await axios.post(
      'https://widevine-proxy.example.com/cenc/license',
      req.body,
      {
        headers: {
          'Content-Type': 'application/octet-stream',
          'X-Content-ID': contentId,
          'X-Security-Level': securityLevel,
          'X-License-Duration': '86400'  // 24 hours
        },
        responseType: 'arraybuffer'
      }
    );

    // Log license acquisition
    await logLicenseAcquisition({
      userId,
      contentId,
      securityLevel,
      timestamp: new Date(),
      success: true
    });

    res.set('Content-Type', 'application/octet-stream');
    res.send(Buffer.from(licenseResponse.data));

  } catch (error) {
    console.error('License error:', error);

    await logLicenseAcquisition({
      userId,
      contentId,
      error: error.message,
      timestamp: new Date(),
      success: false
    });

    res.status(500).json({error: 'License acquisition failed'});
  }
});

async function checkUserEntitlement(userId, authToken) {
  // Validate JWT token
  // Check subscription status
  // Verify content access rights
  return true; // Simplified
}

app.listen(3000);
```

---

## FairPlay Streaming Implementation

### Architecture

```
┌──────────────┐
│  AVPlayer    │
│  (iOS/macOS) │
└──────┬───────┘
       │ 1. resourceLoader delegate
       │
┌──────▼──────────────────────────┐
│  Application (Swift)            │
│  - Load FairPlay certificate    │
│  - Create SPC (license request) │
│  - Request CKC (license)        │
└──────┬──────────────────────────┘
       │ 2. POST SPC + auth
       │
┌──────▼──────────────────────────┐
│  FairPlay License Server (KSM)  │
│  - Validate SPC                 │
│  - Check entitlements           │
│  - Generate CKC                 │
└──────┬──────────────────────────┘
       │ 3. Return CKC
┌──────▼───────┐
│  AVPlayer    │
│  - Decrypt   │
│  - Playback  │
└──────────────┘
```

### iOS/tvOS Implementation

**Swift AVFoundation FairPlay**:
```swift
import AVFoundation
import AVKit

class FairPlayManager: NSObject {
    private var asset: AVURLAsset?
    private let contentKeySession: AVContentKeySession
    private let applicationCertificate: Data

    init(certificateURL: URL) throws {
        // Load FairPlay application certificate
        self.applicationCertificate = try Data(contentsOf: certificateURL)

        // Create content key session
        self.contentKeySession = AVContentKeySession(keySystem: .fairPlayStreaming)

        super.init()

        contentKeySession.setDelegate(self, queue: DispatchQueue.main)
    }

    func setupPlayback(url: URL) -> AVPlayerItem {
        // Create asset
        asset = AVURLAsset(url: url)

        // Add asset to content key session
        contentKeySession.addContentKeyRecipient(asset!)

        // Create player item
        return AVPlayerItem(asset: asset!)
    }
}

extension FairPlayManager: AVContentKeySessionDelegate {
    func contentKeySession(
        _ session: AVContentKeySession,
        didProvide keyRequest: AVContentKeyRequest
    ) {
        // Handle key request
        handleContentKeyRequest(keyRequest)
    }

    private func handleContentKeyRequest(_ keyRequest: AVContentKeyRequest) {
        guard let contentKeyIdentifier = keyRequest.identifier as? String,
              let contentIdentifier = contentKeyIdentifier.replacingOccurrences(
                of: "skd://",
                with: ""
              ).data(using: .utf8) else {
            keyRequest.processContentKeyResponseError(NSError(
                domain: "FairPlay",
                code: -1,
                userInfo: [NSLocalizedDescriptionKey: "Invalid content identifier"]
            ))
            return
        }

        do {
            // Create SPC (Server Playback Context / license request)
            let spcData = try keyRequest.makeStreamingContentKeyRequestData(
                forApp: applicationCertificate,
                contentIdentifier: contentIdentifier,
                options: nil
            )

            // Request license (CKC) from server
            requestLicense(spcData: spcData, contentId: contentKeyIdentifier) { ckcData, error in
                if let ckcData = ckcData {
                    // Create content key response
                    let keyResponse = AVContentKeyResponse(
                        fairPlayStreamingKeyResponseData: ckcData
                    )
                    keyRequest.processContentKeyResponse(keyResponse)
                } else {
                    keyRequest.processContentKeyResponseError(
                        error ?? NSError(
                            domain: "FairPlay",
                            code: -2,
                            userInfo: [NSLocalizedDescriptionKey: "License request failed"]
                        )
                    )
                }
            }
        } catch {
            keyRequest.processContentKeyResponseError(error)
        }
    }

    private func requestLicense(
        spcData: Data,
        contentId: String,
        completion: @escaping (Data?, Error?) -> Void
    ) {
        // Prepare license request
        var request = URLRequest(url: URL(string: "https://license.example.com/fairplay")!)
        request.httpMethod = "POST"
        request.httpBody = spcData
        request.setValue("application/octet-stream", forHTTPHeaderField: "Content-Type")
        request.setValue(getUserAuthToken(), forHTTPHeaderField: "X-Auth-Token")
        request.setValue(contentId, forHTTPHeaderField: "X-Content-ID")

        // Send request
        URLSession.shared.dataTask(with: request) { data, response, error in
            if let error = error {
                completion(nil, error)
                return
            }

            guard let httpResponse = response as? HTTPURLResponse,
                  (200...299).contains(httpResponse.statusCode),
                  let ckcData = data else {
                completion(nil, NSError(
                    domain: "FairPlay",
                    code: -3,
                    userInfo: [NSLocalizedDescriptionKey: "Invalid server response"]
                ))
                return
            }

            completion(ckcData, nil)
        }.resume()
    }
}

// Usage
let fairPlayManager = try FairPlayManager(
    certificateURL: URL(string: "https://example.com/fairplay.cer")!
)
let playerItem = fairPlayManager.setupPlayback(
    url: URL(string: "https://cdn.example.com/master.m3u8")!
)
let player = AVPlayer(playerItem: playerItem)
player.play()
```

### License Server (FairPlay KSM)

**Node.js FairPlay License Server**:
```javascript
const express = require('express');
const crypto = require('crypto');
const app = express();

// Load FairPlay private key (from Apple)
const FAIRPLAY_PRIVATE_KEY = loadPrivateKey();
const FAIRPLAY_IV = Buffer.from('...'); // 16-byte IV
const FAIRPLAY_SECRET_KEY = Buffer.from('...'); // 32-byte secret

app.post('/fairplay', express.raw({type: 'application/octet-stream', limit: '10mb'}), async (req, res) => {
  try {
    const spcData = req.body;  // SPC from client
    const authToken = req.headers['x-auth-token'];
    const contentId = req.headers['x-content-id'];

    // Validate user entitlement
    const isEntitled = await checkUserEntitlement(authToken, contentId);
    if (!isEntitled) {
      return res.status(403).json({error: 'Not entitled'});
    }

    // Process SPC and generate CKC (license)
    const ckcData = generateCKC(spcData, contentId);

    // Log license acquisition
    await logLicenseAcquisition({
      authToken,
      contentId,
      timestamp: new Date(),
      success: true
    });

    res.set('Content-Type', 'application/octet-stream');
    res.send(ckcData);

  } catch (error) {
    console.error('FairPlay license error:', error);
    res.status(500).json({error: 'License generation failed'});
  }
});

function generateCKC(spcData, contentId) {
  // This is a simplified example
  // In production, use Apple's FairPlay Streaming Server SDK (KSM)

  // Decrypt SPC
  const decipher = crypto.createDecipheriv('aes-256-cbc', FAIRPLAY_SECRET_KEY, FAIRPLAY_IV);
  let decrypted = Buffer.concat([decipher.update(spcData), decipher.final()]);

  // Generate content key (AES-128)
  const contentKey = crypto.randomBytes(16);

  // Encrypt content key for client
  const cipher = crypto.createCipheriv('aes-256-cbc', FAIRPLAY_SECRET_KEY, FAIRPLAY_IV);
  const encryptedKey = Buffer.concat([cipher.update(contentKey), cipher.final()]);

  // Build CKC response
  const ckcData = buildCKCResponse(encryptedKey, contentId);

  return ckcData;
}

function buildCKCResponse(encryptedKey, contentId) {
  // Construct CKC (Content Key Context) response
  // This is a simplified version; production uses Apple's SDK
  return encryptedKey;
}

app.listen(3000);
```

---

## Playback Policies & Restrictions

### License Duration

**Rental Model**:
```javascript
{
  "policy": {
    "rental": {
      "playback_duration_seconds": 172800,  // 48 hours from first play
      "license_duration_seconds": 2592000    // 30 days to start watching
    }
  }
}
```

**Subscription Model**:
```javascript
{
  "policy": {
    "subscription": {
      "license_duration_seconds": 86400,     // 24 hours (renewable)
      "offline_license": true,               // Allow offline playback
      "offline_duration_seconds": 604800     // 7 days offline
    }
  }
}
```

### Output Protection (HDCP)

**HDCP Requirements**:
```
Content Type          Min HDCP Level    Max Resolution
──────────────────────────────────────────────────────
SD Content            None              480p
HD Content (720p)     HDCP 1.x          720p
FHD Content (1080p)   HDCP 2.2          1080p
4K Content            HDCP 2.2          4K
4K HDR/Dolby Vision   HDCP 2.2          4K HDR
```

**Policy Configuration** (Widevine):
```json
{
  "content_key_specs": [{
    "track_type": "VIDEO",
    "security_level": 1,
    "hdcp_restriction": {
      "hdcp_version": "HDCP_V2_2",
      "max_resolution": "3840x2160"
    }
  }]
}
```

### Concurrent Streams

**Implementation** (License Server):
```javascript
async function checkConcurrentStreams(userId, contentId) {
  // Get active sessions for user
  const activeSessions = await getActiveSessions(userId);

  // Check concurrent limit (e.g., 2 streams)
  const MAX_CONCURRENT_STREAMS = 2;

  if (activeSessions.length >= MAX_CONCURRENT_STREAMS) {
    // Check if same content is being watched
    const watchingSameContent = activeSessions.some(s => s.contentId === contentId);

    if (!watchingSameContent) {
      throw new Error('Concurrent stream limit exceeded');
    }
  }

  // Register new session
  await registerSession({
    userId,
    contentId,
    sessionId: generateSessionId(),
    startTime: new Date()
  });

  return true;
}
```

---

## Security Best Practices

### Key Management

**Key Rotation**:
```
Frequency Recommendations:
├─ Live Content: Every 4-8 hours
├─ Premium VOD: Every 24 hours
├─ Standard VOD: Every 7 days
└─ Archive Content: Every 30 days

Implementation:
- Rotate keys without re-encoding content
- Use CENC with multiple key IDs
- Maintain key history for offline playback
```

**Key Storage**:
```
DO:
✓ Store keys in HSM (Hardware Security Module)
✓ Use AWS KMS, Google Cloud KMS, Azure Key Vault
✓ Encrypt keys at rest (AES-256)
✓ Limit key access to license server only
✓ Audit all key access

DON'T:
✗ Store keys in application code
✗ Commit keys to version control
✗ Store keys in plain text
✗ Share keys across environments
```

### Token-Based Authentication

**JWT for License Requests**:
```javascript
const jwt = require('jsonwebtoken');

function generateLicenseToken(userId, contentId) {
  const payload = {
    sub: userId,
    cid: contentId,
    iat: Math.floor(Date.now() / 1000),
    exp: Math.floor(Date.now() / 1000) + (60 * 15)  // 15 min expiry
  };

  return jwt.sign(payload, process.env.JWT_SECRET, {
    algorithm: 'HS256'
  });
}

function validateLicenseToken(token) {
  try {
    const decoded = jwt.verify(token, process.env.JWT_SECRET);
    return decoded;
  } catch (error) {
    throw new Error('Invalid or expired token');
  }
}
```

### Forensic Watermarking

**Session-Based Watermarking**:
```
Purpose: Track pirated content back to source

Implementation:
1. Generate unique watermark per session
   └─ Embed user ID, session ID, timestamp

2. Embed in video (invisible to user)
   ├─ A/B variant watermarking
   ├─ Temporal watermarking (frame pattern)
   └─ Frequency domain watermarking

3. Piracy detection
   ├─ Scan pirate sites
   ├─ Extract watermark
   └─ Identify source account

Providers:
- Irdeto TraceMark
- Nagra NexGuard
- Verimatrix ViewRight
```

---

## Testing & Validation

### DRM Testing Checklist

**Pre-Production**:
- [ ] Widevine L1/L3 playback tested
- [ ] FairPlay playback tested (iOS, macOS, tvOS)
- [ ] PlayReady playback tested (Windows, Xbox)
- [ ] Multi-DRM compatibility verified
- [ ] License acquisition time < 200ms (p95)
- [ ] License persistence/offline playback tested
- [ ] Concurrent stream limits enforced
- [ ] HDCP requirements validated

**Device Matrix**:
```
Platform         Device               DRM System    Status
─────────────────────────────────────────────────────────────
iOS 15+          iPhone 12+           FairPlay      ✓ Tested
iOS 15+          iPad Pro             FairPlay      ✓ Tested
macOS 12+        MacBook Pro (M1)     FairPlay      ✓ Tested
Android 10+      Pixel 6              Widevine L1   ✓ Tested
Android 10+      Samsung S21          Widevine L1   ✓ Tested
Windows 10+      Surface Pro          PlayReady     ✓ Tested
Chrome (Desktop) Any                  Widevine      ✓ Tested
Safari (macOS)   Any                  FairPlay      ✓ Tested
Smart TV         Samsung (Tizen)      PlayReady     ✓ Tested
Smart TV         LG (webOS)           PlayReady     ✓ Tested
Xbox Series X    Gaming               PlayReady     ✓ Tested
```

### Common Issues & Solutions

**Issue: License acquisition fails (403)**
```
Cause: Authentication or entitlement failure
Solutions:
- Verify auth token is valid and not expired
- Check user subscription status
- Validate content access rights
- Review license server logs
```

**Issue: Playback works on some devices, not others**
```
Cause: DRM security level mismatch
Solutions:
- Check Widevine security level (L1 vs L3)
- Verify HDCP support on device
- Fallback to lower quality for unsupported devices
```

**Issue: Slow license acquisition (> 1s)**
```
Cause: License server latency or network issues
Solutions:
- Deploy license server in multiple regions
- Use CDN for license delivery
- Implement license caching
- Optimize database queries
```

---

## Monitoring & Analytics

### Key Metrics

**License Server Metrics**:
```
Metric                      Target      Alert Threshold
──────────────────────────────────────────────────────────
License Success Rate        > 99.5%     < 99%
License Latency (p95)       < 200ms     > 500ms
Concurrent License Requests N/A         Sudden spike
License Denials             < 0.5%      > 2%
Token Validation Failures   < 0.1%      > 1%
```

**Security Metrics**:
```
Metric                      Target      Alert Threshold
──────────────────────────────────────────────────────────
Failed Auth Attempts        < 1%        > 5%
Suspicious Activity         0           Any detection
Piracy Reports              0           Any report
Device Revocations          < 0.01%     > 0.1%
```

### Logging Example

```javascript
async function logLicenseAcquisition(event) {
  await db.licenses.insert({
    user_id: event.userId,
    content_id: event.contentId,
    drm_system: event.drmSystem,  // widevine, fairplay, playready
    security_level: event.securityLevel,  // L1, L3, etc.
    device_id: event.deviceId,
    session_id: event.sessionId,
    license_duration: event.licenseDuration,
    success: event.success,
    error: event.error,
    latency_ms: event.latency,
    timestamp: event.timestamp,
    ip_address: event.ipAddress,
    user_agent: event.userAgent
  });

  // Real-time metrics
  metrics.increment('license.requests', {
    drm: event.drmSystem,
    status: event.success ? 'success' : 'failure'
  });

  metrics.histogram('license.latency', event.latency, {
    drm: event.drmSystem
  });
}
```

---

## Cost Considerations

### DRM Licensing Costs

**Widevine**:
- License Fee: Free for streaming services
- Per-device fees: Paid by device manufacturers

**FairPlay**:
- License Fee: Free for Apple Developer Program members ($99/year)
- No per-stream fees

**PlayReady**:
- License Fee: Varies (contact Microsoft)
- Per-device licensing available

### Multi-DRM Services

**Commercial Multi-DRM Providers**:
```
Provider      Pricing Model           Approx. Cost
──────────────────────────────────────────────────────────
BuyDRM        Per-license             $0.002 - $0.01/license
EZDRM         Per-stream hour         $0.005 - $0.02/hour
Irdeto        Enterprise pricing      Contact for quote
Verimatrix    Enterprise pricing      Contact for quote
Axinom        Per-license             $0.001 - $0.005/license
```

**Cost Optimization**:
- Cache licenses client-side (reduce license requests)
- Implement license server yourself (if volume is high)
- Use multi-DRM services for lower volumes
- Negotiate volume discounts

---

## References

1. **W3C Encrypted Media Extensions (EME)**: https://www.w3.org/TR/encrypted-media/
2. **ISO CENC (23001-7)**: Common encryption standard
3. **Widevine Documentation**: https://developers.google.com/widevine
4. **FairPlay Streaming**: https://developer.apple.com/streaming/fps/
5. **PlayReady**: https://www.microsoft.com/playready/
6. **Shaka Player DRM Config**: https://github.com/shaka-project/shaka-player

---

**Version**: 1.0
**Last Updated**: 2025-11-19
**Maintained By**: Media & Entertainment Technology Domain
