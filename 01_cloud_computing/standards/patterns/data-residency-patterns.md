# Data Residency and Compliance Architecture Patterns

## Overview

Data residency patterns ensure compliance with data sovereignty laws, privacy regulations (GDPR, CCPA, HIPAA), and corporate policies that govern where data can be stored and processed. This guide covers architectural patterns for managing data across geographic boundaries while maintaining compliance.

## Table of Contents

1. [Regional Isolation Pattern](#regional-isolation-pattern)
2. [Data Sovereignty Pattern](#data-sovereignty-pattern)
3. [Cross-Border Data Transfer Pattern](#cross-border-data-transfer-pattern)
4. [Encryption Boundary Pattern](#encryption-boundary-pattern)
5. [Data Classification Pattern](#data-classification-pattern)
6. [Geo-Fencing Pattern](#geo-fencing-pattern)
7. [Compliant Backup Pattern](#compliant-backup-pattern)

## Key Regulations

```
┌─────────────────────────────────────────────────────┐
│  Major Data Protection Regulations                  │
├─────────────────────────────────────────────────────┤
│                                                     │
│  GDPR (Europe)                                      │
│  └─ Data must stay in EU/EEA or adequate countries │
│  └─ Right to erasure, portability                  │
│  └─ DPIAs for high-risk processing                 │
│                                                     │
│  CCPA/CPRA (California)                            │
│  └─ Consumer data rights                           │
│  └─ Opt-out of data sales                         │
│                                                     │
│  LGPD (Brazil)                                      │
│  └─ Similar to GDPR                                │
│                                                     │
│  PDPA (Singapore)                                   │
│  └─ Consent and notification requirements          │
│                                                     │
│  HIPAA (US Healthcare)                             │
│  └─ PHI protection requirements                    │
│                                                     │
│  PCI DSS (Payment Card)                            │
│  └─ Cardholder data protection                    │
│                                                     │
│  China Cybersecurity Law                           │
│  └─ Data localization requirements                │
│                                                     │
└─────────────────────────────────────────────────────┘
```

---

## 1. Regional Isolation Pattern

### Description

Completely isolate data and processing within specific geographic regions to ensure compliance with local data sovereignty laws.

### When to Use

- Strict data sovereignty requirements (China, Russia)
- GDPR compliance for EU data
- Regulatory requirements mandate local storage
- Multi-tenant SaaS with region-specific customers
- Financial services with jurisdictional requirements

### Architecture Diagram

```
┌─────────────────────────────────────────────────────┐
│              Global Layer (Metadata Only)            │
│  ┌────────────┐  ┌────────────┐  ┌────────────┐   │
│  │   User     │  │  Billing   │  │  Routing   │   │
│  │ Directory  │  │   System   │  │  Service   │   │
│  └────────────┘  └────────────┘  └────────────┘   │
└─────────────────────────────────────────────────────┘
                         │
         ┌───────────────┼───────────────┐
         │               │               │
┌────────▼────────┐ ┌───▼────────┐ ┌───▼────────┐
│   EU Region     │ │ US Region  │ │APAC Region │
│   (Isolated)    │ │ (Isolated) │ │ (Isolated) │
├─────────────────┤ ├────────────┤ ├────────────┤
│ ┌─────────────┐ │ │┌──────────┐│ │┌──────────┐│
│ │EU Customers │ │ ││US Cust.  ││ ││APAC Cust.││
│ │    Data     │ │ ││   Data   ││ ││   Data   ││
│ └─────────────┘ │ │└──────────┘│ │└──────────┘│
│ ┌─────────────┐ │ │┌──────────┐│ │┌──────────┐│
│ │EU Database  │ │ ││US DB     ││ ││APAC DB   ││
│ │(Frankfurt)  │ │ ││(Virginia)││ ││(Tokyo)   ││
│ └─────────────┘ │ │└──────────┘│ │└──────────┘│
│ ┌─────────────┐ │ │┌──────────┐│ │┌──────────┐│
│ │EU Storage   │ │ ││US Storage││ ││APAC Store││
│ │(S3 EU-WEST) │ │ ││(S3 EAST) ││ ││(S3 TOKYO)││
│ └─────────────┘ │ │└──────────┘│ │└──────────┘│
└─────────────────┘ └────────────┘ └────────────┘

       NO CROSS-REGION DATA TRANSFER
```

### Implementation Example

```python
# regional_data_manager.py
from enum import Enum
from typing import Dict, Optional
import boto3
from dataclasses import dataclass

class DataRegion(Enum):
    EU = "eu-west-1"
    US = "us-east-1"
    APAC = "ap-northeast-1"
    CHINA = "cn-north-1"

class DataClassification(Enum):
    PUBLIC = "public"
    INTERNAL = "internal"
    CONFIDENTIAL = "confidential"
    RESTRICTED = "restricted"

@dataclass
class RegionalCompliance:
    region: DataRegion
    regulations: list[str]
    allowed_transfers: list[DataRegion]
    encryption_required: bool
    retention_days: int

class RegionalDataManager:
    def __init__(self):
        self.compliance_rules = {
            DataRegion.EU: RegionalCompliance(
                region=DataRegion.EU,
                regulations=["GDPR", "ePrivacy"],
                allowed_transfers=[],  # No transfers allowed without consent
                encryption_required=True,
                retention_days=90
            ),
            DataRegion.US: RegionalCompliance(
                region=DataRegion.US,
                regulations=["CCPA", "HIPAA"],
                allowed_transfers=[],  # Restricted transfers
                encryption_required=True,
                retention_days=365
            ),
            DataRegion.APAC: RegionalCompliance(
                region=DataRegion.APAC,
                regulations=["PDPA", "APPI"],
                allowed_transfers=[],
                encryption_required=True,
                retention_days=180
            ),
            DataRegion.CHINA: RegionalCompliance(
                region=DataRegion.CHINA,
                regulations=["Cybersecurity Law"],
                allowed_transfers=[],  # Strictly prohibited
                encryption_required=True,
                retention_days=730
            )
        }

        # Initialize regional clients
        self.regional_clients = {
            region: boto3.client('s3', region_name=region.value)
            for region in DataRegion
        }

    def determine_data_region(self, user_location: str,
                              data_type: str) -> DataRegion:
        """Determine appropriate region based on user location"""
        location_mapping = {
            'DE': DataRegion.EU, 'FR': DataRegion.EU, 'IT': DataRegion.EU,
            'UK': DataRegion.EU, 'ES': DataRegion.EU, 'NL': DataRegion.EU,
            'US': DataRegion.US, 'CA': DataRegion.US, 'MX': DataRegion.US,
            'JP': DataRegion.APAC, 'SG': DataRegion.APAC, 'AU': DataRegion.APAC,
            'CN': DataRegion.CHINA
        }

        return location_mapping.get(user_location, DataRegion.US)

    def validate_data_storage(self, region: DataRegion,
                             data_classification: DataClassification,
                             metadata: Dict) -> bool:
        """Validate if data can be stored in region"""
        compliance = self.compliance_rules[region]

        # Check encryption requirements
        if compliance.encryption_required and not metadata.get('encrypted'):
            raise ValueError(f"Encryption required for {region}")

        # Check data classification
        if data_classification == DataClassification.RESTRICTED:
            if region not in [DataRegion.EU, DataRegion.US]:
                raise ValueError("Restricted data only in EU/US")

        return True

    def store_data_regionally(self, user_id: str,
                             user_region: DataRegion,
                             data: bytes,
                             metadata: Dict) -> str:
        """Store data in appropriate regional bucket"""
        # Validate storage compliance
        classification = DataClassification[metadata.get('classification', 'INTERNAL')]
        self.validate_data_storage(user_region, classification, metadata)

        # Get regional S3 client
        s3_client = self.regional_clients[user_region]
        bucket_name = f"user-data-{user_region.value}"

        # Add compliance metadata
        compliance_metadata = {
            **metadata,
            'region': user_region.value,
            'regulations': ','.join(self.compliance_rules[user_region].regulations),
            'encrypted': 'true',
            'retention_days': str(self.compliance_rules[user_region].retention_days)
        }

        # Store with encryption
        key = f"users/{user_id}/data/{metadata['filename']}"
        s3_client.put_object(
            Bucket=bucket_name,
            Key=key,
            Body=data,
            ServerSideEncryption='aws:kms',
            Metadata=compliance_metadata,
            StorageClass='STANDARD_IA'
        )

        return f"s3://{bucket_name}/{key}"

    def check_transfer_allowed(self, source_region: DataRegion,
                              dest_region: DataRegion,
                              consent: bool = False) -> bool:
        """Check if cross-region transfer is allowed"""
        source_compliance = self.compliance_rules[source_region]

        # China and restricted regions never allow transfers
        if source_region == DataRegion.CHINA:
            return False

        # EU requires explicit consent for transfers
        if source_region == DataRegion.EU and not consent:
            return False

        # Check if destination in allowed list
        return dest_region in source_compliance.allowed_transfers or consent

    def enforce_data_deletion(self, user_id: str,
                            region: DataRegion) -> Dict:
        """GDPR Right to Erasure - Delete all user data"""
        s3_client = self.regional_clients[region]
        bucket_name = f"user-data-{region.value}"
        prefix = f"users/{user_id}/"

        deleted_objects = []

        # List all objects for user
        paginator = s3_client.get_paginator('list_objects_v2')
        pages = paginator.paginate(Bucket=bucket_name, Prefix=prefix)

        for page in pages:
            if 'Contents' not in page:
                continue

            for obj in page['Contents']:
                # Delete object
                s3_client.delete_object(
                    Bucket=bucket_name,
                    Key=obj['Key']
                )
                deleted_objects.append(obj['Key'])

        # Log deletion for compliance
        self._log_deletion_event(user_id, region, deleted_objects)

        return {
            'user_id': user_id,
            'region': region.value,
            'deleted_count': len(deleted_objects),
            'status': 'completed'
        }

    def _log_deletion_event(self, user_id: str,
                           region: DataRegion,
                           objects: list):
        """Log deletion for audit trail"""
        # Implementation for compliance logging
        pass


# API endpoint for regional data storage
from flask import Flask, request, jsonify

app = Flask(__name__)
data_manager = RegionalDataManager()

@app.route('/api/store-data', methods=['POST'])
def store_data():
    """Store data with regional compliance"""
    user_id = request.json['user_id']
    user_country = request.json['country']
    data = request.files['file'].read()
    metadata = request.json.get('metadata', {})

    # Determine region
    region = data_manager.determine_data_region(user_country, 'user_data')

    # Store regionally
    location = data_manager.store_data_regionally(
        user_id=user_id,
        user_region=region,
        data=data,
        metadata=metadata
    )

    return jsonify({
        'status': 'success',
        'location': location,
        'region': region.value,
        'regulations': data_manager.compliance_rules[region].regulations
    })

@app.route('/api/delete-user-data', methods=['DELETE'])
def delete_user_data():
    """GDPR Right to Erasure"""
    user_id = request.json['user_id']
    region = DataRegion[request.json['region']]

    result = data_manager.enforce_data_deletion(user_id, region)

    return jsonify(result)
```

### Terraform Configuration

```hcl
# Regional isolation with strict boundaries

# EU Region - GDPR Compliant
module "eu_region" {
  source = "./modules/regional-stack"
  providers = {
    aws = aws.eu-west-1
  }

  region_name         = "eu"
  compliance_tags = {
    Regulation      = "GDPR"
    DataResidency   = "EU"
    EncryptionReq   = "true"
    RetentionDays   = "90"
  }

  # Prevent cross-region replication
  enable_replication = false

  # Enforce encryption
  enforce_encryption_in_transit  = true
  enforce_encryption_at_rest     = true

  # Block public access
  block_public_access = true
}

# S3 Bucket with regional lock
resource "aws_s3_bucket" "eu_data" {
  provider = aws.eu-west-1
  bucket   = "user-data-eu-west-1"

  tags = {
    Region      = "EU"
    Compliance  = "GDPR"
    NoTransfer  = "true"
  }
}

# Bucket policy preventing cross-region access
resource "aws_s3_bucket_policy" "eu_regional_lock" {
  provider = aws.eu-west-1
  bucket   = aws_s3_bucket.eu_data.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid    = "DenyNonEURegionAccess"
        Effect = "Deny"
        Principal = "*"
        Action = "s3:*"
        Resource = [
          "${aws_s3_bucket.eu_data.arn}/*",
          aws_s3_bucket.eu_data.arn
        ]
        Condition = {
          StringNotEquals = {
            "aws:RequestedRegion" = ["eu-west-1", "eu-central-1"]
          }
        }
      },
      {
        Sid    = "DenyCrossRegionReplication"
        Effect = "Deny"
        Principal = "*"
        Action = "s3:ReplicateObject"
        Resource = "${aws_s3_bucket.eu_data.arn}/*"
      }
    ]
  })
}

# Enable encryption by default
resource "aws_s3_bucket_server_side_encryption_configuration" "eu_encryption" {
  provider = aws.eu-west-1
  bucket   = aws_s3_bucket.eu_data.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm     = "aws:kms"
      kms_master_key_id = aws_kms_key.eu_data_key.id
    }
    bucket_key_enabled = true
  }
}

# Regional KMS key (cannot be used outside region)
resource "aws_kms_key" "eu_data_key" {
  provider                = aws.eu-west-1
  description             = "EU region data encryption key"
  deletion_window_in_days = 30
  enable_key_rotation     = true
  multi_region            = false  # Prevent cross-region use

  tags = {
    Region     = "EU"
    Compliance = "GDPR"
  }
}

# Database with regional isolation
resource "aws_db_instance" "eu_database" {
  provider = aws.eu-west-1

  identifier     = "eu-user-data"
  engine         = "postgres"
  engine_version = "14.7"
  instance_class = "db.t3.medium"

  # Prevent read replicas in other regions
  backup_retention_period = 7
  skip_final_snapshot     = false

  # Encryption
  storage_encrypted = true
  kms_key_id        = aws_kms_key.eu_data_key.arn

  # Network isolation
  db_subnet_group_name   = aws_db_subnet_group.eu_private.name
  vpc_security_group_ids = [aws_security_group.eu_db.id]

  tags = {
    Region     = "EU"
    Compliance = "GDPR"
    Isolation  = "true"
  }
}

# CloudWatch Logs with retention policy
resource "aws_cloudwatch_log_group" "eu_application" {
  provider          = aws.eu-west-1
  name              = "/aws/application/eu"
  retention_in_days = 90  # GDPR retention

  kms_key_id = aws_kms_key.eu_data_key.arn

  tags = {
    Region     = "EU"
    Compliance = "GDPR"
  }
}

# Config rule to enforce regional isolation
resource "aws_config_config_rule" "regional_isolation" {
  provider = aws.eu-west-1
  name     = "ensure-regional-data-isolation"

  source {
    owner             = "AWS"
    source_identifier = "S3_BUCKET_REPLICATION_ENABLED"
  }

  # Ensure replication is NOT enabled
  scope {
    compliance_resource_types = ["AWS::S3::Bucket"]
  }
}
```

### Trade-offs

**Pros:**
- Complete compliance with data sovereignty laws
- Clear regulatory boundaries
- Simplified compliance auditing
- No cross-border data transfer risks

**Cons:**
- Duplicated infrastructure costs
- Complex global user management
- Difficult to implement global features
- Potential performance issues for traveling users

### Anti-patterns

- **Accidental Cross-Region Replication**: Enabling replication violates isolation
- **Shared Encryption Keys**: Using multi-region KMS keys
- **Centralized Logging**: Aggregating logs from all regions to one location
- **Global CDN Without Controls**: Serving sensitive data via global CDN

### Real-world Examples

**Microsoft**: Azure has dedicated Germany and China clouds for data sovereignty.

**Salesforce**: Maintains completely separate instances (Hyperforce) for GDPR compliance.

**SAP**: Runs isolated regional datacenters with no cross-border transfers for regulated industries.

---

## 2. Data Sovereignty Pattern

### Description

Ensure data remains under the jurisdiction and laws of a specific country or region, with controls preventing unauthorized transfers.

### When to Use

- Operating in countries with strict localization laws (China, Russia, India)
- Handling government or military data
- Financial services with regulatory requirements
- Healthcare data under local privacy laws

### Architecture Diagram

```
┌──────────────────────────────────────────┐
│      Data Sovereignty Framework          │
└──────────────────────────────────────────┘
                    │
    ┌───────────────┼───────────────┐
    │               │               │
┌───▼───┐      ┌───▼───┐      ┌───▼───┐
│ Data  │      │Access │      │Export │
│Location│     │Control│      │Control│
└───┬───┘      └───┬───┘      └───┬───┘
    │              │              │
    ▼              ▼              ▼
┌─────────────────────────────────────┐
│  Sovereignty Controls               │
├─────────────────────────────────────┤
│ ✓ Geographic boundaries enforced   │
│ ✓ Local encryption keys only       │
│ ✓ No foreign admin access          │
│ ✓ Audit logs in-country            │
│ ✓ Data lineage tracking            │
│ ✓ Transfer approval workflow       │
└─────────────────────────────────────┘
```

### Implementation Example

```python
# data_sovereignty_controller.py
from typing import Optional, List
import boto3
from enum import Enum

class Jurisdiction(Enum):
    EU = "european_union"
    US = "united_states"
    CHINA = "china"
    RUSSIA = "russia"
    INDIA = "india"
    BRAZIL = "brazil"

class SovereigntyController:
    def __init__(self):
        self.sovereignty_rules = {
            Jurisdiction.CHINA: {
                'allowed_regions': ['cn-north-1', 'cn-northwest-1'],
                'allowed_export': [],
                'requires_local_admin': True,
                'requires_local_keys': True,
                'audit_retention_years': 3,
                'regulations': ['Cybersecurity Law', 'PIPL']
            },
            Jurisdiction.RUSSIA: {
                'allowed_regions': ['ru-central-1'],
                'allowed_export': [],
                'requires_local_admin': True,
                'requires_local_keys': True,
                'audit_retention_years': 5,
                'regulations': ['Federal Law 152-FZ']
            },
            Jurisdiction.EU: {
                'allowed_regions': ['eu-west-1', 'eu-central-1'],
                'allowed_export': ['adequacy_decision_countries'],
                'requires_local_admin': False,
                'requires_local_keys': True,
                'audit_retention_years': 7,
                'regulations': ['GDPR']
            },
            Jurisdiction.INDIA: {
                'allowed_regions': ['ap-south-1'],
                'allowed_export': [],
                'requires_local_admin': True,
                'requires_local_keys': True,
                'audit_retention_years': 5,
                'regulations': ['Personal Data Protection Bill']
            }
        }

    def validate_data_location(self, jurisdiction: Jurisdiction,
                               current_region: str) -> bool:
        """Validate data is in correct jurisdiction"""
        rules = self.sovereignty_rules[jurisdiction]
        return current_region in rules['allowed_regions']

    def check_export_permission(self, source_jurisdiction: Jurisdiction,
                               dest_jurisdiction: Jurisdiction,
                               data_type: str,
                               approval_token: Optional[str] = None) -> bool:
        """Check if cross-border transfer is allowed"""
        source_rules = self.sovereignty_rules[source_jurisdiction]

        # Check if destination is in allowed list
        if dest_jurisdiction.value not in source_rules['allowed_export']:
            if not approval_token:
                return False

            # Verify approval token
            return self._validate_export_approval(
                source_jurisdiction,
                dest_jurisdiction,
                approval_token
            )

        return True

    def _validate_export_approval(self, source: Jurisdiction,
                                  dest: Jurisdiction,
                                  token: str) -> bool:
        """Validate regulatory approval for data export"""
        # Implementation would check against approval database
        # This is a simplified example
        return False  # Deny by default

    def enforce_local_access_control(self, jurisdiction: Jurisdiction,
                                    admin_location: str) -> bool:
        """Ensure admins are in same jurisdiction"""
        rules = self.sovereignty_rules[jurisdiction]

        if rules['requires_local_admin']:
            return admin_location in rules['allowed_regions']

        return True

    def create_compliance_report(self, jurisdiction: Jurisdiction) -> dict:
        """Generate compliance report for auditors"""
        rules = self.sovereignty_rules[jurisdiction]

        return {
            'jurisdiction': jurisdiction.value,
            'regulations': rules['regulations'],
            'data_locations': rules['allowed_regions'],
            'export_restrictions': rules['allowed_export'],
            'local_admin_required': rules['requires_local_admin'],
            'local_encryption_required': rules['requires_local_keys'],
            'audit_retention': f"{rules['audit_retention_years']} years"
        }
```

### Real-world Examples

**ByteDance/TikTok**: Separate data storage for Chinese vs. international users.

**Apple**: iCloud data for Chinese users stored in China with local partners.

**AWS**: Separate China regions operated by local partners (Sinnet, NWCD).

---

## 3. Cross-Border Data Transfer Pattern

### Description

Implement controlled mechanisms for transferring data across borders while maintaining compliance with data protection regulations.

### Standard Contractual Clauses (SCCs)

```
┌────────────────────────────────────────┐
│   Cross-Border Transfer Mechanisms     │
├────────────────────────────────────────┤
│                                        │
│  1. Standard Contractual Clauses (EU) │
│     └─ Legal framework for transfers  │
│                                        │
│  2. Binding Corporate Rules (BCRs)    │
│     └─ Internal data transfer rules   │
│                                        │
│  3. Adequacy Decisions                │
│     └─ EU-approved countries          │
│                                        │
│  4. Privacy Shield (Invalidated)      │
│     └─ Replaced by EU-US Data        │
│        Privacy Framework              │
│                                        │
│  5. Consent-Based Transfers           │
│     └─ Explicit user consent          │
│                                        │
└────────────────────────────────────────┘
```

### Implementation Example

```python
# cross_border_transfer.py
from dataclasses import dataclass
from datetime import datetime
from enum import Enum

class TransferMechanism(Enum):
    SCC = "standard_contractual_clauses"
    BCR = "binding_corporate_rules"
    CONSENT = "user_consent"
    ADEQUACY = "adequacy_decision"
    DEROGATION = "derogation"

@dataclass
class TransferRequest:
    data_id: str
    source_country: str
    dest_country: str
    data_category: str
    purpose: str
    mechanism: TransferMechanism
    consent_id: Optional[str]
    approved: bool = False
    approved_by: Optional[str] = None
    approved_at: Optional[datetime] = None

class CrossBorderTransferManager:
    def __init__(self):
        # Countries with EU adequacy decision
        self.adequacy_countries = [
            'CH', 'UK', 'IL', 'NZ', 'CA', 'JP', 'KR'  # Simplified list
        ]

    def assess_transfer(self, request: TransferRequest) -> dict:
        """Assess if cross-border transfer is allowed"""

        # Check if adequacy decision exists
        if request.dest_country in self.adequacy_countries:
            return {
                'allowed': True,
                'mechanism': TransferMechanism.ADEQUACY,
                'requires_approval': False
            }

        # Check for valid SCCs
        if request.mechanism == TransferMechanism.SCC:
            return {
                'allowed': True,
                'mechanism': TransferMechanism.SCC,
                'requires_approval': True,
                'requires_dpia': True  # Data Protection Impact Assessment
            }

        # Check for explicit consent
        if request.mechanism == TransferMechanism.CONSENT:
            if not request.consent_id:
                return {'allowed': False, 'reason': 'No consent provided'}

            consent_valid = self._validate_consent(request.consent_id)
            return {
                'allowed': consent_valid,
                'mechanism': TransferMechanism.CONSENT,
                'requires_approval': False
            }

        # Check BCRs
        if request.mechanism == TransferMechanism.BCR:
            return {
                'allowed': True,
                'mechanism': TransferMechanism.BCR,
                'requires_approval': True
            }

        return {'allowed': False, 'reason': 'No valid transfer mechanism'}

    def _validate_consent(self, consent_id: str) -> bool:
        """Validate user consent for transfer"""
        # Implementation would check consent database
        return True

    def log_transfer(self, request: TransferRequest):
        """Log transfer for audit trail"""
        # Required for GDPR Article 30
        pass
```

---

## 4. Encryption Boundary Pattern

### Description

Use encryption to create jurisdictional boundaries, ensuring data can only be accessed within authorized regions through regional encryption keys.

### Architecture Diagram

```
┌──────────────────────────────────────────┐
│         Regional KMS Keys                │
├──────────────────────────────────────────┤
│                                          │
│  EU Key         US Key       APAC Key   │
│  (eu-west-1)    (us-east-1)  (tokyo)    │
│      │              │            │       │
│      ▼              ▼            ▼       │
│  ┌────────┐    ┌────────┐   ┌────────┐ │
│  │EU Data │    │US Data │   │APAC    │ │
│  │Encrypted   │Encrypted│   │Data    │ │
│  │with EU │    │with US │   │Encrypt │ │
│  │Key     │    │Key     │   │APAC Key│ │
│  └────────┘    └────────┘   └────────┘ │
│                                          │
│  Keys cannot decrypt data from other    │
│  regions - enforcement at crypto layer  │
└──────────────────────────────────────────┘
```

### Real-world Examples

**Google Cloud**: EKM (External Key Manager) for customer-controlled keys per region.

**AWS**: Regional KMS keys with no cross-region capabilities.

---

## 5. Data Classification Pattern

### Description

Classify data based on sensitivity and apply appropriate regional controls based on classification level.

### Classification Levels

```yaml
data_classification:
  public:
    description: "Publicly available information"
    restrictions: none
    storage_regions: all
    encryption: optional

  internal:
    description: "Internal business information"
    restrictions: employee_access_only
    storage_regions: all_company_regions
    encryption: required

  confidential:
    description: "Sensitive business information"
    restrictions: need_to_know_basis
    storage_regions: restricted_regions
    encryption: required
    key_rotation: 90_days

  restricted:
    description: "Regulated data (PII, PHI, PCI)"
    restrictions: strict_access_controls
    storage_regions: compliance_regions_only
    encryption: required_with_cmk
    key_rotation: 30_days
    audit_logging: mandatory
    data_residency: enforced

  highly_restricted:
    description: "Trade secrets, top secret"
    restrictions: executive_approval_required
    storage_regions: single_region_only
    encryption: required_with_hsm
    key_rotation: 7_days
    audit_logging: comprehensive
    data_residency: strictly_enforced
    access_logging: real_time
```

---

## 6. Geo-Fencing Pattern

### Description

Implement geographic access controls that prevent data access from outside authorized regions, even with valid credentials.

### Implementation Example

```python
# geo_fence.py
import boto3
from typing import List, Tuple

class GeoFence:
    def __init__(self):
        self.allowed_regions = {}

    def add_fence(self, data_id: str, allowed_regions: List[str],
                  allowed_countries: List[str] = None):
        """Define geographic fence for data"""
        self.allowed_regions[data_id] = {
            'regions': allowed_regions,
            'countries': allowed_countries or []
        }

    def check_access(self, data_id: str,
                    access_region: str,
                    access_country: str) -> Tuple[bool, str]:
        """Check if access from location is allowed"""
        if data_id not in self.allowed_regions:
            return True, "No fence defined"

        fence = self.allowed_regions[data_id]

        # Check region
        if access_region not in fence['regions']:
            return False, f"Access from {access_region} not allowed"

        # Check country if specified
        if fence['countries'] and access_country not in fence['countries']:
            return False, f"Access from {access_country} not allowed"

        return True, "Access allowed"


# S3 Bucket Policy with geo-fencing
resource "aws_s3_bucket_policy" "geo_fence" {
  bucket = aws_s3_bucket.data.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid    = "DenyAccessOutsideEU"
        Effect = "Deny"
        Principal = "*"
        Action = "s3:*"
        Resource = [
          "${aws_s3_bucket.data.arn}/*",
          aws_s3_bucket.data.arn
        ]
        Condition = {
          StringNotEquals = {
            "aws:RequestedRegion" = [
              "eu-west-1",
              "eu-central-1"
            ]
          }
        }
      }
    ]
  })
}
```

---

## 7. Compliant Backup Pattern

### Description

Ensure backups comply with data residency requirements and don't inadvertently transfer data across borders.

### Best Practices

```
┌──────────────────────────────────────────┐
│      Compliant Backup Strategy           │
├──────────────────────────────────────────┤
│                                          │
│  1. Same-Region Backups                 │
│     └─ Backups stay in source region    │
│                                          │
│  2. Regional Retention Policies         │
│     └─ Different retention by region    │
│                                          │
│  3. Encrypted Backups                   │
│     └─ Regional keys only               │
│                                          │
│  4. No Cross-Region Replication         │
│     └─ Unless explicitly approved       │
│                                          │
│  5. Backup Access Logs                  │
│     └─ Track all backup access          │
│                                          │
└──────────────────────────────────────────┘
```

---

## Tool Recommendations

### Compliance Management Tools

**Data Residency:**
- AWS Control Tower (multi-account governance)
- Azure Policy (compliance enforcement)
- GCP Organization Policy Service
- HashiCorp Sentinel (policy as code)

**Data Discovery & Classification:**
- AWS Macie
- Azure Purview
- Google Cloud DLP
- BigID
- OneTrust

**Encryption & Key Management:**
- AWS KMS
- Azure Key Vault
- GCP Cloud KMS
- HashiCorp Vault
- Thales CipherTrust

**Compliance Monitoring:**
- AWS Config
- Azure Security Center
- GCP Security Command Center
- Prisma Cloud (Palo Alto)
- CloudHealth

### Regulatory Frameworks

**GDPR Compliance:**
- OneTrust
- TrustArc
- Securiti.ai

**Multi-Regulation:**
- Vanta
- Drata
- Secureframe

---

## Summary

Data residency and compliance patterns are critical for:

1. **Legal Compliance**: Meeting data sovereignty requirements
2. **Customer Trust**: Demonstrating data protection commitment
3. **Risk Mitigation**: Avoiding regulatory penalties
4. **Market Access**: Operating in regulated markets

### Key Implementation Principles

- **Design for Compliance**: Build residency controls from the start
- **Default to Restriction**: Restrict by default, allow explicitly
- **Automate Enforcement**: Use policy-as-code and automation
- **Maintain Audit Trails**: Log all data movements
- **Regular Audits**: Continuously verify compliance
- **Stay Updated**: Regulations evolve frequently

### FAANG Examples

**Amazon**: Separate AWS partitions for GovCloud (US) and China
**Meta**: Distributed data architecture with regional isolation
**Apple**: Country-specific iCloud data storage
**Netflix**: Content licensing drives regional data strategies
**Google**: Regional compliance zones for Cloud Platform

Remember: **Data residency is not just about where data is stored, but also where it can be accessed from and by whom.**
