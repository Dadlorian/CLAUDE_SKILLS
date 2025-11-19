# Video Codec Comparison

## Compression Efficiency

**Bitrate for same quality (normalized to H.264 = 100%)**:
- H.264/AVC: 100% (baseline)
- H.265/HEVC: 50% (50% smaller)
- AV1: 35% (65% smaller than H.264)
- VVC/H.266: 25% (75% smaller than H.264)

## Encoding Speed

| Codec | Real-time Factor | Hardware Support |
|-------|-----------------|------------------|
| H.264 | 5-10x (fast) | Universal |
| H.265 | 2-5x (medium) | Modern GPUs |
| AV1 | 0.5-2x (slow) | Limited (Intel, AMD) |
| VP9 | 1-3x (medium) | Google hardware |

## Compatibility

| Codec | Browser Support | Mobile Support | Smart TV |
|-------|----------------|----------------|----------|
| H.264 | 100% | 100% | 100% |
| H.265 | Safari, Edge | iOS, some Android | Most modern |
| AV1 | Chrome, Firefox, Edge | Android 10+ | Limited |
| VP9 | Chrome, Firefox, Edge | Android | YouTube only |

## Recommendations

- **Maximum Compatibility**: H.264
- **4K Streaming**: H.265 (50% bandwidth savings)
- **Future-Proofing**: AV1 (royalty-free, excellent compression)
- **YouTube Platform**: VP9
