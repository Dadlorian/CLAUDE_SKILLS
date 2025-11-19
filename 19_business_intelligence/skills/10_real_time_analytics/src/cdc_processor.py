"""Change Data Capture Processor"""
import json
from kafka import KafkaConsumer
from clickhouse_driver import Client

consumer = KafkaConsumer(
    'mysql.ecommerce.orders',
    bootstrap_servers=['localhost:9092'],
    value_deserializer=lambda m: json.loads(m.decode('utf-8'))
)

clickhouse = Client(host='clickhouse')

for message in consumer:
    change = message.value
    operation = change['payload']['op']
    
    if operation == 'c':  # Create
        data = change['payload']['after']
        clickhouse.execute(
            "INSERT INTO orders VALUES",
            [(data['id'], data['user_id'], data['total'])]
        )
    elif operation == 'u':  # Update
        data = change['payload']['after']
        clickhouse.execute(
            "ALTER TABLE orders UPDATE total = %(total)s WHERE id = %(id)s",
            {'total': data['total'], 'id': data['id']}
        )
    elif operation == 'd':  # Delete
        data = change['payload']['before']
        clickhouse.execute(
            "ALTER TABLE orders DELETE WHERE id = %(id)s",
            {'id': data['id']}
        )
