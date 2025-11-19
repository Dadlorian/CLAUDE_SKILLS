# Audio Codec & Bitrate Quick Reference

## Codec Comparison

| Codec | Quality | Bandwidth Efficiency | Browser Support | Best Use Case |
|-------|---------|---------------------|-----------------|---------------|
| **AAC** | Excellent | Good | Universal | Mobile apps, general streaming |
| **Opus** | Excellent | Excellent | Modern browsers | WebRTC, low-latency streaming |
| **MP3** | Good | Fair | Universal | Legacy support, podcasts |
| **Vorbis** | Good | Good | Most browsers | Open-source projects |
| **FLAC** | Lossless | Poor | Limited | Hi-fi, archival |
| **ALAC** | Lossless | Poor | Safari only | Apple ecosystem |

## Recommended Bitrates by Use Case

### Music Streaming

| Quality Tier | AAC | Opus | MP3 | Use Case |
|--------------|-----|------|-----|----------|
| **Ultra (Hi-Fi)** | 320kbps | 256kbps | 320kbps | Audiophiles, premium tier |
| **High** | 256kbps | 160kbps | 256kbps | Standard premium quality |
| **Medium** | 128kbps | 96kbps | 192kbps | Default streaming quality |
| **Low** | 96kbps | 64kbps | 128kbps | Mobile, limited bandwidth |
| **Minimal** | 64kbps | 48kbps | 96kbps | Very poor connections |

### Voice/Podcast

| Quality | AAC | Opus | Use Case |
|---------|-----|------|----------|
| **High** | 96kbps | 64kbps | Music podcasts, audiobooks |
| **Medium** | 64kbps | 48kbps | Talk shows, interviews |
| **Low** | 48kbps | 32kbps | Emergency, very poor network |

## Platform-Specific Recommendations

### Spotify
- **Free**: Opus 160kbps (web), AAC 160kbps (mobile)
- **Premium**: Opus 256kbps (web), AAC 256kbps (mobile)
- **Download**: AAC 320kbps

### Apple Music
- **Standard**: AAC 256kbps
- **Lossless**: ALAC 16-bit/44.1kHz (~1411kbps)
- **Hi-Res Lossless**: ALAC 24-bit/192kHz (~9216kbps)

### YouTube Music
- **Low**: AAC 48kbps
- **Normal**: AAC 128kbps
- **High**: AAC 256kbps

### Tidal
- **Standard**: AAC 320kbps
- **HiFi**: FLAC 16-bit/44.1kHz (~1411kbps)
- **HiFi Plus**: MQA/FLAC 24-bit/96kHz

## Sample Rate Guidelines

| Sample Rate | Use Case | Storage/Bandwidth |
|-------------|----------|-------------------|
| **44.1 kHz** | CD quality, standard music | Standard |
| **48 kHz** | Professional video, broadcasting | +9% vs 44.1kHz |
| **88.2 kHz** | High-res audio mastering | 2x CD quality |
| **96 kHz** | High-res streaming (Tidal, Qobuz) | 2.2x CD quality |
| **192 kHz** | Ultra high-res (diminishing returns) | 4.4x CD quality |

## Bit Depth Comparison

| Bit Depth | Dynamic Range | Use Case |
|-----------|---------------|----------|
| **16-bit** | 96 dB | CD quality, streaming |
| **24-bit** | 144 dB | Professional audio, hi-res |
| **32-bit float** | Unlimited | Audio production |

## Bandwidth Requirements

### Per Stream

| Quality | Bitrate | Data/Hour | Data/Day (4h) |
|---------|---------|-----------|---------------|
| **Ultra** | 320kbps | 144 MB | 576 MB |
| **High** | 256kbps | 115 MB | 460 MB |
| **Medium** | 128kbps | 58 MB | 232 MB |
| **Low** | 96kbps | 43 MB | 172 MB |
| **Minimal** | 64kbps | 29 MB | 116 MB |

### For 1 Million Users

| Concurrent Users | Quality | Total Bandwidth | Cost/Month (AWS) |
|-----------------|---------|-----------------|------------------|
| 100K | High (256kbps) | 3.2 Tbps | ~$100K |
| 100K | Medium (128kbps) | 1.6 Tbps | ~$50K |
| 100K | Low (96kbps) | 1.2 Tbps | ~$37K |

*Cost estimates for bandwidth only, excluding storage and compute*

## Storage Requirements

### Per Track (3.5 minute average)

| Format | Bitrate | Size |
|--------|---------|------|
| **AAC 320kbps** | 320kbps | 8.4 MB |
| **AAC 256kbps** | 256kbps | 6.7 MB |
| **AAC 128kbps** | 128kbps | 3.4 MB |
| **Opus 256kbps** | 256kbps | 6.7 MB |
| **Opus 128kbps** | 128kbps | 3.4 MB |
| **MP3 320kbps** | 320kbps | 8.4 MB |
| **FLAC Lossless** | ~1000kbps | 26 MB |

### For 50 Million Track Catalog

| Formats Stored | Storage per Track | Total Storage |
|----------------|------------------|---------------|
| **Single (256k AAC)** | 6.7 MB | 335 TB |
| **Multi (320k, 256k, 128k, 96k AAC)** | 24 MB | 1.2 PB |
| **Multi + Lossless** | 50 MB | 2.5 PB |

## Transcoding Parameters

### FFmpeg Commands

```bash
# High quality AAC
ffmpeg -i input.wav -c:a aac -b:a 256k -ar 44100 output.aac

# High quality Opus
ffmpeg -i input.wav -c:a libopus -b:a 128k -vbr on output.opus

# High quality MP3
ffmpeg -i input.wav -c:a libmp3lame -b:a 320k -ar 44100 output.mp3

# FLAC lossless
ffmpeg -i input.wav -c:a flac -compression_level 8 output.flac

# Batch transcode to multiple formats
for bitrate in 320k 256k 128k 96k; do
  ffmpeg -i input.wav -c:a aac -b:a $bitrate output_$bitrate.aac
done
```

## Audio Normalization Standards

| Standard | Target | Use Case |
|----------|--------|----------|
| **EBU R128** | -23 LUFS | European broadcast |
| **ATSC A/85** | -24 LKFS | US broadcast |
| **Spotify** | -14 LUFS | Music streaming |
| **Apple Music** | -16 LUFS | Music streaming |
| **YouTube** | -14 LUFS | Video platform |
| **Tidal** | -14 LUFS | Hi-fi streaming |

## Quality Perception

| Bitrate Range | Perceived Quality | Listener Type |
|---------------|-------------------|---------------|
| **320kbps+** | Transparent | Audiophiles can't distinguish from lossless |
| **256kbps** | Excellent | Vast majority can't tell difference |
| **192-128kbps** | Very Good | Most listeners satisfied |
| **96-128kbps** | Good | Acceptable for casual listening |
| **64-96kbps** | Fair | Noticeable artifacts, voice okay |
| **< 64kbps** | Poor | Only for emergency use |

## Latency Comparison

| Codec | Algorithmic Latency | Total Latency* |
|-------|---------------------|----------------|
| **Opus** | 5-22.5 ms | 100-200 ms |
| **AAC-LC** | 40-80 ms | 200-300 ms |
| **AAC-HE** | 80-120 ms | 300-400 ms |
| **MP3** | 50-100 ms | 200-300 ms |
| **Vorbis** | 40-80 ms | 200-300 ms |

*Total includes encoding, network, and decoding

## Browser Compatibility Matrix

| Codec | Chrome | Firefox | Safari | Edge | Mobile |
|-------|--------|---------|--------|------|--------|
| **AAC** | ✅ | ✅ | ✅ | ✅ | ✅ |
| **Opus** | ✅ | ✅ | ✅ | ✅ | ✅ (modern) |
| **MP3** | ✅ | ✅ | ✅ | ✅ | ✅ |
| **Vorbis** | ✅ | ✅ | ⚠️ | ✅ | ⚠️ |
| **FLAC** | ✅ | ✅ | ✅ | ✅ | ⚠️ |
| **ALAC** | ❌ | ❌ | ✅ | ❌ | iOS only |

✅ Full support | ⚠️ Limited support | ❌ No support

## Adaptive Bitrate Switching Rules

### Network Speed Mapping

| Connection | Speed | Recommended Bitrate |
|------------|-------|-------------------|
| **5G** | 100+ Mbps | 320kbps (unlimited) |
| **4G/LTE** | 5-50 Mbps | 256kbps |
| **3G** | 384 Kbps - 2 Mbps | 128kbps |
| **2G** | 50-100 Kbps | 64kbps |
| **Poor** | < 50 Kbps | 48kbps |

### Buffer-Based Switching

| Buffer Level | Action |
|--------------|--------|
| **> 30s** | Switch to higher quality |
| **15-30s** | Maintain current quality |
| **5-15s** | Switch to lower quality |
| **< 5s** | Emergency: lowest quality |
| **Buffering** | Immediate switch to lower |

## Cost Optimization Strategies

1. **Progressive Quality**: Start medium, adapt based on user behavior
2. **Time-Based**: Lower quality during peak hours (congestion pricing)
3. **Geography**: Adjust based on regional bandwidth costs
4. **User Tier**: Free users get lower max quality
5. **Device Type**: Mobile gets lower default vs desktop
6. **WiFi Detection**: Higher quality on WiFi vs cellular
7. **Cache Popular**: Cache top tracks at multiple bitrates
8. **Codec Choice**: Prefer Opus (better quality per bit)

## Testing & QA Checklist

- [ ] ABX listening tests at each bitrate
- [ ] Test playback on all target devices
- [ ] Verify gapless playback transitions
- [ ] Test adaptive switching under varying network
- [ ] Check loudness normalization consistency
- [ ] Verify metadata preservation after encoding
- [ ] Test offline download/playback
- [ ] Measure actual bandwidth usage
- [ ] Check for audio artifacts (pre-echo, aliasing)
- [ ] Verify sample rate conversion quality

## Recommended Tech Stack

### Encoding
- **FFmpeg**: Industry standard, all codecs
- **fdk-aac**: Best AAC encoder quality
- **libopus**: Official Opus encoder
- **LAME**: Best MP3 encoder

### Playback
- **Web**: HTML5 Audio, Howler.js, Tone.js
- **Mobile**: ExoPlayer (Android), AVPlayer (iOS)
- **Desktop**: Electron with Howler.js

### Streaming
- **Protocol**: HLS (HTTP Live Streaming)
- **CDN**: CloudFront, Fastly, Cloudflare
- **Storage**: S3, GCS, Azure Blob

### Monitoring
- **Quality**: PESQ, POLQA scoring
- **Bandwidth**: CloudWatch, DataDog
- **Player**: Custom telemetry, Google Analytics
