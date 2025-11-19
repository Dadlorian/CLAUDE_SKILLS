// load-test.js - Standard load test with gradual ramp-up
import http from 'k6/http';
import { check, group, sleep } from 'k6';
import { Rate, Trend, Counter } from 'k6/metrics';

// Custom metrics
let errorRate = new Rate('errors');
let responseTime = new Trend('response_time');
let requestCount = new Counter('requests');

export let options = {
  stages: [
    { duration: '2m', target: 100 },   // Ramp up to 100 users
    { duration: '5m', target: 100 },   // Stay at 100 users
    { duration: '2m', target: 200 },   // Ramp to 200 users
    { duration: '5m', target: 200 },   // Stay at 200 users
    { duration: '2m', target: 0 },     // Ramp down to 0
  ],
  thresholds: {
    'http_req_duration': ['p(95)<500', 'p(99)<1000'],
    'http_req_failed': ['rate<0.01'],
    'errors': ['rate<0.01'],
    'http_reqs': ['rate>100'],  // Minimum 100 RPS
  },
};

const BASE_URL = __ENV.BASE_URL || 'https://test-api.k6.io';

export default function() {
  group('Public API Tests', function() {
    // List crocodiles
    let listRes = http.get(`${BASE_URL}/public/crocodiles/`);
    let success = check(listRes, {
      'status is 200': (r) => r.status === 200,
      'response time < 500ms': (r) => r.timings.duration < 500,
    });

    errorRate.add(!success);
    responseTime.add(listRes.timings.duration);
    requestCount.add(1);

    sleep(1);

    // Get specific crocodile
    let getRes = http.get(`${BASE_URL}/public/crocodiles/1/`);
    check(getRes, {
      'status is 200': (r) => r.status === 200,
      'has id field': (r) => JSON.parse(r.body).id !== undefined,
    });

    sleep(1);
  });
}

export function handleSummary(data) {
  return {
    'load-test-results.json': JSON.stringify(data),
    'load-test-summary.txt': textSummary(data, { indent: ' ', enableColors: false }),
  };
}
