"""BACnet Integration for Building Automation"""
import BAC0
import time
from datetime import datetime

class BACnetController:
    def __init__(self, ip_address):
        self.bacnet = BAC0.connect(ip=ip_address)
        self.devices = {}
        
    def discover_devices(self):
        """Discover all BACnet devices on network"""
        self.bacnet.whois()
        time.sleep(5)
        for device in self.bacnet.devices:
            self.devices[device.id] = device
        return self.devices
        
    def read_temperature(self, device_id, object_id=1):
        """Read temperature from analog input"""
        value = self.bacnet.read(f'{device_id}:1 analogInput {object_id} presentValue')
        return value
        
    def write_setpoint(self, device_id, object_id, temperature, priority=8):
        """Write temperature setpoint"""
        self.bacnet.write(f'{device_id}:1 analogValue {object_id} presentValue {temperature} - {priority}')
        
    def read_zone_data(self, device_id):
        """Read all zone sensors"""
        data = {
            'temperature': self.bacnet.read(f'{device_id}:1 analogInput 1 presentValue'),
            'humidity': self.bacnet.read(f'{device_id}:1 analogInput 2 presentValue'),
            'occupancy': self.bacnet.read(f'{device_id}:1 binaryInput 1 presentValue'),
            'setpoint': self.bacnet.read(f'{device_id}:1 analogValue 1 presentValue')
        }
        return data
        
    def subscribe_cov(self, device_id, object_id, callback):
        """Subscribe to change-of-value notifications"""
        self.bacnet.subscribe_cov(f'{device_id}:1 analogInput {object_id}', callback=callback)

# Example usage
if __name__ == '__main__':
    controller = BACnetController('192.168.1.10/24')
    devices = controller.discover_devices()
    
    for device_id in devices:
        data = controller.read_zone_data(device_id)
        print(f"Device {device_id}: {data}")
