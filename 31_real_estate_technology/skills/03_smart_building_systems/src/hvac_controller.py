"""HVAC Control Logic"""
from datetime import datetime, time as dt_time

class HVACController:
    def __init__(self, zone_config):
        self.zone_config = zone_config
        
    def calculate_setpoint(self, zone_id, current_time=None):
        """Calculate appropriate setpoint based on schedule"""
        if current_time is None:
            current_time = datetime.now()
            
        zone = self.zone_config[zone_id]
        is_occupied = self.is_occupied_time(zone, current_time)
        
        if is_occupied:
            return zone['occupied_setpoint']
        else:
            return zone['unoccupied_setpoint']
            
    def is_occupied_time(self, zone, current_time):
        """Check if current time is within occupied schedule"""
        weekday = current_time.weekday()
        current = current_time.time()
        
        if weekday < 5:  # Monday-Friday
            start = dt_time(7, 0)
            end = dt_time(18, 0)
            return start <= current <= end
        return False
        
    def control_zone(self, zone_id, temperature, occupancy, outdoor_temp):
        """Main control logic"""
        setpoint = self.calculate_setpoint(zone_id)
        
        # Occupancy override
        if occupancy['occupied']:
            setpoint = self.zone_config[zone_id]['occupied_setpoint']
        elif occupancy.get('minutes_vacant', 0) > 30:
            setpoint = self.zone_config[zone_id]['unoccupied_setpoint']
            
        # Calculate heating/cooling demand
        error = setpoint - temperature
        
        # Economizer logic
        use_economizer = self.should_use_economizer(setpoint, outdoor_temp)
        
        return {
            'setpoint': setpoint,
            'heating_demand': max(0, error),
            'cooling_demand': max(0, -error),
            'economizer': use_economizer
        }
        
    def should_use_economizer(self, setpoint, outdoor_temp):
        """Determine if economizer should be active"""
        return 55 < outdoor_temp < setpoint - 5
        
    def demand_control_ventilation(self, co2_level):
        """Calculate ventilation rate based on CO2"""
        if co2_level > 1000:
            return 1.5  # 150% of minimum
        elif co2_level > 800:
            return 1.2  # 120% of minimum
        else:
            return 1.0  # Minimum outdoor air

# Example usage
zone_config = {
    'zone_1': {
        'occupied_setpoint': 72,
        'unoccupied_setpoint': 78
    }
}

controller = HVACController(zone_config)
result = controller.control_zone('zone_1', 75, {'occupied': True}, 65)
print(result)
