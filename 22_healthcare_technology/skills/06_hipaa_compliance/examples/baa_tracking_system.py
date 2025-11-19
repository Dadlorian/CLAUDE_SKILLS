"""Business Associate Agreement Tracking System"""
from datetime import datetime, timedelta

class BAATracker:
    def __init__(self):
        self.business_associates = []

    def add_ba(self, ba_info):
        """Add or update business associate"""
        ba = {
            'name': ba_info['name'],
            'service': ba_info['service'],
            'baa_signed': ba_info.get('baa_signed', False),
            'baa_date': ba_info.get('baa_date'),
            'baa_expiration': ba_info.get('baa_expiration'),
            'last_assessment': ba_info.get('last_assessment'),
            'risk_level': ba_info.get('risk_level', 'MEDIUM'),
            'phi_types': ba_info.get('phi_types', []),
            'contact_email': ba_info.get('contact_email'),
            'soc2_report': ba_info.get('soc2_report', False),
            'incidents': []
        }
        self.business_associates.append(ba)
        return ba

    def get_expiring_baas(self, days=90):
        """Get BAAs expiring within specified days"""
        today = datetime.now()
        threshold = today + timedelta(days=days)
        
        expiring = []
        for ba in self.business_associates:
            if ba['baa_expiration']:
                exp_date = datetime.fromisoformat(ba['baa_expiration'])
                if today <= exp_date <= threshold:
                    expiring.append(ba)
        
        return expiring

    def get_unsigned_baas(self):
        """Get BAs without signed BAAs"""
        return [ba for ba in self.business_associates if not ba['baa_signed']]

    def needs_assessment(self, ba):
        """Check if BA needs reassessment"""
        if not ba['last_assessment']:
            return True
        
        last = datetime.fromisoformat(ba['last_assessment'])
        return datetime.now() - last > timedelta(days=365)

    def record_incident(self, ba_name, incident_details):
        """Record incident reported by BA"""
        for ba in self.business_associates:
            if ba['name'] == ba_name:
                ba['incidents'].append({
                    'date': datetime.now().isoformat(),
                    'details': incident_details
                })
                break
