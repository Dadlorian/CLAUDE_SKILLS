"""
Kafka Consumer for Real-Time Events
Consumes events from Kafka with proper offset management
"""
from kafka import KafkaConsumer
from kafka.errors import KafkaError
import json
import logging
from typing import Callable

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EventConsumer:
    def __init__(self, bootstrap_servers: list, topic: str, group_id: str):
        self.consumer = KafkaConsumer(
            topic,
            bootstrap_servers=bootstrap_servers,
            group_id=group_id,
            value_deserializer=lambda m: json.loads(m.decode('utf-8')),
            key_deserializer=lambda k: k.decode('utf-8') if k else None,
            auto_offset_reset='earliest',
            enable_auto_commit=False,  # Manual commit for reliability
            max_poll_records=500,
            max_poll_interval_ms=300000  # 5 minutes
        )
        
    def consume(self, process_func: Callable, batch_size: int = 100):
        """Consume messages and process in batches"""
        try:
            batch = []
            
            for message in self.consumer:
                try:
                    event = message.value
                    batch.append(event)
                    
                    # Process batch when full
                    if len(batch) >= batch_size:
                        process_func(batch)
                        self.consumer.commit()
                        batch = []
                        
                except Exception as e:
                    logger.error(f"Error processing message: {e}")
                    # Send to DLQ
                    self._send_to_dlq(message)
            
            # Process remaining batch
            if batch:
                process_func(batch)
                self.consumer.commit()
                
        except KeyboardInterrupt:
            logger.info("Shutting down consumer...")
        finally:
            self.consumer.close()
    
    def _send_to_dlq(self, message):
        """Send failed message to dead letter queue"""
        # Implementation for DLQ
        pass

# Example usage
def process_events(events):
    for event in events:
        print(f"Processing: {event['event_type']} - {event['user_id']}")

if __name__ == "__main__":
    consumer = EventConsumer(
        bootstrap_servers=['localhost:9092'],
        topic='events',
        group_id='analytics-consumer'
    )
    
    consumer.consume(process_events)
