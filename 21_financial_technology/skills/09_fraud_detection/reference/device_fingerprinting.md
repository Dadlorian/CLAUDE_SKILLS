# Device Fingerprinting Reference

## Overview
Device fingerprinting creates a unique identifier for devices based on hardware, software, and behavioral characteristics. Enables device tracking across sessions and detection of device-based fraud patterns.

## Fingerprint Components

### Hardware Identifiers
- **Device type**: Desktop, laptop, tablet, mobile
- **Manufacturer**: Apple, Samsung, Dell, etc.
- **Device model**: iPhone 13 Pro, Galaxy S21, etc.
- **Serial number**: Unique device identifier (limited access)
- **IMEI/IMSI**: Mobile-specific identifiers
- **MAC address**: Network adapter identification
- **GPU details**: Graphics processor info
- **CPU details**: Processor core count, architecture
- **RAM size**: Memory capacity
- **Storage**: Disk size and partitions

### Operating System
- **OS type**: Windows, macOS, iOS, Android, Linux
- **OS version**: Specific version number
- **Build number**: OS build identifier
- **Patch level**: Security update status
- **Timezone**: System timezone setting
- **Language**: System locale and language
- **Keyboard layouts**: Installed input methods

### Browser Details
- **Browser type**: Chrome, Firefox, Safari, Edge
- **Browser version**: Specific version number
- **User-Agent string**: Full user-agent header
- **Engine**: Rendering engine (Webkit, Gecko, Blink)
- **JavaScript version**: Supported JS features
- **WebGL**: Graphics API support
- **Canvas fingerprinting**: Pixel rendering
- **Font support**: Installed fonts
- **Plugin list**: Installed extensions/plugins

### Network Information
- **IP address**: Device's IP address (variable)
- **ISP details**: Internet service provider
- **Proxy/VPN detection**: Anonymization usage
- **Network type**: Wifi, cellular, ethernet
- **DNS servers**: Configured DNS servers
- **Connection speed**: Estimated bandwidth
- **Geolocation**: IP-based location

### Software Installation
- **Installed applications**: Software list
- **Antivirus software**: Security software presence
- **Security patches**: Update status
- **Browser extensions**: Installed add-ons
- **Downloaded fonts**: Custom font usage
- **Codec support**: Video/audio formats

## Fingerprinting Techniques

### Client-Side Fingerprinting
```
Browser-based detection using JavaScript:
1. Canvas fingerprinting: Draw text, check pixel rendering
2. WebGL fingerprinting: GPU-specific rendering
3. Font detection: Test installed fonts
4. Plugin detection: Flash, Java, etc.
5. Battery API: Device battery status
6. Screen properties: Resolution, orientation
```

### Server-Side Fingerprinting
```
Server analysis of HTTP headers and requests:
1. User-Agent parsing
2. Accept-Language header
3. Accepted content types
4. Accept-Encoding details
5. Referer information
6. Custom HTTP headers
7. TLS cipher preferences
8. TCP/IP stack analysis
```

### Hybrid Fingerprinting
- Client-side script generates fingerprint
- Comparison with server-side baseline
- Confidence scoring
- Multi-layer verification

## Fingerprint Uniqueness & Stability

### High Entropy Components
- **Screen resolution**: Many variations
- **Timezone**: Global diversity
- **Language**: Multiple languages
- **Installed fonts**: User-specific
- **Plugins**: Optional installations
- **Browser version**: Frequent updates

### Low Entropy Components
- **Browser type**: Limited choices
- **OS type**: Few major versions
- **User-Agent**: Common values
- **Resolution width**: Grouped values

### Persistence
- **Persistent components**: Rarely change
  - OS type, OS version, device model
  - Timezone, language
  - Installed fonts

- **Volatile components**: Frequent changes
  - Browser version (auto-updates)
  - IP address (network changes)
  - Installed plugins (user installs)

## Device Identification Use Cases

### Device Risk Assessment
```
Risk Factors:
- Device age (first seen date)
- Device fraud history
- Device chargeback history
- Multiple accounts per device
- Velocity on device (transactions per device)
- Device location changes
```

### New Device Detection
- Compare fingerprint to customer baseline
- Flag new devices for verification
- Track device introduction
- Monitor for suspicious device additions

### Fraud Ring Detection
- Multiple accounts from same device
- Same device across different customer accounts
- Device used in multiple fraud cases
- Device switching patterns

### Account Takeover Detection
- Device mismatch with account baseline
- New device sudden emergence
- Multiple devices in rapid succession
- Geographic device changes (impossibility)

## Implementation Challenges

### Fingerprint Accuracy
- **False positives**: Legitimate device changes
  - Browser updates changing fingerprint
  - System updates modifying components
  - Legitimate device replacements

- **False negatives**: Attacker device spoofing
  - VM with similar configuration
  - Browser extension masking
  - Coordinated fingerprint matching

### Privacy & Tracking Concerns
- **User privacy**: Tracking across services
- **Consent requirements**: GDPR, CCPA compliance
- **Transparency**: User awareness
- **Do Not Track**: Browser privacy settings
- **Fingerprint resistance**: Privacy browser modes

### Device Variations
- **Mobile devices**: Frequent model changes
- **Updates**: OS and browser auto-updates
- **Virtualization**: VM different fingerprints
- **Emulation**: Emulator fingerprints
- **Jailbreak/Root**: System modifications

## Fingerprinting Evasion

### Spoofing Techniques
- Browser extension modification
- User-Agent manipulation
- Canvas fingerprint spoofing
- Header injection
- JavaScript obfuscation

### Detection of Spoofing
- Inconsistency between components
- Impossible fingerprint combinations
- Mismatch with historical data
- Device profile contradiction

## Fingerprint Scoring

### Single Component Risk
```
Device_Risk =
  0.3 * Device_Age_Risk +
  0.2 * Device_History_Risk +
  0.2 * Device_Velocity_Risk +
  0.2 * Device_Location_Risk +
  0.1 * Device_Consistency_Risk
```

### Combined Fingerprint Risk
- Hash fingerprint to unique identifier
- Track across sessions
- Accumulate historical risk data
- Compare to account baseline

### Adaptive Fingerprinting
- Multiple fingerprint algorithms
- Consensus scoring across methods
- Weighting by fingerprint stability
- Regular recalibration

## Device Lifecycle

### Device Onboarding
```
1. User creates account on new device
2. Fingerprint captured
3. Verification required (email, SMS, 2FA)
4. Device added to customer whitelist
5. Device risk score initialized at medium
```

### Device Monitoring
```
1. Transactions flagged to device
2. Device risk accumulated
3. Behavioral patterns tracked
4. Anomaly detection active
5. Alerts on device compromise
```

### Device Offboarding
```
1. Customer confirms device loss/change
2. Device marked inactive
3. Linked accounts reviewed
4. Security check on related accounts
5. Historical data retained for 1-2 years
```

## Comparison with Other Methods

### vs. IP Address
- More persistent than IP
- More unique than IP
- Less volatile than IP
- Cannot be spoofed easily
- Works across networks

### vs. Behavioral Biometrics
- Faster to establish baseline
- Less user friction
- More technical than behavioral
- Complementary techniques
- Device + behavior = stronger signal

### vs. Authentication Factors
- Non-intrusive vs 2FA
- Continuous vs on-demand
- Risk assessment vs verification
- Works with other methods
