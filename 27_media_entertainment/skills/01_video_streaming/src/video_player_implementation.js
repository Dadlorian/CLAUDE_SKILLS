// Complete Video.js Player with Analytics

const player = videojs('my-video', {
  controls: true,
  autoplay: false,
  preload: 'metadata',
  fluid: true,
  responsive: true
});

// Load HLS stream
player.src({
  src: 'https://cdn.example.com/master.m3u8',
  type: 'application/x-mpegURL'
});

// Quality of Experience (QoE) Tracking
const qoeMetrics = {
  playRequestTime: null,
  videoStartTime: null,
  rebufferCount: 0,
  rebufferDuration: 0,
  bitrateChanges: [],
  errors: []
};

// Track video start time
player.on('loadstart', () => {
  qoeMetrics.playRequestTime = performance.now();
});

player.on('canplay', () => {
  if (!qoeMetrics.videoStartTime) {
    qoeMetrics.videoStartTime = performance.now() - qoeMetrics.playRequestTime;
    console.log('Video Start Time:', qoeMetrics.videoStartTime, 'ms');
    
    // Send to analytics
    sendAnalytics('video_start', {
      startupTime: qoeMetrics.videoStartTime,
      videoId: getVideoId()
    });
  }
});

// Track rebuffering
let rebufferStart = null;
player.on('waiting', () => {
  rebufferStart = performance.now();
  qoeMetrics.rebufferCount++;
});

player.on('playing', () => {
  if (rebufferStart) {
    const rebufferTime = performance.now() - rebufferStart;
    qoeMetrics.rebufferDuration += rebufferTime;
    rebufferStart = null;
    
    console.log('Rebuffer event:', rebufferTime, 'ms');
    sendAnalytics('rebuffer', {
      duration: rebufferTime,
      totalRebuffers: qoeMetrics.rebufferCount
    });
  }
});

// Track errors
player.on('error', (e) => {
  const error = player.error();
  qoeMetrics.errors.push({
    code: error.code,
    message: error.message,
    timestamp: Date.now()
  });
  
  console.error('Playback error:', error);
  sendAnalytics('error', {
    errorCode: error.code,
    errorMessage: error.message
  });
});

// Track quality changes
player.on('qualitychange', () => {
  const quality = player.currentQuality();
  qoeMetrics.bitrateChanges.push({
    quality: quality,
    timestamp: Date.now()
  });
  
  console.log('Quality changed to:', quality);
});

// Send analytics to backend
function sendAnalytics(eventType, data) {
  fetch('/api/analytics/events', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({
      eventType,
      timestamp: Date.now(),
      videoId: getVideoId(),
      sessionId: getSessionId(),
      ...data
    })
  });
}

function getVideoId() {
  return document.querySelector('[data-video-id]').dataset.videoId;
}

function getSessionId() {
  return player.techGet_('sessionId') || generateSessionId();
}

// Report final metrics on page unload
window.addEventListener('beforeunload', () => {
  sendAnalytics('session_end', {
    totalRebuffers: qoeMetrics.rebufferCount,
    totalRebufferDuration: qoeMetrics.rebufferDuration,
    bitrateChanges: qoeMetrics.bitrateChanges.length,
    errors: qoeMetrics.errors.length,
    watchTime: player.currentTime()
  });
});
