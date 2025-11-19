"""
Security Architecture Toolkit
Comprehensive tools for threat modeling, risk assessment, and security architecture design
"""

from enum import Enum
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Set
from datetime import datetime
import json


# ==================== Threat Modeling ====================

class ThreatCategory(Enum):
    """STRIDE threat categories"""
    SPOOFING = "Spoofing Identity"
    TAMPERING = "Tampering with Data"
    REPUDIATION = "Repudiation"
    INFORMATION_DISCLOSURE = "Information Disclosure"
    DENIAL_OF_SERVICE = "Denial of Service"
    ELEVATION_OF_PRIVILEGE = "Elevation of Privilege"


class Severity(Enum):
    """Risk severity levels"""
    CRITICAL = "Critical"
    HIGH = "High"
    MEDIUM = "Medium"
    LOW = "Low"
    INFO = "Informational"


@dataclass
class Component:
    """System component for threat modeling"""
    component_id: str
    name: str
    component_type: str  # web_server, database, api, etc.
    description: str
    trust_boundary: str
    data_processed: List[str] = field(default_factory=list)
    dependencies: List[str] = field(default_factory=list)


@dataclass
class DataFlow:
    """Data flow between components"""
    flow_id: str
    name: str
    source_component: str
    destination_component: str
    protocol: str
    port: Optional[int] = None
    encrypted: bool = False
    authenticated: bool = False
    sensitive_data: bool = False
    description: str = ""


@dataclass
class Threat:
    """Identified threat"""
    threat_id: str
    title: str
    category: ThreatCategory
    affected_component: str
    description: str
    severity: Severity
    likelihood: int  # 1-5
    impact: int  # 1-5
    mitigation: str
    mitigation_status: str = "Proposed"  # Proposed, Implemented, Accepted Risk
    cve_references: List[str] = field(default_factory=list)


@dataclass
class Control:
    """Security control"""
    control_id: str
    name: str
    description: str
    control_type: str  # Preventive, Detective, Corrective
    implementation_status: str  # Planned, In Progress, Implemented
    effectiveness: str  # Low, Medium, High
    cost: str  # Low, Medium, High
    threats_mitigated: List[str] = field(default_factory=list)


class ThreatModelingEngine:
    """
    STRIDE-based threat modeling engine

    Features:
    - Component and data flow modeling
    - Automated threat identification
    - Risk scoring
    - Control mapping
    - Report generation
    """

    def __init__(self, system_name: str):
        self.system_name = system_name
        self.components: Dict[str, Component] = {}
        self.data_flows: Dict[str, DataFlow] = {}
        self.threats: Dict[str, Threat] = {}
        self.controls: Dict[str, Control] = {}

    def add_component(self, component: Component):
        """Add system component"""
        self.components[component.component_id] = component

    def add_data_flow(self, data_flow: DataFlow):
        """Add data flow"""
        self.data_flows[data_flow.flow_id] = data_flow

    def identify_threats(self) -> List[Threat]:
        """Automatically identify threats using STRIDE"""
        identified_threats = []

        # Analyze each component
        for comp_id, component in self.components.items():
            # Spoofing threats
            identified_threats.extend(
                self._identify_spoofing_threats(component)
            )

            # Denial of Service threats
            identified_threats.extend(
                self._identify_dos_threats(component)
            )

            # Elevation of Privilege threats
            identified_threats.extend(
                self._identify_elevation_threats(component)
            )

        # Analyze data flows
        for flow_id, data_flow in self.data_flows.items():
            # Tampering threats
            identified_threats.extend(
                self._identify_tampering_threats(data_flow)
            )

            # Information Disclosure threats
            identified_threats.extend(
                self._identify_disclosure_threats(data_flow)
            )

            # Repudiation threats
            identified_threats.extend(
                self._identify_repudiation_threats(data_flow)
            )

        # Add to threat store
        for threat in identified_threats:
            self.threats[threat.threat_id] = threat

        return identified_threats

    def _identify_spoofing_threats(self, component: Component) -> List[Threat]:
        """Identify spoofing/authentication threats"""
        threats = []

        if component.component_type in ['api', 'web_server', 'service']:
            threat = Threat(
                threat_id=f"SPOOF-{component.component_id}-001",
                title=f"Spoofing attack on {component.name}",
                category=ThreatCategory.SPOOFING,
                affected_component=component.component_id,
                description=f"Attacker could spoof identity to access {component.name}",
                severity=Severity.HIGH,
                likelihood=3,
                impact=4,
                mitigation="Implement strong authentication (OAuth 2.0, mTLS, API keys)"
            )
            threats.append(threat)

        return threats

    def _identify_tampering_threats(self, data_flow: DataFlow) -> List[Threat]:
        """Identify tampering threats"""
        threats = []

        if not data_flow.encrypted and data_flow.sensitive_data:
            threat = Threat(
                threat_id=f"TAMP-{data_flow.flow_id}-001",
                title=f"Data tampering in {data_flow.name}",
                category=ThreatCategory.TAMPERING,
                affected_component=data_flow.source_component,
                description=f"Unencrypted sensitive data could be tampered in transit",
                severity=Severity.CRITICAL,
                likelihood=4,
                impact=5,
                mitigation="Enable TLS 1.2+ encryption, implement integrity checks (HMAC)"
            )
            threats.append(threat)

        return threats

    def _identify_repudiation_threats(self, data_flow: DataFlow) -> List[Threat]:
        """Identify repudiation threats"""
        threats = []

        if not data_flow.authenticated:
            threat = Threat(
                threat_id=f"REPU-{data_flow.flow_id}-001",
                title=f"Repudiation of actions in {data_flow.name}",
                category=ThreatCategory.REPUDIATION,
                affected_component=data_flow.source_component,
                description="Users could deny performing actions due to lack of logging",
                severity=Severity.MEDIUM,
                likelihood=2,
                impact=3,
                mitigation="Implement comprehensive audit logging, digital signatures"
            )
            threats.append(threat)

        return threats

    def _identify_disclosure_threats(self, data_flow: DataFlow) -> List[Threat]:
        """Identify information disclosure threats"""
        threats = []

        if not data_flow.encrypted and data_flow.sensitive_data:
            threat = Threat(
                threat_id=f"DISC-{data_flow.flow_id}-001",
                title=f"Information disclosure in {data_flow.name}",
                category=ThreatCategory.INFORMATION_DISCLOSURE,
                affected_component=data_flow.source_component,
                description="Sensitive data transmitted without encryption",
                severity=Severity.CRITICAL,
                likelihood=4,
                impact=5,
                mitigation="Implement TLS 1.2+, use VPN for sensitive communications"
            )
            threats.append(threat)

        return threats

    def _identify_dos_threats(self, component: Component) -> List[Threat]:
        """Identify denial of service threats"""
        threats = []

        if component.component_type in ['api', 'web_server', 'database']:
            threat = Threat(
                threat_id=f"DOS-{component.component_id}-001",
                title=f"DoS attack on {component.name}",
                category=ThreatCategory.DENIAL_OF_SERVICE,
                affected_component=component.component_id,
                description="Service could be overwhelmed by excessive requests",
                severity=Severity.HIGH,
                likelihood=4,
                impact=4,
                mitigation="Implement rate limiting, DDoS protection, auto-scaling"
            )
            threats.append(threat)

        return threats

    def _identify_elevation_threats(self, component: Component) -> List[Threat]:
        """Identify privilege escalation threats"""
        threats = []

        if component.component_type in ['api', 'web_server', 'database']:
            threat = Threat(
                threat_id=f"ELEV-{component.component_id}-001",
                title=f"Privilege escalation in {component.name}",
                category=ThreatCategory.ELEVATION_OF_PRIVILEGE,
                affected_component=component.component_id,
                description="Attacker could escalate privileges",
                severity=Severity.CRITICAL,
                likelihood=2,
                impact=5,
                mitigation="Implement least privilege, RBAC, regular access reviews"
            )
            threats.append(threat)

        return threats

    def calculate_risk_score(self, threat: Threat) -> int:
        """Calculate risk score (DREAD methodology)"""
        # DREAD: Damage, Reproducibility, Exploitability, Affected users, Discoverability
        # Simplified: Likelihood * Impact
        return threat.likelihood * threat.impact

    def generate_threat_report(self) -> dict:
        """Generate comprehensive threat model report"""
        threats_by_severity = {
            Severity.CRITICAL: [],
            Severity.HIGH: [],
            Severity.MEDIUM: [],
            Severity.LOW: [],
            Severity.INFO: []
        }

        for threat in self.threats.values():
            threats_by_severity[threat.severity].append(threat)

        report = {
            'system_name': self.system_name,
            'generated_at': datetime.now().isoformat(),
            'summary': {
                'total_components': len(self.components),
                'total_data_flows': len(self.data_flows),
                'total_threats': len(self.threats),
                'critical_threats': len(threats_by_severity[Severity.CRITICAL]),
                'high_threats': len(threats_by_severity[Severity.HIGH]),
                'medium_threats': len(threats_by_severity[Severity.MEDIUM]),
                'low_threats': len(threats_by_severity[Severity.LOW])
            },
            'threats_by_severity': {
                severity.value: [
                    {
                        'threat_id': t.threat_id,
                        'title': t.title,
                        'category': t.category.value,
                        'affected_component': t.affected_component,
                        'risk_score': self.calculate_risk_score(t),
                        'mitigation': t.mitigation
                    }
                    for t in threats
                ]
                for severity, threats in threats_by_severity.items()
            }
        }

        return report


# ==================== Risk Assessment ====================

@dataclass
class RiskScenario:
    """Risk scenario for assessment"""
    scenario_id: str
    title: str
    description: str
    threat_source: str
    vulnerability: str
    likelihood: int  # 1-5
    impact: int  # 1-5
    current_controls: List[str] = field(default_factory=list)
    proposed_controls: List[str] = field(default_factory=list)
    risk_owner: str = ""


class RiskAssessmentEngine:
    """
    Quantitative and qualitative risk assessment

    Features:
    - Risk identification
    - Likelihood and impact assessment
    - Risk scoring (quantitative)
    - Risk matrix generation
    - Treatment recommendations
    """

    def __init__(self):
        self.risk_scenarios: Dict[str, RiskScenario] = {}
        self.risk_appetite = {
            'critical': 0,  # Accept 0 critical risks
            'high': 2,      # Accept max 2 high risks
            'medium': 10,   # Accept max 10 medium risks
            'low': 50       # Accept max 50 low risks
        }

    def add_risk_scenario(self, scenario: RiskScenario):
        """Add risk scenario"""
        self.risk_scenarios[scenario.scenario_id] = scenario

    def calculate_inherent_risk(self, scenario: RiskScenario) -> int:
        """Calculate inherent risk (before controls)"""
        return scenario.likelihood * scenario.impact

    def calculate_residual_risk(
        self,
        scenario: RiskScenario,
        control_effectiveness: float = 0.7
    ) -> float:
        """Calculate residual risk (after controls)"""
        inherent_risk = self.calculate_inherent_risk(scenario)

        # Reduce risk based on control effectiveness
        if scenario.current_controls:
            reduction_factor = len(scenario.current_controls) * control_effectiveness
            reduction_factor = min(reduction_factor, 0.9)  # Max 90% reduction
            residual_risk = inherent_risk * (1 - reduction_factor)
        else:
            residual_risk = inherent_risk

        return max(residual_risk, 0)

    def classify_risk_level(self, risk_score: float) -> str:
        """Classify risk level based on score"""
        if risk_score >= 20:
            return "Critical"
        elif risk_score >= 15:
            return "High"
        elif risk_score >= 8:
            return "Medium"
        else:
            return "Low"

    def recommend_treatment(self, scenario: RiskScenario) -> str:
        """Recommend risk treatment strategy"""
        inherent_risk = self.calculate_inherent_risk(scenario)
        residual_risk = self.calculate_residual_risk(scenario)
        risk_level = self.classify_risk_level(residual_risk)

        if risk_level in ["Critical", "High"]:
            return "Mitigate - Implement additional controls"
        elif risk_level == "Medium":
            if residual_risk < inherent_risk * 0.5:
                return "Accept - Risk adequately controlled"
            else:
                return "Mitigate - Strengthen existing controls"
        else:
            return "Accept - Risk within acceptable tolerance"

    def generate_risk_matrix(self) -> List[List[str]]:
        """Generate risk matrix visualization"""
        # 5x5 risk matrix
        matrix = [[[] for _ in range(5)] for _ in range(5)]

        for scenario in self.risk_scenarios.values():
            # Likelihood (1-5) maps to rows (0-4)
            # Impact (1-5) maps to columns (0-4)
            row = 5 - scenario.likelihood  # Reverse for display
            col = scenario.impact - 1

            matrix[row][col].append({
                'id': scenario.scenario_id,
                'title': scenario.title
            })

        return matrix

    def generate_risk_register(self) -> dict:
        """Generate comprehensive risk register"""
        register = {
            'assessment_date': datetime.now().isoformat(),
            'risk_scenarios': []
        }

        for scenario in self.risk_scenarios.values():
            inherent_risk = self.calculate_inherent_risk(scenario)
            residual_risk = self.calculate_residual_risk(scenario)

            register['risk_scenarios'].append({
                'scenario_id': scenario.scenario_id,
                'title': scenario.title,
                'description': scenario.description,
                'threat_source': scenario.threat_source,
                'vulnerability': scenario.vulnerability,
                'likelihood': scenario.likelihood,
                'impact': scenario.impact,
                'inherent_risk_score': inherent_risk,
                'inherent_risk_level': self.classify_risk_level(inherent_risk),
                'current_controls': scenario.current_controls,
                'residual_risk_score': residual_risk,
                'residual_risk_level': self.classify_risk_level(residual_risk),
                'treatment_recommendation': self.recommend_treatment(scenario),
                'risk_owner': scenario.risk_owner
            })

        # Sort by residual risk (descending)
        register['risk_scenarios'].sort(
            key=lambda x: x['residual_risk_score'],
            reverse=True
        )

        return register


# ==================== Security Architecture Design ====================

class SecurityArchitecture:
    """
    Security architecture design and validation

    Features:
    - Architecture pattern library
    - Security control mapping
    - Compliance checking
    - Architecture validation
    """

    def __init__(self, architecture_name: str):
        self.architecture_name = architecture_name
        self.layers = {
            'edge': [],
            'application': [],
            'data': [],
            'infrastructure': []
        }
        self.security_controls = {}
        self.compliance_requirements = set()

    def add_security_control(
        self,
        layer: str,
        control_name: str,
        control_details: dict
    ):
        """Add security control to architecture layer"""
        if layer not in self.layers:
            raise ValueError(f"Invalid layer: {layer}")

        self.layers[layer].append({
            'control_name': control_name,
            'details': control_details
        })

        self.security_controls[control_name] = {
            'layer': layer,
            'details': control_details
        }

    def validate_defense_in_depth(self) -> dict:
        """Validate defense-in-depth implementation"""
        validation_results = {
            'valid': True,
            'issues': [],
            'recommendations': []
        }

        # Check each layer has controls
        for layer, controls in self.layers.items():
            if not controls:
                validation_results['valid'] = False
                validation_results['issues'].append(
                    f"Layer '{layer}' has no security controls"
                )
                validation_results['recommendations'].append(
                    f"Add security controls to {layer} layer"
                )

        # Check for critical controls
        critical_controls = [
            'authentication',
            'authorization',
            'encryption',
            'logging',
            'monitoring'
        ]

        implemented_controls = set(self.security_controls.keys())

        for critical_control in critical_controls:
            if critical_control not in implemented_controls:
                validation_results['valid'] = False
                validation_results['issues'].append(
                    f"Missing critical control: {critical_control}"
                )

        return validation_results

    def map_to_compliance_framework(self, framework: str) -> dict:
        """Map architecture controls to compliance framework"""
        # Example: NIST CSF mapping
        nist_csf_mapping = {
            'authentication': ['PR.AC-1', 'PR.AC-7'],
            'authorization': ['PR.AC-4', 'PR.AC-5'],
            'encryption': ['PR.DS-1', 'PR.DS-2'],
            'logging': ['DE.AE-3', 'DE.CM-1'],
            'monitoring': ['DE.CM-7', 'DE.DP-4'],
            'backup': ['PR.IP-4'],
            'patching': ['PR.IP-1', 'PR.IP-12']
        }

        mapped_controls = {}
        coverage = {
            'identified': [],
            'protected': [],
            'detected': [],
            'responded': [],
            'recovered': []
        }

        for control_name in self.security_controls.keys():
            if control_name in nist_csf_mapping:
                mapped_controls[control_name] = nist_csf_mapping[control_name]

                for control_id in nist_csf_mapping[control_name]:
                    function = control_id.split('.')[0]
                    if function == 'ID':
                        coverage['identified'].append(control_id)
                    elif function == 'PR':
                        coverage['protected'].append(control_id)
                    elif function == 'DE':
                        coverage['detected'].append(control_id)
                    elif function == 'RS':
                        coverage['responded'].append(control_id)
                    elif function == 'RC':
                        coverage['recovered'].append(control_id)

        return {
            'framework': framework,
            'mapped_controls': mapped_controls,
            'coverage': coverage
        }

    def generate_architecture_diagram_data(self) -> dict:
        """Generate data for architecture diagram"""
        return {
            'architecture_name': self.architecture_name,
            'layers': {
                layer: [
                    {
                        'name': control['control_name'],
                        'type': control['details'].get('type', 'unknown')
                    }
                    for control in controls
                ]
                for layer, controls in self.layers.items()
            },
            'security_controls_count': len(self.security_controls),
            'defense_in_depth_score': self._calculate_depth_score()
        }

    def _calculate_depth_score(self) -> int:
        """Calculate defense-in-depth score (0-100)"""
        # Simple scoring: layers with controls * 20 (max 5 layers = 100)
        layers_with_controls = sum(1 for controls in self.layers.values() if controls)
        return min(layers_with_controls * 20, 100)


# ==================== Example Usage ====================

if __name__ == "__main__":
    print("=" * 60)
    print("THREAT MODELING EXAMPLE")
    print("=" * 60)

    # Create threat model
    tm = ThreatModelingEngine("E-Commerce Platform")

    # Add components
    web_server = Component(
        component_id="web-01",
        name="Web Application Server",
        component_type="web_server",
        description="Frontend web application",
        trust_boundary="DMZ",
        data_processed=["user_credentials", "personal_info"]
    )

    api_gateway = Component(
        component_id="api-01",
        name="API Gateway",
        component_type="api",
        description="Backend API gateway",
        trust_boundary="DMZ",
        data_processed=["payment_info", "user_data"]
    )

    database = Component(
        component_id="db-01",
        name="PostgreSQL Database",
        component_type="database",
        description="Primary database",
        trust_boundary="Internal",
        data_processed=["all_sensitive_data"]
    )

    tm.add_component(web_server)
    tm.add_component(api_gateway)
    tm.add_component(database)

    # Add data flows
    user_to_web = DataFlow(
        flow_id="flow-01",
        name="User to Web Server",
        source_component="user",
        destination_component="web-01",
        protocol="HTTPS",
        port=443,
        encrypted=True,
        authenticated=False,
        sensitive_data=True,
        description="User authentication and browsing"
    )

    web_to_api = DataFlow(
        flow_id="flow-02",
        name="Web to API",
        source_component="web-01",
        destination_component="api-01",
        protocol="HTTPS",
        port=8443,
        encrypted=True,
        authenticated=True,
        sensitive_data=True,
        description="API calls from web app"
    )

    api_to_db = DataFlow(
        flow_id="flow-03",
        name="API to Database",
        source_component="api-01",
        destination_component="db-01",
        protocol="PostgreSQL",
        port=5432,
        encrypted=False,  # Unencrypted - will trigger threat
        authenticated=True,
        sensitive_data=True,
        description="Database queries"
    )

    tm.add_data_flow(user_to_web)
    tm.add_data_flow(web_to_api)
    tm.add_data_flow(api_to_db)

    # Identify threats
    threats = tm.identify_threats()
    print(f"\nIdentified {len(threats)} threats:")
    for threat in threats[:5]:  # Show first 5
        print(f"\n- {threat.title}")
        print(f"  Category: {threat.category.value}")
        print(f"  Severity: {threat.severity.value}")
        print(f"  Mitigation: {threat.mitigation}")

    # Generate report
    report = tm.generate_threat_report()
    print(f"\n\nThreat Model Summary:")
    print(f"- Total Threats: {report['summary']['total_threats']}")
    print(f"- Critical: {report['summary']['critical_threats']}")
    print(f"- High: {report['summary']['high_threats']}")

    print("\n" + "=" * 60)
    print("RISK ASSESSMENT EXAMPLE")
    print("=" * 60)

    # Create risk assessment
    ra = RiskAssessmentEngine()

    # Add risk scenarios
    sql_injection_risk = RiskScenario(
        scenario_id="RISK-001",
        title="SQL Injection in User Login",
        description="Attacker exploits SQL injection vulnerability",
        threat_source="External attacker",
        vulnerability="Insufficient input validation",
        likelihood=4,
        impact=5,
        current_controls=["WAF", "Input validation"],
        proposed_controls=["Parameterized queries", "Code review"],
        risk_owner="Development Team"
    )

    ra.add_risk_scenario(sql_injection_risk)

    # Generate risk register
    risk_register = ra.generate_risk_register()
    print("\nRisk Register:")
    for scenario in risk_register['risk_scenarios']:
        print(f"\n- {scenario['title']}")
        print(f"  Inherent Risk: {scenario['inherent_risk_level']} ({scenario['inherent_risk_score']})")
        print(f"  Residual Risk: {scenario['residual_risk_level']} ({scenario['residual_risk_score']:.2f})")
        print(f"  Treatment: {scenario['treatment_recommendation']}")

    print("\n" + "=" * 60)
    print("SECURITY ARCHITECTURE EXAMPLE")
    print("=" * 60)

    # Create security architecture
    arch = SecurityArchitecture("Cloud-Native Application")

    # Add controls
    arch.add_security_control(
        'edge',
        'waf',
        {'type': 'preventive', 'provider': 'CloudFlare'}
    )

    arch.add_security_control(
        'application',
        'authentication',
        {'type': 'preventive', 'method': 'OAuth 2.0'}
    )

    arch.add_security_control(
        'data',
        'encryption',
        {'type': 'preventive', 'algorithm': 'AES-256-GCM'}
    )

    # Validate
    validation = arch.validate_defense_in_depth()
    print(f"\nDefense-in-Depth Valid: {validation['valid']}")
    if validation['issues']:
        print("Issues:")
        for issue in validation['issues']:
            print(f"  - {issue}")

    # Map to NIST CSF
    compliance_mapping = arch.map_to_compliance_framework("NIST CSF")
    print(f"\nNIST CSF Coverage:")
    for function, controls in compliance_mapping['coverage'].items():
        print(f"  {function.title()}: {len(controls)} controls")

    print("\n" + "=" * 60)
