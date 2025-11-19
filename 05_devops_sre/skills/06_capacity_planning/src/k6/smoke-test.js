// smoke-test.js - Minimal load test to verify system works
import http from 'k6/http';
import { check, sleep } from 'k6';

export let options = {
  vus: 1,
  duration: '1m',
  thresholds: {
    http_req_failed: ['rate<0.01'],
    http_req_duration: ['p(99)<1000'],
  },
};

const BASE_URL = __ENV.BASE_URL || 'https://test-api.k6.io';

export default function() {
  // Health check
  let healthRes = http.get(`${BASE_URL}/public/crocodiles/`);
  check(healthRes, {
    'status is 200': (r) => r.status === 200,
    'response has data': (r) => r.body.length > 0,
  });

  sleep(1);
}

export function handleSummary(data) {
  return {
    'stdout': textSummary(data, { indent: ' ', enableColors: true }),
    'smoke-test-results.json': JSON.stringify(data),
  };
}
