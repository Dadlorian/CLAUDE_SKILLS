// video-streaming-scenario.js - Netflix-style video streaming load test
import http from 'k6/http';
import { check, group, sleep } from 'k6';
import { Rate, Trend, Counter } from 'k6/metrics';

// Custom metrics
let streamStartTime = new Trend('stream_start_time');
let bufferEvents = new Rate('buffer_events');
let videoQuality = new Trend('video_quality_mbps');
let concurrentStreams = new Counter('concurrent_streams');
let chunkDownloadTime = new Trend('chunk_download_time');

export let options = {
  stages: [
    { duration: '2m', target: 1000 },   // Early evening
    { duration: '10m', target: 5000 },  // Prime time start
    { duration: '20m', target: 10000 }, // Peak viewing
    { duration: '10m', target: 5000 },  // Late evening
    { duration: '2m', target: 0 },      // Night
  ],
  thresholds: {
    'stream_start_time': ['p(90)<1000', 'p(99)<2000'],  // Sub-second start
    'buffer_events': ['rate<0.005'],  // < 0.5% rebuffer rate
    'http_req_duration{type:manifest}': ['p(95)<200'],
    'http_req_duration{type:chunk}': ['p(95)<500'],
    'chunk_download_time': ['p(95)<400'],
  },
};

const CDN_URL = __ENV.CDN_URL || 'https://test-api.k6.io';
const API_URL = __ENV.API_URL || 'https://test-api.k6.io';

// Video catalog
const videos = [
  { id: 1, title: 'Action Movie', duration: 7200, quality: ['4K', 'HD', 'SD'] },
  { id: 2, title: 'Drama Series S01E01', duration: 2700, quality: ['HD', 'SD'] },
  { id: 3, title: 'Documentary', duration: 5400, quality: ['4K', 'HD', 'SD'] },
  { id: 4, title: 'Comedy Special', duration: 3600, quality: ['HD', 'SD'] },
];

export default function() {
  let video = videos[Math.floor(Math.random() * videos.length)];
  let quality = video.quality[Math.floor(Math.random() * video.quality.length)];
  let sessionData = {};

  // 1. Browse catalog
  group('Browse Catalog', function() {
    let res = http.get(`${API_URL}/catalog`, {
      tags: { type: 'api' },
    });

    check(res, {
      'catalog loaded': (r) => r.status === 200,
    });

    sleep(5);  // User browses
  });

  // 2. Get video details
  group('Video Details', function() {
    let res = http.get(`${API_URL}/videos/${video.id}`, {
      tags: { type: 'api' },
    });

    check(res, {
      'video details loaded': (r) => r.status === 200,
    });

    sleep(3);  // User reads description
  });

  // 3. Start playback
  group('Video Playback', function() {
    // Request video manifest (adaptive streaming)
    let manifestStart = Date.now();
    let manifest = http.get(`${CDN_URL}/videos/${video.id}/manifest.mpd`, {
      tags: { type: 'manifest' },
    });

    check(manifest, {
      'manifest loaded': (r) => r.status === 200,
      'manifest valid': (r) => r.body.length > 0,
    });

    let startTime = Date.now() - manifestStart;
    streamStartTime.add(startTime);
    concurrentStreams.add(1);

    // Simulate video streaming (chunks)
    // Each chunk = 5 seconds of video
    let watchDuration = Math.min(video.duration, 60);  // Watch up to 60 seconds
    let chunks = Math.floor(watchDuration / 5);

    for (let i = 0; i < chunks; i++) {
      let chunkStart = Date.now();

      let chunkRes = http.get(`${CDN_URL}/videos/${video.id}/${quality}/chunk_${i}.m4s`, {
        tags: { type: 'chunk', quality: quality },
      });

      let chunkSuccess = check(chunkRes, {
        'chunk loaded': (r) => r.status === 200,
        'chunk not empty': (r) => r.body.length > 0,
      });

      if (!chunkSuccess) {
        bufferEvents.add(1);
        console.log(`Buffering event at chunk ${i}`);
      } else {
        bufferEvents.add(0);
      }

      // Track download time
      let downloadTime = Date.now() - chunkStart;
      chunkDownloadTime.add(downloadTime);

      // Simulate quality based on chunk size
      let qualityMbps = quality === '4K' ? 25 : quality === 'HD' ? 8 : 3;
      videoQuality.add(qualityMbps);

      // 5 seconds per chunk
      sleep(5);

      // Random playback stop (30% drop-off)
      if (Math.random() < 0.3) {
        console.log(`User stopped watching at ${(i + 1) * 5}s`);
        break;
      }
    }

    // Track session end
    concurrentStreams.add(-1);
  });

  // 4. Post-playback (recommendations, ratings)
  if (Math.random() < 0.2) {
    group('Rate Video', function() {
      let payload = JSON.stringify({
        video_id: video.id,
        rating: Math.floor(Math.random() * 5) + 1,
      });

      http.post(`${API_URL}/ratings`, payload, {
        headers: { 'Content-Type': 'application/json' },
        tags: { type: 'api' },
      });

      sleep(1);
    });
  }

  sleep(10);  // User continues browsing
}

export function handleSummary(data) {
  let summary = {
    timestamp: new Date().toISOString(),
    duration: data.state.testRunDurationMs / 1000,
    streaming_metrics: {
      total_requests: data.metrics.http_reqs.values.count,
      stream_start_time: {
        p50: data.metrics.stream_start_time.values['p(50)'],
        p90: data.metrics.stream_start_time.values['p(90)'],
        p99: data.metrics.stream_start_time.values['p(99)'],
      },
      rebuffer_rate: data.metrics.buffer_events.values.rate,
      avg_quality_mbps: data.metrics.video_quality_mbps.values.avg,
      chunk_download: {
        p50: data.metrics.chunk_download_time.values['p(50)'],
        p95: data.metrics.chunk_download_time.values['p(95)'],
      },
    },
    performance: {
      manifest_latency_p95: data.metrics['http_req_duration{type:manifest}'] ?
        data.metrics['http_req_duration{type:manifest}'].values['p(95)'] : null,
      chunk_latency_p95: data.metrics['http_req_duration{type:chunk}'] ?
        data.metrics['http_req_duration{type:chunk}'].values['p(95)'] : null,
    },
  };

  return {
    'video-streaming-results.json': JSON.stringify(summary, null, 2),
    'stdout': `
Video Streaming Load Test Complete
===================================
Stream Start Time (p90): ${summary.streaming_metrics.stream_start_time.p90.toFixed(2)}ms
Rebuffer Rate: ${(summary.streaming_metrics.rebuffer_rate * 100).toFixed(2)}%
Average Quality: ${summary.streaming_metrics.avg_quality_mbps.toFixed(1)} Mbps
Chunk Download (p95): ${summary.streaming_metrics.chunk_download.p95.toFixed(2)}ms
`,
  };
}
