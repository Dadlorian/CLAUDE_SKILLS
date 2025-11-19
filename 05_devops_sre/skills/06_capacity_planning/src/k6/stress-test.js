// stress-test.js - Find breaking point of the system
import http from 'k6/http';
import { check, sleep } from 'k6';

export let options = {
  stages: [
    { duration: '2m', target: 100 },    // Normal load
    { duration: '5m', target: 100 },
    { duration: '2m', target: 200 },    // Increased load
    { duration: '5m', target: 200 },
    { duration: '2m', target: 300 },    // High load
    { duration: '5m', target: 300 },
    { duration: '2m', target: 400 },    // Extreme load
    { duration: '5m', target: 400 },
    { duration: '10m', target: 0 },     // Recovery
  ],
  thresholds: {
    'http_req_duration': ['p(99)<2000'],  // More lenient
  },
};

const BASE_URL = __ENV.BASE_URL || 'https://test-api.k6.io';

export default function() {
  let res = http.get(`${BASE_URL}/public/crocodiles/`);

  check(res, {
    'status is 200': (r) => r.status === 200,
  });

  // Log performance degradation
  if (res.timings.duration > 1000) {
    console.log(`Warning: Slow response ${res.timings.duration}ms at ${__VU} VUs`);
  }

  sleep(1);
}

export function handleSummary(data) {
  // Identify breaking point
  let breakingPoint = 'Not found';

  for (let [key, value] of Object.entries(data.metrics)) {
    if (key === 'http_req_duration' && value.values.p95 > 1000) {
      breakingPoint = 'System degraded beyond acceptable limits';
    }
  }

  return {
    'stress-test-results.json': JSON.stringify(data),
    'stdout': `\nStress Test Complete\nBreaking Point: ${breakingPoint}\n`,
  };
}
