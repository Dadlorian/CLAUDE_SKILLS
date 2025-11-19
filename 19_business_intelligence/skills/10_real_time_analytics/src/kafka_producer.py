"""
Kafka Producer for Real-Time Events
Sends events to Kafka with proper serialization and error handling
"""
from kafka import KafkaProducer
from kafka.errors import KafkaError
import json
import logging
from datetime import datetime
from typing import Dict, Any

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EventProducer:
    def __init__(self, bootstrap_servers: list, topic: str):
        self.topic = topic
        self.producer = KafkaProducer(
            bootstrap_servers=bootstrap_servers,
            value_serializer=lambda v: json.dumps(v).encode('utf-8'),
            key_serializer=lambda k: k.encode('utf-8') if k else None,
            compression_type='lz4',
            batch_size=32768,  # 32KB
            linger_ms=10,      # Wait 10ms to batch
            acks='all',        # Wait for all replicas
            retries=3,
            max_in_flight_requests_per_connection=5
        )
        
    def send_event(self, event: Dict[str, Any], key: str = None):
        """Send event to Kafka with callback"""
        try:
            # Add timestamp if not present
            if 'timestamp' not in event:
                event['timestamp'] = datetime.utcnow().isoformat()
            
            future = self.producer.send(
                self.topic,
                key=key,
                value=event
            )
            
            # Add callback
            future.add_callback(self._on_send_success)
            future.add_errback(self._on_send_error)
            
            return future
            
        except Exception as e:
            logger.error(f"Failed to send event: {e}")
            raise
    
    def _on_send_success(self, record_metadata):
        logger.debug(f"Message sent to {record_metadata.topic} "
                    f"partition {record_metadata.partition} "
                    f"offset {record_metadata.offset}")
    
    def _on_send_error(self, exc):
        logger.error(f"Error sending message: {exc}")
    
    def flush(self):
        """Flush all buffered messages"""
        self.producer.flush()
    
    def close(self):
        """Close producer"""
        self.producer.close()

# Example usage
if __name__ == "__main__":
    producer = EventProducer(
        bootstrap_servers=['localhost:9092'],
        topic='events'
    )
    
    # Send sample events
    for i in range(100):
        event = {
            'event_id': f'evt_{i}',
            'user_id': i % 10,
            'event_type': 'page_view',
            'page': f'/page/{i}',
            'revenue': i * 10.5 if i % 5 == 0 else None
        }
        
        producer.send_event(event, key=str(event['user_id']))
    
    producer.flush()
    producer.close()
