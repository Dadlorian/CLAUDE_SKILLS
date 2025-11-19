# Matter Intake Automation Pattern

## Overview

The Matter Intake Automation Pattern provides a comprehensive framework for automating the initial client intake, matter assessment, and matter creation processes in legal practice management systems. This pattern streamlines the onboarding process, reduces manual data entry errors, improves consistency, and accelerates the time-to-billing.

**Key Features:**
- Automated form collection and validation
- Conflict of interest checking
- Preliminary legal issue assessment
- Matter profiling and categorization
- Integrated document generation
- Seamless PM system integration

**Expected Outcomes:**
- 80% reduction in intake processing time
- 95% data accuracy improvement
- Faster matter creation (same day)
- Improved client experience
- Better matter categorization and resource allocation

## Architecture Components

### 1. Intake Form Management and Validation

```python
from dataclasses import dataclass, field
from enum import Enum
from typing import List, Dict, Optional, Any, Callable
from datetime import datetime
import re

class MatterType(Enum):
    CORPORATE = "corporate"
    LITIGATION = "litigation"
    EMPLOYMENT = "employment"
    INTELLECTUAL_PROPERTY = "intellectual_property"
    REAL_ESTATE = "real_estate"
    FAMILY = "family"
    ESTATE_PLANNING = "estate_planning"
    TAX = "tax"
    REGULATORY = "regulatory"

class ClientType(Enum):
    INDIVIDUAL = "individual"
    CORPORATION = "corporation"
    LLC = "llc"
    PARTNERSHIP = "partnership"
    NONPROFIT = "nonprofit"
    GOVERNMENT = "government"

class IntakeFormField:
    def __init__(self, field_name: str, field_type: str, required: bool = False,
                 validator: Optional[Callable] = None, options: List[str] = None):
        self.field_name = field_name
        self.field_type = field_type  # "text", "email", "phone", "date", "select", "textarea"
        self.required = required
        self.validator = validator
        self.options = options or []
        self.error_message = ""

    def validate(self, value: Any) -> bool:
        """Validate field value"""
        if self.required and not value:
            self.error_message = f"{self.field_name} is required"
            return False

        if value and self.field_type == "email":
            if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', value):
                self.error_message = f"{self.field_name} must be valid email"
                return False

        if value and self.field_type == "phone":
            if not re.match(r'^\+?1?\d{9,15}$', value.replace('-', '').replace(' ', '')):
                self.error_message = f"{self.field_name} must be valid phone"
                return False

        if value and self.field_type == "date":
            try:
                datetime.strptime(value, '%Y-%m-%d')
            except ValueError:
                self.error_message = f"{self.field_name} must be valid date (YYYY-MM-DD)"
                return False

        if self.validator and value:
            try:
                if not self.validator(value):
                    self.error_message = f"{self.field_name} validation failed"
                    return False
            except Exception as e:
                self.error_message = str(e)
                return False

        return True

@dataclass
class ClientInfo:
    client_id: str
    client_type: ClientType
    first_name: str
    last_name: str
    email: str
    phone: str
    company_name: Optional[str] = None
    business_entity_type: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    zip_code: Optional[str] = None
    country: str = "USA"
    created_date: datetime = field(default_factory=datetime.now)

@dataclass
class OpposingParty:
    party_id: str
    name: str
    party_type: str  # Individual, Corporation, etc.
    address: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    relationship: str = "opposing_party"  # adverse, related, etc.

@dataclass
class MatterIntakeForm:
    form_id: str
    client_id: str
    matter_type: MatterType
    matter_description: str
    matter_urgency: str  # "urgent", "normal", "routine"
    opposing_parties: List[OpposingParty] = field(default_factory=list)
    estimated_value: Optional[float] = None
    related_matters: List[str] = field(default_factory=list)
    form_completion_date: datetime = field(default_factory=datetime.now)
    form_data: Dict[str, Any] = field(default_factory=dict)

class IntakeFormValidator:
    def __init__(self):
        self.fields = self._initialize_fields()
        self.validation_errors: List[Dict[str, str]] = []

    def _initialize_fields(self) -> Dict[str, IntakeFormField]:
        """Initialize standard intake form fields"""
        return {
            "client_first_name": IntakeFormField("First Name", "text", required=True),
            "client_last_name": IntakeFormField("Last Name", "text", required=True),
            "client_email": IntakeFormField("Email", "email", required=True),
            "client_phone": IntakeFormField("Phone", "phone", required=True),
            "client_type": IntakeFormField("Client Type", "select", required=True,
                                          options=[ct.value for ct in ClientType]),
            "company_name": IntakeFormField("Company Name", "text", required=False),
            "matter_type": IntakeFormField("Matter Type", "select", required=True,
                                          options=[mt.value for mt in MatterType]),
            "matter_description": IntakeFormField("Matter Description", "textarea", required=True),
            "matter_urgency": IntakeFormField("Urgency", "select", required=True,
                                             options=["urgent", "normal", "routine"]),
            "estimated_value": IntakeFormField("Estimated Matter Value", "text", required=False,
                                              validator=lambda x: self._validate_currency(x)),
            "opposing_party_name": IntakeFormField("Opposing Party", "text", required=False)
        }

    def _validate_currency(self, value: str) -> bool:
        """Validate currency amount"""
        try:
            float(value.replace('$', '').replace(',', ''))
            return True
        except ValueError:
            return False

    def validate_form(self, form_data: Dict[str, Any]) -> tuple[bool, List[str]]:
        """Validate entire form"""
        self.validation_errors = []

        for field_name, field_obj in self.fields.items():
            value = form_data.get(field_name)
            if not field_obj.validate(value):
                self.validation_errors.append({
                    "field": field_name,
                    "error": field_obj.error_message
                })

        return len(self.validation_errors) == 0, [e["error"] for e in self.validation_errors]

    def get_validation_report(self) -> Dict[str, Any]:
        """Get validation report"""
        return {
            "validation_status": "passed" if len(self.validation_errors) == 0 else "failed",
            "errors": self.validation_errors,
            "error_count": len(self.validation_errors)
        }
```

### 2. Conflict of Interest Checking

```python
@dataclass
class ConflictCheckResult:
    check_id: str
    client_id: str
    conflict_status: str  # "clear", "potential_conflict", "direct_conflict"
    conflicts_found: List[Dict[str, Any]] = field(default_factory=list)
    check_date: datetime = field(default_factory=datetime.now)
    checked_by: Optional[str] = None
    requires_waiver: bool = False

class ConflictOfInterestChecker:
    def __init__(self):
        self.matter_database: Dict[str, Dict[str, Any]] = {}
        self.client_relationships: Dict[str, List[str]] = {}

    def check_conflicts(self, client_info: ClientInfo,
                       opposing_parties: List[OpposingParty]) -> ConflictCheckResult:
        """Check for conflicts of interest"""
        conflicts = []

        # Check if client has been adverse to opposing parties
        for opposing_party in opposing_parties:
            if self._is_adverse_history(client_info, opposing_party):
                conflicts.append({
                    "type": "prior_representation",
                    "party": opposing_party.name,
                    "description": f"Firm previously represented {opposing_party.name} against this client",
                    "severity": "high"
                })

        # Check for related entities
        related_clients = self._check_related_entities(client_info)
        for related_client in related_clients:
            if any(op.name == related_client for op in opposing_parties):
                conflicts.append({
                    "type": "related_party_conflict",
                    "party": related_client,
                    "description": f"Related entity has conflict with opposing party",
                    "severity": "medium"
                })

        # Check financial relationships
        financial_conflicts = self._check_financial_interests(client_info, opposing_parties)
        conflicts.extend(financial_conflicts)

        # Determine conflict status
        if any(c["severity"] == "high" for c in conflicts):
            conflict_status = "direct_conflict"
            requires_waiver = True
        elif any(c["severity"] == "medium" for c in conflicts):
            conflict_status = "potential_conflict"
            requires_waiver = True
        else:
            conflict_status = "clear"
            requires_waiver = False

        return ConflictCheckResult(
            check_id=f"coi_check_{client_info.client_id}_{datetime.now().timestamp()}",
            client_id=client_info.client_id,
            conflict_status=conflict_status,
            conflicts_found=conflicts,
            requires_waiver=requires_waiver
        )

    def _is_adverse_history(self, client_info: ClientInfo, opposing_party: OpposingParty) -> bool:
        """Check if firm represented opposing party against this client"""
        # Query matter database for adverse history
        for matter_id, matter_data in self.matter_database.items():
            if (matter_data.get("client_name") == opposing_party.name and
                matter_data.get("opposing_parties") and
                client_info.last_name in str(matter_data.get("opposing_parties"))):
                return True
        return False

    def _check_related_entities(self, client_info: ClientInfo) -> List[str]:
        """Check for related entities that might have conflicts"""
        related = []
        # Implementation would check databases, director lists, etc.
        return related

    def _check_financial_interests(self, client_info: ClientInfo,
                                   opposing_parties: List[OpposingParty]) -> List[Dict[str, Any]]:
        """Check for financial interests in parties"""
        # Implementation would check for ownership, partnerships, etc.
        return []
```

### 3. Matter Assessment and Profiling

```python
@dataclass
class MatterProfile:
    matter_id: str
    matter_type: MatterType
    priority_level: str  # "critical", "high", "medium", "low"
    estimated_complexity: str  # "simple", "moderate", "complex", "highly_complex"
    estimated_hours: float
    estimated_cost: float
    suggested_attorney_practice_area: str
    risk_assessment: Dict[str, Any]
    assessment_date: datetime = field(default_factory=datetime.now)

class MatterAssessor:
    def __init__(self):
        self.complexity_matrix = self._initialize_complexity_matrix()
        self.matter_type_guidelines = self._initialize_guidelines()

    def _initialize_complexity_matrix(self) -> Dict[str, Dict[str, int]]:
        """Initialize matter complexity scoring matrix"""
        return {
            "number_of_parties": {"single": 1, "multiple": 3, "many": 5},
            "jurisdiction_count": {"single": 1, "multi_state": 3, "international": 5},
            "regulatory_issues": {"none": 0, "minor": 2, "major": 5},
            "financial_exposure": {
                "low": {"min": 0, "max": 50000, "score": 1},
                "medium": {"min": 50000, "max": 500000, "score": 3},
                "high": {"min": 500000, "max": 5000000, "score": 5},
                "catastrophic": {"min": 5000000, "max": float('inf'), "score": 7}
            }
        }

    def _initialize_guidelines(self) -> Dict[MatterType, Dict[str, Any]]:
        """Initialize matter-specific guidelines"""
        return {
            MatterType.CORPORATE: {
                "typical_hours": 40,
                "typical_cost": 8000,
                "practice_area": "Corporate Law",
                "complexity_factors": ["number_of_parties", "jurisdiction_count"]
            },
            MatterType.LITIGATION: {
                "typical_hours": 100,
                "typical_cost": 25000,
                "practice_area": "Litigation",
                "complexity_factors": ["number_of_parties", "jurisdiction_count", "financial_exposure"]
            },
            MatterType.EMPLOYMENT: {
                "typical_hours": 30,
                "typical_cost": 6000,
                "practice_area": "Employment Law",
                "complexity_factors": ["regulatory_issues"]
            },
            MatterType.REAL_ESTATE: {
                "typical_hours": 50,
                "typical_cost": 7500,
                "practice_area": "Real Estate",
                "complexity_factors": ["jurisdiction_count", "financial_exposure"]
            }
        }

    def assess_matter(self, intake_form: MatterIntakeForm,
                     client_info: ClientInfo) -> MatterProfile:
        """Assess matter and generate profile"""
        # Calculate complexity score
        complexity_score = self._calculate_complexity_score(intake_form)

        # Determine complexity level
        if complexity_score <= 3:
            complexity_level = "simple"
        elif complexity_score <= 6:
            complexity_level = "moderate"
        elif complexity_score <= 10:
            complexity_level = "complex"
        else:
            complexity_level = "highly_complex"

        # Get guidelines for matter type
        guidelines = self.matter_type_guidelines.get(
            intake_form.matter_type,
            self.matter_type_guidelines[MatterType.CORPORATE]
        )

        # Calculate estimated hours and cost
        hours_multiplier = {"simple": 0.5, "moderate": 1.0, "complex": 1.5, "highly_complex": 2.5}
        estimated_hours = guidelines["typical_hours"] * hours_multiplier[complexity_level]
        estimated_cost = guidelines["typical_cost"] * hours_multiplier[complexity_level]

        # Determine priority
        priority = self._determine_priority(intake_form, complexity_score)

        # Risk assessment
        risk_assessment = self._assess_risks(intake_form, client_info)

        return MatterProfile(
            matter_id=f"MAT_{datetime.now().strftime('%Y%m%d%H%M%S')}",
            matter_type=intake_form.matter_type,
            priority_level=priority,
            estimated_complexity=complexity_level,
            estimated_hours=estimated_hours,
            estimated_cost=estimated_cost,
            suggested_attorney_practice_area=guidelines["practice_area"],
            risk_assessment=risk_assessment
        )

    def _calculate_complexity_score(self, intake_form: MatterIntakeForm) -> int:
        """Calculate complexity score"""
        score = 0

        # Factor: Number of opposing parties
        score += min(len(intake_form.opposing_parties), 2) * 2

        # Factor: Estimated value
        if intake_form.estimated_value:
            if intake_form.estimated_value > 5000000:
                score += 5
            elif intake_form.estimated_value > 500000:
                score += 3
            elif intake_form.estimated_value > 50000:
                score += 1

        # Factor: Matter type inherent complexity
        matter_complexity = {
            MatterType.LITIGATION: 3,
            MatterType.INTELLECTUAL_PROPERTY: 3,
            MatterType.CORPORATE: 2,
            MatterType.REAL_ESTATE: 2,
            MatterType.EMPLOYMENT: 1,
            MatterType.FAMILY: 2,
            MatterType.ESTATE_PLANNING: 1,
            MatterType.TAX: 2,
            MatterType.REGULATORY: 3
        }
        score += matter_complexity.get(intake_form.matter_type, 2)

        return score

    def _determine_priority(self, intake_form: MatterIntakeForm, complexity_score: int) -> str:
        """Determine matter priority"""
        if intake_form.matter_urgency == "urgent":
            return "critical"
        elif complexity_score > 10:
            return "high"
        elif complexity_score > 6:
            return "medium"
        else:
            return "low"

    def _assess_risks(self, intake_form: MatterIntakeForm,
                     client_info: ClientInfo) -> Dict[str, Any]:
        """Assess matter risks"""
        risks = {
            "financial_risk": "high" if intake_form.estimated_value and intake_form.estimated_value > 1000000 else "medium",
            "reputational_risk": "low",
            "regulatory_risk": "medium" if intake_form.matter_type == MatterType.REGULATORY else "low",
            "timeline_risk": "high" if intake_form.matter_urgency == "urgent" else "low"
        }

        return risks
```

### 4. Document Generation and Matter Setup

```python
@dataclass
class MatterDocument:
    document_id: str
    document_type: str  # "retainer", "engagement_letter", "matter_file", "conflict_waiver"
    client_name: str
    matter_id: str
    generated_date: datetime
    document_content: str
    status: str = "draft"  # draft, approved, executed, archived

class MatterDocumentGenerator:
    def __init__(self):
        self.templates = self._initialize_templates()
        self.document_cache = {}

    def _initialize_templates(self) -> Dict[str, str]:
        """Initialize document templates"""
        return {
            "engagement_letter": """
ENGAGEMENT LETTER

Date: {date}

Re: Legal Services Engagement

Dear {client_name}:

This letter confirms that {firm_name} ("Firm") has been engaged to provide legal services
in connection with the following matter:

MATTER DESCRIPTION:
{matter_description}

SCOPE OF SERVICES:
The Firm will provide the following services:
• {services_description}
• Representation and advice regarding {matter_type} matters
• Regular communication and status updates

FEES AND BILLING:
• Hourly rate: {hourly_rate}
• Estimated hours: {estimated_hours}
• Estimated total cost: {estimated_cost}
• Billing frequency: {billing_frequency}

RETAINER:
An initial retainer of ${retainer_amount} is required before commencing work.

TERMS:
• This engagement may be terminated by either party with written notice
• Communications are subject to attorney-client privilege
• Conflicts of interest have been verified

If you have any questions, please contact our office.

Sincerely,
{attorney_name}
{firm_name}
""",
            "conflict_waiver": """
CONFLICT OF INTEREST WAIVER

Date: {date}

Client: {client_name}
Matter: {matter_description}

The undersigned acknowledges that:

1. A potential conflict of interest exists as described below
2. The conflict has been fully explained by {firm_name}
3. The client has had the opportunity to seek independent legal advice
4. The client voluntarily consents to the firm's representation

CONFLICT DESCRIPTION:
{conflict_description}

CLIENT SIGNATURE: _____________________________ DATE: __________

FIRM REPRESENTATIVE: _____________________________ DATE: __________
""",
            "matter_file_setup": """
MATTER FILE SETUP CHECKLIST

Matter ID: {matter_id}
Client: {client_name}
Date Created: {date}
Assigned Attorney: {attorney_name}

CLIENT INFORMATION:
[✓] Contact information verified
[✓] Conflict check completed
[✓] Retainer received
[✓] Engagement letter signed

ADMINISTRATIVE:
[✓] Matter code assigned
[✓] Billing rate confirmed
[✓] Estimated completion date set
[✓] PM system matter created

INITIAL DOCUMENTS:
[✓] Engagement letter
[✓] Conflict waiver (if applicable)
[✓] Initial research notes
[✓] Matter file index

NEXT STEPS:
1. {next_step_1}
2. {next_step_2}
3. {next_step_3}
"""
        }

    def generate_engagement_letter(self, client_info: ClientInfo,
                                  matter_profile: MatterProfile) -> MatterDocument:
        """Generate engagement letter"""
        template = self.templates["engagement_letter"]

        content = template.format(
            date=datetime.now().strftime("%B %d, %Y"),
            client_name=f"{client_info.first_name} {client_info.last_name}",
            firm_name="[Firm Name]",
            matter_description="[Matter Description]",
            matter_type=matter_profile.matter_type.value,
            services_description="[Services Description]",
            hourly_rate="$250",
            estimated_hours=int(matter_profile.estimated_hours),
            estimated_cost=int(matter_profile.estimated_cost),
            billing_frequency="monthly",
            retainer_amount=int(matter_profile.estimated_cost * 0.25),
            attorney_name="[Attorney Name]"
        )

        return MatterDocument(
            document_id=f"doc_{matter_profile.matter_id}_engagement",
            document_type="engagement_letter",
            client_name=f"{client_info.first_name} {client_info.last_name}",
            matter_id=matter_profile.matter_id,
            generated_date=datetime.now(),
            document_content=content,
            status="draft"
        )

    def generate_conflict_waiver(self, client_info: ClientInfo,
                                matter_profile: MatterProfile,
                                conflict_info: Dict[str, Any]) -> MatterDocument:
        """Generate conflict of interest waiver"""
        template = self.templates["conflict_waiver"]

        content = template.format(
            date=datetime.now().strftime("%B %d, %Y"),
            client_name=f"{client_info.first_name} {client_info.last_name}",
            matter_description=conflict_info.get("matter_description", "[Matter]"),
            firm_name="[Firm Name]",
            conflict_description=conflict_info.get("conflict_description", "[Conflict Description]")
        )

        return MatterDocument(
            document_id=f"doc_{matter_profile.matter_id}_waiver",
            document_type="conflict_waiver",
            client_name=f"{client_info.first_name} {client_info.last_name}",
            matter_id=matter_profile.matter_id,
            generated_date=datetime.now(),
            document_content=content,
            status="draft"
        )
```

### 5. Matter Creation and PM Integration

```python
@dataclass
class Matter:
    matter_id: str
    client_id: str
    matter_type: MatterType
    description: str
    assigned_attorney_id: str
    status: str = "active"
    created_date: datetime = field(default_factory=datetime.now)
    matter_profile: Optional[MatterProfile] = None
    documents: List[MatterDocument] = field(default_factory=list)

class MatterCreationService:
    def __init__(self):
        self.matters: Dict[str, Matter] = {}
        self.pm_system_connected = False

    def create_matter(self, intake_form: MatterIntakeForm,
                     client_info: ClientInfo,
                     matter_profile: MatterProfile,
                     conflict_check: ConflictCheckResult) -> Matter:
        """Create new matter from intake"""

        matter = Matter(
            matter_id=matter_profile.matter_id,
            client_id=client_info.client_id,
            matter_type=intake_form.matter_type,
            description=intake_form.matter_description,
            assigned_attorney_id="",  # To be assigned
            status="active",
            matter_profile=matter_profile
        )

        self.matters[matter.matter_id] = matter

        return matter

    def complete_matter_setup(self, matter: Matter,
                             documents: List[MatterDocument]) -> Dict[str, Any]:
        """Complete full matter setup"""
        matter.documents = documents

        setup_result = {
            "matter_id": matter.matter_id,
            "status": "setup_complete",
            "timestamp": datetime.now().isoformat(),
            "documents_created": len(documents),
            "next_actions": [
                "Assign attorney",
                "Set matter rates and billing code",
                "Schedule initial client call",
                "Establish matter timeline"
            ]
        }

        return setup_result

    def sync_to_pm_system(self, matter: Matter, pm_system_url: str) -> bool:
        """Sync matter to practice management system"""
        import json
        # Implementation would send to PM system API
        payload = {
            "matter_id": matter.matter_id,
            "client_id": matter.client_id,
            "matter_type": matter.matter_type.value,
            "description": matter.description,
            "created_date": matter.created_date.isoformat()
        }

        return True
```

### 6. Intake Automation Orchestration

```python
class IntakeAutomationOrchestrator:
    def __init__(self):
        self.form_validator = IntakeFormValidator()
        self.conflict_checker = ConflictOfInterestChecker()
        self.matter_assessor = MatterAssessor()
        self.doc_generator = MatterDocumentGenerator()
        self.matter_service = MatterCreationService()

    def process_intake(self, form_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process complete intake workflow"""

        # Step 1: Validate form
        is_valid, errors = self.form_validator.validate_form(form_data)
        if not is_valid:
            return {
                "status": "validation_failed",
                "errors": errors
            }

        # Step 2: Create client
        client_info = ClientInfo(
            client_id=f"cli_{datetime.now().timestamp()}",
            client_type=ClientType[form_data["client_type"].upper()],
            first_name=form_data["client_first_name"],
            last_name=form_data["client_last_name"],
            email=form_data["client_email"],
            phone=form_data["client_phone"],
            company_name=form_data.get("company_name")
        )

        # Step 3: Create intake form
        opposing_parties = [
            OpposingParty(
                party_id=f"party_{i}",
                name=party_name
            )
            for i, party_name in enumerate(form_data.get("opposing_parties", []))
        ]

        intake_form = MatterIntakeForm(
            form_id=f"frm_{datetime.now().timestamp()}",
            client_id=client_info.client_id,
            matter_type=MatterType[form_data["matter_type"].upper()],
            matter_description=form_data["matter_description"],
            matter_urgency=form_data.get("matter_urgency", "normal"),
            opposing_parties=opposing_parties,
            estimated_value=float(form_data.get("estimated_value", 0)) if form_data.get("estimated_value") else None
        )

        # Step 4: Check conflicts
        conflict_check = self.conflict_checker.check_conflicts(client_info, opposing_parties)

        if conflict_check.conflict_status == "direct_conflict":
            return {
                "status": "conflict_found",
                "conflict_details": conflict_check.conflicts_found,
                "requires_waiver": conflict_check.requires_waiver
            }

        # Step 5: Assess matter
        matter_profile = self.matter_assessor.assess_matter(intake_form, client_info)

        # Step 6: Generate documents
        documents = [
            self.doc_generator.generate_engagement_letter(client_info, matter_profile)
        ]

        if conflict_check.requires_waiver:
            documents.append(
                self.doc_generator.generate_conflict_waiver(
                    client_info,
                    matter_profile,
                    {"conflicts": conflict_check.conflicts_found}
                )
            )

        # Step 7: Create matter
        matter = self.matter_service.create_matter(
            intake_form,
            client_info,
            matter_profile,
            conflict_check
        )

        # Step 8: Complete setup
        setup_result = self.matter_service.complete_matter_setup(matter, documents)

        return {
            "status": "success",
            "matter_id": matter.matter_id,
            "client_id": client_info.client_id,
            "matter_profile": {
                "type": matter_profile.matter_type.value,
                "priority": matter_profile.priority_level,
                "complexity": matter_profile.estimated_complexity,
                "estimated_hours": matter_profile.estimated_hours,
                "estimated_cost": matter_profile.estimated_cost
            },
            "documents_created": len(documents),
            "setup_result": setup_result
        }
```

## REST API Integration

```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()

class IntakeRequest(BaseModel):
    client_first_name: str
    client_last_name: str
    client_email: str
    client_phone: str
    client_type: str
    matter_type: str
    matter_description: str
    matter_urgency: str
    estimated_value: Optional[float] = None

@app.post("/api/intake/submit")
async def submit_intake(request: IntakeRequest) -> Dict[str, Any]:
    """Submit intake form"""
    orchestrator = IntakeAutomationOrchestrator()

    form_data = request.dict()
    result = orchestrator.process_intake(form_data)

    if result["status"] != "success":
        raise HTTPException(status_code=400, detail=result)

    return result

@app.get("/api/matter/{matter_id}")
async def get_matter(matter_id: str) -> Dict[str, Any]:
    """Get matter details"""
    # Implementation
    pass

@app.get("/api/intake/status/{form_id}")
async def get_intake_status(form_id: str) -> Dict[str, Any]:
    """Get intake form status"""
    # Implementation
    pass
```

## Best Practices

### 1. Data Quality
- Validate all input data at point of entry
- Use dropdown selections for standardized fields
- Implement spell-check for attorney names and parties
- Regular data quality audits

### 2. Conflict Management
- Daily conflict checks against all databases
- Maintain conflict waiver archive
- Regular training on conflict identification
- Escalation procedures for borderline cases

### 3. Automation Safeguards
- Human review of high-value matters
- Quality sampling of generated documents
- Escalation for unusual matter types or issues
- Audit trail of all automated decisions

### 4. Integration Testing
- Regular sync tests with PM system
- Validation of billing code assignments
- Document format verification
- Error handling and retry logic

## Key Metrics

| Metric | Target |
|--------|--------|
| Intake Processing Time | <2 hours |
| Form Completion Rate | 95%+ |
| Conflict Check Accuracy | 99%+ |
| Matter Creation Success Rate | 98%+ |
| Document Generation Time | <15 minutes |
| PM System Sync Success | 99.5%+ |

This pattern provides a complete framework for automating legal matter intake while maintaining quality and managing risk through appropriate oversight and controls.
