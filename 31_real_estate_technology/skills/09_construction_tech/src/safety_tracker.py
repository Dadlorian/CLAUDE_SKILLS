"""Construction Safety Tracking"""
from datetime import datetime

class SafetyTracker:
    def __init__(self):
        self.incidents = []
        self.inspections = []
        
    def log_incident(self, incident_type, severity, description):
        """Log safety incident"""
        incident = {
            'type': incident_type,
            'severity': severity,  # minor, moderate, serious
            'description': description,
            'timestamp': datetime.now(),
            'status': 'open'
        }
        self.incidents.append(incident)
        
        if severity == 'serious':
            self.send_alert(incident)
            
        return incident
        
    def log_inspection(self, inspector, findings):
        """Log safety inspection"""
        inspection = {
            'inspector': inspector,
            'timestamp': datetime.now(),
            'findings': findings,
            'corrective_actions': []
        }
        self.inspections.append(inspection)
        return inspection
        
    def calculate_safety_metrics(self):
        """Calculate safety KPIs"""
        total_incidents = len(self.incidents)
        serious_incidents = len([i for i in self.incidents if i['severity'] == 'serious'])
        
        return {
            'total_incidents': total_incidents,
            'serious_incidents': serious_incidents,
            'days_since_last_incident': self.days_since_last_incident(),
            'incident_rate': self.calculate_incident_rate()
        }
        
    def days_since_last_incident(self):
        if not self.incidents:
            return 0
            
        last = max(self.incidents, key=lambda x: x['timestamp'])
        return (datetime.now() - last['timestamp']).days
        
    def send_alert(self, incident):
        """Send alert for serious incidents"""
        # Email/SMS safety manager
        pass
