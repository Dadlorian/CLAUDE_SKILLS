// spike-test.js - Test sudden traffic increases
import http from 'k6/http';
import { check, sleep } from 'k6';

export let options = {
  stages: [
    { duration: '10s', target: 100 },   // Normal load
    { duration: '1m', target: 100 },
    { duration: '10s', target: 1400 },  // Spike to 1400 users
    { duration: '3m', target: 1400 },   // Stay at spike
    { duration: '10s', target: 100 },   // Back to normal
    { duration: '3m', target: 100 },
    { duration: '10s', target: 0 },
  ],
  thresholds: {
    'http_req_duration': ['p(99)<1000'],
    'http_req_failed': ['rate<0.05'],  // Allow 5% errors during spike
  },
};

const BASE_URL = __ENV.BASE_URL || 'https://test-api.k6.io';

export default function() {
  let res = http.get(`${BASE_URL}/public/crocodiles/`);

  check(res, {
    'status is 200': (r) => r.status === 200,
  });

  sleep(1);
}

export function handleSummary(data) {
  return {
    'spike-test-results.json': JSON.stringify(data),
  };
}
