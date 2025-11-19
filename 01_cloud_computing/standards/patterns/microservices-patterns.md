# Microservices Architecture Patterns

## Overview

Microservices architecture patterns enable building scalable, maintainable, and resilient distributed systems by decomposing applications into small, independent services. This guide covers essential patterns for successful microservices implementation.

## Table of Contents

1. [Service Discovery Pattern](#service-discovery-pattern)
2. [Circuit Breaker Pattern](#circuit-breaker-pattern)
3. [Saga Pattern](#saga-pattern)
4. [CQRS Pattern](#cqrs-pattern)
5. [API Gateway Pattern](#api-gateway-pattern)
6. [Sidecar Pattern](#sidecar-pattern)
7. [Strangler Fig Pattern](#strangler-fig-pattern)
8. [Bulkhead Pattern](#bulkhead-pattern)

---

## 1. Service Discovery Pattern

### Description

Enable services to dynamically discover and communicate with each other without hard-coded addresses. Essential for cloud-native microservices that scale and move across hosts.

### When to Use

- Dynamic service scaling (auto-scaling groups)
- Container orchestration (Kubernetes, ECS)
- Multi-instance services
- Services deployed across multiple availability zones
- Frequent deployments with changing IPs

### Types of Service Discovery

**Client-Side Discovery:**
- Client queries service registry
- Client load balances between instances
- Examples: Netflix Eureka, Consul

**Server-Side Discovery:**
- Load balancer queries service registry
- Client calls load balancer
- Examples: AWS ELB, Kubernetes Service

### Architecture Diagram

```
┌──────────────────────────────────────────────────────┐
│           Service Discovery Architecture              │
└──────────────────────────────────────────────────────┘

Client-Side Discovery:
┌────────────┐
│  Client    │
│  Service   │
└─────┬──────┘
      │ 1. Query registry
      ▼
┌─────────────┐
│  Service    │
│  Registry   │◄─── Services register themselves
│  (Consul)   │
└─────┬───────┘
      │ 2. Get instances
      ▼
┌──────────────────────────────────┐
│  Service Instances               │
│  ┌────────┐ ┌────────┐ ┌──────┐│
│  │Instance│ │Instance│ │Inst..││
│  │   A    │ │   B    │ │  C   ││
│  └────────┘ └────────┘ └──────┘│
└──────────────────────────────────┘
      ▲ 3. Direct call with client-side load balancing


Server-Side Discovery:
┌────────────┐
│  Client    │
│  Service   │
└─────┬──────┘
      │ 1. Call load balancer
      ▼
┌─────────────┐
│    Load     │◄─── 2. Query registry
│  Balancer   │     ┌─────────────┐
│   (ALB)     │────►│  Service    │
└─────┬───────┘     │  Registry   │
      │             └─────────────┘
      │ 3. Route to healthy instance
      ▼
┌──────────────────────────────────┐
│  Service Instances               │
│  ┌────────┐ ┌────────┐ ┌──────┐│
│  │Instance│ │Instance│ │Inst..││
│  │   A    │ │   B    │ │  C   ││
│  └────────┘ └────────┘ └──────┘│
└──────────────────────────────────┘
```

### Implementation Example - Consul

```python
# service_discovery.py
import consul
import requests
from typing import List, Optional, Dict
import random

class ServiceDiscovery:
    def __init__(self, consul_host: str = 'localhost', consul_port: int = 8500):
        self.consul = consul.Consul(host=consul_host, port=consul_port)

    def register_service(self, service_name: str, service_id: str,
                        address: str, port: int,
                        tags: List[str] = None,
                        health_check_url: str = None):
        """Register a service with Consul"""

        check = None
        if health_check_url:
            check = consul.Check.http(
                health_check_url,
                interval='10s',
                timeout='5s',
                deregister='30s'
            )

        self.consul.agent.service.register(
            name=service_name,
            service_id=service_id,
            address=address,
            port=port,
            tags=tags or [],
            check=check
        )

        print(f"Registered {service_name} ({service_id}) at {address}:{port}")

    def deregister_service(self, service_id: str):
        """Deregister a service"""
        self.consul.agent.service.deregister(service_id)
        print(f"Deregistered service: {service_id}")

    def discover_service(self, service_name: str,
                        tag: Optional[str] = None) -> List[Dict]:
        """Discover healthy instances of a service"""

        # Query Consul for service
        index, services = self.consul.health.service(
            service_name,
            passing=True,  # Only healthy instances
            tag=tag
        )

        instances = []
        for service in services:
            instances.append({
                'id': service['Service']['ID'],
                'address': service['Service']['Address'],
                'port': service['Service']['Port'],
                'tags': service['Service']['Tags'],
                'metadata': service['Service']['Meta']
            })

        return instances

    def get_service_url(self, service_name: str,
                       load_balance: str = 'random') -> Optional[str]:
        """Get URL for a service instance"""

        instances = self.discover_service(service_name)

        if not instances:
            return None

        # Load balancing strategy
        if load_balance == 'random':
            instance = random.choice(instances)
        elif load_balance == 'round_robin':
            # Simplified round-robin
            instance = instances[0]
        else:
            instance = instances[0]

        return f"http://{instance['address']}:{instance['port']}"

    def call_service(self, service_name: str, path: str,
                    method: str = 'GET', **kwargs) -> requests.Response:
        """Make HTTP call to discovered service"""

        url = self.get_service_url(service_name)
        if not url:
            raise Exception(f"Service {service_name} not found")

        full_url = f"{url}{path}"
        return requests.request(method, full_url, **kwargs)


# Flask application with service registration
from flask import Flask, jsonify
import socket
import atexit

app = Flask(__name__)
discovery = ServiceDiscovery()

# Service configuration
SERVICE_NAME = 'user-service'
SERVICE_ID = f'{SERVICE_NAME}-{socket.gethostname()}'
SERVICE_PORT = 5000

@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({'status': 'healthy'}), 200

@app.route('/api/users/<user_id>')
def get_user(user_id):
    """Example API endpoint"""
    return jsonify({
        'user_id': user_id,
        'service_id': SERVICE_ID
    })

def register_with_consul():
    """Register this service with Consul"""
    hostname = socket.gethostname()
    ip_address = socket.gethostbyname(hostname)

    discovery.register_service(
        service_name=SERVICE_NAME,
        service_id=SERVICE_ID,
        address=ip_address,
        port=SERVICE_PORT,
        tags=['api', 'v1'],
        health_check_url=f'http://{ip_address}:{SERVICE_PORT}/health'
    )

def deregister_from_consul():
    """Deregister on shutdown"""
    discovery.deregister_service(SERVICE_ID)

# Register on startup
register_with_consul()

# Deregister on shutdown
atexit.register(deregister_from_consul)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=SERVICE_PORT)
```

### Kubernetes Service Discovery

```yaml
# kubernetes-service-discovery.yaml

# Service automatically creates DNS entry
apiVersion: v1
kind: Service
metadata:
  name: user-service
  labels:
    app: user-service
spec:
  selector:
    app: user-service
  ports:
  - name: http
    port: 80
    targetPort: 8080
  type: ClusterIP

---
# Deployment with multiple replicas
apiVersion: apps/v1
kind: Deployment
metadata:
  name: user-service
spec:
  replicas: 3
  selector:
    matchLabels:
      app: user-service
  template:
    metadata:
      labels:
        app: user-service
    spec:
      containers:
      - name: user-service
        image: myregistry/user-service:v1
        ports:
        - containerPort: 8080
        env:
        - name: ORDER_SERVICE_URL
          value: "http://order-service"  # DNS-based discovery
        - name: PAYMENT_SERVICE_URL
          value: "http://payment-service"
        livenessProbe:
          httpGet:
            path: /health
            port: 8080
          initialDelaySeconds: 30
        readinessProbe:
          httpGet:
            path: /ready
            port: 8080
          initialDelaySeconds: 5

---
# Headless service for direct pod discovery
apiVersion: v1
kind: Service
metadata:
  name: user-service-headless
spec:
  clusterIP: None  # Headless service
  selector:
    app: user-service
  ports:
  - port: 8080
```

### Trade-offs

**Pros:**
- Dynamic scaling and deployment
- High availability through multiple instances
- Automatic failover
- Technology agnostic
- Zero-downtime deployments

**Cons:**
- Additional infrastructure complexity
- Service registry as potential SPOF
- Network latency for registry queries
- Consistency challenges

### Anti-patterns

- **Hardcoded Addresses**: Using static IPs or hostnames
- **No Health Checks**: Routing to unhealthy instances
- **Single Registry Instance**: No redundancy for registry
- **Caching Without TTL**: Stale service locations

### Real-world Examples

**Netflix**: Eureka for service discovery across thousands of microservices.

**Uber**: Uses hyperbahn (TChannel) for service discovery at massive scale.

**Spotify**: Combination of Consul and Kubernetes service discovery.

---

## 2. Circuit Breaker Pattern

### Description

Prevent cascading failures by detecting when a service is failing and temporarily stopping requests to it, giving it time to recover.

### When to Use

- External service dependencies
- High-latency or unreliable services
- Preventing cascade failures
- Need for graceful degradation
- Protecting system resources

### Circuit States

```
┌──────────────────────────────────────────┐
│      Circuit Breaker State Machine       │
└──────────────────────────────────────────┘

         ┌─────────┐
    ┌───►│ CLOSED  │
    │    │ (Normal)│
    │    └────┬────┘
    │         │
    │         │ Failures exceed threshold
    │         │
    │    ┌────▼────┐
    │    │  OPEN   │◄────┐
    │    │(Blocked)│     │
    │    └────┬────┘     │ Immediate fail
    │         │          │
    │         │ After timeout
    │         │
    │    ┌────▼────────┐
    └────│ HALF-OPEN   │
         │  (Testing)  │
         └─────────────┘
              │    │
              │    └──► Failures → OPEN
              │
              └──► Successes → CLOSED
```

### Implementation Example

```python
# circuit_breaker.py
from enum import Enum
from datetime import datetime, timedelta
from typing import Callable, Any
import time
from functools import wraps

class CircuitState(Enum):
    CLOSED = "closed"      # Normal operation
    OPEN = "open"          # Failing, reject requests
    HALF_OPEN = "half_open"  # Testing recovery

class CircuitBreaker:
    def __init__(self,
                 failure_threshold: int = 5,
                 success_threshold: int = 2,
                 timeout: int = 60,
                 expected_exception: type = Exception):
        """
        Args:
            failure_threshold: Failures before opening circuit
            success_threshold: Successes to close from half-open
            timeout: Seconds before trying half-open state
            expected_exception: Exception type to catch
        """
        self.failure_threshold = failure_threshold
        self.success_threshold = success_threshold
        self.timeout = timeout
        self.expected_exception = expected_exception

        self.failure_count = 0
        self.success_count = 0
        self.last_failure_time = None
        self.state = CircuitState.CLOSED

    def call(self, func: Callable, *args, **kwargs) -> Any:
        """Execute function with circuit breaker protection"""

        if self.state == CircuitState.OPEN:
            # Check if timeout has passed
            if self._should_attempt_reset():
                self.state = CircuitState.HALF_OPEN
                print("Circuit breaker: Moving to HALF_OPEN state")
            else:
                raise Exception("Circuit breaker is OPEN - service unavailable")

        try:
            # Execute the function
            result = func(*args, **kwargs)

            # Success
            self._on_success()
            return result

        except self.expected_exception as e:
            # Failure
            self._on_failure()
            raise e

    def _should_attempt_reset(self) -> bool:
        """Check if enough time has passed to try recovery"""
        if self.last_failure_time is None:
            return True

        return datetime.now() >= self.last_failure_time + timedelta(seconds=self.timeout)

    def _on_success(self):
        """Handle successful call"""
        self.failure_count = 0

        if self.state == CircuitState.HALF_OPEN:
            self.success_count += 1
            if self.success_count >= self.success_threshold:
                self.state = CircuitState.CLOSED
                self.success_count = 0
                print("Circuit breaker: CLOSED (recovered)")

    def _on_failure(self):
        """Handle failed call"""
        self.failure_count += 1
        self.last_failure_time = datetime.now()
        self.success_count = 0

        if self.failure_count >= self.failure_threshold:
            self.state = CircuitState.OPEN
            print(f"Circuit breaker: OPEN (threshold {self.failure_threshold} exceeded)")

    def __call__(self, func: Callable) -> Callable:
        """Decorator usage"""
        @wraps(func)
        def wrapper(*args, **kwargs):
            return self.call(func, *args, **kwargs)
        return wrapper


# Example usage with external service
import requests

payment_circuit = CircuitBreaker(
    failure_threshold=3,
    timeout=30,
    expected_exception=requests.RequestException
)

@payment_circuit
def call_payment_service(order_id: str, amount: float):
    """Call external payment service with circuit breaker"""
    response = requests.post(
        'http://payment-service/api/charge',
        json={'order_id': order_id, 'amount': amount},
        timeout=5
    )
    response.raise_for_status()
    return response.json()


# Advanced Circuit Breaker with metrics
from dataclasses import dataclass, field
from collections import deque

@dataclass
class CircuitBreakerMetrics:
    total_calls: int = 0
    successful_calls: int = 0
    failed_calls: int = 0
    rejected_calls: int = 0
    recent_errors: deque = field(default_factory=lambda: deque(maxlen=100))

class AdvancedCircuitBreaker:
    def __init__(self, failure_threshold: int = 5,
                 timeout: int = 60,
                 window_size: int = 100):
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.window_size = window_size

        self.state = CircuitState.CLOSED
        self.last_failure_time = None
        self.metrics = CircuitBreakerMetrics()

        # Sliding window for failure rate
        self.recent_calls = deque(maxlen=window_size)

    def call(self, func: Callable, *args, **kwargs) -> Any:
        """Execute with advanced circuit breaker logic"""
        self.metrics.total_calls += 1

        # Check circuit state
        if self.state == CircuitState.OPEN:
            if self._should_attempt_reset():
                self.state = CircuitState.HALF_OPEN
            else:
                self.metrics.rejected_calls += 1
                raise Exception(f"Circuit OPEN - failure rate: {self._failure_rate():.2%}")

        try:
            result = func(*args, **kwargs)
            self._record_success()
            return result

        except Exception as e:
            self._record_failure(e)
            raise e

    def _record_success(self):
        """Record successful call"""
        self.recent_calls.append(True)
        self.metrics.successful_calls += 1

        if self.state == CircuitState.HALF_OPEN:
            # Successful test, close circuit
            self.state = CircuitState.CLOSED
            print("Circuit breaker CLOSED after successful recovery")

    def _record_failure(self, error: Exception):
        """Record failed call"""
        self.recent_calls.append(False)
        self.metrics.failed_calls += 1
        self.metrics.recent_errors.append({
            'timestamp': datetime.now(),
            'error': str(error)
        })
        self.last_failure_time = datetime.now()

        # Check if should open circuit
        if self._failure_rate() >= (self.failure_threshold / self.window_size):
            self.state = CircuitState.OPEN
            print(f"Circuit breaker OPEN - failure rate: {self._failure_rate():.2%}")

    def _failure_rate(self) -> float:
        """Calculate failure rate in sliding window"""
        if not self.recent_calls:
            return 0.0

        failures = sum(1 for call in self.recent_calls if not call)
        return failures / len(self.recent_calls)

    def _should_attempt_reset(self) -> bool:
        """Check if timeout has passed"""
        if self.last_failure_time is None:
            return True
        return datetime.now() >= self.last_failure_time + timedelta(seconds=self.timeout)

    def get_metrics(self) -> dict:
        """Get circuit breaker metrics"""
        return {
            'state': self.state.value,
            'total_calls': self.metrics.total_calls,
            'successful_calls': self.metrics.successful_calls,
            'failed_calls': self.metrics.failed_calls,
            'rejected_calls': self.metrics.rejected_calls,
            'failure_rate': f"{self._failure_rate():.2%}",
            'recent_errors_count': len(self.metrics.recent_errors)
        }
```

### Terraform - AWS App Mesh Circuit Breaker

```hcl
# App Mesh Virtual Node with circuit breaker
resource "aws_appmesh_virtual_node" "service_with_circuit_breaker" {
  name      = "payment-service"
  mesh_name = aws_appmesh_mesh.main.id

  spec {
    backend {
      virtual_service {
        virtual_service_name = "external-payment-api"
      }
    }

    listener {
      port_mapping {
        port     = 8080
        protocol = "http"
      }

      # Circuit breaker configuration
      outlier_detection {
        max_ejection_percent = 50
        max_server_errors    = 5
        interval {
          unit  = "s"
          value = 10
        }
        base_ejection_duration {
          unit  = "s"
          value = 30
        }
      }
    }

    service_discovery {
      aws_cloud_map {
        service_name   = "payment-service"
        namespace_name = aws_service_discovery_private_dns_namespace.main.name
      }
    }
  }
}
```

### Real-world Examples

**Netflix**: Hystrix library (now in maintenance mode) - pioneered circuit breaker pattern.

**Amazon**: Circuit breakers throughout AWS services to prevent cascading failures.

**Google**: Implements circuit breakers in GCP services and recommends for customers.

---

## 3. Saga Pattern

### Description

Manage distributed transactions across microservices using a sequence of local transactions, with compensating transactions for rollback.

### When to Use

- Multi-service transactions
- No distributed transaction support (2PC not feasible)
- Need for eventual consistency
- Long-running business processes
- E-commerce order processing

### Types of Sagas

**Choreography-Based:**
- Services communicate via events
- Decentralized coordination
- Each service knows what to do

**Orchestration-Based:**
- Central orchestrator coordinates
- Explicit workflow definition
- Better for complex flows

### Architecture Diagram

```
Choreography-Based Saga:

┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│   Order     │    │  Payment    │    │  Inventory  │
│  Service    │    │  Service    │    │  Service    │
└──────┬──────┘    └──────┬──────┘    └──────┬──────┘
       │                  │                  │
       │ OrderCreated     │                  │
       ├─────────────────►│                  │
       │                  │ PaymentProcessed │
       │                  ├─────────────────►│
       │                  │                  │
       │                  │◄─────────────────┤
       │                  │ InventoryReserved│
       │◄─────────────────┤                  │
       │   PaymentOK      │                  │
       │                  │                  │
       │  If failure:     │                  │
       │  CompensateOrder │                  │
       ├─────────────────►│                  │
       │                  │ RefundPayment    │
       │                  ├─────────────────►│
       │                  │                  │


Orchestration-Based Saga:

              ┌─────────────────┐
              │  Saga           │
              │  Orchestrator   │
              └────────┬────────┘
                       │
       ┌───────────────┼───────────────┐
       │               │               │
┌──────▼──────┐ ┌─────▼──────┐ ┌─────▼──────┐
│   Order     │ │  Payment   │ │ Inventory  │
│  Service    │ │  Service   │ │  Service   │
└─────────────┘ └────────────┘ └────────────┘

  1. Create Order → 2. Process Payment → 3. Reserve Inventory
         ↓                 ↓                      ↓
    Success          Success/Fail           Success/Fail
         ↓                 ↓                      ↓
    Compensate    ←  Compensate  ←    Compensate
  (If any step fails)
```

### Implementation Example

```python
# saga_orchestrator.py
from enum import Enum
from typing import List, Callable, Dict, Any
from dataclasses import dataclass
import uuid

class SagaStepStatus(Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"
    COMPENSATED = "compensated"

@dataclass
class SagaStep:
    name: str
    action: Callable
    compensation: Callable
    status: SagaStepStatus = SagaStepStatus.PENDING
    result: Any = None
    error: Any = None

class SagaOrchestrator:
    def __init__(self, saga_id: str = None):
        self.saga_id = saga_id or str(uuid.uuid4())
        self.steps: List[SagaStep] = []
        self.completed_steps: List[SagaStep] = []

    def add_step(self, name: str, action: Callable, compensation: Callable):
        """Add a step to the saga"""
        step = SagaStep(name=name, action=action, compensation=compensation)
        self.steps.append(step)
        return self

    def execute(self) -> Dict:
        """Execute saga - all steps or compensate on failure"""
        print(f"Starting saga {self.saga_id}")

        try:
            # Execute each step
            for step in self.steps:
                print(f"Executing step: {step.name}")

                try:
                    # Execute action
                    result = step.action()
                    step.result = result
                    step.status = SagaStepStatus.COMPLETED
                    self.completed_steps.append(step)
                    print(f"Step {step.name} completed successfully")

                except Exception as e:
                    # Step failed - trigger compensation
                    step.status = SagaStepStatus.FAILED
                    step.error = str(e)
                    print(f"Step {step.name} failed: {e}")

                    # Compensate completed steps
                    self._compensate()

                    return {
                        'saga_id': self.saga_id,
                        'status': 'failed',
                        'failed_step': step.name,
                        'error': str(e)
                    }

            # All steps completed
            return {
                'saga_id': self.saga_id,
                'status': 'completed',
                'steps_executed': len(self.completed_steps)
            }

        except Exception as e:
            print(f"Saga execution error: {e}")
            self._compensate()
            raise

    def _compensate(self):
        """Compensate all completed steps in reverse order"""
        print(f"Compensating saga {self.saga_id}")

        for step in reversed(self.completed_steps):
            try:
                print(f"Compensating step: {step.name}")
                step.compensation()
                step.status = SagaStepStatus.COMPENSATED
                print(f"Step {step.name} compensated successfully")

            except Exception as e:
                print(f"Compensation failed for {step.name}: {e}")
                # Log compensation failure - may need manual intervention


# Example: Order Processing Saga
import requests

class OrderSaga:
    def __init__(self, order_data: Dict):
        self.order_data = order_data
        self.order_id = None
        self.payment_id = None
        self.reservation_id = None

    def execute(self):
        """Execute order processing saga"""
        saga = SagaOrchestrator()

        saga.add_step(
            name="Create Order",
            action=self.create_order,
            compensation=self.cancel_order
        ).add_step(
            name="Process Payment",
            action=self.process_payment,
            compensation=self.refund_payment
        ).add_step(
            name="Reserve Inventory",
            action=self.reserve_inventory,
            compensation=self.release_inventory
        ).add_step(
            name="Send Confirmation",
            action=self.send_confirmation,
            compensation=self.send_cancellation
        )

        return saga.execute()

    # Transaction steps
    def create_order(self):
        """Create order in order service"""
        response = requests.post(
            'http://order-service/api/orders',
            json=self.order_data
        )
        response.raise_for_status()
        result = response.json()
        self.order_id = result['order_id']
        return result

    def process_payment(self):
        """Process payment"""
        response = requests.post(
            'http://payment-service/api/payments',
            json={
                'order_id': self.order_id,
                'amount': self.order_data['total'],
                'payment_method': self.order_data['payment_method']
            }
        )
        response.raise_for_status()
        result = response.json()
        self.payment_id = result['payment_id']
        return result

    def reserve_inventory(self):
        """Reserve inventory"""
        response = requests.post(
            'http://inventory-service/api/reservations',
            json={
                'order_id': self.order_id,
                'items': self.order_data['items']
            }
        )
        response.raise_for_status()
        result = response.json()
        self.reservation_id = result['reservation_id']
        return result

    def send_confirmation(self):
        """Send order confirmation"""
        response = requests.post(
            'http://notification-service/api/send',
            json={
                'order_id': self.order_id,
                'type': 'order_confirmation',
                'email': self.order_data['customer_email']
            }
        )
        response.raise_for_status()
        return response.json()

    # Compensation steps
    def cancel_order(self):
        """Cancel order"""
        if self.order_id:
            requests.delete(f'http://order-service/api/orders/{self.order_id}')

    def refund_payment(self):
        """Refund payment"""
        if self.payment_id:
            requests.post(
                f'http://payment-service/api/payments/{self.payment_id}/refund'
            )

    def release_inventory(self):
        """Release inventory reservation"""
        if self.reservation_id:
            requests.delete(
                f'http://inventory-service/api/reservations/{self.reservation_id}'
            )

    def send_cancellation(self):
        """Send cancellation notice"""
        if self.order_id:
            requests.post(
                'http://notification-service/api/send',
                json={
                    'order_id': self.order_id,
                    'type': 'order_cancelled',
                    'email': self.order_data['customer_email']
                }
            )


# Usage
order_data = {
    'items': [{'sku': 'ABC123', 'quantity': 2}],
    'total': 99.99,
    'payment_method': 'credit_card',
    'customer_email': 'customer@example.com'
}

saga = OrderSaga(order_data)
result = saga.execute()
print(result)
```

### Real-world Examples

**Uber**: Uses Sagas for trip booking and payment processing across multiple services.

**Amazon**: Order processing involves saga-like patterns across inventory, payment, and shipping.

---

## 4. CQRS Pattern

### Description

Command Query Responsibility Segregation - Separate read and write operations using different models, optimizing each for its specific use case.

### When to Use

- Different read/write performance requirements
- Complex business logic
- Event sourcing implementation
- Scalability needs differ for reads vs writes
- Multiple read representations needed

### Architecture Diagram

```
┌────────────────────────────────────────────────────┐
│              CQRS Architecture                     │
└────────────────────────────────────────────────────┘

                    ┌─────────────┐
                    │   Client    │
                    └──────┬──────┘
                           │
              ┌────────────┼────────────┐
              │            │            │
        Commands        Queries      Events
              │            │            │
        ┌─────▼─────┐┌────▼────┐      │
        │  Command  ││  Query  │      │
        │  Handler  ││ Handler │      │
        └─────┬─────┘└────┬────┘      │
              │           │            │
        ┌─────▼─────┐┌───▼──────┐    │
        │  Write    ││   Read    │    │
        │  Model    ││  Model    │    │
        │           ││           │    │
        │ Postgres  ││  Redis    │    │
        │ (Master)  ││  ElasticS │    │
        └─────┬─────┘└───────────┘    │
              │                       │
              │  Domain Events        │
              └───────────────────────┘
                      │
              ┌───────▼────────┐
              │  Event Store   │
              │  (Event Source)│
              └────────────────┘
```

### Implementation Example

```python
# cqrs_implementation.py
from dataclasses import dataclass
from typing import List, Dict, Any
from abc import ABC, abstractmethod
import uuid
from datetime import datetime

# Commands (Write Side)
@dataclass
class Command(ABC):
    """Base command"""
    command_id: str = None

    def __post_init__(self):
        if not self.command_id:
            self.command_id = str(uuid.uuid4())

@dataclass
class CreateOrderCommand(Command):
    user_id: str
    items: List[Dict]
    total_amount: float

@dataclass
class CancelOrderCommand(Command):
    order_id: str
    reason: str

# Events (Domain Events)
@dataclass
class Event(ABC):
    """Base event"""
    event_id: str = None
    timestamp: datetime = None

    def __post_init__(self):
        if not self.event_id:
            self.event_id = str(uuid.uuid4())
        if not self.timestamp:
            self.timestamp = datetime.now()

@dataclass
class OrderCreatedEvent(Event):
    order_id: str
    user_id: str
    items: List[Dict]
    total_amount: float

@dataclass
class OrderCancelledEvent(Event):
    order_id: str
    reason: str

# Queries (Read Side)
@dataclass
class Query(ABC):
    """Base query"""
    pass

@dataclass
class GetOrderQuery(Query):
    order_id: str

@dataclass
class GetUserOrdersQuery(Query):
    user_id: str
    status: str = None

# Write Model (Command Side)
class OrderWriteModel:
    def __init__(self, db_connection):
        self.db = db_connection

    def create_order(self, command: CreateOrderCommand) -> OrderCreatedEvent:
        """Handle create order command"""
        order_id = str(uuid.uuid4())

        # Write to database
        self.db.execute("""
            INSERT INTO orders (order_id, user_id, items, total_amount, status)
            VALUES (%s, %s, %s, %s, %s)
        """, (order_id, command.user_id, command.items,
              command.total_amount, 'pending'))

        # Emit event
        event = OrderCreatedEvent(
            order_id=order_id,
            user_id=command.user_id,
            items=command.items,
            total_amount=command.total_amount
        )

        return event

    def cancel_order(self, command: CancelOrderCommand) -> OrderCancelledEvent:
        """Handle cancel order command"""

        # Update database
        self.db.execute("""
            UPDATE orders
            SET status = 'cancelled', cancelled_reason = %s
            WHERE order_id = %s
        """, (command.reason, command.order_id))

        # Emit event
        event = OrderCancelledEvent(
            order_id=command.order_id,
            reason=command.reason
        )

        return event

# Read Model (Query Side)
class OrderReadModel:
    def __init__(self, cache_connection, search_connection):
        self.cache = cache_connection
        self.search = search_connection

    def get_order(self, query: GetOrderQuery) -> Dict:
        """Get single order (from cache)"""

        # Try cache first
        cached = self.cache.get(f"order:{query.order_id}")
        if cached:
            return cached

        # Fallback to search
        result = self.search.get(
            index='orders',
            id=query.order_id
        )

        # Cache for next time
        self.cache.set(f"order:{query.order_id}", result)

        return result

    def get_user_orders(self, query: GetUserOrdersQuery) -> List[Dict]:
        """Get user orders (from search)"""

        search_query = {
            'query': {
                'bool': {
                    'must': [
                        {'term': {'user_id': query.user_id}}
                    ]
                }
            },
            'sort': [{'created_at': 'desc'}]
        }

        if query.status:
            search_query['query']['bool']['must'].append(
                {'term': {'status': query.status}}
            )

        results = self.search.search(
            index='orders',
            body=search_query
        )

        return [hit['_source'] for hit in results['hits']['hits']]

# Event Handler (Synchronizes Read Models)
class OrderEventHandler:
    def __init__(self, cache, search):
        self.cache = cache
        self.search = search

    def handle(self, event: Event):
        """Handle domain events and update read models"""

        if isinstance(event, OrderCreatedEvent):
            self._handle_order_created(event)
        elif isinstance(event, OrderCancelledEvent):
            self._handle_order_cancelled(event)

    def _handle_order_created(self, event: OrderCreatedEvent):
        """Update read models when order created"""

        order_doc = {
            'order_id': event.order_id,
            'user_id': event.user_id,
            'items': event.items,
            'total_amount': event.total_amount,
            'status': 'pending',
            'created_at': event.timestamp.isoformat()
        }

        # Update cache
        self.cache.set(f"order:{event.order_id}", order_doc)

        # Update search index
        self.search.index(
            index='orders',
            id=event.order_id,
            body=order_doc
        )

    def _handle_order_cancelled(self, event: OrderCancelledEvent):
        """Update read models when order cancelled"""

        # Update cache
        cached = self.cache.get(f"order:{event.order_id}")
        if cached:
            cached['status'] = 'cancelled'
            cached['cancelled_reason'] = event.reason
            self.cache.set(f"order:{event.order_id}", cached)

        # Update search index
        self.search.update(
            index='orders',
            id=event.order_id,
            body={
                'doc': {
                    'status': 'cancelled',
                    'cancelled_reason': event.reason
                }
            }
        )

# Command Bus
class CommandBus:
    def __init__(self):
        self.handlers = {}

    def register(self, command_type: type, handler: Callable):
        """Register command handler"""
        self.handlers[command_type] = handler

    def execute(self, command: Command) -> Event:
        """Execute command"""
        handler = self.handlers.get(type(command))
        if not handler:
            raise ValueError(f"No handler for {type(command)}")

        return handler(command)

# Query Bus
class QueryBus:
    def __init__(self):
        self.handlers = {}

    def register(self, query_type: type, handler: Callable):
        """Register query handler"""
        self.handlers[query_type] = handler

    def execute(self, query: Query) -> Any:
        """Execute query"""
        handler = self.handlers.get(type(query))
        if not handler:
            raise ValueError(f"No handler for {type(query)}")

        return handler(query)
```

### Real-world Examples

**Microsoft**: Azure architecture extensively uses CQRS with Event Sourcing.

**StackOverflow**: Separates read/write models for performance optimization.

---

## 5. API Gateway Pattern

### Description

Single entry point for all client requests, handling routing, authentication, rate limiting, and request/response transformation.

### When to Use

- Multiple microservices exposed to clients
- Cross-cutting concerns (auth, logging, rate limiting)
- Different clients need different data formats
- Service aggregation required
- Backend for Frontend (BFF) pattern

### Responsibilities

```
┌──────────────────────────────────────────┐
│     API Gateway Responsibilities         │
├──────────────────────────────────────────┤
│                                          │
│  1. Request Routing                      │
│  2. Authentication & Authorization       │
│  3. Rate Limiting & Throttling           │
│  4. Request/Response Transformation      │
│  5. Protocol Translation (REST/gRPC)     │
│  6. API Composition/Aggregation          │
│  7. Caching                              │
│  8. Load Balancing                       │
│  9. Circuit Breaking                     │
│  10. Logging & Monitoring                │
│  11. API Versioning                      │
│  12. CORS Handling                       │
│                                          │
└──────────────────────────────────────────┘
```

### Architecture Diagram

```
┌──────────┐  ┌──────────┐  ┌──────────┐
│  Web     │  │ Mobile   │  │  IoT     │
│  Client  │  │  App     │  │ Device   │
└─────┬────┘  └─────┬────┘  └─────┬────┘
      │             │             │
      └─────────────┼─────────────┘
                    │
              ┌─────▼─────┐
              │    API    │
              │  Gateway  │
              └─────┬─────┘
                    │
      ┌─────────────┼─────────────┬──────────────┐
      │             │             │              │
┌─────▼────┐  ┌────▼────┐  ┌────▼────┐   ┌────▼────┐
│  User    │  │ Order   │  │ Payment │   │Product  │
│ Service  │  │ Service │  │ Service │   │Service  │
└──────────┘  └─────────┘  └─────────┘   └─────────┘
```

### Real-world Examples

**Netflix**: Zuul API Gateway handles billions of requests daily.

**Amazon**: API Gateway for AWS Lambda and microservices.

**Uber**: Custom API Gateway (APIGateway-L7) routing millions of requests.

---

## 6. Sidecar Pattern

### Description

Deploy helper components alongside main application containers to provide supporting features without changing application code.

### Common Sidecars

```
┌──────────────────────────────────────────┐
│         Common Sidecar Functions         │
├──────────────────────────────────────────┤
│  - Service Mesh Proxy (Envoy, Linkerd)  │
│  - Logging Agent (Fluentd)              │
│  - Monitoring (Prometheus exporter)      │
│  - Security (TLS termination)           │
│  - Configuration (Consul Template)       │
│  - Secrets (Vault agent)                │
└──────────────────────────────────────────┘
```

### Real-world Examples

**Istio**: Envoy sidecar for service mesh capabilities.

**Datadog**: DogStatsD sidecar for metrics collection.

---

## Summary

Microservices patterns enable:
- **Scalability**: Independent scaling of services
- **Resilience**: Fault isolation and graceful degradation
- **Flexibility**: Technology diversity and independent deployment
- **Maintainability**: Smaller, focused codebases

### Pattern Selection Guide

| Requirement | Pattern |
|-------------|---------|
| Service location | Service Discovery |
| Prevent cascades | Circuit Breaker |
| Distributed transactions | Saga |
| Read/write optimization | CQRS |
| Client entry point | API Gateway |
| Supporting features | Sidecar |

### Tool Recommendations

- **Service Mesh**: Istio, Linkerd, Consul Connect
- **API Gateway**: Kong, AWS API Gateway, Azure API Management
- **Service Discovery**: Consul, Eureka, Kubernetes
- **Resilience**: Resilience4j, Polly, Hystrix
- **Orchestration**: Kubernetes, AWS ECS, Nomad
