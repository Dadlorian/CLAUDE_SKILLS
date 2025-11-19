# Complete HLS Streaming Setup Guide

## Step 1: Prepare Source Video
```bash
ffmpeg -i source.mp4 -c:v libx264 -preset slow -crf 20 -c:a aac -b:a 192k prepared.mp4
```

## Step 2: Generate Multi-Bitrate HLS
```bash
#!/bin/bash

INPUT="prepared.mp4"
OUTPUT_DIR="output"

mkdir -p $OUTPUT_DIR

# 720p
ffmpeg -i $INPUT \
  -c:v libx264 -b:v 2500k -maxrate 2500k -bufsize 5000k \
  -vf "scale=1280:720" -c:a aac -b:a 128k \
  -f hls -hls_time 6 -hls_list_size 0 \
  -hls_segment_filename "$OUTPUT_DIR/720p_%03d.ts" \
  $OUTPUT_DIR/720p.m3u8

# 1080p  
ffmpeg -i $INPUT \
  -c:v libx264 -b:v 5000k -maxrate 5000k -bufsize 10000k \
  -vf "scale=1920:1080" -c:a aac -b:a 192k \
  -f hls -hls_time 6 -hls_list_size 0 \
  -hls_segment_filename "$OUTPUT_DIR/1080p_%03d.ts" \
  $OUTPUT_DIR/1080p.m3u8

# Create master playlist
cat > $OUTPUT_DIR/master.m3u8 << 'PLAYLIST'
#EXTM3U
#EXT-X-VERSION:6
#EXT-X-STREAM-INF:BANDWIDTH=2500000,RESOLUTION=1280x720
720p.m3u8
#EXT-X-STREAM-INF:BANDWIDTH=5000000,RESOLUTION=1920x1080
1080p.m3u8
PLAYLIST
```

## Step 3: Upload to CDN
```bash
aws s3 sync output/ s3://my-bucket/videos/video_123/ --acl public-read
```

## Step 4: Test Playback
```html
<video id="video" controls></video>
<script src="https://cdn.jsdelivr.net/npm/hls.js@latest"></script>
<script>
  if(Hls.isSupported()) {
    var video = document.getElementById('video');
    var hls = new Hls();
    hls.loadSource('https://cdn.example.com/videos/video_123/master.m3u8');
    hls.attachMedia(video);
  }
</script>
```

## Step 5: Monitor Performance
- Video Start Time: < 2s
- Rebuffer Ratio: < 0.5%
- Cache Hit Ratio: > 90%
