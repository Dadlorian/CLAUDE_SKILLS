# E-Discovery API Integration Patterns

## Document Information
- **Version**: 1.0.0
- **Last Updated**: 2025-11-19
- **Authority**: EDRM Framework, Relativity, Nuix, Logikcull Documentation
- **Scope**: API integration patterns for major e-discovery platforms

## Table of Contents
1. [Introduction](#introduction)
2. [EDRM Framework Integration](#edrm-framework-integration)
3. [Relativity API Integration](#relativity-api-integration)
4. [Nuix API Integration](#nuix-api-integration)
5. [Logikcull API Integration](#logikcull-api-integration)
6. [Common E-Discovery Patterns](#common-e-discovery-patterns)
7. [Technology-Assisted Review (TAR)](#technology-assisted-review-tar)
8. [Production and Export](#production-and-export)
9. [Analytics and Reporting](#analytics-and-reporting)
10. [Security and Privilege Protection](#security-and-privilege-protection)

---

## Introduction

### E-Discovery Landscape

**Major Platforms:**

1. **Relativity**: Market-leading enterprise e-discovery platform
   - REST API for data management
   - Processing and analytics capabilities
   - Advanced AI/TAR features

2. **Nuix**: Processing and early case assessment platform
   - Powerful data processing engine
   - Advanced analytics
   - Java-based REST API

3. **Logikcull**: Cloud-based e-discovery for mid-market
   - User-friendly interface
   - Rapid deployment
   - Simple REST API

4. **Others**: Disco, Everlaw, CS Disco, Clearwell

### EDRM Framework

**Electronic Discovery Reference Model (EDRM) Phases:**
```
Information Governance → Identification → Preservation → Collection →
Processing → Review → Analysis → Production → Presentation
```

### E-Discovery Workflow Requirements

**Key Capabilities:**
- Custodian management
- Legal hold tracking
- Data collection and processing
- Document review and coding
- Privilege identification
- Production management
- Analytics and TAR
- Audit trail maintenance

---

## EDRM Framework Integration

### EDRM Data Model

**Core Entities:**
```python
from dataclasses import dataclass
from typing import List, Optional
from datetime import datetime
from enum import Enum

class EDRMPhase(Enum):
    """EDRM lifecycle phases"""
    INFORMATION_GOVERNANCE = "information_governance"
    IDENTIFICATION = "identification"
    PRESERVATION = "preservation"
    COLLECTION = "collection"
    PROCESSING = "processing"
    REVIEW = "review"
    ANALYSIS = "analysis"
    PRODUCTION = "production"
    PRESENTATION = "presentation"

@dataclass
class Custodian:
    """Document custodian"""
    custodian_id: str
    name: str
    email: str
    department: str
    employment_status: str  # Active, Terminated, Contractor
    legal_hold_status: bool
    collection_status: str
    data_sources: List[str]  # Email, file shares, mobile device, etc.

@dataclass
class LegalHold:
    """Legal hold notice"""
    hold_id: str
    matter_id: str
    hold_name: str
    issued_date: datetime
    custodians: List[Custodian]
    preservation_scope: dict
    status: str  # Active, Released
    release_date: Optional[datetime]

@dataclass
class DataSource:
    """Data source for collection"""
    source_id: str
    custodian_id: str
    source_type: str  # Email, FileShare, Database, Mobile
    location: str
    date_range_start: datetime
    date_range_end: datetime
    collection_status: str
    total_items: int
    total_size_gb: float

@dataclass
class Document:
    """E-discovery document"""
    document_id: str
    bates_number: str
    custodian: str
    source_path: str
    file_name: str
    file_type: str
    file_size_bytes: int
    created_date: datetime
    modified_date: datetime
    author: str
    recipients: List[str]
    subject: str
    email_from: Optional[str]
    email_to: Optional[List[str]]
    email_cc: Optional[List[str]]
    email_bcc: Optional[List[str]]
    has_attachments: bool
    attachment_count: int
    parent_document_id: Optional[str]
    family_id: str  # Email and all attachments share family ID
    md5_hash: str
    extracted_text: str
    review_status: str
    responsiveness: Optional[str]
    privilege_status: Optional[str]
    issues_coded: List[str]
    tags: List[str]

@dataclass
class ReviewBatch:
    """Document review batch assignment"""
    batch_id: str
    reviewer_id: str
    assigned_date: datetime
    due_date: datetime
    documents: List[str]  # Document IDs
    status: str  # Assigned, InProgress, Completed
    completed_date: Optional[datetime]
```

### EDRM API Pattern

```python
class EDRMIntegration:
    """Base class for EDRM-compliant integrations"""

    def __init__(self, platform_client):
        self.client = platform_client

    # Identification Phase
    def identify_custodians(self, matter_id):
        """Identify key custodians for matter"""
        raise NotImplementedError

    # Preservation Phase
    def issue_legal_hold(self, hold_data):
        """Issue legal hold to custodians"""
        raise NotImplementedError

    def track_hold_acknowledgments(self, hold_id):
        """Track custodian acknowledgments"""
        raise NotImplementedError

    # Collection Phase
    def collect_data(self, collection_spec):
        """Collect data from custodian sources"""
        raise NotImplementedError

    def verify_collection_integrity(self, collection_id):
        """Verify collection data integrity"""
        raise NotImplementedError

    # Processing Phase
    def process_collected_data(self, processing_spec):
        """Process collected data"""
        raise NotImplementedError

    def deduplicate_documents(self, dedup_method='md5'):
        """Deduplicate documents"""
        raise NotImplementedError

    # Review Phase
    def create_review_batches(self, batch_spec):
        """Create document review batches"""
        raise NotImplementedError

    def assign_reviewers(self, batch_id, reviewer_id):
        """Assign reviewers to batches"""
        raise NotImplementedError

    # Production Phase
    def create_production(self, production_spec):
        """Create document production"""
        raise NotImplementedError

    def export_production(self, production_id, format='pdf'):
        """Export production documents"""
        raise NotImplementedError
```

---

## Relativity API Integration

### Relativity REST API

**Authentication:**
```python
import requests
from requests.auth import HTTPBasicAuth

class RelativityClient:
    """Client for Relativity REST API"""

    def __init__(self, instance_url, username, password):
        """
        Initialize Relativity client

        Args:
            instance_url: Relativity instance URL (e.g., https://instance.relativity.com)
            username: Relativity username
            password: Relativity password
        """
        self.instance_url = instance_url.rstrip('/')
        self.api_base = f"{self.instance_url}/Relativity.REST/api"
        self.auth = HTTPBasicAuth(username, password)

        self.session = requests.Session()
        self.session.auth = self.auth
        self.session.headers.update({
            'Content-Type': 'application/json',
            'X-CSRF-Header': '-'  # CSRF protection
        })

    def get_workspace_id(self, workspace_name):
        """Get workspace ID by name"""
        response = self.session.post(
            f"{self.api_base}/Relativity.Services.Workspace.IWorkspaceModule/Workspace Manager/QueryAsync",
            json={
                "request": {
                    "condition": f"'Name' == '{workspace_name}'",
                    "fields": ["ArtifactID", "Name"]
                }
            }
        )
        response.raise_for_status()

        results = response.json()['Results']
        if results:
            return results[0]['Artifact']['ArtifactID']
        else:
            raise ValueError(f"Workspace not found: {workspace_name}")
```

### Document Management

**Querying Documents:**
```python
def query_documents(self, workspace_id, query_condition, fields=None):
    """
    Query documents in Relativity workspace

    Args:
        workspace_id: Workspace artifact ID
        query_condition: Relativity condition (e.g., "'Custodian' == 'John Smith'")
        fields: List of field names to retrieve

    Returns:
        List of documents matching query
    """
    if fields is None:
        fields = [
            'Control Number',
            'File Name',
            'Custodian',
            'Email From',
            'Email To',
            'Date Sent',
            'Responsiveness',
            'Privilege Status'
        ]

    response = self.session.post(
        f"{self.api_base}/Relativity.Services.Query.IQueryModule/Query Manager/QueryAsync",
        json={
            "request": {
                "objectType": {
                    "artifactTypeID": 10  # Document artifact type
                },
                "condition": query_condition,
                "fields": [{"Name": field} for field in fields],
                "queryHint": "UseIndexV2"
            },
            "workspaceID": workspace_id
        }
    )
    response.raise_for_status()

    return response.json()['Objects']

def update_document_fields(self, workspace_id, document_id, field_updates):
    """
    Update document fields

    Args:
        workspace_id: Workspace artifact ID
        document_id: Document artifact ID
        field_updates: dict of field name -> value

    Returns:
        Updated document
    """
    # Build field update request
    update_request = {
        "workspaceID": workspace_id,
        "request": {
            "Object": {
                "ArtifactID": document_id
            },
            "FieldValues": [
                {
                    "Field": {"Name": field_name},
                    "Value": value
                }
                for field_name, value in field_updates.items()
            ]
        }
    }

    response = self.session.post(
        f"{self.api_base}/Relativity.Objects.IObjectManager/Object Manager/UpdateAsync",
        json=update_request
    )
    response.raise_for_status()

    return response.json()

def mass_update_documents(self, workspace_id, query_condition, field_updates):
    """
    Mass update documents matching query

    Args:
        workspace_id: Workspace artifact ID
        query_condition: Query to select documents
        field_updates: Fields to update

    Returns:
        Number of documents updated
    """
    response = self.session.post(
        f"{self.api_base}/Relativity.Services.MassUpdate.IMassUpdateModule/Mass Update Manager/UpdateDocumentsAsync",
        json={
            "workspaceID": workspace_id,
            "request": {
                "SearchCondition": query_condition,
                "FieldValues": [
                    {
                        "Field": {"Name": field_name},
                        "Value": value
                    }
                    for field_name, value in field_updates.items()
                ]
            }
        }
    )
    response.raise_for_status()

    result = response.json()
    return result.get('TotalUpdated', 0)
```

### Production Management

**Create Production:**
```python
def create_production(self, workspace_id, production_name, saved_search_id, numbering_spec):
    """
    Create document production

    Args:
        workspace_id: Workspace ID
        production_name: Production name
        saved_search_id: Saved search defining production set
        numbering_spec: Bates numbering specification
            - prefix: str
            - number_of_digits: int
            - starting_number: int

    Returns:
        Production artifact ID
    """
    production_data = {
        "workspaceID": workspace_id,
        "production": {
            "Name": production_name,
            "DataSource": {
                "ArtifactID": saved_search_id  # Saved search
            },
            "BatesPrefix": numbering_spec['prefix'],
            "NumberOfDigits": numbering_spec['number_of_digits'],
            "BatesStartingNumber": numbering_spec['starting_number'],
            "ProductionType": "ImagesAndNatives",
            "Placeholder": {
                "Placeholder": "REDACTED"
            }
        }
    }

    response = self.session.post(
        f"{self.api_base}/Relativity.Productions.Services.IProductionModule/Production Manager/CreateSingleAsync",
        json=production_data
    )
    response.raise_for_status()

    return response.json()['ArtifactID']

def stage_production(self, workspace_id, production_id):
    """Stage production (assign Bates numbers)"""
    response = self.session.post(
        f"{self.api_base}/Relativity.Productions.Services.IProductionModule/Production Manager/StageAsync",
        json={
            "workspaceID": workspace_id,
            "productionID": production_id
        }
    )
    response.raise_for_status()

    return response.json()

def run_production(self, workspace_id, production_id):
    """Run production to generate output files"""
    response = self.session.post(
        f"{self.api_base}/Relativity.Productions.Services.IProductionModule/Production Manager/RunAsync",
        json={
            "workspaceID": workspace_id,
            "productionID": production_id
        }
    )
    response.raise_for_status()

    return response.json()
```

### Analytics and Conceptual Search

**Conceptual Index:**
```python
def create_conceptual_index(self, workspace_id, saved_search_id, index_name):
    """
    Create conceptual analytics index

    Args:
        workspace_id: Workspace ID
        saved_search_id: Saved search defining document set
        index_name: Name for index

    Returns:
        Index artifact ID
    """
    response = self.session.post(
        f"{self.api_base}/Relativity.Analytics.Services.IConceptualIndexModule/Conceptual Analytics Index Manager/CreateSingleAsync",
        json={
            "workspaceID": workspace_id,
            "index": {
                "Name": index_name,
                "SavedSearch": {
                    "ArtifactID": saved_search_id
                }
            }
        }
    )
    response.raise_for_status()

    return response.json()['ArtifactID']

def run_conceptual_search(self, workspace_id, index_id, search_terms):
    """
    Run conceptual search against index

    Args:
        workspace_id: Workspace ID
        index_id: Conceptual index ID
        search_terms: Search query

    Returns:
        List of similar documents with relevance scores
    """
    response = self.session.post(
        f"{self.api_base}/Relativity.Analytics.Services.IConceptualSearchModule/Conceptual Search Manager/SearchAsync",
        json={
            "workspaceID": workspace_id,
            "request": {
                "ConceptualIndex": {
                    "ArtifactID": index_id
                },
                "SearchText": search_terms,
                "MaxResults": 100
            }
        }
    )
    response.raise_for_status()

    return response.json()['Results']
```

---

## Nuix API Integration

### Nuix REST API

```python
class NuixClient:
    """Client for Nuix REST API"""

    def __init__(self, server_url, username, password):
        """
        Initialize Nuix client

        Args:
            server_url: Nuix server URL
            username: Nuix username
            password: Nuix password
        """
        self.server_url = server_url.rstrip('/')
        self.api_base = f"{self.server_url}/nuix-restful-service/svc/v1"

        self.session = requests.Session()
        self._authenticate(username, password)

    def _authenticate(self, username, password):
        """Authenticate with Nuix"""
        response = self.session.post(
            f"{self.api_base}/security/login",
            json={
                "username": username,
                "password": password
            }
        )
        response.raise_for_status()

        token = response.json()['token']
        self.session.headers.update({
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        })

    def create_case(self, case_name, case_location, investigator):
        """
        Create new Nuix case

        Args:
            case_name: Case name
            case_location: File system path for case
            investigator: Investigator name

        Returns:
            Case GUID
        """
        response = self.session.post(
            f"{self.api_base}/cases",
            json={
                "name": case_name,
                "location": case_location,
                "investigator": investigator,
                "description": f"E-Discovery case: {case_name}"
            }
        )
        response.raise_for_status()

        return response.json()['caseGuid']

    def process_evidence(self, case_guid, evidence_spec):
        """
        Process evidence into Nuix case

        Args:
            case_guid: Case GUID
            evidence_spec: Evidence processing specification
                - evidence_path: str or list
                - processing_profile: str
                - worker_count: int
                - options: dict

        Returns:
            Processing job ID
        """
        processing_request = {
            "evidenceStore": evidence_spec.get('evidence_path'),
            "processingProfile": evidence_spec.get('processing_profile', 'default'),
            "parallelProcessingSettings": {
                "workerCount": evidence_spec.get('worker_count', 4)
            }
        }

        if 'options' in evidence_spec:
            processing_request.update(evidence_spec['options'])

        response = self.session.post(
            f"{self.api_base}/cases/{case_guid}/processing",
            json=processing_request
        )
        response.raise_for_status()

        return response.json()['jobId']

    def search_items(self, case_guid, query):
        """
        Search items in Nuix case

        Args:
            case_guid: Case GUID
            query: Nuix query string

        Returns:
            List of matching items
        """
        response = self.session.post(
            f"{self.api_base}/cases/{case_guid}/search",
            json={
                "query": query,
                "options": {
                    "sortBy": "dateTime",
                    "sortOrder": "descending"
                }
            }
        )
        response.raise_for_status()

        return response.json()['items']

    def export_items(self, case_guid, query, export_spec):
        """
        Export items from Nuix case

        Args:
            case_guid: Case GUID
            query: Query to select items
            export_spec: Export specification
                - export_type: 'concordance', 'pdf', 'native'
                - output_path: str
                - numbering: dict

        Returns:
            Export job ID
        """
        export_request = {
            "query": query,
            "exportType": export_spec['export_type'],
            "outputPath": export_spec['output_path']
        }

        if 'numbering' in export_spec:
            export_request['numberingOptions'] = export_spec['numbering']

        response = self.session.post(
            f"{self.api_base}/cases/{case_guid}/export",
            json=export_request
        )
        response.raise_for_status()

        return response.json()['jobId']
```

### Advanced Processing

**Nuix Processing Profiles:**
```python
def create_processing_profile(self, profile_spec):
    """
    Create custom processing profile

    Args:
        profile_spec: Processing profile specification
            - name: str
            - email_processing: dict
            - file_processing: dict
            - text_extraction: dict
            - forensic_processing: bool

    Returns:
        Profile ID
    """
    profile_data = {
        "name": profile_spec['name'],
        "processText": True,
        "processImages": True,
        "traversalScope": "full_traversal",
        "emailProcessing": {
            "extractEmails": True,
            "processEmbedded": True,
            "rfc822Processing": "full"
        },
        "fileProcessing": {
            "extractArchives": True,
            "maxNestingDepth": profile_spec.get('max_nesting', 25),
            "processEncrypted": True
        },
        "textExtraction": {
            "extractText": True,
            "processHiddenData": True
        },
        "forensicProcessing": profile_spec.get('forensic_processing', False)
    }

    response = self.session.post(
        f"{self.api_base}/processing-profiles",
        json=profile_data
    )
    response.raise_for_status()

    return response.json()['profileId']
```

---

## Logikcull API Integration

```python
class LogikcullClient:
    """Client for Logikcull REST API"""

    def __init__(self, api_key):
        """
        Initialize Logikcull client

        Args:
            api_key: Logikcull API key
        """
        self.api_base = "https://app.logikcull.com/api/v1"
        self.session = requests.Session()
        self.session.headers.update({
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        })

    def create_project(self, project_name, matter_id=None):
        """Create new project"""
        response = self.session.post(
            f"{self.api_base}/projects",
            json={
                "name": project_name,
                "matter_id": matter_id
            }
        )
        response.raise_for_status()
        return response.json()

    def upload_documents(self, project_id, file_paths):
        """Upload documents to project"""
        upload_results = []

        for file_path in file_paths:
            with open(file_path, 'rb') as f:
                files = {'file': f}
                response = self.session.post(
                    f"{self.api_base}/projects/{project_id}/documents",
                    files=files
                )
                response.raise_for_status()
                upload_results.append(response.json())

        return upload_results

    def search_documents(self, project_id, search_query):
        """Search documents"""
        response = self.session.post(
            f"{self.api_base}/projects/{project_id}/search",
            json={"query": search_query}
        )
        response.raise_for_status()
        return response.json()['documents']

    def create_production(self, project_id, production_spec):
        """Create document production"""
        response = self.session.post(
            f"{self.api_base}/projects/{project_id}/productions",
            json=production_spec
        )
        response.raise_for_status()
        return response.json()
```

---

## Common E-Discovery Patterns

### Custodian Management Pattern

```python
class CustodianManager:
    """Manage custodians across e-discovery lifecycle"""

    def __init__(self, ediscovery_client, hr_system_client):
        self.ediscovery = ediscovery_client
        self.hr_system = hr_system_client

    def identify_custodians(self, matter_keywords, departments=None):
        """
        Identify key custodians based on matter

        Args:
            matter_keywords: Keywords related to matter
            departments: Optional department filter

        Returns:
            List of potential custodians
        """
        # Query HR system for employees matching criteria
        employees = self.hr_system.search_employees(
            keywords=matter_keywords,
            departments=departments
        )

        custodians = []
        for emp in employees:
            custodian = Custodian(
                custodian_id=emp['employee_id'],
                name=emp['name'],
                email=emp['email'],
                department=emp['department'],
                employment_status=emp['status'],
                legal_hold_status=False,
                collection_status='Not Started',
                data_sources=self._identify_data_sources(emp)
            )
            custodians.append(custodian)

        return custodians

    def _identify_data_sources(self, employee):
        """Identify potential data sources for employee"""
        sources = ['Email']  # Everyone has email

        if employee.get('has_laptop'):
            sources.append('Laptop')

        if employee.get('has_mobile'):
            sources.append('Mobile Device')

        if employee.get('network_shares'):
            sources.extend(employee['network_shares'])

        return sources

    def issue_legal_hold(self, custodians, matter_info):
        """Issue legal hold to custodians"""
        hold = LegalHold(
            hold_id=generate_id(),
            matter_id=matter_info['matter_id'],
            hold_name=matter_info['matter_name'],
            issued_date=datetime.utcnow(),
            custodians=custodians,
            preservation_scope=matter_info['preservation_scope'],
            status='Active',
            release_date=None
        )

        # Send hold notices
        for custodian in custodians:
            self._send_hold_notice(custodian, hold)

        # Track in e-discovery system
        self.ediscovery.create_legal_hold(hold)

        return hold
```

---

## Technology-Assisted Review (TAR)

### TAR Implementation Pattern

```python
class TARWorkflow:
    """Technology-Assisted Review workflow"""

    def __init__(self, ediscovery_client, ml_service):
        self.ediscovery = ediscovery_client
        self.ml_service = ml_service

    def create_tar_project(self, workspace_id, review_criteria):
        """
        Create TAR project

        Args:
            workspace_id: E-discovery workspace
            review_criteria: Responsiveness criteria

        Returns:
            TAR project ID
        """
        # Create saved search for full document set
        all_docs_search = self.ediscovery.create_saved_search(
            workspace_id,
            name="TAR_Full_Document_Set",
            query="NOT [System Created Date] == NULL"
        )

        # Create TAR project
        tar_project = self.ml_service.create_tar_project(
            name="Predictive Coding Project",
            document_set=all_docs_search,
            review_fields=['Responsiveness', 'Privilege']
        )

        return tar_project['project_id']

    def seed_set_review(self, project_id, seed_size=500):
        """
        Generate and review seed set

        Args:
            project_id: TAR project ID
            seed_size: Number of documents in seed set

        Returns:
            Seed set document IDs
        """
        # Generate statistically representative seed set
        seed_set = self.ml_service.generate_seed_set(
            project_id,
            size=seed_size,
            sampling_method='stratified'
        )

        # Assign to senior attorney for review
        self.assign_review_batch(
            documents=seed_set,
            reviewer='senior_attorney',
            priority='High',
            instructions='Seed set review for TAR model training'
        )

        return seed_set

    def train_tar_model(self, project_id):
        """Train TAR model on reviewed seed set"""
        training_result = self.ml_service.train_model(
            project_id,
            algorithm='continuous_active_learning'
        )

        return {
            'model_id': training_result['model_id'],
            'precision': training_result['metrics']['precision'],
            'recall': training_result['metrics']['recall'],
            'f1_score': training_result['metrics']['f1']
        }

    def continuous_active_learning(self, project_id, target_recall=0.95):
        """
        Implement continuous active learning

        Args:
            project_id: TAR project ID
            target_recall: Target recall percentage

        Returns:
            CAL session results
        """
        current_recall = 0.0
        round_number = 1

        while current_recall < target_recall:
            # Select documents for review (most uncertain)
            review_batch = self.ml_service.select_cal_batch(
                project_id,
                batch_size=100
            )

            # Assign for review
            self.assign_review_batch(
                documents=review_batch,
                reviewer='assigned_attorney',
                round=round_number
            )

            # Wait for review completion (in practice, check asynchronously)
            # ...

            # Update model with new training data
            self.ml_service.update_model(project_id)

            # Calculate current recall
            metrics = self.ml_service.get_model_metrics(project_id)
            current_recall = metrics['recall']

            print(f"Round {round_number}: Recall = {current_recall:.2%}")
            round_number += 1

        return {
            'rounds_completed': round_number - 1,
            'final_recall': current_recall,
            'documents_reviewed': (round_number - 1) * 100
        }

    def validate_tar_model(self, project_id, validation_set_size=500):
        """
        Validate TAR model with independent control set

        Args:
            project_id: TAR project ID
            validation_set_size: Size of validation set

        Returns:
            Validation results
        """
        # Generate validation set (separate from training)
        validation_set = self.ml_service.generate_validation_set(
            project_id,
            size=validation_set_size,
            exclude_training=True
        )

        # Manual review of validation set
        self.assign_review_batch(
            documents=validation_set,
            reviewer='senior_attorney',
            instructions='Validation set - independent review'
        )

        # Compare manual review to model predictions
        validation_results = self.ml_service.validate_model(
            project_id,
            validation_set
        )

        return {
            'precision': validation_results['precision'],
            'recall': validation_results['recall'],
            'f1_score': validation_results['f1'],
            'elusion': validation_results['elusion'],
            'richness': validation_results['richness']
        }
```

### TAR Defensibility Documentation

```python
def generate_tar_defensibility_report(self, project_id):
    """
    Generate defensibility report for TAR process

    Per EDRM TAR Guidelines and case law (Da Silva Moore, etc.)
    """
    report = {
        'matter_info': self.get_matter_info(),
        'tar_protocol': {
            'methodology': 'Continuous Active Learning',
            'seed_set_size': 500,
            'seed_set_selection': 'Stratified random sample',
            'target_recall': 0.95,
            'validation_method': 'Independent control set (500 docs)'
        },
        'training_results': {
            'rounds_completed': 12,
            'total_documents_reviewed': 1200,
            'model_performance': {
                'precision': 0.87,
                'recall': 0.96,
                'f1_score': 0.91
            }
        },
        'validation_results': {
            'validation_set_size': 500,
            'validation_precision': 0.85,
            'validation_recall': 0.94,
            'margin_of_error': 0.03
        },
        'quality_control': {
            'seed_set_reviewer': 'Senior Partner John Doe',
            'reviewers': ['Attorney 1', 'Attorney 2', 'Attorney 3'],
            'reviewer_agreement': 0.89,  # Kappa statistic
            'spot_checks_performed': 25
        },
        'production_statistics': {
            'total_document_population': 50000,
            'responsive_documents_identified': 8500,
            'richness': 0.17,  # 17% responsive
            'documents_produced': 8200,  # After privilege review
            'documents_withheld_privilege': 300
        }
    }

    return report
```

---

## Production and Export

### Production Workflow

```python
class ProductionManager:
    """Manage document production process"""

    def __init__(self, ediscovery_client):
        self.client = ediscovery_client

    def create_production_set(self, workspace_id, production_spec):
        """
        Create production document set

        Args:
            production_spec: Production specification
                - name: str
                - saved_search_id: Documents to produce
                - numbering: Bates numbering spec
                - format: 'pdf', 'native', 'tiff'
                - redactions: Apply redactions
                - privilege_log: Generate privilege log

        Returns:
            Production set ID
        """
        # Apply privilege filter
        if production_spec.get('privilege_log'):
            privileged_docs = self.client.query_documents(
                workspace_id,
                "'Privilege Status' == 'Privileged'"
            )

            # Generate privilege log
            privilege_log = self.generate_privilege_log(
                workspace_id,
                privileged_docs
            )

        # Create production
        production_id = self.client.create_production(
            workspace_id,
            production_spec['name'],
            production_spec['saved_search_id'],
            production_spec['numbering']
        )

        # Stage production (assign Bates numbers)
        self.client.stage_production(workspace_id, production_id)

        # Run production
        self.client.run_production(workspace_id, production_id)

        return {
            'production_id': production_id,
            'privilege_log': privilege_log if production_spec.get('privilege_log') else None
        }

    def generate_privilege_log(self, workspace_id, privileged_docs):
        """
        Generate privilege log per FRCP Rule 26(b)(5)

        Returns:
            Privilege log data
        """
        privilege_log = []

        for doc in privileged_docs:
            entry = {
                'bates_number': doc.get('Control Number'),
                'document_date': doc.get('Date Sent'),
                'author': doc.get('Email From') or doc.get('Author'),
                'recipients': doc.get('Email To', []),
                'cc_recipients': doc.get('Email CC', []),
                'subject': doc.get('Subject') or doc.get('File Name'),
                'privilege_type': doc.get('Privilege Type', 'Attorney-Client'),
                'description': 'Privileged communication',
                'basis_for_privilege': doc.get('Privilege Basis')
            }
            privilege_log.append(entry)

        return privilege_log

    def export_load_file(self, production_id, format='concordance'):
        """
        Export production with load file

        Args:
            production_id: Production ID
            format: 'concordance', 'ipro', 'opticon'

        Returns:
            Export package path
        """
        # Generate load file in specified format
        # Concordance DAT file format example
        pass
```

---

## Analytics and Reporting

### E-Discovery Analytics

```python
class EDiscoveryAnalytics:
    """Analytics for e-discovery matters"""

    def __init__(self, ediscovery_client):
        self.client = ediscovery_client

    def generate_matter_statistics(self, workspace_id):
        """Generate comprehensive matter statistics"""
        stats = {
            'total_documents': self.client.get_document_count(workspace_id),
            'total_size_gb': self.client.get_total_size(workspace_id),
            'custodians': self.client.get_custodian_count(workspace_id),
            'date_range': self.client.get_date_range(workspace_id),
            'file_type_breakdown': self.get_file_type_breakdown(workspace_id),
            'custodian_breakdown': self.get_custodian_breakdown(workspace_id),
            'review_statistics': self.get_review_statistics(workspace_id),
            'communication_analytics': self.get_communication_analytics(workspace_id)
        }

        return stats

    def get_file_type_breakdown(self, workspace_id):
        """Analyze document types"""
        # Query by file extension
        file_types = {}
        for ext in ['.docx', '.pdf', '.xlsx', '.pptx', '.msg', '.txt']:
            count = self.client.query_count(
                workspace_id,
                f"'File Extension' == '{ext}'"
            )
            file_types[ext] = count

        return file_types

    def get_communication_analytics(self, workspace_id):
        """Analyze email communications"""
        # Email volume over time
        # Communication network analysis
        # Thread analysis
        pass
```

---

## Security and Privilege Protection

### Privilege Identification

```python
class PrivilegeDetector:
    """Detect potentially privileged documents"""

    PRIVILEGE_KEYWORDS = [
        'attorney-client', 'privileged', 'confidential',
        'legal advice', 'work product', 'in confidence',
        'attorney eyes only', 'ACP', 'legal opinion'
    ]

    ATTORNEY_DOMAINS = [
        '@lawfirm.com', '@counsel.com', '@legal.com'
    ]

    def scan_for_privilege(self, document):
        """
        Scan document for privilege indicators

        Returns:
            Privilege likelihood score and reasons
        """
        score = 0
        reasons = []

        # Check participants
        if self._has_attorney_participant(document):
            score += 30
            reasons.append("Attorney participant detected")

        # Check subject line
        if self._has_privilege_keyword(document.get('subject', '')):
            score += 25
            reasons.append("Privilege keyword in subject")

        # Check extracted text
        if self._has_privilege_keyword(document.get('extracted_text', '')):
            score += 20
            reasons.append("Privilege keyword in content")

        # Check document type
        if document.get('file_type') in ['.docx', '.pdf']:
            # More likely to be legal documents
            score += 5

        return {
            'privilege_score': min(score, 100),
            'recommend_review': score >= 50,
            'reasons': reasons
        }

    def _has_attorney_participant(self, document):
        """Check if attorney involved in communication"""
        participants = []
        participants.append(document.get('email_from', ''))
        participants.extend(document.get('email_to', []))
        participants.extend(document.get('email_cc', []))

        for participant in participants:
            if any(domain in participant for domain in self.ATTORNEY_DOMAINS):
                return True

        return False

    def _has_privilege_keyword(self, text):
        """Check for privilege keywords"""
        text_lower = text.lower()
        return any(keyword in text_lower for keyword in self.PRIVILEGE_KEYWORDS)
```

---

## Document Control

**Version**: 1.0.0
**Last Updated**: 2025-11-19
**Maintained By**: Legal Technology E-Discovery Team

*E-discovery platforms evolve rapidly. Consult current vendor documentation and EDRM guidelines for latest best practices.*
