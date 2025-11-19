"""Schema Registry Client for Avro Serialization"""
from confluent_kafka import avro
from confluent_kafka.avro import AvroProducer, AvroConsumer
from confluent_kafka.avro.cached_schema_registry_client import CachedSchemaRegistryClient

value_schema_str = """
{
   "type": "record",
   "name": "Event",
   "namespace": "com.analytics.events",
   "fields": [
       {"name": "event_id", "type": "string"},
       {"name": "user_id", "type": "long"},
       {"name": "timestamp", "type": "long"},
       {"name": "event_type", "type": "string"},
       {"name": "revenue", "type": ["null", "double"], "default": null}
   ]
}
"""

value_schema = avro.loads(value_schema_str)

producer = AvroProducer({
    'bootstrap.servers': 'localhost:9092',
    'schema.registry.url': 'http://localhost:8081'
}, default_value_schema=value_schema)

# Send event
producer.produce(topic='events', value={
    'event_id': 'evt_123',
    'user_id': 12345,
    'timestamp': 1642246200000,
    'event_type': 'purchase',
    'revenue': 99.99
})
producer.flush()
