# Performance Optimization Guide

## Step 1: Database Optimization

### Indexing Strategy
```python
from sqlalchemy import Index, Column, String, Integer, DateTime

class OptimizedPatient(Base):
    __tablename__ = 'patients'

    id = Column(Integer, primary_key=True)
    mrn = Column(String(50), unique=True)  # Auto-indexed
    family_name = Column(String(100))
    given_name = Column(String(100))
    dob = Column(DateTime)
    gender = Column(String(1))
    created_at = Column(DateTime)

    # Add composite indexes for common queries
    __table_args__ = (
        Index('idx_family_given', 'family_name', 'given_name'),
        Index('idx_dob', 'dob'),
        Index('idx_mrn_active', 'mrn'),
        Index('idx_created_at', 'created_at'),
    )

# Query with indexes
def find_patient(mrn):
    """Optimized patient lookup - O(log n)"""
    return db.query(OptimizedPatient).filter(OptimizedPatient.mrn == mrn).first()

def search_patients(family_name, given_name):
    """Optimized search - uses composite index"""
    return db.query(OptimizedPatient).filter(
        OptimizedPatient.family_name == family_name,
        OptimizedPatient.given_name == given_name
    ).all()
```

### Query Optimization
```python
from sqlalchemy import orm

class OptimizedQueries:
    def __init__(self, db_session):
        self.db = db_session

    def get_patient_with_observations(self, patient_id):
        """Use eager loading to prevent N+1 queries"""
        return self.db.query(Patient).options(
            orm.joinedload(Patient.observations)
        ).filter(Patient.id == patient_id).first()

    def bulk_patient_update(self, updates):
        """Batch operations are more efficient"""
        self.db.bulk_update_mappings(Patient, updates)
        self.db.commit()

    def paginated_search(self, limit=50, offset=0):
        """Implement pagination for large result sets"""
        return self.db.query(Patient).offset(offset).limit(limit).all()

    def use_database_functions(self):
        """Let database do filtering"""
        from sqlalchemy import func

        # Count in database, not in Python
        count = self.db.query(func.count(Patient.id)).filter(
            Patient.created_at > datetime.utcnow() - timedelta(days=30)
        ).scalar()

        return count

    def optimize_connection_pool(self):
        """Configure connection pooling"""
        from sqlalchemy import create_engine

        engine = create_engine(
            'postgresql://user:pass@localhost/db',
            pool_size=20,  # Number of connections
            max_overflow=40,  # Additional overflow connections
            pool_recycle=3600,  # Recycle connections after 1 hour
            pool_pre_ping=True  # Test connections before use
        )

        return engine
```

## Step 2: Caching Strategy

### Redis Caching
```python
from redis import Redis
import json

class CachingLayer:
    def __init__(self):
        self.cache = Redis(host='localhost', port=6379, db=0)
        self.ttl = {
            'patient': 300,      # 5 minutes
            'observation': 600,  # 10 minutes
            'terminology': 86400 # 1 day
        }

    def get_cached(self, key):
        """Get from cache"""
        data = self.cache.get(key)
        return json.loads(data) if data else None

    def set_cached(self, key, value, ttl=None):
        """Set in cache with expiration"""
        self.cache.setex(
            key,
            ttl or self.ttl.get('default', 3600),
            json.dumps(value)
        )

    def get_patient(self, patient_id):
        """Get patient with caching"""
        cache_key = f"patient:{patient_id}"

        # Try cache first
        patient = self.get_cached(cache_key)
        if patient:
            return patient

        # Fetch from database
        patient = self.db.get_patient(patient_id)

        # Cache result
        if patient:
            self.set_cached(cache_key, patient, self.ttl['patient'])

        return patient

    def invalidate_patient(self, patient_id):
        """Invalidate patient cache on update"""
        self.cache.delete(f"patient:{patient_id}")

    def cache_observations(self, patient_id, observations):
        """Cache observation results"""
        cache_key = f"observations:{patient_id}"
        self.set_cached(cache_key, observations, self.ttl['observation'])

    def warm_cache(self):
        """Pre-load frequently accessed data"""
        # Load top patients
        popular_patients = self.db.get_popular_patients(limit=1000)
        for patient in popular_patients:
            cache_key = f"patient:{patient['id']}"
            self.set_cached(cache_key, patient, self.ttl['patient'])
```

## Step 3: API Performance

### Response Caching
```python
from functools import wraps
import hashlib

class APIOptimization:
    def cache_api_response(self, ttl=300):
        """Decorator to cache API responses"""
        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                # Generate cache key from request
                cache_key = self.generate_cache_key(func.__name__, args, kwargs)

                # Try cache
                cached = cache.get(cache_key)
                if cached:
                    return cached

                # Execute function
                result = func(*args, **kwargs)

                # Cache result
                cache.setex(cache_key, ttl, json.dumps(result))

                return result

            return wrapper
        return decorator

    def generate_cache_key(self, func_name, args, kwargs):
        """Generate unique cache key"""
        key_data = f"{func_name}:{str(args)}:{str(kwargs)}"
        return hashlib.md5(key_data.encode()).hexdigest()

    def implement_pagination(self, query, page=1, page_size=50):
        """Implement efficient pagination"""
        total = query.count()
        items = query.offset((page - 1) * page_size).limit(page_size).all()

        return {
            'items': items,
            'total': total,
            'pages': (total + page_size - 1) // page_size,
            'current_page': page
        }

    def use_selective_fields(self, query, fields=None):
        """Only fetch required fields"""
        if fields:
            # Select specific columns only
            return query.with_entities(*fields).all()
        return query.all()
```

### Compression
```python
from flask import Flask, make_response
from flask_compress import Compress

app = Flask(__name__)
Compress(app)  # Auto-gzip responses

# Or manual compression
@app.after_request
def compress_response(response):
    if 'gzip' in request.headers.get('Accept-Encoding', ''):
        import gzip
        response.data = gzip.compress(response.data)
        response.headers['Content-Encoding'] = 'gzip'
    return response
```

## Step 4: Message Queue Optimization

### Asynchronous Processing
```python
from celery import Celery

celery = Celery('healthcare_integration')

class AsyncProcessing:
    @celery.task(bind=True, max_retries=3)
    def process_hl7_async(self, hl7_message):
        """Process HL7 asynchronously"""
        try:
            # Long-running operation
            result = self.process_hl7(hl7_message)
            return result
        except Exception as e:
            # Retry with exponential backoff
            self.retry(exc=e, countdown=60 * (2 ** self.request.retries))

    @celery.task
    def send_notification(self, patient_id, message):
        """Send notification asynchronously"""
        notify_service.send(patient_id, message)

    @celery.task
    def batch_import(self, import_id):
        """Import large dataset asynchronously"""
        for record in get_import_batch(import_id):
            process_record(record)

# Monitor queue
from celery import group, chain

def check_queue_health():
    """Monitor queue status"""
    inspect = celery.control.inspect()
    stats = inspect.stats()
    active = inspect.active()

    return {
        'queue_depth': sum(len(v) for v in active.values()),
        'worker_count': len(stats)
    }
```

## Step 5: Load Balancing

### Nginx Configuration
```nginx
upstream fhir_backends {
    least_conn;  # Load balancing method
    server 192.168.1.10:8000 max_fails=3 fail_timeout=30s;
    server 192.168.1.11:8000 max_fails=3 fail_timeout=30s;
    server 192.168.1.12:8000 max_fails=3 fail_timeout=30s;
}

server {
    listen 80;
    server_name api.healthcare.example.com;

    client_max_body_size 50M;

    gzip on;
    gzip_types text/plain application/json;

    location /fhir/ {
        proxy_pass http://fhir_backends;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;

        # Connection timeout
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;

        # Buffering
        proxy_buffering on;
        proxy_buffer_size 4k;
        proxy_buffers 8 4k;
    }

    location ~ /healthcheck$ {
        access_log off;
        proxy_pass http://fhir_backends;
    }
}
```

## Step 6: Monitoring Performance

### Metrics Collection
```python
from prometheus_client import Counter, Histogram, Gauge
import time

class PerformanceMetrics:
    # Request latency
    request_latency = Histogram(
        'request_latency_seconds',
        'Request latency in seconds',
        ['method', 'endpoint']
    )

    # Database queries
    db_query_time = Histogram(
        'db_query_seconds',
        'Database query time',
        ['query_type']
    )

    # Cache hit rate
    cache_hits = Counter(
        'cache_hits_total',
        'Total cache hits'
    )

    cache_misses = Counter(
        'cache_misses_total',
        'Total cache misses'
    )

    # Active connections
    active_connections = Gauge(
        'active_connections',
        'Number of active connections'
    )

    def measure_request(self, method, endpoint):
        """Measure request latency"""
        start_time = time.time()
        yield
        duration = time.time() - start_time
        self.request_latency.labels(method=method, endpoint=endpoint).observe(duration)

    def measure_query(self, query_type):
        """Measure database query"""
        start_time = time.time()
        yield
        duration = time.time() - start_time
        self.db_query_time.labels(query_type=query_type).observe(duration)

    def cache_accessed(self, hit):
        """Record cache access"""
        if hit:
            self.cache_hits.inc()
        else:
            self.cache_misses.inc()

    def report_performance(self):
        """Generate performance report"""
        return {
            'avg_request_latency': self.request_latency._sum / self.request_latency._count,
            'cache_hit_rate': (self.cache_hits._value) / (self.cache_hits._value + self.cache_misses._value) * 100,
            'active_connections': self.active_connections._value
        }
```

## Performance Targets

| Metric | Target | Monitoring |
|--------|--------|-----------|
| API Response Time (p95) | < 500ms | Prometheus |
| Database Query Time (p95) | < 100ms | New Relic |
| Cache Hit Rate | > 80% | Application metrics |
| Message Processing Latency | < 5s | Queue monitoring |
| System CPU Usage | < 70% | Grafana dashboard |
| Memory Usage | < 80% | System monitoring |
| Network Bandwidth | < 70% capacity | Network monitoring |

## Next Steps

1. Profile current performance
2. Identify bottlenecks
3. Implement caching
4. Optimize queries
5. Deploy load balancing
6. Monitor with metrics
