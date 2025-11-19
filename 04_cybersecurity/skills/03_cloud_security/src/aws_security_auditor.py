"""
AWS Security Auditor
Automated security assessment for AWS resources
"""

from typing import Dict, List
from dataclasses import dataclass
from datetime import datetime


@dataclass
class SecurityFinding:
    """Security finding from audit"""
    severity: str  # Critical, High, Medium, Low
    resource_type: str
    resource_id: str
    finding: str
    remediation: str


class AWSSecurityAuditor:
    """
    AWS Security Auditor

    Features:
    - S3 bucket security assessment
    - IAM policy review
    - Security group audit
    - Encryption verification
    - Compliance checking
    """

    def __init__(self):
        self.findings: List[SecurityFinding] = []

    def audit_s3_bucket(self, bucket_config: Dict) -> List[SecurityFinding]:
        """Audit S3 bucket configuration"""
        findings = []

        # Check public access
        if bucket_config.get('public_access_block_enabled') == False:
            findings.append(SecurityFinding(
                severity="Critical",
                resource_type="S3 Bucket",
                resource_id=bucket_config['name'],
                finding="Public access not blocked",
                remediation="Enable Block Public Access settings"
            ))

        # Check encryption
        if not bucket_config.get('encryption_enabled'):
            findings.append(SecurityFinding(
                severity="High",
                resource_type="S3 Bucket",
                resource_id=bucket_config['name'],
                finding="Server-side encryption not enabled",
                remediation="Enable default encryption (AES-256 or KMS)"
            ))

        # Check versioning
        if not bucket_config.get('versioning_enabled'):
            findings.append(SecurityFinding(
                severity="Medium",
                resource_type="S3 Bucket",
                resource_id=bucket_config['name'],
                finding="Versioning not enabled",
                remediation="Enable versioning for data protection"
            ))

        # Check logging
        if not bucket_config.get('logging_enabled'):
            findings.append(SecurityFinding(
                severity="Medium",
                resource_type="S3 Bucket",
                resource_id=bucket_config['name'],
                finding="Access logging not enabled",
                remediation="Enable server access logging"
            ))

        return findings

    def audit_security_group(self, sg_config: Dict) -> List[SecurityFinding]:
        """Audit security group rules"""
        findings = []

        for rule in sg_config.get('ingress_rules', []):
            # Check for unrestricted access
            if rule.get('cidr') == '0.0.0.0/0':
                if rule.get('port') in [22, 3389]:  # SSH, RDP
                    findings.append(SecurityFinding(
                        severity="Critical",
                        resource_type="Security Group",
                        resource_id=sg_config['id'],
                        finding=f"Port {rule['port']} open to 0.0.0.0/0",
                        remediation="Restrict access to specific IP ranges"
                    ))
                elif rule.get('port_range') == 'all':
                    findings.append(SecurityFinding(
                        severity="Critical",
                        resource_type="Security Group",
                        resource_id=sg_config['id'],
                        finding="All ports open to 0.0.0.0/0",
                        remediation="Restrict to required ports only"
                    ))

        return findings

    def audit_iam_policy(self, policy: Dict) -> List[SecurityFinding]:
        """Audit IAM policy for security issues"""
        findings = []

        for statement in policy.get('Statement', []):
            # Check for overly permissive policies
            if statement.get('Effect') == 'Allow':
                if statement.get('Action') == '*' and statement.get('Resource') == '*':
                    findings.append(SecurityFinding(
                        severity="Critical",
                        resource_type="IAM Policy",
                        resource_id=policy.get('PolicyName', 'Unknown'),
                        finding="Policy grants full access (Action: *, Resource: *)",
                        remediation="Implement least privilege - restrict actions and resources"
                    ))

                # Check for dangerous actions
                dangerous_actions = ['iam:*', 'sts:AssumeRole', 'ec2:*', 's3:*']
                actions = statement.get('Action', [])
                if isinstance(actions, str):
                    actions = [actions]

                for action in actions:
                    if any(dangerous in action for dangerous in dangerous_actions):
                        findings.append(SecurityFinding(
                            severity="High",
                            resource_type="IAM Policy",
                            resource_id=policy.get('PolicyName', 'Unknown'),
                            finding=f"Potentially dangerous action: {action}",
                            remediation="Review and scope down permissions"
                        ))

        return findings

    def audit_ec2_instance(self, instance_config: Dict) -> List[SecurityFinding]:
        """Audit EC2 instance configuration"""
        findings = []

        # Check encryption
        if not instance_config.get('ebs_encrypted'):
            findings.append(SecurityFinding(
                severity="High",
                resource_type="EC2 Instance",
                resource_id=instance_config['instance_id'],
                finding="EBS volumes not encrypted",
                remediation="Enable EBS encryption for all volumes"
            ))

        # Check IMDSv2
        if instance_config.get('metadata_options', {}).get('http_tokens') != 'required':
            findings.append(SecurityFinding(
                severity="Medium",
                resource_type="EC2 Instance",
                resource_id=instance_config['instance_id'],
                finding="IMDSv2 not enforced",
                remediation="Require IMDSv2 for instance metadata"
            ))

        # Check monitoring
        if not instance_config.get('monitoring_enabled'):
            findings.append(SecurityFinding(
                severity="Low",
                resource_type="EC2 Instance",
                resource_id=instance_config['instance_id'],
                finding="Detailed monitoring not enabled",
                remediation="Enable detailed monitoring"
            ))

        return findings

    def generate_report(self) -> Dict:
        """Generate comprehensive audit report"""
        severity_counts = {'Critical': 0, 'High': 0, 'Medium': 0, 'Low': 0}

        for finding in self.findings:
            severity_counts[finding.severity] += 1

        return {
            'audit_date': datetime.now().isoformat(),
            'total_findings': len(self.findings),
            'by_severity': severity_counts,
            'findings': [
                {
                    'severity': f.severity,
                    'resource_type': f.resource_type,
                    'resource_id': f.resource_id,
                    'finding': f.finding,
                    'remediation': f.remediation
                }
                for f in self.findings
            ]
        }


if __name__ == "__main__":
    auditor = AWSSecurityAuditor()

    # Example S3 audit
    s3_config = {
        'name': 'my-bucket',
        'public_access_block_enabled': False,
        'encryption_enabled': False,
        'versioning_enabled': True,
        'logging_enabled': False
    }

    findings = auditor.audit_s3_bucket(s3_config)
    auditor.findings.extend(findings)

    # Generate report
    report = auditor.generate_report()
    print(f"Total findings: {report['total_findings']}")
    print(f"Critical: {report['by_severity']['Critical']}")
