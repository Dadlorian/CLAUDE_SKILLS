# HLS Quick Reference

## Master Playlist (.m3u8)
```m3u8
#EXTM3U
#EXT-X-VERSION:6
#EXT-X-STREAM-INF:BANDWIDTH=2500000,RESOLUTION=1280x720,CODECS="avc1.64001f,mp4a.40.2"
720p.m3u8
#EXT-X-STREAM-INF:BANDWIDTH=5000000,RESOLUTION=1920x1080,CODECS="avc1.640028,mp4a.40.2"
1080p.m3u8
```

## Media Playlist
```m3u8
#EXTM3U
#EXT-X-VERSION:6
#EXT-X-TARGETDURATION:6
#EXT-X-MEDIA-SEQUENCE:0
#EXT-X-PLAYLIST-TYPE:VOD
#EXTINF:6.0,
segment_0.ts
#EXTINF:6.0,
segment_1.ts
#EXT-X-ENDLIST
```

## Key Commands

**Generate HLS**:
```bash
ffmpeg -i input.mp4 -c:v libx264 -c:a aac -f hls -hls_time 6 -hls_list_size 0 -hls_segment_filename "seg_%03d.ts" output.m3u8
```

**Validate HLS**:
```bash
mediastreamvalidator output.m3u8
```
