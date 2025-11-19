# Complete Load Testing Guide with k6

## Table of Contents
1. [Introduction](#introduction)
2. [Installation](#installation)
3. [Basic Concepts](#basic-concepts)
4. [Test Scenarios](#test-scenarios)
5. [Advanced Features](#advanced-features)
6. [CI/CD Integration](#cicd-integration)
7. [Best Practices](#best-practices)
8. [Real-World Examples](#real-world-examples)

---

## Introduction

k6 is a modern load testing tool built for developers and DevOps teams. Written in Go, it uses JavaScript (ES6+) for scripting and provides excellent performance and developer experience.

### Why k6?

- **High Performance**: 30,000+ VUs per node
- **Developer-Friendly**: JavaScript scripting
- **CI/CD Native**: Designed for automation
- **Protocol Support**: HTTP/1.1, HTTP/2, WebSocket, gRPC
- **Real-Time Metrics**: Built-in Prometheus integration
- **Cloud Integration**: k6 Cloud for distributed testing

---

## Installation

### macOS
```bash
brew install k6
```

### Linux
```bash
# Debian/Ubuntu
sudo gpg -k
sudo gpg --no-default-keyring --keyring /usr/share/keyrings/k6-archive-keyring.gpg --keyserver hkp://keyserver.ubuntu.com:80 --recv-keys C5AD17C747E3415A3642D57D77C6C491D6AC1D69
echo "deb [signed-by=/usr/share/keyrings/k6-archive-keyring.gpg] https://dl.k6.io/deb stable main" | sudo tee /etc/apt/sources.list.d/k6.list
sudo apt-get update
sudo apt-get install k6

# Fedora/CentOS
sudo dnf install https://dl.k6.io/rpm/repo.rpm
sudo dnf install k6
```

### Docker
```bash
docker pull grafana/k6:latest

# Run test
docker run -i grafana/k6:latest run - <script.js
```

### Verify Installation
```bash
k6 version
```

---

## Basic Concepts

### Virtual Users (VUs)

Virtual Users simulate concurrent users executing your test script.

```javascript
export let options = {
  vus: 10,        // 10 concurrent users
  duration: '30s', // Run for 30 seconds
};

export default function() {
  // Each VU executes this function repeatedly
  http.get('https://test.k6.io');
}
```

### Test Lifecycle

```javascript
// 1. init code (executed once per VU)
import http from 'k6/http';
import { check, sleep } from 'k6';

// 2. setup code (executed once)
export function setup() {
  let res = http.get('https://api.example.com/setup');
  return { data: res.json() };
}

// 3. VU code (executed repeatedly)
export default function(data) {
  let res = http.get('https://api.example.com/users');
  check(res, { 'status is 200': (r) => r.status === 200 });
  sleep(1);
}

// 4. teardown code (executed once)
export function teardown(data) {
  http.post('https://api.example.com/cleanup', JSON.stringify(data));
}
```

### Metrics

k6 provides built-in metrics:

```javascript
// Built-in metrics
- http_req_duration       // Request duration
- http_req_failed        // Failed request rate
- http_reqs              // Requests per second
- vus                    // Active virtual users
- vus_max                // Maximum VUs
- data_received          // Data received
- data_sent              // Data sent
- iteration_duration     // Iteration time
```

### Checks vs. Thresholds

**Checks**: Validate responses (don't stop test)
```javascript
check(response, {
  'status is 200': (r) => r.status === 200,
  'response time < 500ms': (r) => r.timings.duration < 500,
});
```

**Thresholds**: Pass/fail criteria (stop test if failed)
```javascript
export let options = {
  thresholds: {
    http_req_duration: ['p(95)<500'],  // 95% of requests < 500ms
    http_req_failed: ['rate<0.01'],    // Error rate < 1%
  },
};
```

---

## Test Scenarios

### 1. Smoke Test
Verify system works with minimal load.

```javascript
// smoke-test.js
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

export default function() {
  let res = http.get('https://api.example.com/health');
  check(res, {
    'status is 200': (r) => r.status === 200,
    'response has data': (r) => r.body.length > 0,
  });
  sleep(1);
}
```

**Run:**
```bash
k6 run smoke-test.js
```

### 2. Load Test
Test system under expected load.

```javascript
// load-test.js
import http from 'k6/http';
import { check, sleep } from 'k6';

export let options = {
  stages: [
    { duration: '2m', target: 100 },   // Ramp up to 100 users
    { duration: '5m', target: 100 },   // Stay at 100 users
    { duration: '2m', target: 200 },   // Ramp to 200 users
    { duration: '5m', target: 200 },   // Stay at 200 users
    { duration: '2m', target: 0 },     // Ramp down to 0
  ],
  thresholds: {
    http_req_duration: ['p(95)<500', 'p(99)<1000'],
    http_req_failed: ['rate<0.01'],
    http_reqs: ['rate>100'],  // Minimum 100 RPS
  },
};

export default function() {
  let res = http.get('https://api.example.com/users');
  check(res, {
    'status is 200': (r) => r.status === 200,
  });
  sleep(1);
}
```

**Run:**
```bash
k6 run load-test.js
```

### 3. Stress Test
Find system breaking point.

```javascript
// stress-test.js
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
    http_req_duration: ['p(99)<2000'],  // More lenient threshold
  },
};

export default function() {
  let res = http.get('https://api.example.com/users');
  check(res, { 'status is 200': (r) => r.status === 200 });
  sleep(1);
}
```

### 4. Spike Test
Test sudden traffic increases.

```javascript
// spike-test.js
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
    http_req_duration: ['p(99)<1000'],
    http_req_failed: ['rate<0.05'],  // Allow 5% errors during spike
  },
};

export default function() {
  let res = http.get('https://api.example.com/users');
  check(res, { 'status is 200': (r) => r.status === 200 });
  sleep(1);
}
```

### 5. Soak Test
Test long-term stability.

```javascript
// soak-test.js
import http from 'k6/http';
import { check, sleep } from 'k6';

export let options = {
  stages: [
    { duration: '2m', target: 400 },    // Ramp up
    { duration: '3h56m', target: 400 }, // Stay for ~4 hours
    { duration: '2m', target: 0 },      // Ramp down
  ],
  thresholds: {
    http_req_duration: ['p(95)<500'],
    http_req_failed: ['rate<0.01'],
  },
};

export default function() {
  let res = http.get('https://api.example.com/users');
  check(res, { 'status is 200': (r) => r.status === 200 });
  sleep(1);
}
```

**Run:**
```bash
# Run in background and save results
nohup k6 run soak-test.js > soak-test-results.txt 2>&1 &
```

---

## Advanced Features

### Custom Metrics

```javascript
import http from 'k6/http';
import { Trend, Rate, Counter, Gauge } from 'k6/metrics';

// Define custom metrics
let myTrend = new Trend('waiting_time');
let myRate = new Rate('error_rate');
let myCounter = new Counter('total_requests');
let myGauge = new Gauge('active_connections');

export default function() {
  let start = new Date();
  let res = http.get('https://api.example.com/users');
  let duration = new Date() - start;

  myTrend.add(duration);
  myRate.add(res.status !== 200);
  myCounter.add(1);
  myGauge.add(10);  // Example: track connections
}
```

### HTTP Request Options

```javascript
import http from 'k6/http';

export default function() {
  let params = {
    headers: {
      'Content-Type': 'application/json',
      'Authorization': 'Bearer token123',
    },
    tags: {
      name: 'UserAPI',
      endpoint: '/users',
    },
    timeout: '60s',
  };

  // GET request
  let res = http.get('https://api.example.com/users', params);

  // POST request
  let payload = JSON.stringify({
    name: 'John Doe',
    email: 'john@example.com',
  });
  res = http.post('https://api.example.com/users', payload, params);

  // Multiple requests in batch
  let responses = http.batch([
    ['GET', 'https://api.example.com/users/1', null, params],
    ['GET', 'https://api.example.com/users/2', null, params],
    ['GET', 'https://api.example.com/users/3', null, params],
  ]);
}
```

### Authentication

#### Bearer Token
```javascript
import http from 'k6/http';

export default function() {
  let params = {
    headers: {
      'Authorization': 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...',
    },
  };
  http.get('https://api.example.com/protected', params);
}
```

#### Login Flow
```javascript
import http from 'k6/http';
import { check } from 'k6';

export function setup() {
  // Login once and get token
  let loginRes = http.post('https://api.example.com/login', JSON.stringify({
    username: 'testuser',
    password: 'password123',
  }), {
    headers: { 'Content-Type': 'application/json' },
  });

  check(loginRes, { 'login successful': (r) => r.status === 200 });

  return { token: loginRes.json('token') };
}

export default function(data) {
  let params = {
    headers: {
      'Authorization': `Bearer ${data.token}`,
    },
  };
  http.get('https://api.example.com/users', params);
}
```

### Data Parameterization

```javascript
import http from 'k6/http';
import { SharedArray } from 'k6/data';
import papaparse from 'https://jslib.k6.io/papaparse/5.1.1/index.js';

// Load CSV data once
const users = new SharedArray('users', function() {
  return papaparse.parse(open('./users.csv'), { header: true }).data;
});

export default function() {
  // Get random user
  let user = users[Math.floor(Math.random() * users.length)];

  let payload = JSON.stringify({
    username: user.username,
    email: user.email,
  });

  http.post('https://api.example.com/users', payload, {
    headers: { 'Content-Type': 'application/json' },
  });
}
```

### Response Validation

```javascript
import http from 'k6/http';
import { check } from 'k6';

export default function() {
  let res = http.get('https://api.example.com/users/1');

  check(res, {
    // Status checks
    'status is 200': (r) => r.status === 200,

    // Response time checks
    'response time < 500ms': (r) => r.timings.duration < 500,

    // Body checks
    'has user id': (r) => r.json('id') !== undefined,
    'has email': (r) => r.json('email') !== undefined,

    // Header checks
    'has content-type': (r) => r.headers['Content-Type'] !== undefined,

    // Regex checks
    'email format valid': (r) => /\S+@\S+\.\S+/.test(r.json('email')),
  });
}
```

### Scenarios (Advanced Load Patterns)

```javascript
import http from 'k6/http';

export let options = {
  scenarios: {
    // Constant VUs
    constant_load: {
      executor: 'constant-vus',
      vus: 50,
      duration: '5m',
      gracefulStop: '30s',
    },

    // Ramping VUs
    ramping_load: {
      executor: 'ramping-vus',
      startVUs: 0,
      stages: [
        { duration: '2m', target: 100 },
        { duration: '5m', target: 100 },
        { duration: '2m', target: 0 },
      ],
      gracefulRampDown: '30s',
    },

    // Constant request rate
    constant_rps: {
      executor: 'constant-arrival-rate',
      rate: 100,           // 100 requests per timeUnit
      timeUnit: '1s',      // per second
      duration: '10m',
      preAllocatedVUs: 50,
      maxVUs: 200,
    },

    // Ramping request rate
    ramping_rps: {
      executor: 'ramping-arrival-rate',
      startRate: 0,
      timeUnit: '1s',
      preAllocatedVUs: 50,
      maxVUs: 500,
      stages: [
        { duration: '2m', target: 100 },
        { duration: '5m', target: 200 },
        { duration: '2m', target: 0 },
      ],
    },

    // Per-VU iterations
    shared_iterations: {
      executor: 'shared-iterations',
      vus: 10,
      iterations: 1000,  // Total iterations shared among VUs
      maxDuration: '10m',
    },
  },
};

export default function() {
  http.get('https://test.k6.io');
}
```

---

## CI/CD Integration

### GitHub Actions

```yaml
# .github/workflows/load-test.yml
name: Load Testing

on:
  pull_request:
    branches: [main]
  schedule:
    - cron: '0 0 * * *'  # Daily

jobs:
  load-test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Install k6
        run: |
          sudo gpg -k
          sudo gpg --no-default-keyring --keyring /usr/share/keyrings/k6-archive-keyring.gpg --keyserver hkp://keyserver.ubuntu.com:80 --recv-keys C5AD17C747E3415A3642D57D77C6C491D6AC1D69
          echo "deb [signed-by=/usr/share/keyrings/k6-archive-keyring.gpg] https://dl.k6.io/deb stable main" | sudo tee /etc/apt/sources.list.d/k6.list
          sudo apt-get update
          sudo apt-get install k6

      - name: Run k6 load test
        run: k6 run tests/load-test.js

      - name: Upload results
        if: always()
        uses: actions/upload-artifact@v3
        with:
          name: k6-results
          path: '*.json'
```

### GitLab CI

```yaml
# .gitlab-ci.yml
load-test:
  image: grafana/k6:latest
  stage: test
  script:
    - k6 run --out json=results.json tests/load-test.js
  artifacts:
    paths:
      - results.json
    expire_in: 1 week
  only:
    - merge_requests
    - schedules
```

### Jenkins Pipeline

```groovy
// Jenkinsfile
pipeline {
  agent any

  stages {
    stage('Load Test') {
      steps {
        script {
          docker.image('grafana/k6:latest').inside {
            sh 'k6 run --out json=results.json tests/load-test.js'
          }
        }
      }
    }

    stage('Analyze Results') {
      steps {
        script {
          def results = readJSON file: 'results.json'
          def p95 = results.metrics.http_req_duration.values.p95
          if (p95 > 500) {
            error("Performance regression detected: p95=${p95}ms")
          }
        }
      }
    }
  }

  post {
    always {
      archiveArtifacts artifacts: 'results.json', fingerprint: true
    }
  }
}
```

### Output to InfluxDB + Grafana

```bash
# Run k6 with InfluxDB output
k6 run --out influxdb=http://localhost:8086/k6 load-test.js

# With authentication
k6 run --out influxdb=http://localhost:8086/k6?username=admin&password=secret load-test.js
```

**Grafana Dashboard:**
```json
{
  "dashboard": {
    "title": "k6 Load Test Results",
    "panels": [
      {
        "title": "Virtual Users",
        "targets": [{"query": "SELECT mean(\"value\") FROM \"vus\" WHERE $timeFilter GROUP BY time($__interval)"}]
      },
      {
        "title": "Request Rate",
        "targets": [{"query": "SELECT mean(\"rate\") FROM \"http_reqs\" WHERE $timeFilter GROUP BY time($__interval)"}]
      },
      {
        "title": "Response Time",
        "targets": [
          {"query": "SELECT percentile(\"value\", 50) FROM \"http_req_duration\" WHERE $timeFilter GROUP BY time($__interval)"},
          {"query": "SELECT percentile(\"value\", 95) FROM \"http_req_duration\" WHERE $timeFilter GROUP BY time($__interval)"},
          {"query": "SELECT percentile(\"value\", 99) FROM \"http_req_duration\" WHERE $timeFilter GROUP BY time($__interval)"}
        ]
      }
    ]
  }
}
```

---

## Best Practices

### 1. Test Environment
```yaml
DO:
  - Test in production-like environment
  - Use same infrastructure setup
  - Test with production data volumes
  - Replicate network topology

DON'T:
  - Test against production (unless chaos engineering)
  - Use undersized test environment
  - Test with minimal data
  - Ignore network conditions
```

### 2. Test Design
```javascript
// Good: Realistic user behavior
export default function() {
  // Browse homepage
  http.get('https://example.com/');
  sleep(2);

  // Search for product
  http.get('https://example.com/search?q=laptop');
  sleep(3);

  // View product
  http.get('https://example.com/products/123');
  sleep(5);

  // Add to cart
  http.post('https://example.com/cart', JSON.stringify({
    product_id: 123,
    quantity: 1,
  }));
  sleep(1);
}

// Bad: Unrealistic hammering
export default function() {
  http.get('https://example.com/api/endpoint');
  http.get('https://example.com/api/endpoint');
  http.get('https://example.com/api/endpoint');
  // No sleep, unrealistic pattern
}
```

### 3. Gradual Load Increase
```javascript
export let options = {
  stages: [
    { duration: '5m', target: 100 },   // Gradual ramp
    { duration: '10m', target: 100 },  // Sustain
    { duration: '5m', target: 200 },   // Gradual increase
    { duration: '10m', target: 200 },  // Sustain
    { duration: '5m', target: 0 },     // Gradual ramp down
  ],
};

// Not recommended: Instant spike (unless spike testing)
export let options = {
  stages: [
    { duration: '1s', target: 1000 },  // Too fast
  ],
};
```

### 4. Monitoring During Tests
```bash
# Monitor system metrics during test
- CPU utilization
- Memory usage
- Network I/O
- Disk I/O
- Application logs
- Database performance
- Cache hit rate
```

### 5. Think Time / Sleep
```javascript
// Realistic user think time
export default function() {
  http.get('https://example.com/page1');
  sleep(Math.random() * 5 + 2);  // 2-7 seconds

  http.get('https://example.com/page2');
  sleep(Math.random() * 3 + 1);  // 1-4 seconds
}
```

### 6. Error Handling
```javascript
import { check, fail } from 'k6';
import http from 'k6/http';

export default function() {
  let res = http.get('https://api.example.com/users');

  if (!check(res, { 'status is 200': (r) => r.status === 200 })) {
    console.error(`Request failed: ${res.status} ${res.body}`);
    // Don't fail entire test, just log and continue
  }

  // Only fail on critical errors
  if (res.status === 500) {
    fail('Server error detected');
  }
}
```

---

## Real-World Examples

### Example 1: E-Commerce Load Test

```javascript
// ecommerce-load-test.js
import http from 'k6/http';
import { check, group, sleep } from 'k6';
import { Rate, Trend } from 'k6/metrics';

// Custom metrics
let checkoutErrors = new Rate('checkout_errors');
let checkoutDuration = new Trend('checkout_duration');

export let options = {
  stages: [
    { duration: '5m', target: 100 },   // Black Friday ramp up
    { duration: '15m', target: 500 },  // Peak shopping
    { duration: '10m', target: 1000 }, // Flash sale spike
    { duration: '15m', target: 500 },  // Cool down
    { duration: '5m', target: 0 },
  ],
  thresholds: {
    'http_req_duration': ['p(95)<1000', 'p(99)<2000'],
    'checkout_errors': ['rate<0.01'],
    'group_duration{group:::Checkout}': ['p(95)<3000'],
  },
};

const BASE_URL = 'https://api.example.com';

export function setup() {
  // Load product catalog
  let res = http.get(`${BASE_URL}/products`);
  return {
    products: res.json(),
  };
}

export default function(data) {
  let product = data.products[Math.floor(Math.random() * data.products.length)];

  group('Homepage', function() {
    let res = http.get(`${BASE_URL}/`);
    check(res, { 'homepage loaded': (r) => r.status === 200 });
    sleep(2);
  });

  group('Product Search', function() {
    let res = http.get(`${BASE_URL}/search?q=${product.category}`);
    check(res, {
      'search successful': (r) => r.status === 200,
      'results returned': (r) => r.json('results').length > 0,
    });
    sleep(3);
  });

  group('Product Detail', function() {
    let res = http.get(`${BASE_URL}/products/${product.id}`);
    check(res, {
      'product loaded': (r) => r.status === 200,
      'product available': (r) => r.json('stock') > 0,
    });
    sleep(5);
  });

  group('Add to Cart', function() {
    let res = http.post(`${BASE_URL}/cart`, JSON.stringify({
      product_id: product.id,
      quantity: 1,
    }), {
      headers: { 'Content-Type': 'application/json' },
    });
    check(res, { 'added to cart': (r) => r.status === 200 });
    sleep(2);
  });

  // Only 30% proceed to checkout
  if (Math.random() < 0.3) {
    group('Checkout', function() {
      let start = new Date();
      let res = http.post(`${BASE_URL}/checkout`, JSON.stringify({
        payment_method: 'credit_card',
        shipping_address: 'Test Address',
      }), {
        headers: { 'Content-Type': 'application/json' },
      });

      let success = check(res, {
        'checkout successful': (r) => r.status === 200,
      });

      checkoutErrors.add(!success);
      checkoutDuration.add(new Date() - start);
      sleep(1);
    });
  }

  sleep(1);
}

export function teardown(data) {
  // Cleanup test data
  console.log('Test completed');
}
```

### Example 2: API Microservices Test

```javascript
// microservices-test.js
import http from 'k6/http';
import { check, group } from 'k6';
import { Counter, Trend } from 'k6/metrics';

// Custom metrics per service
let userServiceCalls = new Counter('user_service_calls');
let orderServiceCalls = new Counter('order_service_calls');
let inventoryServiceCalls = new Counter('inventory_service_calls');

export let options = {
  scenarios: {
    user_service: {
      executor: 'constant-arrival-rate',
      rate: 100,
      timeUnit: '1s',
      duration: '10m',
      preAllocatedVUs: 50,
      maxVUs: 200,
      exec: 'userServiceTest',
    },
    order_service: {
      executor: 'constant-arrival-rate',
      rate: 50,
      timeUnit: '1s',
      duration: '10m',
      preAllocatedVUs: 25,
      maxVUs: 100,
      exec: 'orderServiceTest',
    },
    inventory_service: {
      executor: 'constant-arrival-rate',
      rate: 75,
      timeUnit: '1s',
      duration: '10m',
      preAllocatedVUs: 35,
      maxVUs: 150,
      exec: 'inventoryServiceTest',
    },
  },
  thresholds: {
    'http_req_duration{service:user}': ['p(95)<200'],
    'http_req_duration{service:order}': ['p(95)<500'],
    'http_req_duration{service:inventory}': ['p(95)<100'],
  },
};

const BASE_URL = 'https://api.example.com';

export function userServiceTest() {
  let res = http.get(`${BASE_URL}/users/${Math.floor(Math.random() * 10000)}`, {
    tags: { service: 'user' },
  });
  check(res, { 'user service ok': (r) => r.status === 200 });
  userServiceCalls.add(1);
}

export function orderServiceTest() {
  let res = http.get(`${BASE_URL}/orders/${Math.floor(Math.random() * 50000)}`, {
    tags: { service: 'order' },
  });
  check(res, { 'order service ok': (r) => r.status === 200 });
  orderServiceCalls.add(1);
}

export function inventoryServiceTest() {
  let res = http.get(`${BASE_URL}/inventory/${Math.floor(Math.random() * 5000)}`, {
    tags: { service: 'inventory' },
  });
  check(res, { 'inventory service ok': (r) => r.status === 200 });
  inventoryServiceCalls.add(1);
}
```

### Example 3: Netflix-Style Video Streaming Test

```javascript
// video-streaming-test.js
import http from 'k6/http';
import { check, group, sleep } from 'k6';
import { Rate, Trend } from 'k6/metrics';

// Custom metrics
let streamStartTime = new Trend('stream_start_time');
let bufferEvents = new Rate('buffer_events');
let videoQuality = new Trend('video_quality');

export let options = {
  stages: [
    { duration: '2m', target: 1000 },   // Prime time start
    { duration: '10m', target: 5000 },  // Peak viewing
    { duration: '20m', target: 10000 }, // Maximum concurrent streams
    { duration: '10m', target: 5000 },
    { duration: '2m', target: 0 },
  ],
  thresholds: {
    'stream_start_time': ['p(90)<1000', 'p(99)<2000'],
    'buffer_events': ['rate<0.005'],  // < 0.5% rebuffer rate
    'http_req_duration{type:manifest}': ['p(95)<200'],
    'http_req_duration{type:chunk}': ['p(95)<500'],
  },
};

const CDN_URL = 'https://cdn.example.com';
const API_URL = 'https://api.example.com';

export function setup() {
  // Get available content
  let res = http.get(`${API_URL}/catalog`);
  return { videos: res.json() };
}

export default function(data) {
  let video = data.videos[Math.floor(Math.random() * data.videos.length)];

  group('Browse Catalog', function() {
    http.get(`${API_URL}/catalog`, { tags: { type: 'api' } });
    sleep(5);
  });

  group('Video Playback', function() {
    // Request video manifest
    let manifestStart = new Date();
    let manifest = http.get(`${CDN_URL}/videos/${video.id}/manifest.mpd`, {
      tags: { type: 'manifest' },
    });
    check(manifest, { 'manifest loaded': (r) => r.status === 200 });

    let startTime = new Date() - manifestStart;
    streamStartTime.add(startTime);

    // Simulate streaming chunks (30 seconds of playback = 6 chunks at 5s each)
    for (let i = 0; i < 6; i++) {
      let chunkRes = http.get(`${CDN_URL}/videos/${video.id}/chunk_${i}.m4s`, {
        tags: { type: 'chunk' },
      });

      let chunkSuccess = check(chunkRes, {
        'chunk loaded': (r) => r.status === 200,
      });

      if (!chunkSuccess) {
        bufferEvents.add(1);
      }

      // Track video quality (simulated)
      videoQuality.add(chunkRes.body.length);

      sleep(5);  // 5 seconds per chunk
    }
  });

  sleep(10);  // User continues browsing
}
```

---

## Troubleshooting

### High Memory Usage
```bash
# Use SharedArray for large datasets
import { SharedArray } from 'k6/data';

const data = new SharedArray('data', function() {
  return JSON.parse(open('./large-file.json'));
});
```

### Slow Test Execution
```bash
# Enable HTTP/2
export let options = {
  insecureSkipTLSVerify: true,
  noConnectionReuse: false,
};

# Use batch requests
http.batch([
  ['GET', 'url1'],
  ['GET', 'url2'],
  ['GET', 'url3'],
]);
```

### Failed Checks Not Failing Test
```bash
# Use thresholds instead
export let options = {
  thresholds: {
    checks: ['rate>0.95'],  // 95% of checks must pass
  },
};
```

---

## References

- [k6 Documentation](https://k6.io/docs/)
- [k6 Examples](https://k6.io/docs/examples/)
- [k6 Cloud](https://k6.io/cloud/)
- [Awesome k6](https://github.com/grafana/awesome-k6)
- [Netflix Tech Blog - Performance](https://netflixtechblog.com/)
