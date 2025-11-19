"""Prometheus Metrics Collector"""
from prometheus_client import Counter, Histogram, Gauge, start_http_server
import time

# Define metrics
events_processed = Counter('events_processed_total', 
                          'Total events processed',
                          ['source', 'event_type'])

processing_latency = Histogram('processing_latency_seconds',
                              'Processing latency in seconds',
                              buckets=[0.01, 0.05, 0.1, 0.5, 1, 5])

consumer_lag = Gauge('consumer_lag_messages',
                    'Consumer lag in messages',
                    ['topic', 'partition'])

class MetricsCollector:
    def record_event(self, source, event_type):
        events_processed.labels(source=source, event_type=event_type).inc()
    
    def record_latency(self, latency_seconds):
        processing_latency.observe(latency_seconds)
    
    def update_lag(self, topic, partition, lag):
        consumer_lag.labels(topic=topic, partition=str(partition)).set(lag)

if __name__ == '__main__':
    start_http_server(8000)
    collector = MetricsCollector()
    
    while True:
        collector.record_event('kafka', 'page_view')
        time.sleep(1)
