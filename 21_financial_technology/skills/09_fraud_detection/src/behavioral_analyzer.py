"""
Behavioral Analyzer - Analyze user behavior patterns
"""

import numpy as np
from typing import Dict


class BehavioralAnalyzer:
    """Analyze behavioral patterns"""

    def __init__(self, customer_profiles: Dict = None):
        self.profiles = customer_profiles or {}

    def score_behavioral_anomaly(self, customer_id: str,
                                  session_data: Dict) -> float:
        """Score behavioral anomaly"""
        if customer_id not in self.profiles:
            return 0.5  # Unknown

        profile = self.profiles[customer_id]

        score = 0.0

        # Check typing speed
        if 'typing_speed' in session_data:
            baseline = profile.get('avg_typing_speed', 45)
            current = session_data['typing_speed']
            z_score = abs(current - baseline) / max(profile.get('std_typing_speed', 10), 1)
            score += min(z_score / 3.0, 1.0) * 0.3

        # Check time of day
        hour = session_data.get('hour', 12)
        active_hours = profile.get('active_hours', list(range(9, 18)))
        if hour not in active_hours:
            score += 0.3

        # Check device
        known_devices = profile.get('known_devices', [])
        if session_data.get('device_id') not in known_devices:
            score += 0.4

        return min(score, 1.0)
