# Security Architecture Frameworks Comparison

## Overview

This reference guide compares major security architecture frameworks, their strengths, use cases, and implementation approaches.

## Framework Comparison Matrix

| Framework | Focus Area | Complexity | Best For | Industry Adoption |
|-----------|-----------|------------|----------|-------------------|
| NIST CSF | Risk management | Medium | All industries | Very High |
| SABSA | Business-driven | High | Enterprise | Medium |
| TOGAF | EA with security | High | Enterprise | High |
| ISO 27001 | ISMS | Medium | Compliance | Very High |
| CIS Controls | Technical controls | Low-Medium | SMB/Enterprise | High |
| COBIT | IT Governance | Medium-High | IT departments | High |
| Zero Trust | Network security | Medium | Cloud/Modern | Growing |

## 1. NIST Cybersecurity Framework (CSF)

### Overview
Risk-based framework organized around five core functions.

### Core Functions

```yaml
nist_csf:
  identify:
    asset_management: "ID.AM"
    business_environment: "ID.BE"
    governance: "ID.GV"
    risk_assessment: "ID.RA"
    risk_management_strategy: "ID.RM"
    supply_chain_risk_management: "ID.SC"

  protect:
    identity_management_authentication: "PR.AC"
    awareness_training: "PR.AT"
    data_security: "PR.DS"
    information_protection: "PR.IP"
    maintenance: "PR.MA"
    protective_technology: "PR.PT"

  detect:
    anomalies_events: "DE.AE"
    security_continuous_monitoring: "DE.CM"
    detection_processes: "DE.DP"

  respond:
    response_planning: "RS.RP"
    communications: "RS.CO"
    analysis: "RS.AN"
    mitigation: "RS.MI"
    improvements: "RS.IM"

  recover:
    recovery_planning: "RC.RP"
    improvements: "RC.IM"
    communications: "RC.CO"
```

### Implementation Tiers

```python
# NIST CSF Implementation Tiers
class NISTCSFTiers:
    TIERS = {
        'tier_1_partial': {
            'risk_management': 'Ad hoc',
            'integrated_risk': 'Limited awareness',
            'external_participation': 'Not formalized',
            'characteristics': [
                'Reactive risk management',
                'Limited awareness of cyber risk',
                'No collaboration with external parties'
            ]
        },
        'tier_2_risk_informed': {
            'risk_management': 'Risk-informed',
            'integrated_risk': 'Aware but not formalized',
            'external_participation': 'Aware of external info',
            'characteristics': [
                'Risk management approved by management',
                'Cyber risk awareness but not enterprise-wide',
                'Limited external collaboration'
            ]
        },
        'tier_3_repeatable': {
            'risk_management': 'Repeatable',
            'integrated_risk': 'Organization-wide approach',
            'external_participation': 'Formal collaboration',
            'characteristics': [
                'Formal risk management policies',
                'Enterprise-wide cyber risk awareness',
                'Regular external collaboration'
            ]
        },
        'tier_4_adaptive': {
            'risk_management': 'Adaptive',
            'integrated_risk': 'Fully integrated',
            'external_participation': 'Real-time collaboration',
            'characteristics': [
                'Continuous improvement',
                'Risk-informed decision making',
                'Proactive threat intelligence sharing'
            ]
        }
    }
```

### Strengths
- Industry-neutral and widely adopted
- Risk-based approach
- Flexible implementation
- Strong government support

### Limitations
- Not prescriptive on technical controls
- Requires interpretation for specific use cases
- Can be overwhelming for small organizations

## 2. SABSA (Sherwood Applied Business Security Architecture)

### Overview
Business-driven enterprise security architecture framework based on Zachman Framework.

### SABSA Matrix

```
┌─────────────────────────────────────────────────────────┐
│              SABSA Matrix (Simplified)                  │
├──────────┬────────────────────────────────────────────┤
│          │ What    │ Why     │ How     │ Who    │ Where│
├──────────┼─────────┼─────────┼─────────┼────────┼──────┤
│Contextual│ Assets  │ Drivers │ Process │ People │ Loc. │
│(Business)│         │         │         │        │      │
├──────────┼─────────┼─────────┼─────────┼────────┼──────┤
│Conceptual│ Services│ Policies│ Strategy│ Organi-│ Domain│
│(Architect)│        │         │         │zation  │      │
├──────────┼─────────┼─────────┼─────────┼────────┼──────┤
│Logical   │ Entities│ Rules   │ Services│ Roles  │ Sites│
│(Designer)│         │         │         │        │      │
├──────────┼─────────┼─────────┼─────────┼────────┼──────┤
│Physical  │ Data    │ Standar-│ Mechani-│ Users  │ Plat-│
│(Builder) │ Formats │ ds      │ sms     │        │ forms│
├──────────┼─────────┼─────────┼─────────┼────────┼──────┤
│Component │ Items   │ Compli- │ Products│ Identit│ Addre│
│(Tradesman)│        │ ance    │         │ ies    │ sses │
└──────────┴─────────┴─────────┴─────────┴────────┴──────┘
```

### Business Attributes

```python
# SABSA Business Attributes
class SABSAAttributes:
    BUSINESS_ATTRIBUTES = {
        'availability': {
            'metric': 'Percentage uptime',
            'requirement': '99.99% availability',
            'controls': [
                'Redundancy',
                'Failover',
                'Disaster recovery',
                'High availability clusters'
            ]
        },
        'integrity': {
            'metric': 'Data accuracy and completeness',
            'requirement': 'Zero unauthorized modifications',
            'controls': [
                'Digital signatures',
                'Hash verification',
                'Change control',
                'Audit trails'
            ]
        },
        'confidentiality': {
            'metric': 'Unauthorized access attempts',
            'requirement': 'Zero data breaches',
            'controls': [
                'Encryption',
                'Access controls',
                'Data classification',
                'DLP'
            ]
        },
        'accountability': {
            'metric': 'Audit log completeness',
            'requirement': '100% action traceability',
            'controls': [
                'Comprehensive logging',
                'User identification',
                'Non-repudiation',
                'Audit reviews'
            ]
        },
        'auditability': {
            'metric': 'Audit trail accessibility',
            'requirement': 'Real-time access to logs',
            'controls': [
                'Centralized logging',
                'Log integrity protection',
                'SIEM integration',
                'Compliance reporting'
            ]
        }
    }
```

### Strengths
- Business-aligned approach
- Comprehensive methodology
- Strong traceability from business to technical

### Limitations
- Complex and resource-intensive
- Requires significant expertise
- Less prescriptive on technical implementation

## 3. Zero Trust Architecture

### Overview
Security model that assumes no implicit trust and verifies every access request.

### Core Principles

```python
# Zero Trust Architecture Components
class ZeroTrustArchitecture:
    def __init__(self):
        self.pillars = {
            'identity': self._identity_pillar(),
            'devices': self._device_pillar(),
            'networks': self._network_pillar(),
            'applications': self._application_pillar(),
            'data': self._data_pillar()
        }

    def _identity_pillar(self) -> dict:
        return {
            'principles': [
                'Strong authentication (MFA)',
                'Least privilege access',
                'Just-in-time access',
                'Continuous verification'
            ],
            'controls': {
                'authentication': {
                    'mfa_required': True,
                    'passwordless_preferred': True,
                    'adaptive_authentication': True,
                    'risk_based_auth': True
                },
                'authorization': {
                    'rbac': True,
                    'abac': True,
                    'dynamic_policies': True,
                    'session_monitoring': True
                }
            }
        }

    def _device_pillar(self) -> dict:
        return {
            'principles': [
                'Device inventory and visibility',
                'Device health verification',
                'Automated remediation',
                'Secure configuration'
            ],
            'controls': {
                'device_trust': {
                    'mdm_enrollment': 'Required',
                    'compliance_checking': True,
                    'encryption_required': True,
                    'os_version_minimum': 'Defined'
                },
                'posture_assessment': {
                    'antivirus_active': True,
                    'firewall_enabled': True,
                    'patches_current': True,
                    'unauthorized_software': 'Blocked'
                }
            }
        }

    def _network_pillar(self) -> dict:
        return {
            'principles': [
                'Micro-segmentation',
                'Encryption everywhere',
                'Network visibility',
                'Least privilege network access'
            ],
            'controls': {
                'segmentation': {
                    'software_defined_perimeter': True,
                    'application_segmentation': True,
                    'user_based_segmentation': True
                },
                'encryption': {
                    'tls_everywhere': True,
                    'minimum_version': 'TLS 1.2',
                    'certificate_validation': True
                }
            }
        }

    def _application_pillar(self) -> dict:
        return {
            'principles': [
                'Application discovery and inventory',
                'Secure development practices',
                'API security',
                'Runtime protection'
            ],
            'controls': {
                'access_control': {
                    'oauth2_oidc': True,
                    'api_gateway': True,
                    'rate_limiting': True,
                    'input_validation': True
                },
                'monitoring': {
                    'runtime_protection': True,
                    'behavior_analysis': True,
                    'threat_detection': True
                }
            }
        }

    def _data_pillar(self) -> dict:
        return {
            'principles': [
                'Data classification',
                'Encryption at rest and in transit',
                'Data loss prevention',
                'Access based on data sensitivity'
            ],
            'controls': {
                'protection': {
                    'encryption_at_rest': 'AES-256',
                    'encryption_in_transit': 'TLS 1.2+',
                    'dlp_policies': True,
                    'data_masking': True
                },
                'governance': {
                    'classification_mandatory': True,
                    'access_based_on_classification': True,
                    'data_lifecycle_management': True
                }
            }
        }
```

### Implementation Maturity Model

```yaml
zero_trust_maturity:
  traditional:
    description: "Perimeter-based security"
    characteristics:
      - VPN for remote access
      - Trust internal network
      - Basic authentication
      - Firewall at perimeter

  initial:
    description: "Beginning Zero Trust journey"
    characteristics:
      - MFA for external access
      - Some network segmentation
      - Basic device posture checking
      - Application-level authentication

  advanced:
    description: "Significant Zero Trust adoption"
    characteristics:
      - MFA everywhere
      - Micro-segmentation
      - Device trust verification
      - Risk-based access
      - Encrypted communications

  optimal:
    description: "Full Zero Trust implementation"
    characteristics:
      - Continuous verification
      - Dynamic policy enforcement
      - Automated threat response
      - Comprehensive visibility
      - Data-centric security
```

## 4. CIS Controls v8

### Overview
Prioritized set of actions to protect against common cyber threats.

### Implementation Groups

```python
# CIS Controls v8 Implementation Groups
class CISControlsV8:
    IMPLEMENTATION_GROUPS = {
        'ig1': {
            'description': 'Basic cyber hygiene',
            'organization_size': 'Small',
            'resources': 'Limited',
            'controls': [
                'CIS 1: Inventory of Enterprise Assets',
                'CIS 2: Inventory of Software Assets',
                'CIS 3: Data Protection',
                'CIS 4: Secure Configuration',
                'CIS 5: Account Management',
                'CIS 6: Access Control Management',
                'CIS 7: Continuous Vulnerability Management',
                'CIS 8: Audit Log Management',
                'CIS 9: Email and Web Browser Protections',
                'CIS 10: Malware Defenses',
                'CIS 11: Data Recovery',
                'CIS 12: Network Infrastructure Management',
                'CIS 13: Network Monitoring',
                'CIS 14: Security Awareness Training',
                'CIS 15: Service Provider Management',
                'CIS 16: Application Software Security'
            ]
        },
        'ig2': {
            'description': 'Helps manage IT infrastructure',
            'organization_size': 'Medium',
            'resources': 'Moderate',
            'controls': 'IG1 + additional safeguards for CIS 1-16'
        },
        'ig3': {
            'description': 'Advanced security program',
            'organization_size': 'Large',
            'resources': 'Significant',
            'controls': 'IG1 + IG2 + CIS 17-18 (advanced controls)'
        }
    }

    @staticmethod
    def get_control_details(control_number: int) -> dict:
        """Get details for specific CIS control"""
        controls = {
            1: {
                'title': 'Inventory and Control of Enterprise Assets',
                'description': 'Actively manage all hardware',
                'safeguards': [
                    '1.1: Establish and Maintain Inventory',
                    '1.2: Address Unauthorized Assets',
                    '1.3: Utilize Asset Management Tool',
                    '1.4: Use Dynamic Host Configuration Protocol',
                    '1.5: Use Client Certificates'
                ]
            },
            4: {
                'title': 'Secure Configuration of Enterprise Assets',
                'description': 'Establish and maintain secure configurations',
                'safeguards': [
                    '4.1: Establish and Maintain Secure Configuration Process',
                    '4.2: Establish and Maintain Security Configuration Standard',
                    '4.3: Configure Automatic Session Locking',
                    '4.4: Implement and Manage Network-Based Firewall',
                    '4.5: Implement and Manage Host-Based Firewall',
                    '4.6: Securely Manage Enterprise Assets and Software',
                    '4.7: Manage Default Accounts',
                    '4.8: Uninstall or Disable Unnecessary Services',
                    '4.9: Configure Trusted DNS Servers',
                    '4.10: Enforce Automatic Device Lockout',
                    '4.11: Enforce Remote Wipe Capability',
                    '4.12: Separate Enterprise Workspaces'
                ]
            },
            6: {
                'title': 'Access Control Management',
                'description': 'Use processes and tools to properly manage access',
                'safeguards': [
                    '6.1: Establish Access Granting Process',
                    '6.2: Establish Access Revoking Process',
                    '6.3: Require MFA',
                    '6.4: Require MFA for Remote Network Access',
                    '6.5: Require MFA for Administrative Access',
                    '6.6: Establish and Maintain Privileged Access Management',
                    '6.7: Centralize Account Management',
                    '6.8: Define and Maintain Role-Based Access Control'
                ]
            }
        }
        return controls.get(control_number, {})
```

## 5. ISO/IEC 27001

### Overview
International standard for information security management systems (ISMS).

### Control Categories (Annex A)

```yaml
iso_27001_controls:
  organizational_controls:
    - Information security policies
    - Organization of information security
    - Human resource security
    - Asset management
    - Access control
    - Supplier relationships

  people_controls:
    - Employment terms and conditions
    - Information security awareness
    - Disciplinary process
    - Responsibilities after employment

  physical_controls:
    - Physical security perimeters
    - Physical entry controls
    - Securing offices and facilities
    - Protecting against external threats
    - Working in secure areas
    - Delivery and loading areas

  technological_controls:
    - User endpoint devices
    - Privileged access rights
    - Information access restriction
    - Access to source code
    - Secure authentication
    - Capacity management
    - Protection against malware
    - Managing technical vulnerabilities
    - Information backup
    - Event logging
    - Monitoring activities
    - Clock synchronization
    - Use of privileged utility programs
    - Installation of software
    - Networks security
    - Network segregation
    - Web filtering
    - Use of cryptography
    - Secure development lifecycle
    - Application security requirements
    - Secure system architecture
    - Secure coding
    - Security testing in development
    - Outsourced development
    - Separation of environments
    - Change management
    - Test information
    - Protection during audit
```

### ISMS Implementation

```python
# ISO 27001 ISMS Implementation
class ISO27001ISMS:
    def __init__(self):
        self.pdca_cycle = {
            'plan': self._plan_phase(),
            'do': self._do_phase(),
            'check': self._check_phase(),
            'act': self._act_phase()
        }

    def _plan_phase(self) -> dict:
        """ISMS Planning Phase"""
        return {
            'context_of_organization': [
                'Understand organizational context',
                'Understand stakeholder needs',
                'Determine ISMS scope',
                'Establish ISMS'
            ],
            'leadership': [
                'Leadership and commitment',
                'Information security policy',
                'Roles and responsibilities'
            ],
            'planning': [
                'Risk assessment',
                'Risk treatment',
                'Information security objectives',
                'Planning to achieve objectives'
            ]
        }

    def _do_phase(self) -> dict:
        """ISMS Implementation Phase"""
        return {
            'support': [
                'Resources',
                'Competence',
                'Awareness',
                'Communication',
                'Documented information'
            ],
            'operation': [
                'Operational planning and control',
                'Information security risk assessment',
                'Information security risk treatment'
            ]
        }

    def _check_phase(self) -> dict:
        """ISMS Monitoring Phase"""
        return {
            'performance_evaluation': [
                'Monitoring and measurement',
                'Internal audit',
                'Management review'
            ]
        }

    def _act_phase(self) -> dict:
        """ISMS Improvement Phase"""
        return {
            'improvement': [
                'Nonconformity and corrective action',
                'Continual improvement'
            ]
        }
```

## Framework Selection Guide

### Decision Matrix

```python
# Framework selection decision matrix
def select_framework(organization_profile: dict) -> list:
    """
    Recommend security frameworks based on organization profile

    Args:
        organization_profile: {
            'industry': str,
            'size': str,  # 'small', 'medium', 'large'
            'maturity': str,  # 'low', 'medium', 'high'
            'compliance_requirements': list,
            'cloud_adoption': str  # 'none', 'partial', 'full'
        }

    Returns:
        List of recommended frameworks
    """
    recommendations = []

    # Industry-specific
    if organization_profile['industry'] in ['healthcare', 'finance']:
        recommendations.append('ISO 27001')
        recommendations.append('NIST CSF')

    # Size-based
    if organization_profile['size'] == 'small':
        recommendations.append('CIS Controls IG1')
    elif organization_profile['size'] == 'medium':
        recommendations.append('CIS Controls IG2')
        recommendations.append('NIST CSF')
    else:
        recommendations.append('SABSA')
        recommendations.append('TOGAF')
        recommendations.append('ISO 27001')

    # Cloud-based
    if organization_profile['cloud_adoption'] in ['partial', 'full']:
        recommendations.append('Zero Trust')
        recommendations.append('NIST CSF')

    # Compliance-driven
    if 'PCI-DSS' in organization_profile['compliance_requirements']:
        recommendations.append('CIS Controls')
    if 'HIPAA' in organization_profile['compliance_requirements']:
        recommendations.append('NIST CSF')
        recommendations.append('ISO 27001')

    return list(set(recommendations))  # Remove duplicates
```

## References

- NIST Cybersecurity Framework v1.1
- SABSA Institute
- ISO/IEC 27001:2022
- CIS Controls v8
- NIST SP 800-207: Zero Trust Architecture
- TOGAF 9.2 Security Architecture

---

**Last Updated:** 2025-01-19
**Version:** 1.0
