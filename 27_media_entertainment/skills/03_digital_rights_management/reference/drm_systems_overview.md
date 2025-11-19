# DRM Systems Overview

## Widevine (Google)

**Platforms**: Android, Chrome, Firefox, ChromeOS
**Security Levels**:
- L1: Hardware DRM (TEE), supports 4K/HDR
- L2: Software decryption, hardware crypto
- L3: Software only, limited to SD/720p

**License Server**: Custom or Google Widevine Cloud

## FairPlay Streaming (Apple)

**Platforms**: iOS, iPadOS, macOS, tvOS, Safari
**Security**: Hardware-backed (Secure Enclave)
**Max Quality**: 4K, HDR10, Dolby Vision
**License Server**: Custom FairPlay KSM

## PlayReady (Microsoft)

**Platforms**: Windows, Xbox, Smart TVs (Samsung, LG), Edge
**Security Levels**:
- SL3000: Hardware DRM
- SL2000: Software with restrictions  
- SL150: Software only

**License Server**: PlayReady Server SDK or custom

## Multi-DRM Providers

**BuyDRM KeyOS**: $0.002 - $0.01 per license
**EZDRM**: $0.005 - $0.02 per stream hour
**Irdeto**: Enterprise pricing
**Axinom**: $0.001 - $0.005 per license
