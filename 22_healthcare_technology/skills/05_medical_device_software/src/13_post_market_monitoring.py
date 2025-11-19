"""Post-Market Surveillance Real-World Performance Monitoring"""
import statistics
from datetime import datetime, timedelta
from typing import List, Dict

class PerformanceMonitor:
    """
    Monitor real-world device performance per FDA SaMD guidance.
    
    Requirements:
    - REQ-POST-002: Track real-world algorithm performance
    - REQ-POST-003: Alert if performance degrades
    - Regulatory: FDA expects postmarket surveillance plan
    """
    
    def __init__(self, device_id: str, baseline_sensitivity: float = 0.95):
        self.device_id = device_id
        self.baseline_sensitivity = baseline_sensitivity
        self.performance_data: List[Dict] = []
        self.alert_threshold = 0.90  # Alert if drops below 90%
    
    def record_reading(self, patient_id: str, predicted_value: float, 
                      actual_value: float, timestamp: str = None):
        """
        Record algorithm prediction vs actual result.
        Test Case: TC-MONITOR-001
        """
        
        if timestamp is None:
            timestamp = datetime.now().isoformat()
        
        # Calculate if prediction was correct
        accuracy_margin = 15  # ±15 mg/dL acceptable
        is_correct = abs(predicted_value - actual_value) <= accuracy_margin
        
        record = {
            'timestamp': timestamp,
            'patient_id': patient_id,
            'predicted': predicted_value,
            'actual': actual_value,
            'correct': is_correct,
            'margin': abs(predicted_value - actual_value)
        }
        
        self.performance_data.append(record)
        
        return is_correct
    
    def calculate_sensitivity(self) -> float:
        """
        Calculate current algorithm sensitivity.
        Model Card Requirement: Report performance metrics
        """
        if not self.performance_data:
            return None
        
        correct_predictions = sum(1 for d in self.performance_data if d['correct'])
        sensitivity = correct_predictions / len(self.performance_data)
        
        return sensitivity
    
    def check_for_performance_degradation(self) -> Dict:
        """
        Detect performance degradation per real-world monitoring plan.
        
        If detected → Trigger corrective action
        """
        
        if len(self.performance_data) < 100:
            return {'degradation_detected': False, 'reason': 'Insufficient data'}
        
        # Calculate recent performance (last 100 readings)
        recent_data = self.performance_data[-100:]
        recent_sensitivity = sum(1 for d in recent_data if d['correct']) / 100
        
        # Compare to baseline
        degradation_percent = ((self.baseline_sensitivity - recent_sensitivity) / 
                             self.baseline_sensitivity * 100)
        
        degraded = recent_sensitivity < self.alert_threshold
        
        return {
            'degradation_detected': degraded,
            'baseline_sensitivity': self.baseline_sensitivity,
            'current_sensitivity': recent_sensitivity,
            'degradation_percent': degradation_percent,
            'action': 'INVESTIGATE' if degraded else 'CONTINUE_MONITORING'
        }
    
    def analyze_by_patient_subgroup(self, subgroup_key: str) -> Dict:
        """
        FDA Requirement: Analyze algorithm performance across subgroups
        (age, gender, ethnicity, disease severity)
        
        Purpose: Detect bias or population-specific failures
        """
        
        # Group by subgroup key
        subgroups = {}
        for record in self.performance_data:
            # Simulated subgroup assignment
            subgroup = record['patient_id'][:2]  # Use patient ID prefix
            
            if subgroup not in subgroups:
                subgroups[subgroup] = []
            subgroups[subgroup].append(record)
        
        # Calculate metrics for each subgroup
        subgroup_analysis = {}
        for subgroup, records in subgroups.items():
            if len(records) >= 10:  # Minimum sample
                correct = sum(1 for r in records if r['correct'])
                sensitivity = correct / len(records)
                avg_margin = statistics.mean(r['margin'] for r in records)
                
                subgroup_analysis[subgroup] = {
                    'count': len(records),
                    'sensitivity': sensitivity,
                    'average_margin': avg_margin,
                    'flag_for_review': sensitivity < 0.90
                }
        
        return subgroup_analysis
    
    def generate_postmarket_report(self) -> Dict:
        """
        Generate quarterly post-market surveillance report for FDA.
        
        Regulatory: FDA SaMD guidance requires real-world performance tracking
        """
        
        return {
            'report_period': datetime.now().isoformat(),
            'device_id': self.device_id,
            'total_readings': len(self.performance_data),
            'overall_sensitivity': self.calculate_sensitivity(),
            'degradation_analysis': self.check_for_performance_degradation(),
            'subgroup_analysis': self.analyze_by_patient_subgroup('patient_group'),
            'recommendations': self._generate_recommendations()
        }
    
    def _generate_recommendations(self) -> List[str]:
        """Generate recommendations based on monitoring data"""
        recommendations = []
        
        sensitivity = self.calculate_sensitivity()
        if sensitivity and sensitivity < self.alert_threshold:
            recommendations.append("Algorithm performance below threshold - investigate")
            recommendations.append("Consider algorithm retraining with current data")
            recommendations.append("Notify FDA if performance drops further")
        
        if len(self.performance_data) > 500:
            recommendations.append("Sufficient real-world data collected for model update")
        
        return recommendations

# Example usage
def example_postmarket_monitoring():
    monitor = PerformanceMonitor("GLUCOSE-001", baseline_sensitivity=0.95)
    
    # Simulate 150 readings over time
    for i in range(150):
        predicted = 120 + (i % 50)  # Simulate varying readings
        actual = predicted + (i % 20 - 10)  # Add some variation
        
        monitor.record_reading(
            patient_id=f"P{i:03d}",
            predicted_value=predicted,
            actual_value=actual
        )
    
    # Generate report
    report = monitor.generate_postmarket_report()
    print(f"Sensitivity: {report['overall_sensitivity']:.2%}")
    print(f"Degradation Detected: {report['degradation_analysis']['degradation_detected']}")
    
    return monitor, report
