"""Flink PyFlink Streaming Job"""
from pyflink.datastream import StreamExecutionEnvironment
from pyflink.datastream.connectors import FlinkKafkaConsumer
from pyflink.common.serialization import SimpleStringSchema
from pyflink.datastream.functions import MapFunction
import json

class EventParser(MapFunction):
    def map(self, value):
        event = json.loads(value)
        return event

env = StreamExecutionEnvironment.get_execution_environment()
env.set_parallelism(4)

kafka_props = {
    'bootstrap.servers': 'localhost:9092',
    'group.id': 'flink-consumer'
}

kafka_source = FlinkKafkaConsumer(
    topics='events',
    deserialization_schema=SimpleStringSchema(),
    properties=kafka_props
)

events = env.add_source(kafka_source).map(EventParser())

events.print()
env.execute("PyFlink Streaming Job")
