# Streaming API Design Guide

## REST API Patterns for Media Platforms

### Video Metadata API
```javascript
// GET /api/v1/videos/:videoId
{
  "id": "video_123",
  "title": "Example Video",
  "duration": 3600,
  "formats": {
    "hls": "https://cdn.example.com/video_123/master.m3u8",
    "dash": "https://cdn.example.com/video_123/manifest.mpd"
  },
  "thumbnails": {
    "small": "https://cdn.example.com/video_123/thumb_320.jpg",
    "large": "https://cdn.example.com/video_123/thumb_1280.jpg"
  },
  "drm": {
    "widevine": "https://license.example.com/widevine",
    "fairplay": "https://license.example.com/fairplay"
  },
  "captions": [
    {"language": "en", "url": "https://cdn.example.com/video_123/en.vtt"},
    {"language": "es", "url": "https://cdn.example.com/video_123/es.vtt"}
  ]
}
```

### Playback Session API
```javascript
// POST /api/v1/playback/sessions
{
  "videoId": "video_123",
  "userId": "user_456",
  "deviceId": "device_789",
  "quality": "auto"
}

// Response
{
  "sessionId": "session_abc",
  "manifestUrl": "https://cdn.example.com/video_123/master.m3u8?session=abc",
  "drmLicense": "https://license.example.com/session/abc",
  "analytics": "https://analytics.example.com/session/abc",
  "expiresAt": "2025-11-20T00:00:00Z"
}
```

### Analytics Event API
```javascript
// POST /api/v1/analytics/events
{
  "sessionId": "session_abc",
  "eventType": "video_start",
  "timestamp": 1700000000,
  "metadata": {
    "videoId": "video_123",
    "bitrate": 5000000,
    "resolution": "1920x1080",
    "startupTime": 1200
  }
}
```

## Best Practices

1. **Use RESTful conventions** for predictable APIs
2. **Version APIs** (/api/v1/, /api/v2/)
3. **Include pagination** for list endpoints
4. **Return detailed errors** with error codes
5. **Use HTTPS** for all endpoints
6. **Implement rate limiting** (per user/IP)
7. **Support CORS** for web players
8. **Cache responses** appropriately

**Version**: 1.0
