"""Digital Twin for Building Simulation"""
import numpy as np

class BuildingDigitalTwin:
    def __init__(self, building_params):
        self.params = building_params
        self.thermal_mass = building_params['thermal_mass']
        self.r_value = building_params['insulation_r_value']
        
    def simulate_temperature(self, outdoor_temp, hvac_power, duration_hours):
        """Simulate indoor temperature over time"""
        dt = 0.1  # 6 minute time steps
        steps = int(duration_hours / dt)
        
        indoor_temp = [self.params['initial_temp']]
        
        for i in range(steps):
            current_temp = indoor_temp[-1]
            
            # Heat loss/gain through walls
            heat_transfer = (outdoor_temp - current_temp) / self.r_value
            
            # HVAC heating/cooling
            hvac_effect = hvac_power * 0.01  # Simplified
            
            # Temperature change
            delta_temp = (heat_transfer + hvac_effect) / self.thermal_mass * dt
            new_temp = current_temp + delta_temp
            
            indoor_temp.append(new_temp)
            
        return indoor_temp
        
    def optimize_hvac_schedule(self, target_temp, outdoor_forecast):
        """Find optimal HVAC schedule"""
        best_schedule = []
        min_cost = float('inf')
        
        # Simple optimization (in practice, use proper algorithm)
        for start_hour in range(24):
            cost = self.calculate_cost(start_hour, target_temp, outdoor_forecast)
            if cost < min_cost:
                min_cost = cost
                best_schedule = {'start': start_hour, 'cost': cost}
                
        return best_schedule
        
    def calculate_cost(self, start_hour, target_temp, outdoor_forecast):
        """Calculate energy cost for schedule"""
        # Simplified cost calculation
        return np.random.random() * 100

# Example
twin = BuildingDigitalTwin({
    'thermal_mass': 5000,
    'insulation_r_value': 20,
    'initial_temp': 70
})

temps = twin.simulate_temperature(outdoor_temp=95, hvac_power=-50, duration_hours=8)
print(f"Final temp: {temps[-1]:.1f}°F")
