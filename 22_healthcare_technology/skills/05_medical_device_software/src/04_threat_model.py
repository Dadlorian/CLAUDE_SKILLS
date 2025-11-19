"""FDA Cybersecurity: Threat Model Implementation"""
from dataclasses import dataclass
from enum import Enum
from typing import List

class ThreatType(Enum):
    """STRIDE threat categories"""
    SPOOFING = "Spoofing Identity"
    TAMPERING = "Tampering Data"
    REPUDIATION = "Repudiation"
    INFO_DISCLOSURE = "Information Disclosure"
    DENIAL_SERVICE = "Denial of Service"
    ELEVATION_PRIV = "Elevation of Privilege"

class Severity(Enum):
    CRITICAL = 4
    HIGH = 3
    MEDIUM = 2
    LOW = 1

@dataclass
class Threat:
    """Security threat per FDA cybersecurity guidance"""
    id: str
    threat_type: ThreatType
    description: str
    asset_affected: str
    likelihood: int  # 1-5
    impact: int      # 1-5
    control_description: str
    control_effectiveness: int  # 1-100 (%)
    
    @property
    def initial_risk(self) -> int:
        return self.likelihood * self.impact
    
    @property
    def residual_risk(self) -> int:
        """Risk after control effectiveness"""
        return int(self.initial_risk * (1 - self.control_effectiveness/100))

class ThreatModel:
    """Threat model per FDA premarket guidance"""
    
    def __init__(self, device_name: str):
        self.device_name = device_name
        self.threats: List[Threat] = []
    
    def add_threat(self, threat: Threat):
        """Document identified threat"""
        self.threats.append(threat)
    
    def summarize(self) -> dict:
        """Generate threat model summary for submission"""
        critical_threats = [t for t in self.threats if t.residual_risk >= 15]
        high_threats = [t for t in self.threats if 9 <= t.residual_risk < 15]
        
        return {
            'device': self.device_name,
            'total_threats_identified': len(self.threats),
            'critical_threats': len(critical_threats),
            'high_threats': len(high_threats),
            'threats': self.threats
        }

# Example: Glucose Monitoring Device Threat Model
def create_glucose_device_threat_model():
    model = ThreatModel("Glucose Monitor SaMD")
    
    # Threat 1: Data tampering
    model.add_threat(Threat(
        id='T001',
        threat_type=ThreatType.TAMPERING,
        description='Attacker modifies glucose readings in transit',
        asset_affected='Patient glucose data',
        likelihood=2,  # Remote
        impact=5,      # Critical
        control_description='Encrypt data with AES-256, use HMAC for integrity',
        control_effectiveness=99
    ))
    
    # Threat 2: Unauthorized access
    model.add_threat(Threat(
        id='T002',
        threat_type=ThreatType.INFO_DISCLOSURE,
        description='PHI accessed by unauthorized user',
        asset_affected='Patient health information',
        likelihood=3,  # Occasional
        impact=4,      # Major
        control_description='Require password + 2FA, role-based access control',
        control_effectiveness=95
    ))
    
    # Threat 3: Denial of Service
    model.add_threat(Threat(
        id='T003',
        threat_type=ThreatType.DENIAL_SERVICE,
        description='Device becomes unavailable due to DoS attack',
        asset_affected='Device availability',
        likelihood=2,  # Remote
        impact=4,      # Major
        control_description='Rate limiting, input validation, server hardening',
        control_effectiveness=85
    ))
    
    return model
