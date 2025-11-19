// Simple RTMP to HLS Live Streaming Server

const NodeMediaServer = require('node-media-server');
const express = require('express');
const cors = require('cors');

// RTMP Server Configuration
const nmsConfig = {
  rtmp: {
    port: 1935,
    chunk_size: 60000,
    gop_cache: true,
    ping: 30,
    ping_timeout: 60
  },
  http: {
    port: 8000,
    mediaroot: './media',
    allow_origin: '*'
  },
  trans: {
    ffmpeg: '/usr/bin/ffmpeg',
    tasks: [
      {
        app: 'live',
        hls: true,
        hlsFlags: '[hls_time=2:hls_list_size=3:hls_flags=delete_segments]',
        hlsKeep: false,
        dash: false
      }
    ]
  }
};

const nms = new NodeMediaServer(nmsConfig);

// Authentication
const validStreamKeys = new Set(['secret_key_123', 'secret_key_456']);

nms.on('prePublish', (id, StreamPath, args) => {
  console.log('[Publish Request]', StreamPath, args);
  
  const streamKey = args.key;
  
  if (!validStreamKeys.has(streamKey)) {
    console.log('[Reject] Invalid stream key:', streamKey);
    const session = nms.getSession(id);
    session.reject();
    return;
  }
  
  console.log('[Accept] Valid stream key');
});

// Stream Events
nms.on('postPublish', (id, StreamPath, args) => {
  console.log('[Stream Started]', StreamPath);
  
  // Notify subscribers
  notifyStreamStart(StreamPath, args);
});

nms.on('donePublish', (id, StreamPath, args) => {
  console.log('[Stream Ended]', StreamPath);
  
  // Notify subscribers
  notifyStreamEnd(StreamPath, args);
});

// Health Monitoring
nms.on('prePlay', (id, StreamPath, args) => {
  console.log('[Viewer Connected]', StreamPath);
});

// Start Server
nms.run();

// API Server for stream info
const app = express();
app.use(cors());
app.use(express.json());

// Get active streams
app.get('/api/streams', (req, res) => {
  const streams = [];
  const sessions = nms.getSession();
  
  for (const [id, session] of Object.entries(sessions)) {
    if (session.isPublishing) {
      streams.push({
        id: id,
        app: session.appname,
        stream: session.streamname,
        viewers: session.subscribers.length,
        startTime: session.startTime
      });
    }
  }
  
  res.json({ streams });
});

// Get stream status
app.get('/api/streams/:streamId/status', (req, res) => {
  const streamId = req.params.streamId;
  const session = nms.getSession(streamId);
  
  if (!session) {
    return res.status(404).json({ error: 'Stream not found' });
  }
  
  res.json({
    id: streamId,
    isLive: session.isPublishing,
    viewers: session.subscribers.length,
    duration: Date.now() - session.startTime,
    bitrate: session.video?.bitrate || 0
  });
});

app.listen(3000, () => {
  console.log('API Server running on port 3000');
});

function notifyStreamStart(streamPath, args) {
  // Send webhook, push notification, etc.
  console.log('TODO: Notify stream start');
}

function notifyStreamEnd(streamPath, args) {
  // Send webhook, update database, etc.
  console.log('TODO: Notify stream end');
}
