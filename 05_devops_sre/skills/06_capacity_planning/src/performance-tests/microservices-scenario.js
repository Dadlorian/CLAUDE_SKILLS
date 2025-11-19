// microservices-scenario.js - Test multiple microservices with different load profiles
import http from 'k6/http';
import { check, group } from 'k6';
import { Counter, Trend } from 'k6/metrics';

// Per-service metrics
let userServiceCalls = new Counter('user_service_calls');
let orderServiceCalls = new Counter('order_service_calls');
let inventoryServiceCalls = new Counter('inventory_service_calls');
let paymentServiceCalls = new Counter('payment_service_calls');

let userServiceLatency = new Trend('user_service_latency');
let orderServiceLatency = new Trend('order_service_latency');
let inventoryServiceLatency = new Trend('inventory_service_latency');
let paymentServiceLatency = new Trend('payment_service_latency');

export let options = {
  scenarios: {
    // User service - High read load
    user_service: {
      executor: 'constant-arrival-rate',
      rate: 200,           // 200 requests per second
      timeUnit: '1s',
      duration: '10m',
      preAllocatedVUs: 100,
      maxVUs: 300,
      exec: 'userServiceTest',
    },

    // Order service - Medium load
    order_service: {
      executor: 'constant-arrival-rate',
      rate: 50,
      timeUnit: '1s',
      duration: '10m',
      preAllocatedVUs: 25,
      maxVUs: 100,
      exec: 'orderServiceTest',
    },

    // Inventory service - High read load
    inventory_service: {
      executor: 'constant-arrival-rate',
      rate: 150,
      timeUnit: '1s',
      duration: '10m',
      preAllocatedVUs: 75,
      maxVUs: 200,
      exec: 'inventoryServiceTest',
    },

    // Payment service - Low load, critical path
    payment_service: {
      executor: 'constant-arrival-rate',
      rate: 20,
      timeUnit: '1s',
      duration: '10m',
      preAllocatedVUs: 10,
      maxVUs: 50,
      exec: 'paymentServiceTest',
    },
  },
  thresholds: {
    'http_req_duration{service:user}': ['p(95)<200'],
    'http_req_duration{service:order}': ['p(95)<500'],
    'http_req_duration{service:inventory}': ['p(95)<100'],
    'http_req_duration{service:payment}': ['p(95)<1000'],
    'http_req_failed{service:payment}': ['rate<0.001'],  // Critical service
  },
};

const BASE_URL = __ENV.BASE_URL || 'https://test-api.k6.io';

// User Service Test
export function userServiceTest() {
  let userId = Math.floor(Math.random() * 10000) + 1;

  group('User Service', function() {
    let start = Date.now();

    let res = http.get(`${BASE_URL}/users/${userId}`, {
      tags: { service: 'user' },
    });

    check(res, {
      'user service ok': (r) => r.status === 200,
      'user has id': (r) => r.json('id') !== undefined,
    });

    userServiceCalls.add(1);
    userServiceLatency.add(Date.now() - start);
  });
}

// Order Service Test
export function orderServiceTest() {
  let orderId = Math.floor(Math.random() * 50000) + 1;

  group('Order Service', function() {
    let start = Date.now();

    // Get order details
    let res = http.get(`${BASE_URL}/orders/${orderId}`, {
      tags: { service: 'order' },
    });

    check(res, {
      'order service ok': (r) => r.status === 200,
    });

    orderServiceCalls.add(1);
    orderServiceLatency.add(Date.now() - start);

    // Create new order (10% of requests)
    if (Math.random() < 0.1) {
      let payload = JSON.stringify({
        user_id: Math.floor(Math.random() * 10000),
        items: [
          { product_id: 1, quantity: 2 },
        ],
      });

      let createRes = http.post(`${BASE_URL}/orders`, payload, {
        headers: { 'Content-Type': 'application/json' },
        tags: { service: 'order' },
      });

      check(createRes, {
        'order created': (r) => r.status === 201,
      });
    }
  });
}

// Inventory Service Test
export function inventoryServiceTest() {
  let productId = Math.floor(Math.random() * 5000) + 1;

  group('Inventory Service', function() {
    let start = Date.now();

    let res = http.get(`${BASE_URL}/inventory/${productId}`, {
      tags: { service: 'inventory' },
    });

    check(res, {
      'inventory service ok': (r) => r.status === 200,
      'has stock info': (r) => r.json('quantity') !== undefined,
    });

    inventoryServiceCalls.add(1);
    inventoryServiceLatency.add(Date.now() - start);
  });
}

// Payment Service Test
export function paymentServiceTest() {
  group('Payment Service', function() {
    let start = Date.now();

    let payload = JSON.stringify({
      order_id: Math.floor(Math.random() * 50000),
      amount: Math.floor(Math.random() * 500) + 10,
      payment_method: 'credit_card',
    });

    let res = http.post(`${BASE_URL}/payments`, payload, {
      headers: { 'Content-Type': 'application/json' },
      tags: { service: 'payment' },
    });

    check(res, {
      'payment processed': (r) => r.status === 200,
      'has transaction id': (r) => r.json('transaction_id') !== undefined,
    });

    paymentServiceCalls.add(1);
    paymentServiceLatency.add(Date.now() - start);
  });
}

export function handleSummary(data) {
  let summary = {
    timestamp: new Date().toISOString(),
    services: {
      user: {
        calls: data.metrics.user_service_calls.values.count,
        avg_latency: data.metrics.user_service_latency.values.avg,
        p95_latency: data.metrics.user_service_latency.values['p(95)'],
      },
      order: {
        calls: data.metrics.order_service_calls.values.count,
        avg_latency: data.metrics.order_service_latency.values.avg,
        p95_latency: data.metrics.order_service_latency.values['p(95)'],
      },
      inventory: {
        calls: data.metrics.inventory_service_calls.values.count,
        avg_latency: data.metrics.inventory_service_latency.values.avg,
        p95_latency: data.metrics.inventory_service_latency.values['p(95)'],
      },
      payment: {
        calls: data.metrics.payment_service_calls.values.count,
        avg_latency: data.metrics.payment_service_latency.values.avg,
        p95_latency: data.metrics.payment_service_latency.values['p(95)'],
      },
    },
  };

  return {
    'microservices-results.json': JSON.stringify(summary, null, 2),
  };
}
