#!/usr/bin/env python3
"""
Custom Prometheus Exporter Example
Demonstrates how to create a custom exporter for application-specific metrics
"""

import time
import random
from prometheus_client import start_http_server, Gauge, Counter, Histogram, Summary, Enum, Info
from prometheus_client.core import GaugeMetricFamily, CounterMetricFamily, REGISTRY
import psutil
import requests

# =============================================================================
# Basic Metrics (using built-in collectors)
# =============================================================================

# Gauge - Can go up and down
active_users = Gauge(
    'myapp_active_users',
    'Number of currently active users'
)

queue_depth = Gauge(
    'myapp_queue_depth',
    'Current depth of processing queue',
    ['queue_name']
)

# Counter - Only goes up
requests_total = Counter(
    'myapp_requests_total',
    'Total number of requests',
    ['method', 'endpoint', 'status']
)

errors_total = Counter(
    'myapp_errors_total',
    'Total number of errors',
    ['error_type']
)

# Histogram - Buckets for distributions
request_duration = Histogram(
    'myapp_request_duration_seconds',
    'Request duration in seconds',
    ['method', 'endpoint'],
    buckets=[0.01, 0.05, 0.1, 0.5, 1.0, 2.5, 5.0, 10.0]
)

# Summary - Percentiles (calculated client-side)
response_size = Summary(
    'myapp_response_size_bytes',
    'Response size in bytes',
    ['endpoint']
)

# Enum - Track state
application_state = Enum(
    'myapp_application_state',
    'Current application state',
    states=['starting', 'running', 'degraded', 'stopped']
)

# Info - Metadata
application_info = Info(
    'myapp_application',
    'Application information'
)

# Set application info (only set once)
application_info.info({
    'version': '1.2.3',
    'environment': 'production',
    'region': 'us-east-1',
    'build_date': '2024-01-15'
})

# =============================================================================
# Custom Collector (for dynamic metrics)
# =============================================================================

class CustomCollector:
    """
    Custom collector for metrics that need to be collected on-demand
    Useful for expensive operations or external system queries
    """

    def collect(self):
        # Example: Collect database statistics
        db_connections = GaugeMetricFamily(
            'myapp_database_connections',
            'Number of database connections',
            labels=['database', 'state']
        )

        # Simulate fetching from database
        db_connections.add_metric(['users_db', 'active'], random.randint(10, 50))
        db_connections.add_metric(['users_db', 'idle'], random.randint(5, 20))
        db_connections.add_metric(['orders_db', 'active'], random.randint(15, 60))
        db_connections.add_metric(['orders_db', 'idle'], random.randint(8, 25))

        yield db_connections

        # Example: Collect external API health
        api_health = GaugeMetricFamily(
            'myapp_external_api_health',
            'Health status of external APIs (1=healthy, 0=unhealthy)',
            labels=['api_name']
        )

        # Simulate checking external APIs
        external_apis = {
            'payment_gateway': random.choice([0, 1]),
            'email_service': random.choice([0, 1]),
            'sms_service': random.choice([0, 1])
        }

        for api_name, health in external_apis.items():
            api_health.add_metric([api_name], health)

        yield api_health

        # Example: Business metrics from database
        business_metrics = CounterMetricFamily(
            'myapp_business_events_total',
            'Total business events',
            labels=['event_type']
        )

        # Simulate fetching from database
        events = {
            'user_signup': random.randint(1000, 5000),
            'order_placed': random.randint(500, 2000),
            'order_completed': random.randint(400, 1800),
            'payment_processed': random.randint(450, 1900)
        }

        for event_type, count in events.items():
            business_metrics.add_metric([event_type], count)

        yield business_metrics

# Register custom collector
REGISTRY.register(CustomCollector())

# =============================================================================
# Application Logic with Metrics
# =============================================================================

def simulate_request(method, endpoint):
    """Simulate handling a request and recording metrics"""

    # Start timer for request duration
    with request_duration.labels(method=method, endpoint=endpoint).time():
        # Simulate request processing
        processing_time = random.uniform(0.01, 2.0)
        time.sleep(processing_time)

        # Simulate response
        status = random.choices(
            ['200', '201', '400', '404', '500'],
            weights=[80, 5, 5, 5, 5]
        )[0]

        # Record request
        requests_total.labels(
            method=method,
            endpoint=endpoint,
            status=status
        ).inc()

        # Record response size
        response_size_bytes = random.randint(100, 10000)
        response_size.labels(endpoint=endpoint).observe(response_size_bytes)

        # Record errors if 5xx
        if status.startswith('5'):
            errors_total.labels(error_type='internal_server_error').inc()
        elif status.startswith('4'):
            errors_total.labels(error_type='client_error').inc()

def simulate_background_tasks():
    """Simulate background tasks that update metrics"""

    # Update active users (simulate fluctuation)
    current = active_users._value._value if hasattr(active_users, '_value') else 0
    change = random.randint(-10, 15)
    new_value = max(0, current + change)
    active_users.set(new_value)

    # Update queue depths
    queue_depth.labels(queue_name='email_queue').set(random.randint(0, 100))
    queue_depth.labels(queue_name='sms_queue').set(random.randint(0, 50))
    queue_depth.labels(queue_name='notification_queue').set(random.randint(0, 200))

    # Update application state
    states = ['running', 'degraded']
    application_state.state(random.choice(states))

# =============================================================================
# Advanced: System Metrics
# =============================================================================

system_cpu_percent = Gauge(
    'myapp_system_cpu_percent',
    'System CPU usage percentage'
)

system_memory_percent = Gauge(
    'myapp_system_memory_percent',
    'System memory usage percentage'
)

system_disk_usage_percent = Gauge(
    'myapp_system_disk_usage_percent',
    'System disk usage percentage',
    ['mount_point']
)

def collect_system_metrics():
    """Collect system-level metrics"""
    system_cpu_percent.set(psutil.cpu_percent())
    system_memory_percent.set(psutil.virtual_memory().percent)

    for partition in psutil.disk_partitions():
        try:
            usage = psutil.disk_usage(partition.mountpoint)
            system_disk_usage_percent.labels(
                mount_point=partition.mountpoint
            ).set(usage.percent)
        except PermissionError:
            pass

# =============================================================================
# Advanced: HTTP Client Metrics
# =============================================================================

http_client_requests_total = Counter(
    'myapp_http_client_requests_total',
    'Total HTTP client requests',
    ['target', 'method', 'status_code']
)

http_client_request_duration = Histogram(
    'myapp_http_client_request_duration_seconds',
    'HTTP client request duration',
    ['target', 'method'],
    buckets=[0.1, 0.5, 1.0, 2.0, 5.0]
)

def make_http_request(url):
    """Make HTTP request with metrics"""
    method = 'GET'
    target = url.split('/')[2]  # Extract domain

    with http_client_request_duration.labels(target=target, method=method).time():
        try:
            response = requests.get(url, timeout=5)
            status = str(response.status_code)
        except requests.RequestException:
            status = 'error'

    http_client_requests_total.labels(
        target=target,
        method=method,
        status_code=status
    ).inc()

# =============================================================================
# Advanced: Cache Metrics
# =============================================================================

cache_hits = Counter(
    'myapp_cache_hits_total',
    'Total cache hits',
    ['cache_name']
)

cache_misses = Counter(
    'myapp_cache_misses_total',
    'Total cache misses',
    ['cache_name']
)

cache_operations_duration = Histogram(
    'myapp_cache_operation_duration_seconds',
    'Cache operation duration',
    ['cache_name', 'operation'],
    buckets=[0.001, 0.005, 0.01, 0.05, 0.1]
)

def simulate_cache_operation(cache_name='redis'):
    """Simulate cache operations"""
    operation = random.choice(['get', 'set', 'delete'])

    with cache_operations_duration.labels(cache_name=cache_name, operation=operation).time():
        time.sleep(random.uniform(0.001, 0.05))

    if operation == 'get':
        if random.random() > 0.2:  # 80% hit rate
            cache_hits.labels(cache_name=cache_name).inc()
        else:
            cache_misses.labels(cache_name=cache_name).inc()

# =============================================================================
# Main Application
# =============================================================================

def main():
    """Main function to run the exporter"""

    # Start Prometheus metrics server
    port = 9200
    print(f"Starting custom exporter on port {port}")
    start_http_server(port)

    # Set initial application state
    application_state.state('running')
    active_users.set(100)

    # Main loop
    iteration = 0
    while True:
        iteration += 1

        # Simulate various requests
        endpoints = ['/api/users', '/api/orders', '/api/products', '/health']
        methods = ['GET', 'POST', 'PUT', 'DELETE']

        for _ in range(random.randint(5, 20)):
            endpoint = random.choice(endpoints)
            method = random.choice(methods) if endpoint != '/health' else 'GET'
            simulate_request(method, endpoint)

        # Simulate background tasks
        simulate_background_tasks()

        # Collect system metrics
        if iteration % 10 == 0:  # Every 10 iterations
            collect_system_metrics()

        # Simulate cache operations
        for _ in range(random.randint(10, 50)):
            simulate_cache_operation()

        # Simulate external HTTP requests
        if iteration % 5 == 0:  # Every 5 iterations
            urls = [
                'https://api.example.com/health',
                'https://payment.example.com/status'
            ]
            # Don't actually make the requests in this example
            # for url in urls:
            #     make_http_request(url)

        # Sleep before next iteration
        time.sleep(1)

if __name__ == '__main__':
    main()
