"""Telematics data analysis and scoring"""
from typing import List, Dict

class TelematicsAnalyzer:
    def analyze_trip(self, trip_data: Dict) -> Dict:
        """Analyze single trip"""
        return {
            "trip_id": trip_data.get('id'),
            "distance": trip_data.get('distance', 0),
            "speed_violations": self._count_speed_violations(trip_data),
            "hard_brakes": self._count_hard_brakes(trip_data),
            "accelerations": self._count_accelerations(trip_data),
            "safety_score": self._calculate_trip_score(trip_data)
        }
    
    def calculate_driver_score(self, trips: List[Dict]) -> int:
        """Calculate overall driver safety score (0-100)"""
        if not trips:
            return 50
        
        scores = [self._calculate_trip_score(trip) for trip in trips]
        avg_score = sum(scores) / len(scores)
        
        return int(avg_score)
    
    def _calculate_trip_score(self, trip: Dict) -> int:
        """Calculate score for a trip"""
        score = 100
        
        # Speeding penalty
        speed_violations = self._count_speed_violations(trip)
        score -= min(speed_violations * 5, 30)
        
        # Harsh braking penalty
        hard_brakes = self._count_hard_brakes(trip)
        score -= min(hard_brakes * 3, 20)
        
        # Acceleration penalty
        accelerations = self._count_accelerations(trip)
        score -= min(accelerations * 2, 15)
        
        return max(score, 0)
    
    def _count_speed_violations(self, trip: Dict) -> int:
        return len([e for e in trip.get('events', []) if e.get('type') == 'speeding'])
    
    def _count_hard_brakes(self, trip: Dict) -> int:
        return len([e for e in trip.get('events', []) if e.get('type') == 'harsh_brake'])
    
    def _count_accelerations(self, trip: Dict) -> int:
        return len([e for e in trip.get('events', []) if e.get('type') == 'acceleration'])

if __name__ == "__main__":
    analyzer = TelematicsAnalyzer()
    trip = {'id': 1, 'distance': 10, 'events': [{'type': 'speeding'}, {'type': 'harsh_brake'}]}
    result = analyzer.analyze_trip(trip)
    print(f"Trip Score: {result}")
