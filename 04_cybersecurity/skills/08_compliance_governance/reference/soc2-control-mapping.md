# SOC 2 Control Mapping

## Trust Service Criteria Common Criteria (CC)

### CC1: Control Environment
| Control ID | Description | Implementation | Evidence |
|------------|-------------|----------------|----------|
| CC1.1 | COSO principles adopted | Board oversight of security | Board meeting minutes |
| CC1.2 | Board oversight | Quarterly security reviews | Review documentation |
| CC1.3 | Organizational structure | Clear roles and responsibilities | Org chart, job descriptions |
| CC1.4 | Competence | Security training program | Training records |
| CC1.5 | Accountability | Performance reviews include security | HR records |

### CC2: Communication & Information
| CC2.1 | Quality information | Security metrics dashboard | Dashboard screenshots |
| CC2.2 | Internal communication | Security awareness program | Training materials, emails |
| CC2.3 | External communication | Incident notification process | Incident response plan |

### CC3: Risk Assessment
| CC3.1 | Risk identification | Annual risk assessment | Risk register |
| CC3.2 | Risk analysis | Risk scoring methodology | Risk analysis document |
| CC3.3 | Fraud risk | Fraud risk assessment | Assessment documentation |
| CC3.4 | Change management | Change control process | Change tickets, approvals |

### CC4: Monitoring
| CC4.1 | Ongoing monitoring | SIEM, security dashboard | Alert logs, dashboards |
| CC4.2 | Deficiency reporting | Vulnerability management | Scan reports, remediation tracking |

### CC5: Control Activities
| CC5.1 | Control selection | Controls mapped to risks | Control matrix |
| CC5.2 | Technology controls | Firewalls, IDS, encryption | Configuration evidence |
| CC5.3 | Outsourcing | Vendor security assessments | SOC 2 reports from vendors |

### CC6: Logical & Physical Access
| CC6.1 | Access provisioning | Identity management process | Access request tickets |
| CC6.2 | User authentication | MFA enforced | MFA enrollment reports |
| CC6.3 | Network segmentation | Firewall rules, VLANs | Network diagrams, firewall configs |
| CC6.4 | Physical access | Badge access, visitor logs | Access logs, visitor sign-in |
| CC6.5 | Endpoint protection | EDR deployed | EDR deployment report |
| CC6.6 | Vulnerability management | Regular scanning, patching | Scan results, patch reports |
| CC6.7 | Data encryption | TLS, disk encryption | SSL certificate, BitLocker status |
| CC6.8 | Customer data access | Least privilege access | Access reviews |

### CC7: System Operations
| CC7.1 | Threat detection | IDS/IPS, SIEM alerts | Alert configurations |
| CC7.2 | Security monitoring | 24/7 SOC or alerts | Monitoring dashboards |
| CC7.3 | Capacity management | Resource monitoring | Capacity reports |
| CC7.4 | Backup & recovery | Automated backups, tested restores | Backup logs, restore tests |
| CC7.5 | Incident response | IR plan, drills | IR plan, drill documentation |

### CC8: Change Management
| CC8.1 | Change authorization | Change approval process | Change tickets |
| CC8.2 | System changes | Testing before production | Test results, approvals |

### CC9: Risk Mitigation
| CC9.1 | Environmental risks | Disaster recovery plan | DR plan, tests |
| CC9.2 | Vendor management | Vendor risk assessments | Vendor reviews, SOC 2 reports |

## Automated Evidence Collection

```python
# SOC 2 evidence automation
evidence_mapping = {
    "CC6.1": {
        "control": "Access provisioning and deprovisioning",
        "evidence": [
            "access_requests_last_12_months.csv",
            "terminated_employees_access_removal.csv",
            "access_review_quarterly.pdf"
        ],
        "automation": "query_jira_access_requests()"
    },
    "CC6.2": {
        "control": "Multi-factor authentication",
        "evidence": [
            "mfa_enrollment_report.pdf",
            "mfa_enforcement_policy.pdf"
        ],
        "automation": "get_mfa_enrollment_stats()"
    },
    "CC6.6": {
        "control": "Vulnerability management",
        "evidence": [
            "vulnerability_scan_results.pdf",
            "remediation_tracking.csv",
            "patching_compliance_report.pdf"
        ],
        "automation": "export_vulnerability_reports()"
    },
    "CC7.2": {
        "control": "Security incident monitoring",
        "evidence": [
            "siem_alerts_summary.pdf",
            "incident_log.csv",
            "escalation_procedures.pdf"
        ],
        "automation": "export_siem_reports()"
    },
    "CC7.5": {
        "control": "Incident response",
        "evidence": [
            "incident_response_plan.pdf",
            "ir_drill_results.pdf",
            "actual_incidents_handled.csv"
        ],
        "automation": "export_incident_reports()"
    }
}
```

## Audit Readiness Checklist

### Pre-Audit (3 months before)
- [ ] Review all control descriptions
- [ ] Identify gaps in evidence
- [ ] Test controls
- [ ] Update policies and procedures
- [ ] Train staff on audit process

### Evidence Collection (2 months before)
- [ ] Collect screenshots of systems
- [ ] Export logs and reports
- [ ] Document exceptions
- [ ] Prepare narratives
- [ ] Organize evidence by control

### Audit Fieldwork (1 month)
- [ ] Provide evidence to auditors
- [ ] Answer inquiries promptly
- [ ] Provide system access as needed
- [ ] Track open items
- [ ] Review draft findings

### Post-Audit
- [ ] Address management points
- [ ] Remediate deficiencies
- [ ] Update control documentation
- [ ] Plan for next audit cycle
