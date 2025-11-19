"""MQTT Sensor Client for IoT data collection"""
import paho.mqtt.client as mqtt
import json
import time
from datetime import datetime

class MQTTSensorClient:
    def __init__(self, broker_url, port=1883):
        self.broker = broker_url
        self.port = port
        self.client = mqtt.Client(client_id="sensor_collector")
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        
    def on_connect(self, client, userdata, flags, rc):
        print(f"Connected with result code {rc}")
        # Subscribe to all building sensors
        client.subscribe("building/+/+/+/temperature")
        client.subscribe("building/+/+/+/occupancy")
        client.subscribe("building/+/+/+/co2")
        
    def on_message(self, client, userdata, msg):
        try:
            data = json.loads(msg.payload.decode())
            # Parse topic
            parts = msg.topic.split('/')
            building_id = parts[1]
            floor = parts[2]
            zone = parts[3]
            sensor_type = parts[4]
            
            # Process sensor data
            self.process_data(building_id, floor, zone, sensor_type, data)
        except Exception as e:
            print(f"Error processing message: {e}")
            
    def process_data(self, building, floor, zone, sensor_type, data):
        # Store in database (InfluxDB example)
        point = {
            "measurement": sensor_type,
            "tags": {
                "building": building,
                "floor": floor,
                "zone": zone
            },
            "fields": {
                "value": data.get('value'),
            },
            "time": datetime.utcnow().isoformat()
        }
        # influx_client.write_points([point])
        print(f"{building}/{floor}/{zone}/{sensor_type}: {data.get('value')}")
        
    def start(self):
        self.client.connect(self.broker, self.port, 60)
        self.client.loop_forever()

if __name__ == '__main__':
    client = MQTTSensorClient('localhost')
    client.start()
