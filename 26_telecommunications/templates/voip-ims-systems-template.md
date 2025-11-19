# VoIP and IMS Systems Implementation Template

## 1. IMS (IP Multimedia Subsystem) Architecture

### 1.1 Core IMS Components

#### Call Session Control Function (CSCF)

```
CSCF Types and Roles:

┌─────────────────────────────────────────────────────┐
│              IMS Network Core                        │
├─────────────────────────────────────────────────────┤
│                                                      │
│  P-CSCF (Proxy)          S-CSCF (Serving)          │
│  ├─ UE Authentication    ├─ Registration            │
│  ├─ Encryption           ├─ User Profile            │
│  └─ Compression          └─ Session Control         │
│                                                      │
│  I-CSCF (Interrogating)  AS (Application Server)   │
│  ├─ Routing              ├─ IMS Services            │
│  ├─ Discovery            └─ VAS Processing          │
│  └─ Load Balancing                                  │
│                                                      │
└─────────────────────────────────────────────────────┘
```

#### Home Subscriber Server (HSS)

```yaml
HSS Database Structure:
  Master User Database:
    - User Identity (IMPI, IMPU)
    - Authentication Vector (AV)
    - Service Profile
    - Subscriber Status
    - Charging Info
    - Access Control Lists

Key Interfaces:
  Cx Interface: CSCF ← → HSS (User Data)
  Dz Interface: CSCF ← → HSS (Charging)
```

#### Application Server (AS)

```yaml
AS Functions:
  IMS Services:
    - Presence and Availability
    - Group Communications
    - Messaging Services
    - Conferencing
    - Emergency Services
    - Voicemail
    - Call Forwarding
    - Rich Communication Services (RCS)
```

### 1.2 IMS Registration Flow

```
User ← → P-CSCF ← → I-CSCF ← → S-CSCF ← → HSS
  ↓        ↓           ↓         ↓        ↓
 REGISTER  (forward)  (query)  (auth)   (validate)
  ↓        ↓           ↓         ↓        ↓
 401  ← (auth challenge) ← (from HSS)
  ↓
 REGISTER + Auth
  ↓
 200 OK (registration success)
  ↓
 Access-Network-Address Header, Via header populated
```

---

## 2. SIP Protocol Fundamentals

### 2.1 SIP Message Structure

```
INVITE sip:bob@biloxi.com SIP/2.0
Via: SIP/2.0/TLS pc33.atlanta.com:5061;branch=z9hG4bK776asdhds
Max-Forwards: 70
To: Bob <sip:bob@biloxi.com>
From: Alice <sip:alice@atlanta.com>;tag=1928301774
Call-ID: a84b4c76e66710@pc33.atlanta.com
CSeq: 314159 INVITE
Contact: <sip:alice@pc33.atlanta.com>
Allow: INVITE, ACK, BYE, CANCEL, OPTIONS, PRACK, SUBSCRIBE, NOTIFY
Supported: 100rel, timer, replaces
Require: 100rel
Content-Type: application/sdp
Content-Length: 142

[SDP Body]
```

### 2.2 SIP Call Flow Ladder Diagram

```
Alice                  P-CSCF               S-CSCF                 Bob
  |                      |                     |                     |
  |---INVITE----------→  |-----INVITE------→  |-----INVITE-------→  |
  |                      |                     |                     |
  |                      |                     |  ←-----100 Trying---|
  | ←--------100---------|                     |                     |
  |                      |                     | ←-----180 Ringing---|
  | ←--------180---------|←---180 Ringing------|                     |
  |                      |                     |                     |
  |                      |                     | ←-----200 OK--------|
  | ←--------200---------|←-----200 OK---------|                     |
  |                      |                     |                     |
  |---ACK---------------→|-----ACK----------→ |-----ACK----------→  |
  |                      |                     |                     |
  |◄═══RTP Media Stream═══════════════════════════════════════════►  |
  |                      |                     |                     |
  |---BYE---------------→|-----BYE----------→ |-----BYE----------→  |
  |                      |                     |                     |
  | ←--------200---------|←-----200 OK---------|←-----200 OK--------|
  |                      |                     |                     |
```

### 2.3 SIP Methods and Response Codes

```yaml
SIP Request Methods:
  Requests:
    - INVITE: Initiate session
    - ACK: Confirm final response
    - BYE: Terminate session
    - CANCEL: Cancel pending request
    - REGISTER: Register user agent
    - OPTIONS: Query capabilities
    - PRACK: Provisional acknowledgment
    - SUBSCRIBE: Subscribe to events
    - NOTIFY: Notify of events
    - MESSAGE: Send instant message
    - PUBLISH: Publish event state
    - INFO: Send call information

Response Codes:
  1xx - Provisional:
    100 Trying, 180 Ringing, 181 Call Is Being Forwarded
  2xx - Success:
    200 OK, 202 Accepted, 204 No Notification
  3xx - Redirection:
    300 Multiple Choices, 301 Moved Permanently
  4xx - Client Error:
    400 Bad Request, 401 Unauthorized, 403 Forbidden, 404 Not Found
  5xx - Server Error:
    500 Server Internal Error, 503 Service Unavailable
  6xx - Global Failure:
    600 Busy Everywhere, 603 Decline, 606 Not Acceptable
```

---

## 3. VoLTE (Voice over LTE) Implementation

### 3.1 VoLTE Architecture

```yaml
VoLTE Network Components:
  RAN (Radio Access Network):
    - eNodeB: Enhanced Node B
    - eHRPD: EvDO HSPA+ Fallback

  EPC (Evolved Packet Core):
    - MME: Mobility Management Entity
    - SGW: Serving Gateway
    - PGW: PDN Gateway

  IMS Core:
    - P/I/S-CSCF
    - HSS
    - AS (for VoLTE services)

  Media Servers:
    - MGCF: Media Gateway Control Function
    - MGW: Media Gateway

VoLTE Call Setup Flow:
  1. UE requests LTE connection
  2. EPC establishes bearer path
  3. IMS registration via P-CSCF
  4. INVITE sent to called party
  5. Voice bearer established
  6. RTP media flows (typically G.711, AMR-WB, EVS)
```

### 3.2 VoLTE QoS Configuration

```yaml
VoLTE Bearers:
  Default Bearer:
    QCI: 5 (GBR)
    Priority: 1
    Bandwidth: 128 Kbps DL / 128 Kbps UL
    Delay: ≤ 150 ms
    Loss Rate: ≤ 10^-2
    Functions: Signaling

  Voice Bearer (Primary):
    QCI: 1 (GBR)
    Priority: 2
    Bandwidth: 256 Kbps DL / 256 Kbps UL
    Delay: ≤ 150 ms
    Loss Rate: ≤ 10^-3
    Functions: Voice media
```

---

## 4. VoWiFi (Voice over WiFi) Implementation

### 4.1 VoWiFi Architecture

```
WiFi UE ← → WiFi AP/Gateway ← → IPSec Tunnel ← → eNodeB
                                     ↓
                              P-CSCF (IMS)
                                     ↓
                              S-CSCF/HSS
```

### 4.2 VoWiFi Configuration Example

```yaml
VoWiFi Security Profile:
  IPSec Protocol:
    - IKEv2: Key Exchange Protocol
    - Phase 1 Encryption: AES-256-CBC
    - Phase 1 Authentication: SHA-256
    - Phase 2 Encryption: AES-256 GCM
    - Phase 2 Authentication: HMAC-SHA-256
    - Lifetime: 3600 seconds

  Certificate Pinning:
    - PIN Root CA: SHA-256 fingerprint
    - PIN Intermediate: SHA-256 fingerprint
    - Fallback: HSS FQDN

  P-CSCF Discovery:
    Method 1: DHCP Option 131/132
    Method 2: DNS SRV (_ims-root._sip.carrier.com)
    Method 3: Manual configuration
```

### 4.3 WiFi to Cellular Handover

```
WiFi Call (Established)
  ↓
SRVCC Triggered (Signal Strength Threshold)
  ↓
S-CSCF Initiates SRVCC
  ↓
MGCF Creates Cellular Call Path
  ↓
Media Switch to LTE Bearer
  ↓
WiFi Connection Released
  ↓
Cellular Call Continues (No Drop)
```

---

## 5. RCS (Rich Communication Services)

### 5.1 RCS Architecture

```yaml
RCS Services:
  One-to-One Communication:
    - Chat (Instant Messaging)
    - File Transfer
    - Image/Video Sharing
    - Presence and Availability

  Group Communication:
    - Group Chat
    - Group File Transfer
    - Call Features (HD Voice, Video, Screen Share)

  Standalone Messaging:
    - Fallback to SMS when unavailable
    - Rich Message Content (MIME types)

  Chat Protocols:
    - MSRP: Message Session Relay Protocol (for messaging)
    - SIP: Session Initiation (for call features)
    - XCAP: XML Configuration Access Protocol (presence)

RCS Server Components:
  - RCS Aggregator / Enabler
  - Presence Server
  - Content Server
  - Chat Server
  - XDM Server (XML Document Management)
```

### 5.2 RCS Chat Message Flow

```
Sender UE                 RCS Server                Recipient UE
  |                           |                         |
  |---SIP INVITE (Chat)------→|                         |
  | ←----100 Trying-----------|                         |
  | ←----200 OK---------------|                         |
  |---ACK--------------------→|                         |
  |                           |-----SIP INVITE (Chat)-→  |
  |                           | ←------100 Trying-------|
  |                           | ←------200 OK----------|
  |                           |---ACK-----------------→ |
  |                           |                         |
  |---MSRP (Message)-------→  |---MSRP (Message)----→   |
  |                           |                         |
  |                           | ←----MSRP (Delivery)-- |
  | ←----MSRP (Delivery)------|                        |
  |                           |                         |
```

---

## 6. WebRTC Integration with IMS

### 6.1 WebRTC-IMS Interworking

```yaml
WebRTC Client:
  - Browser-based client
  - Uses HTTPS for signaling
  - UDP/DTLS for media
  - Signaling Gateway converts SIP ↔ WebSocket

IMS Network:
  - Traditional SIP signaling
  - UDP/SRTP media
  - Codec negotiation via SDP

Interworking Gateway Functions:
  1. SIP ← → HTTP/WebSocket Gateway
  2. Codec transcoding (if needed)
  3. Media gateway (RTP ← → WebRTC)
  4. User authentication/authorization
  5. QoS enforcement
```

### 6.2 WebRTC SDP Offer Example

```
v=0
o=- 20518066601467015 0 IN IP4 192.168.1.100
s=-
t=0 0
a=extmap-allow-mixed
a=msid-semantic: WMS stream1
m=audio 9 UDP/TLS/RTP/SAVP 111 63 103 104 9 0 8 106 105 13 110 112 113 126
c=IN IP4 0.0.0.0
a=rtcp:9 IN IP4 0.0.0.0
a=ice-ufrag:EsIR
a=ice-pwd:lDKr38sK2rLEh+VQvv8bP6Ml
a=fingerprint:sha-256 8F:49:2D:EF:19:1B:3C:4B:51:5C:D7:6E:9F:2A:1D:E4:8E:4A:B2:C6:F8:3D:7A:1B:9C:5E:8D:2F:6B:4A:C9
a=setup:actpass
a=mid:0
a=extmap:1 urn:ietf:params:rtp-hdrext:ssrc-audio-level
a=extmap:4 urn:ietf:params:rtp-hdrext:sdes:mid
a=sendrecv
a=rtcp-mux
a=rtpmap:111 opus/48000/2
a=rtcp-fb:111 transport-cc
a=fmtp:111 minptime=10;useinbandfec=1
a=rtpmap:63 red/48000/2
a=rtpmap:103 ISAC/16000
a=rtpmap:104 ISAC/32000
```

---

## 7. Quality of Service (QoS) Management

### 7.1 IMS QoS Framework

```yaml
QoS Policies by Service:

Voice (Real-time):
  - Target Delay: < 150 ms one-way
  - Jitter: < 40 ms
  - Packet Loss: < 1% (3% acceptable)
  - Bandwidth: 64-128 Kbps per direction
  - Codec: G.711, G.729, AMR-WB

Video (Real-time):
  - Target Delay: < 150 ms one-way
  - Jitter: < 50 ms
  - Packet Loss: < 2%
  - Bandwidth: 256 Kbps - 4 Mbps
  - Codec: H.264, VP8, VP9, H.265

Data/Messaging:
  - Target Delay: < 2 seconds
  - Jitter: Not critical
  - Packet Loss: < 0.1%
  - Bandwidth: Variable
```

### 7.2 QoS Monitoring Configuration

```yaml
QoS Metrics Collection:
  Network Side:
    - SGSN/PGW monitors bearer QoS
    - BBERF enforces policies
    - Measurement Points at SGW, PGW

  UE Side:
    - Application generates RTCP reports
    - Network Measurement Agent (NMA)
    - Reports to PCRF via Gx interface

  Reporting:
    - PCRF: Policy and Charging Rules Function
    - Rx Interface: IMS ← → PCRF QoS negotiation
    - Gx Interface: PGW ← → PCRF bearer control
```

---

## 8. Codec Selection and Transcoding

### 8.1 VoIP Codec Configuration

```yaml
Recommended Codec Priority:

Narrowband (8 kHz):
  1. G.711 (PCM) - 64 Kbps, lowest latency, baseline
  2. G.729 - 8 Kbps, CPU intensive, good MOS
  3. iLBC - 15.2/13.3 Kbps, good for packet loss
  4. GSM-FR - 13.2 Kbps, legacy support

Wideband (16 kHz):
  1. AMR-WB - 6.6-23.85 Kbps, adaptive bitrate
  2. G.722 - 64 Kbps, standard HD voice
  3. Opus - 6-510 Kbps, optimal quality/bandwidth
  4. SILK - 8-40 Kbps (deprecated, Skype legacy)

Ultra-Wideband (32 kHz+):
  1. EVS (Enhanced Voice Services) - 5.9-128 Kbps, 3GPP standard
  2. Opus - supports up to 48 kHz
  3. G.722.1c - 24-32 kHz, 24-48 Kbps
```

### 8.2 Codec Negotiation (SDP)

```
Alice's SDP Offer:
  m=audio 5000 RTP/AVP 97 98 99 0 8
  a=rtpmap:97 opus/48000/2
  a=rtpmap:98 AMR-WB/16000/1
  a=rtpmap:99 G.722/8000/1
  a=rtpmap:0 PCMU/8000/1
  a=rtpmap:8 PCMA/8000/1

Bob's SDP Answer:
  m=audio 6000 RTP/AVP 0 8
  a=rtpmap:0 PCMU/8000/1
  a=rtpmap:8 PCMA/8000/1

Selected Codec: PCMU (G.711) - common to both
```

### 8.3 Transcoding Architecture

```
Narrowband (G.711) ← → Transcoder ← → Wideband (AMR-WB)
                            ↓
                       Media Gateway
                            ↓
Legacy PSTN ← → MGCF ← → Transcoder ← → LTE VoLTE
(G.711)                                (Opus/EVS)
```

---

## 9. Emergency Services (E911/E112)

### 9.1 Enhanced Emergency Call Routing

```yaml
E911/E112 Call Flow:

UE Initiates Emergency Call:
  1. INVITE to sos@ims.3gpp.org or similar
  2. Route Tag: "urn:service:sos"
  3. Call Routing Service (CRS) routes to PSAP (Public Safety Answer Point)
  4. Location Information:
     - GPS coordinates
     - Cell ID/ECGI
     - WiFi AP BSSID (indoors)
     - Civic address

  5. E911/E112 Gateway:
     - Converts IMS → PSTN format
     - Adds Emergency Call ID (ECID)
     - Appends location via PIDF-LO (Presence Information Data Format - Location)
```

### 9.2 Emergency Call SIP Routing

```
Emergency UE                    CSCF                 E-CSCF              PSAP Gateway
  |                              |                      |                       |
  |---INVITE (Emergency)------→  |                      |                       |
  | ←----100 Trying-------------|                       |                       |
  |                              |---Route to E-CSCF-→  |                       |
  |                              |                      |---INVITE--------→     |
  |                              |                      | ←---100 Trying--|     |
  | ←----180 Ringing------------ ←-----180 Ringing------|                       |
  |                              |                      | ←---200 OK------|     |
  |                              |←-----200 OK---------- ←---200 OK------|     |
  |---ACK--------------------→  |-------ACK----------→ |-------ACK------→     |
  |                              |                      |                       |
  |  ◄════ Voice + Location Data ════════════════════════════════════════╝     |
  |                              |                      |                       |
```

### 9.3 Emergency Location Configuration

```yaml
Location Information Elements:

PIDF-LO (Presence Information Data Format - Location):
  - geopriv: Geographic Privacy
  - Point: Latitude, Longitude, Altitude
  - Circle: Radius around point
  - Polygon: Area coverage
  - Civic Address: Street, building, floor
  - Uncertainty: Accuracy radius in meters

Civic Address Format:
  ```
  <civicAddress xml:lang="en-US">
    <country>US</country>
    <state>CA</state>
    <county>San Francisco</county>
    <city>San Francisco</city>
    <street>Market Street</street>
    <housenum>875</housenum>
    <unit>Suite 200</unit>
  </civicAddress>
  ```

Cell ID Based Fallback:
  - Cell ID + eNodeB: ~100m accuracy (urban)
  - WiFi AP BSSID: ~30m accuracy (urban)
  - GPS: 5-10m accuracy (line of sight)
```

---

## 10. PSTN/Legacy Network Interconnection

### 10.1 IMS-PSTN Gateway Architecture

```
IMS Side                                    PSTN Side
┌──────────────────┐                   ┌──────────────────┐
│ S-CSCF           │                   │ Carrier Network  │
│ (SIP Signaling)  │                   │ (ISUP/TDM)       │
└─────────┬────────┘                   └────────┬─────────┘
          │                                     │
       ┌──┴─────────────────────────────────────┴───┐
       │         MGCF (Media Gateway                │
       │         Control Function)                  │
       │  - ISUP/SIP Translation                   │
       │  - Bearer Conversion                      │
       │  - Numbering Translation                  │
       │  - Interworking Logic                     │
       └──┬─────────────────────────────────────────┘
          │
       ┌──┴─────────────────────────────────────────┐
       │    MGW (Media Gateway)                     │
       │  - RTP ← → TDM/PSTN                        │
       │  - Transcoding (if needed)                 │
       │  - Signaling Gateway (SG)                  │
       └────────────────────────────────────────────┘
```

### 10.2 PSTN Call Origination

```
PSTN Caller ← → TDM Network ← → SG/MGW ← → MGCF ← → S-CSCF
                (ISUP Signaling)   ↓       ↓
                                  Bearer  SIP Signaling
                                   ↓
                              IMS Network
                                   ↓
                              Terminating UE
```

### 10.3 Number Mapping Configuration

```yaml
PSTN Number Translation Rules:

Prefix-Based Mapping:
  - Incoming: +1 650 (area code)
    Translates To: sip:+16505551234@carrier.com

  - Incoming: +44 20 (London)
    Translates To: sip:+442071838750@uk-carrier.com

User-Based Mapping:
  - VoIP User: bob@atlanta.com
    PSTN Number: +1 404 555 7890
    Routing: Inbound +1 404 555 7890 → SIP INVITE to bob@atlanta.com

Carrier Route Selection:
  - Route 1: Direct SIP Trunk (primary)
  - Route 2: ISUP Bearer with SIP Signaling (backup)
  - Route 3: Legacy ISDN (fallback)
  - Route 4: H.323 Gateway (legacy support)
```

---

## 11. Security in VoIP/IMS

### 11.1 SIP Authentication Mechanisms

```yaml
SIP Authentication Methods:

Digest Authentication (RFC 2617):
  Challenge:
    401 Unauthorized
    WWW-Authenticate: Digest realm="atlanta.com",
                     domain="sip:atlanta.com",
                     nonce="f84f1cec41e6cbe5aea9c8e88d359",
                     opaque="",
                     algorithm=MD5,
                     qop="auth"

  Response:
    Authorization: Digest username="alice@atlanta.com",
                   realm="atlanta.com",
                   nonce="f84f1cec41e6cbe5aea9c8e88d359",
                   uri="sip:bob@biloxi.com",
                   response="6629fae49393a05397450978507c4ef1",
                   opaque="",
                   qop=auth,
                   nc=00000001,
                   cnonce="0a4f113b"

IMS Authentication-Authorization:
  IMPI (IP Multimedia Private Identity):
    - Private, secret identifier
    - Format: user@home.realm
    - Used for authentication only

  IMPU (IP Multimedia Public User Identity):
    - Public, published identifier
    - Format: sip:user@home.realm or tel:+1-234-567-8900
    - Multiple IMPUs per user

  Authentication Vector (AV):
    - Generated by HSS
    - Contains: RAND, XRES, AUTN, IK, CK
    - Valid for single REGISTER transaction
```

### 11.2 SIP Transport Security (TLS/DTLS)

```yaml
TLS Configuration for SIP:

Protocol: TLS 1.2 minimum (recommended 1.3)
  Cipher Suites:
    - TLS_ECDHE_ECDSA_WITH_AES_256_GCM_SHA384 (preferred)
    - TLS_ECDHE_RSA_WITH_AES_256_GCM_SHA384
    - TLS_ECDHE_ECDSA_WITH_CHACHA20_POLY1305_SHA256
    - TLS_ECDHE_RSA_WITH_CHACHA20_POLY1305_SHA256

Certificate Requirements:
  - Subject Alt Name: SIP URI or FQDN
  - Validity: Minimum 1 year
  - Key Size: RSA 2048-bit minimum (4096 preferred) or ECDSA P-256
  - Signing Algorithm: SHA-256 minimum
  - Issuer: Trusted CA

TLS/SRTP for RTP Media:
  - DTLS (Datagram TLS) over UDP for RTP protection
  - Fingerprint in SDP:
    a=fingerprint:sha-256 8F:49:2D:EF:19:1B:3C:4B:51:5C:D7:6E:9F:2A:1D:E4
  - Key establishment via DTLS handshake
```

### 11.3 SRTP (Secure RTP) Configuration

```yaml
SRTP Profile Selection:

SRTP_AES128_CM_SHA1_80:
  - Encryption: AES-128 Counter Mode
  - Authentication: HMAC-SHA1 (80-bit tag)
  - Backward compatible, baseline
  - Recommended minimum

SRTP_AES128_CM_SHA1_32:
  - Encryption: AES-128 Counter Mode
  - Authentication: HMAC-SHA1 (32-bit tag)
  - Reduced authentication, bandwidth optimization
  - Use only if latency critical

SRTP_AEAD_AES_128_GCM:
  - Encryption + Authentication: AES-128 GCM
  - Combined mode, modern approach
  - Lower computational overhead
  - RECOMMENDED for new deployments

SRTP_AEAD_AES_256_GCM:
  - Encryption + Authentication: AES-256 GCM
  - Stronger security, higher computational cost
  - For highly sensitive communications

Key Management:
  - Master Key Size: 128 or 256 bits
  - Salt Size: 112 bits
  - Derivation: Pseudo-Random Function (PRF)
  - Key Lifetime: 2^31 - 1 packets or session end
```

---

## 12. Troubleshooting and Diagnostics

### 12.1 Common VoIP Issues and Solutions

```yaml
One-Way Audio:

Symptoms:
  - Caller hears callee but not vice versa
  - Media path asymmetry

Causes:
  - Firewall blocking return RTP path
  - NAT double translation
  - Asymmetric routing
  - Media gateway misconfiguration

Diagnosis:
  1. SIP Trace: Verify ACK and media offer/answer
  2. RTP Capture: Check bidirectional flow (tcpdump -i eth0 -X 'udp port 5000:5100')
  3. Packet Loss: Monitor RTCP sender/receiver reports
  4. Firewall Rules: Verify RTP port ranges open both directions

Solution:
  - Configure RTP port ranges symmetrically (e.g., 10000-20000)
  - Verify media_address in SDP matches network interface
  - Check RTCP attributes in SDP (a=rtcp:)
  - Enable RTCP-mux if supported (a=rtcp-mux)

---

Echo Problem:

Symptoms:
  - User hears their own voice delayed
  - Usually 100-200 ms delay

Causes:
  - Echo cancellation disabled
  - Long delay in media path
  - Acoustic echo (speakerphone)
  - Network routing delay

Diagnosis:
  1. Check one-way delay: < 150 ms per RFC
  2. RTCP Jitter Report: rtcp_jitter field
  3. Media Gateway logs: Check echo cancellation status
  4. Codec frame size: Verify PTime (a=ptime:20)

Solution:
  - Enable echo cancellation (EC) on media servers
  - Reduce network latency (optimize routing)
  - Use headset instead of speakerphone
  - Adjust jitter buffer (typical: 20-100 ms)
  - Codec options: a=fmtp:111 minptime=10

---

No Media / Silent Call:

Symptoms:
  - Call connects, but no audio
  - Signaling successful, media fails

Causes:
  - SDP mismatch (no common codec)
  - RTP port not open
  - Media gateway not initialized
  - Codec not properly configured

Diagnosis:
  1. Check SDP m= line intersection for common codecs
  2. Verify media gateway ports: ss -tlnp (check RTP listener)
  3. Check media resources allocation
  4. Review codec availability in both ends

Solution:
  - Configure common codec (e.g., G.711 as fallback)
  - Ensure RTP ports open on firewall (both UDP)
  - Verify media gateway status (systemctl status mediaserver)
  - Check transcoding availability if codecs don't match
  - Validate SDP fmtp parameters (a=fmtp:)
```

### 12.2 Monitoring and Metrics

```yaml
Key Performance Indicators (KPIs):

Call Quality:
  - MOS (Mean Opinion Score): Target > 4.0
  - R-Factor: Target > 70
  - Packet Loss: Target < 1%
  - Latency: Target < 150 ms one-way
  - Jitter: Target < 50 ms

Call Setup Metrics:
  - Setup Time (INVITE to 200 OK): Target < 2 seconds
  - Ringback Delay: Target < 1 second
  - Post-Dial Delay (PDD): Target < 3 seconds

Network Metrics:
  - Bandwidth Utilization: Monitor against QoS limits
  - Bearer Failures: < 0.1% of calls
  - Handover Success Rate: > 98%
  - Availability: > 99.9%

Logging Configuration:

SIP Logger (per call):
  - Call-ID based logging
  - Timestamp correlation
  - Request/response matching
  - Transaction state machine

RTP Monitoring:
  - RTCP Sender Reports: Every 5 seconds typical
  - RTCP Receiver Reports: Jitter, loss, last SR
  - Codec payload type verification
  - Silence suppression detection (CN frames)
```

### 12.3 Network Packet Analysis

```
tcpdump SIP Call Trace:

  tcpdump -i eth0 -w voip.pcap 'udp port 5060 or tcp port 5061 or (udp > 10000 and udp < 20000)'

  Wireshark Filters:
  - SIP only: sip
  - RTP: rtp
  - RTCP: rtcp
  - Specific call: sip.Call-ID == "abc123@host"
  - Specific codec: rtp.p_type == 18 (G.729)

Common RTP Payload Types:
  - 0: PCMU (G.711 μ-law)
  - 8: PCMA (G.711 A-law)
  - 9: G.722
  - 18: G.729
  - 97: Opus (dynamic)
  - 99: AMR-WB (dynamic)
  - 113: EVS (dynamic)
```

---

## 13. Configuration Examples

### 13.1 Kamailio SIP Proxy Configuration

```
# Kamailio IMS P-CSCF Configuration

# Network definitions
listen=udp:192.168.1.10:5060
listen=tcp:192.168.1.10:5061
listen=tls:192.168.1.10:5062

# IMS module parameters
loadmodule "ims_charging"
loadmodule "ims_dialog"
loadmodule "ims_icscf"
loadmodule "ims_qos"

modparam("ims_charging", "origin_host", "pcscf.home")
modparam("ims_charging", "origin_realm", "home.carrier.com")

# SIP routing rules
route {
  if (method == "REGISTER") {
    route(REGISTER);
  }
  else if (method == "INVITE") {
    route(INVITE);
  }
  else {
    route(REQUEST);
  }
}

route[REGISTER] {
  # IMS authentication
  ims_www_authenticate("home.carrier.com");

  # Check AoR
  if (!save("location")) {
    sl_reply_error();
  }
  exit;
}

route[INVITE] {
  # Add dialog for call tracking
  if (is_method("INVITE")) {
    create_dialog();
  }

  # Route to S-CSCF
  route(TO_SCSCF);
}

route[TO_SCSCF] {
  # Forward to next-hop S-CSCF
  $du = "sip:scscf.home.carrier.com:5060";
  t_relay();
}
```

### 13.2 RTP Media Server Configuration (PJSUA)

```
# PJSUA SIP User Agent Configuration

[account_default]
id=sip:alice@atlanta.com
registrar=sip:registrar.atlanta.com
proxy=sip:proxy.atlanta.com
password=secure_password

[transport_udp]
type=udp
port=5060
bind_addr=192.168.1.100

[transport_tls]
type=tls
port=5061
bind_addr=192.168.1.100
verify_server=yes
ca_list_file=/etc/ssl/certs/ca-bundle.crt
cert_file=/etc/ssl/certs/client.crt
priv_key_file=/etc/ssl/private/client.key

[call]
auto_answer=180
max_calls=10
use_srtp=mandatory
srtp_profile=SRTP_AES128_CM_SHA1_80

[audio]
capture_dev=default
playback_dev=default
master_port=4000
clock_rate=16000
quality=4
ptime=20
no_vad=no

[codec]
; Codec priority
priority=OPUS/48000/2
priority=AMR-WB/16000/1
priority=PCMU/8000/1
priority=PCMA/8000/1

[video]
enable=yes
default_clock_rate=90000
format=H264
```

---

## 14. Best Practices Summary

```yaml
Design Principles:
  ✓ Separate signaling and media paths
  ✓ Use TLS for control plane
  ✓ Use SRTP for media plane
  ✓ Implement QoS on bearer network
  ✓ Redundancy for all critical components
  ✓ Comprehensive logging for troubleshooting
  ✓ Regular codec compatibility testing
  ✓ Emergency call routing as non-bypassable

Deployment:
  ✓ Test in lab before production
  ✓ Monitor all KPIs continuously
  ✓ Maintain version compatibility matrix
  ✓ Document all customizations
  ✓ Plan capacity for peak usage
  ✓ Schedule maintenance windows
  ✓ Maintain disaster recovery procedures

Optimization:
  ✓ Tune jitter buffer for network conditions
  ✓ Profile codec CPU usage per codec
  ✓ Balance quality vs. bandwidth
  ✓ Implement dynamic codec selection
  ✓ Monitor bearer utilization trends
  ✓ Optimize transcoding paths (minimize hops)
  ✓ Implement fast reroute for failures
```

---

## References

- 3GPP TS 23.228: IP Multimedia Subsystem (IMS)
- RFC 3261: SIP Protocol
- RFC 3550: RTP - Real-time Transport Protocol
- RFC 3711: The Secure Real-time Transport Protocol (SRTP)
- RFC 5939: Session Description Protocol (SDP) Capability Negotiation
- ETSI TS 182 004: VoLTE/VoWiFi Service Architecture
- GSM Association RCS specification
- WebRTC Standards (W3C/IETF)

---

**Document Version:** 1.0
**Last Updated:** 2025-11-19
**Author:** Telecommunications Engineering Team
