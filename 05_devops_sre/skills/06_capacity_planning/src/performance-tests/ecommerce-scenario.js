// ecommerce-scenario.js - E-commerce user journey load test
import http from 'k6/http';
import { check, group, sleep } from 'k6';
import { Rate, Trend, Counter } from 'k6/metrics';

// Custom metrics
let checkoutErrors = new Rate('checkout_errors');
let checkoutDuration = new Trend('checkout_duration');
let cartAbandonment = new Rate('cart_abandonment');
let productViews = new Counter('product_views');

export let options = {
  stages: [
    { duration: '5m', target: 100 },   // Normal shopping hours
    { duration: '10m', target: 500 },  // Peak shopping
    { duration: '5m', target: 1000 },  // Flash sale
    { duration: '10m', target: 500 },
    { duration: '5m', target: 0 },
  ],
  thresholds: {
    'http_req_duration': ['p(95)<1000', 'p(99)<2000'],
    'checkout_errors': ['rate<0.01'],
    'group_duration{group:::Checkout}': ['p(95)<3000'],
    'cart_abandonment': ['rate<0.7'],  // Expect 70% abandonment
  },
};

const BASE_URL = __ENV.BASE_URL || 'https://test-api.k6.io';

// Sample product catalog
const products = [
  { id: 1, name: 'Laptop', category: 'Electronics', price: 999 },
  { id: 2, name: 'Mouse', category: 'Accessories', price: 29 },
  { id: 3, name: 'Keyboard', category: 'Accessories', price: 79 },
  { id: 4, name: 'Monitor', category: 'Electronics', price: 299 },
  { id: 5, name: 'Webcam', category: 'Accessories', price: 89 },
];

export default function() {
  let product = products[Math.floor(Math.random() * products.length)];
  let sessionData = {};

  // 1. Homepage
  group('Homepage', function() {
    let res = http.get(`${BASE_URL}/`);
    check(res, {
      'homepage loaded': (r) => r.status === 200,
    });
    sleep(2);
  });

  // 2. Browse categories
  group('Category Browse', function() {
    let res = http.get(`${BASE_URL}/categories/${product.category}`);
    check(res, {
      'category loaded': (r) => r.status === 200,
    });
    sleep(3);
  });

  // 3. Product search
  group('Product Search', function() {
    let res = http.get(`${BASE_URL}/search?q=${product.name}`);
    check(res, {
      'search successful': (r) => r.status === 200,
    });
    sleep(2);
  });

  // 4. View product details
  group('Product Detail', function() {
    let res = http.get(`${BASE_URL}/products/${product.id}`);
    check(res, {
      'product loaded': (r) => r.status === 200,
    });
    productViews.add(1);
    sleep(5);
  });

  // 5. Add to cart (80% of users)
  if (Math.random() < 0.8) {
    group('Add to Cart', function() {
      let payload = JSON.stringify({
        product_id: product.id,
        quantity: 1,
      });

      let res = http.post(`${BASE_URL}/cart`, payload, {
        headers: { 'Content-Type': 'application/json' },
      });

      let success = check(res, {
        'added to cart': (r) => r.status === 200,
      });

      if (success) {
        sessionData.cartId = res.json('cart_id');
      }

      sleep(2);
    });

    // 6. Proceed to checkout (30% of users with items in cart)
    if (Math.random() < 0.3 && sessionData.cartId) {
      group('Checkout', function() {
        let start = new Date();

        let payload = JSON.stringify({
          cart_id: sessionData.cartId,
          payment_method: 'credit_card',
          shipping_address: {
            street: '123 Test St',
            city: 'Test City',
            zip: '12345',
          },
        });

        let res = http.post(`${BASE_URL}/checkout`, payload, {
          headers: { 'Content-Type': 'application/json' },
        });

        let success = check(res, {
          'checkout successful': (r) => r.status === 200,
          'order id received': (r) => r.json('order_id') !== undefined,
        });

        checkoutErrors.add(!success);
        checkoutDuration.add(new Date() - start);

        sleep(1);
      });
      cartAbandonment.add(0);  // Completed checkout
    } else {
      cartAbandonment.add(1);  // Abandoned cart
    }
  }

  sleep(1);
}

export function handleSummary(data) {
  let summary = {
    timestamp: new Date().toISOString(),
    duration: data.state.testRunDurationMs / 1000,
    metrics: {
      requests: data.metrics.http_reqs.values.count,
      rps: data.metrics.http_reqs.values.rate,
      errors: data.metrics.http_req_failed.values.rate,
      response_time: {
        p95: data.metrics.http_req_duration.values['p(95)'],
        p99: data.metrics.http_req_duration.values['p(99)'],
      },
      checkout_error_rate: data.metrics.checkout_errors.values.rate,
      cart_abandonment_rate: data.metrics.cart_abandonment.values.rate,
      product_views: data.metrics.product_views.values.count,
    },
  };

  return {
    'ecommerce-results.json': JSON.stringify(summary, null, 2),
  };
}
