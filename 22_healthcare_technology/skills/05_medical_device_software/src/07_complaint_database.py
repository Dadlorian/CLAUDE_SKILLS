"""Post-Market Surveillance: Complaint Database Management"""
from datetime import datetime
from dataclasses import dataclass, asdict
from typing import List, Optional
import json

class Severity(Enum):
    CRITICAL = "Critical - Death/Serious Injury"
    MAJOR = "Major - Significant Impact"
    MINOR = "Minor - Inconvenience"
    INFORMATIONAL = "Informational"

@dataclass
class Complaint:
    """Medical device complaint record per post-market surveillance requirements"""
    complaint_id: str
    date_received: str
    device_model: str
    device_serial: str
    device_version: str
    reporter_name: str
    severity: str
    description: str
    patient_outcome: str
    investigation_status: str  # Open, In Progress, Closed
    root_cause: Optional[str] = None
    corrective_action: Optional[str] = None
    mdr_reported: bool = False

class ComplaintDatabase:
    """
    Maintain complaint records per 21 CFR 803 (MDR) and ISO 14971.
    FDA expects systematic complaint tracking and trend analysis.
    """
    
    def __init__(self, device_name: str):
        self.device_name = device_name
        self.complaints: List[Complaint] = []
    
    def add_complaint(self, complaint: Complaint):
        """Record a new complaint with audit trail"""
        self.complaints.append(complaint)
        print(f"Complaint {complaint.complaint_id} recorded at {datetime.now()}")
    
    def get_critical_complaints(self) -> List[Complaint]:
        """Get all critical complaints requiring immediate investigation"""
        return [c for c in self.complaints if "Critical" in c.severity]
    
    def analyze_trends(self) -> dict:
        """
        Analyze complaint trends for annual FDA report.
        If trend increases: May trigger corrective action.
        """
        
        severity_count = {}
        for complaint in self.complaints:
            sev = complaint.severity
            severity_count[sev] = severity_count.get(sev, 0) + 1
        
        # Identify most common issues
        issues = {}
        for complaint in self.complaints:
            issue = complaint.description[:50]  # First 50 chars
            issues[issue] = issues.get(issue, 0) + 1
        
        # Sort by frequency
        top_issues = sorted(issues.items(), key=lambda x: x[1], reverse=True)[:5]
        
        return {
            'total_complaints': len(self.complaints),
            'by_severity': severity_count,
            'top_issues': top_issues,
            'open_investigations': sum(
                1 for c in self.complaints if c.investigation_status != 'Closed'
            )
        }
    
    def export_for_submission(self, filename: str):
        """Export complaint database for FDA submission"""
        data = {
            'device': self.device_name,
            'export_date': datetime.now().isoformat(),
            'total_complaints': len(self.complaints),
            'trends': self.analyze_trends(),
            'complaints': [asdict(c) for c in self.complaints]
        }
        
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)

# Example: Track glucose monitor complaints
def example_complaint_database():
    db = ComplaintDatabase("Glucose Monitor SaMD")
    
    # Record a complaint
    complaint1 = Complaint(
        complaint_id='COMPLAINT-001',
        date_received='2024-01-15',
        device_model='GlucoTrack Pro',
        device_serial='SN-12345',
        device_version='v2.1.0',
        reporter_name='Hospital Lab Technician',
        severity='Major - Significant Impact',
        description='Glucose reading displays as zero occasionally',
        patient_outcome='Delayed treatment, patient hyperglycemia',
        investigation_status='Closed',
        root_cause='Software rounding error in certain glucose ranges',
        corrective_action='Released v2.2.0 with improved rounding algorithm',
        mdr_reported=True
    )
    
    db.add_complaint(complaint1)
    
    # Analyze trends
    trends = db.analyze_trends()
    print(f"Total complaints: {trends['total_complaints']}")
    
    return db
