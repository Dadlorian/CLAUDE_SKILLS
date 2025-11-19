# Video Production Standards for Technical Documentation

## Overview
Consistent video production standards ensure professional quality, accessibility, and optimal viewing experience across all platforms. This guide establishes technical specifications and best practices for producing technical documentation videos.

## Resolution and Frame Rate Standards

### Display Resolution
- **Primary Format**: 1920x1080 (Full HD / 1080p)
  - Industry standard for web and streaming
  - Balances quality with file size
  - Compatible with most devices and platforms

- **Alternative Resolutions**:
  - 4K (3840x2160): For premium tutorials and high-end production
  - 720p (1280x720): For lower bandwidth environments
  - Square Format (1080x1080): For social media and mobile

### Frame Rate
- **Standard**: 30 fps (frames per second)
  - Suitable for screen capture and presentation content
  - Standard for streaming platforms
  - Reduces file size compared to 60 fps

- **High Motion Content**: 60 fps
  - Recommended for gameplay, complex animations
  - Smoother motion for action-heavy tutorials
  - Consider bandwidth implications

- **Consistency**: Maintain consistent frame rate throughout the entire video
  - Avoid mixing frame rates within a single project
  - Select frame rate before recording begins

## Audio Standards

### Sample Rate and Bit Depth
- **Sample Rate**: 48 kHz (preferred) or 44.1 kHz
  - Industry standard for professional video
  - Ensures compatibility with broadcast and streaming

- **Bit Depth**: 24-bit or 16-bit
  - 24-bit for production and editing
  - 16-bit acceptable for delivery

### Audio Levels
- **Target Level**: -6 dB to -3 dB (peaks)
  - Provides headroom for compression
  - Prevents clipping and distortion

- **Consistency**: Maintain uniform audio levels throughout
  - Use audio normalization during editing
  - Avoid abrupt volume changes between segments

- **Noise Floor**: -60 dB or quieter
  - Background noise should be minimal
  - Use noise reduction tools when necessary

### Audio Channels
- **Mono**: For single-speaker narration
- **Stereo**: For multi-speaker interviews or music
- **5.1 Surround**: Only for premium production content

### Codec Specifications
- **Preferred Codec**: AAC (Advanced Audio Codec)
  - Bitrate: 128-192 kbps for stereo
  - Bitrate: 64-128 kbps for mono

- **Alternative**: MP3
  - Bitrate: 128-320 kbps
  - Less preferred but widely compatible

## Video Codec and Compression

### Codec Selection
- **Primary Codec**: H.264 (AVC)
  - Universal compatibility
  - Excellent compression efficiency
  - Industry standard for delivery

- **Premium Option**: H.265 (HEVC)
  - Better compression at same quality
  - Smaller file sizes
  - Limited compatibility with older devices

### Bitrate Guidelines
- **1080p @ 30fps**: 3,000-6,000 kbps
  - Balanced quality and file size
  - 3,500 kbps recommended for streaming

- **1080p @ 60fps**: 4,500-9,000 kbps

- **4K @ 30fps**: 8,000-16,000 kbps

### Color Space
- **Standard**: Rec. 709 (BT.709)
  - Web and broadcasting standard
  - Ensures consistent color reproduction

- **Color Depth**: 8-bit per channel (4:2:0 chroma subsampling)
  - Industry standard
  - 10-bit for premium production

## File Format and Container

### Recommended Formats
1. **MP4 (.mp4)**
   - Container: MPEG-4
   - Video: H.264
   - Audio: AAC
   - Use case: Universal delivery, streaming

2. **MOV (.mov)**
   - Container: QuickTime
   - Use case: Editing and archival
   - Better for post-production workflows

3. **WebM (.webm)**
   - Container: WebM
   - Video: VP9
   - Use case: Web delivery with better compression

### File Size Optimization
- Target file size: 50-200 MB for 5-10 minute videos
- Use appropriate codec settings
- Balance quality against bandwidth considerations

## Color and Lighting Standards

### Color Grading
- **Color Temperature**: 5500K (daylight balanced)
- **Saturation**: Natural, avoid oversaturation
- **Contrast Ratio**: Maintain legible text (4.5:1 minimum)

### Lighting Setup
- **Key Light**: Primary light source at 45-degree angle
- **Fill Light**: Secondary light to reduce shadows (50% intensity of key)
- **Back Light**: Optional, creates separation from background
- **Minimum Illumination**: 500 lux on face, 300 lux on background

### Screen Capture Considerations
- **Monitor Brightness**: Set to 75-100% for clarity
- **Display Settings**: Ensure text is legible
- **Color Accuracy**: Use calibrated monitors when possible

## Duration and Pacing

### Optimal Video Lengths
- **Introductory Tutorial**: 2-5 minutes
- **Feature Walkthrough**: 5-10 minutes
- **In-depth Guide**: 10-15 minutes
- **Complete Course Module**: 15-30 minutes

### Pacing Guidelines
- **Speaking Rate**: 150-160 words per minute
- **Pause Duration**: 1-2 seconds between concepts
- **Scene Duration**: 5-20 seconds per screen change
- **Transitions**: 300-500ms between scenes

## Quality Assurance Checklist

- [ ] Resolution and frame rate match specifications
- [ ] Audio levels are consistent and clear
- [ ] No clipping or audio distortion
- [ ] Color grading is consistent throughout
- [ ] Text is legible on all screen sizes
- [ ] Video file size is within acceptable range
- [ ] File format compatible with target platforms
- [ ] Metadata (title, description) is complete
- [ ] Closed captions are synchronized
- [ ] Playback tested on multiple devices

## Archival Standards

### Master File
- Store original, uncompressed or lightly compressed
- Use high-quality codec (ProRes, DNxHD)
- Maintain original metadata
- Keep in safe, backed-up location

### Delivery Files
- Create optimized versions for each platform
- Document all encoding settings used
- Maintain file naming conventions
- Version control for updates and revisions

## Platform-Specific Recommendations

### YouTube
- Resolution: 1920x1080 or 3840x2160
- Frame Rate: 30 fps
- Bitrate: 4,500-6,000 kbps

### Vimeo
- Resolution: Up to 4K
- Frame Rate: 24, 25, 30, or 60 fps
- Bitrate: 5,000-8,000 kbps

### Internal Documentation
- Resolution: 1280x720 or 1920x1080
- Frame Rate: 30 fps
- Bitrate: 2,000-4,000 kbps

## Troubleshooting Common Issues

### Audio Problems
- Muffled sound: Check microphone placement and settings
- Background hum: Identify and eliminate source (electrical noise)
- Inconsistent levels: Use audio normalization and compression

### Video Quality Issues
- Pixelation: Increase bitrate or check source resolution
- Color banding: Use 10-bit color or higher bitrate
- Flickering: Check frame rate and lighting setup

### File Compatibility
- Won't play on platform: Verify codec and container format
- Audio out of sync: Re-export with proper codec settings
- Colors look wrong: Check color space and display calibration
