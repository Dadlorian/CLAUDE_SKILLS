# Lobbying Disclosure Compliance Guide

## Table of Contents
1. [Regulatory Overview](#regulatory-overview)
2. [Filing Requirements](#filing-requirements)
3. [Disclosure Architecture](#disclosure-architecture)
4. [Data Collection and Tracking](#data-collection-and-tracking)
5. [Calculation Methodologies](#calculation-methodologies)
6. [Filing Systems](#filing-systems)
7. [Compliance Workflows](#compliance-workflows)
8. [Audit and Monitoring](#audit-and-monitoring)
9. [Regulatory Relationships](#regulatory-relationships)
10. [Best Practices](#best-practices)

## Regulatory Overview

### Federal Lobbying Regulation Framework

Lobbying disclosure requirements are governed by:

1. **Lobbying Disclosure Act (LDA) of 1995**
   - Primary federal lobbying disclosure statute
   - Requires disclosure of lobbying activities and expenditures
   - Applies to organizations spending >$10,000 per quarter on lobbying

2. **Regulation of Lobbying Act**
   - Earlier statute (1946)
   - Still applies to certain activities
   - Has lower reporting thresholds

3. **Foreign Agent Registration Act (FARA)**
   - Requires registration for agents of foreign principals
   - Separate from LDA reporting
   - Stricter requirements and public disclosure

4. **State Lobbying Laws**
   - 50 states have lobbying disclosure requirements
   - Varying thresholds, filing frequencies, and data requirements
   - Often more stringent than federal requirements

### Key Regulatory Bodies

- **Federal Election Commission (FEC)**
- **House Clerk (H-2 offices)**
- **Senate (S-2 offices)**
- **Individual State Legislators and Secretaries of State**

```python
from enum import Enum
from dataclasses import dataclass
from typing import List, Dict, Optional
from datetime import datetime, date

class JurisdictionType(Enum):
    FEDERAL = "federal"
    STATE = "state"
    LOCAL = "local"

class DisclosureType(Enum):
    LOBBYING_ACTIVITY = "lobbying_activity"
    LOBBYING_EXPENDITURE = "lobbying_expenditure"
    FOREIGN_AGENT = "foreign_agent"
    POLITICAL_CONTRIBUTION = "political_contribution"
    GRASSROOTS = "grassroots"

@dataclass
class RegulatoryJurisdiction:
    """Defines lobbying regulations for a jurisdiction"""

    jurisdiction_id: str
    jurisdiction_type: JurisdictionType
    jurisdiction_name: str

    # Thresholds
    reporting_threshold_annual: float  # Annual spending threshold
    reporting_threshold_quarterly: float

    # Filing requirements
    filing_frequency: str  # 'quarterly', 'annual', 'semi-annual'
    filing_deadline_days: int  # Days after period end

    # Required disclosures
    requires_lobbyist_names: bool
    requires_compensation_details: bool
    requires_issue_codes: bool
    requires_issue_descriptions: bool
    requires_client_revenue: bool
    requires_grassroots_lobbying: bool

    # Specific details
    regulatory_authority: str
    filing_url: str
    contact_information: str

    created_at: datetime = None

class DisclosureRegulation:
    """Manages disclosure regulations across jurisdictions"""

    FEDERAL_JURISDICTION = RegulatoryJurisdiction(
        jurisdiction_id='US-FEDERAL',
        jurisdiction_type=JurisdictionType.FEDERAL,
        jurisdiction_name='United States Federal Government',
        reporting_threshold_annual=20000,  # $20k annually
        reporting_threshold_quarterly=5000,  # $5k quarterly
        filing_frequency='quarterly',
        filing_deadline_days=45,
        requires_lobbyist_names=True,
        requires_compensation_details=True,
        requires_issue_codes=True,
        requires_issue_descriptions=True,
        requires_client_revenue=False,
        requires_grassroots_lobbying=True,
        regulatory_authority='Senate Office of Public Records',
        filing_url='https://lda.senate.gov',
        contact_information='lda@senate.gov'
    )

    def __init__(self):
        self.jurisdictions = {
            'US-FEDERAL': self.FEDERAL_JURISDICTION
        }
        self._load_state_jurisdictions()

    def _load_state_jurisdictions(self):
        """Load state lobbying regulations"""
        # California example
        self.jurisdictions['CA'] = RegulatoryJurisdiction(
            jurisdiction_id='CA-STATE',
            jurisdiction_type=JurisdictionType.STATE,
            jurisdiction_name='State of California',
            reporting_threshold_annual=5000,
            reporting_threshold_quarterly=2500,
            filing_frequency='quarterly',
            filing_deadline_days=30,
            requires_lobbyist_names=True,
            requires_compensation_details=True,
            requires_issue_codes=True,
            requires_issue_descriptions=True,
            requires_client_revenue=True,
            requires_grassroots_lobbying=True,
            regulatory_authority='California Secretary of State',
            filing_url='https://calaccess.legislature.ca.gov',
            contact_information='calaccess@legislature.ca.gov'
        )

        # Texas example
        self.jurisdictions['TX'] = RegulatoryJurisdiction(
            jurisdiction_id='TX-STATE',
            jurisdiction_type=JurisdictionType.STATE,
            jurisdiction_name='State of Texas',
            reporting_threshold_annual=0,  # No threshold
            reporting_threshold_quarterly=0,
            filing_frequency='semi-annual',
            filing_deadline_days=20,
            requires_lobbyist_names=True,
            requires_compensation_details=False,
            requires_issue_codes=False,
            requires_issue_descriptions=True,
            requires_client_revenue=False,
            requires_grassroots_lobbying=False,
            regulatory_authority='Texas Ethics Commission',
            filing_url='https://www.ethics.state.tx.us',
            contact_information='www.ethics.state.tx.us'
        )

    def get_applicable_jurisdictions(self, organization: Dict) -> List[RegulatoryJurisdiction]:
        """Determine which jurisdictions require filing"""
        applicable = []

        # Check federal
        applicable.append(self.jurisdictions['US-FEDERAL'])

        # Check states where organization operates
        for state in organization.get('operating_states', []):
            if state in self.jurisdictions:
                applicable.append(self.jurisdictions[state])

        return applicable
```

## Filing Requirements

### Federal Form Components

```python
from enum import Enum

class LDAFormType(Enum):
    FORM_20_INITIAL = "20"
    FORM_21_FIRST_AMENDMENT = "21"
    FORM_25_TERMINATION = "25"

@dataclass
class LobbiedIssue:
    """Represents a specific issue area lobbied on"""

    issue_code: str  # Reference federal issue codes
    issue_description: str
    amount_spent: float
    specific_issues: List[str]

@dataclass
class LobbyistInformation:
    """Information about a registered lobbyist"""

    lobbyist_id: str
    first_name: str
    last_name: str
    middle_initial: Optional[str]
    suffix: Optional[str]
    address: str
    phone: str
    email: str
    employed_since_date: date

    # Affiliations
    is_self_employed: bool
    employer: Optional[str]
    congressional_representatives: List[str]

@dataclass
class ClientInformation:
    """Client lobbied on behalf of"""

    client_id: str
    client_name: str
    state: str
    zip_code: str
    client_business: str

    # Relationship details
    start_date: date
    end_date: Optional[date]
    is_foreign_entity: bool
    foreign_principal: Optional[str]

@dataclass
class LDAForm:
    """Federal LDA Lobbying Disclosure Form"""

    form_id: str
    form_type: LDAFormType
    reporting_organization: str
    reporting_period: str  # "Q1-2024"

    # Organization details
    organization_name: str
    organization_address: str
    organization_phone: str
    organization_contact: str

    # Registrant (representative)
    registrant_organization: str
    registrant_contact: str
    registrant_title: str

    # Financial details
    total_lobbying_expenditures: float
    in_house_lobbying_expenditures: float
    client_reimbursement: float

    # Issue areas
    lobbied_issues: List[LobbiedIssue]

    # Personnel
    in_house_lobbyists: List[LobbyistInformation]
    outside_lobbyists: List[LobbyistInformation]

    # Government officials contacted
    contacted_entities: List[str]  # House, Senate, Executive, etc.

    # Supporting attachments
    attachments: List[str]

    # Filing information
    filed_date: Optional[datetime]
    filing_status: str  # 'draft', 'submitted', 'acknowledged'
    filer_id: Optional[str]
    amendment_indicator: bool

    created_at: datetime
    last_modified: datetime

class FederalLDAGenerator:
    """Generates federal LDA forms"""

    def __init__(self, db_connection):
        self.db = db_connection
        self.issue_codes = self._load_federal_issue_codes()

    def create_lda_form(self, reporting_data: Dict) -> LDAForm:
        """Create LDA form from reporting data"""

        form = LDAForm(
            form_id=f"LDA-{reporting_data['organization_id']}-Q{reporting_data['quarter']}-{reporting_data['year']}",
            form_type=LDAFormType.FORM_20_INITIAL,
            reporting_organization=reporting_data['organization_id'],
            reporting_period=f"Q{reporting_data['quarter']}-{reporting_data['year']}",
            organization_name=reporting_data['organization_name'],
            organization_address=reporting_data['organization_address'],
            organization_phone=reporting_data['organization_phone'],
            organization_contact=reporting_data['primary_contact'],
            registrant_organization=reporting_data.get('registrant_org', ''),
            registrant_contact=reporting_data.get('registrant_contact', ''),
            registrant_title=reporting_data.get('registrant_title', ''),
            total_lobbying_expenditures=self._calculate_total_expenditures(reporting_data),
            in_house_lobbying_expenditures=self._calculate_inhouse_expenditures(reporting_data),
            client_reimbursement=self._calculate_client_reimbursement(reporting_data),
            lobbied_issues=self._extract_lobbied_issues(reporting_data),
            in_house_lobbyists=self._extract_inhouse_lobbyists(reporting_data),
            outside_lobbyists=self._extract_outside_lobbyists(reporting_data),
            contacted_entities=['U.S. House of Representatives', 'U.S. Senate'],
            attachments=self._prepare_attachments(reporting_data),
            filed_date=None,
            filing_status='draft',
            filer_id=None,
            amendment_indicator=False,
            created_at=datetime.now(),
            last_modified=datetime.now()
        )

        return form

    def _load_federal_issue_codes(self) -> Dict[str, str]:
        """Load federal lobbying issue codes"""
        return {
            'AAA': 'Agriculture',
            'ACD': 'Anti-crime/Drug Control',
            'APP': 'Appropriations',
            'ART': 'Arts & Humanities',
            'AUT': 'Automotive',
            'BAN': 'Banking',
            'BUD': 'Budget & Appropriations',
            'CHM': 'Chemistry',
            'COM': 'Communications',
            'CPI': 'Campaign Finance/Political/Individual Rights',
            'CSP': 'Consumer Protection',
            'DOC': 'Domestic Commerce',
            'ECN': 'Economics',
            'EDU': 'Education',
            'ENG': 'Energy',
            'ENV': 'Environmental/Superfund',
            'FAM': 'Family Issues',
            'FIN': 'Financial Institutions',
            'FIR': 'Firearms/Ammunition',
            'FIT': 'Fitness/Sports',
            'FOR': 'Foreign Trade',
            'FUE': 'Fuel/Gas/Oil',
            'GOV': 'Government Issues',
            'GUN': 'Gun Control/Firearms',
            'HAW': 'Hawaiian Issues',
            'HEA': 'Health/Health Care',
            'HOU': 'Housing',
            'IMM': 'Immigration',
            'IND': 'Indian/Native American Issues',
            'INT': 'Intelligence/National Security',
            'INV': 'Investment',
            'JUD': 'Judicial/Legal/Courts',
            'LAB': 'Labor',
            'LAW': 'Law Enforcement/Crime',
            'LBY': 'Lobbying Regulation',
            'LEG': 'Legislative',
            'LIC': 'Licensing',
            'MAN': 'Manufacturing',
            'MAR': 'Maritime',
            'MED': 'Medical Devices',
            'MEN': 'Mental Health',
            'MIA': 'Miscellaneous',
            'MIN': 'Mining',
            'MON': 'Money/Banking',
            'NTU': 'Native American Tribal Issues',
            'OCC': 'Occupational Safety',
            'OFF': 'Offshore',
            'OIL': 'Oil & Gas',
            'PAT': 'Patents/Copyrights',
            'PHA': 'Pharmaceutical',
            'PHO': 'Photography',
            'PUB': 'Public Utilities',
            'REL': 'Religious Issues',
            'RES': 'Research & Development',
            'REV': 'Revenue/Internal Revenue Code',
            'SCI': 'Science/Technology',
            'SEC': 'Securities',
            'SOC': 'Social Issues',
            'TAX': 'Taxation',
            'TEL': 'Telecommunications',
            'TOB': 'Tobacco',
            'TOP': 'Tort Reform/Product Liability',
            'TRA': 'Transportation',
            'TRD': 'Trade/WTO',
            'TUR': 'Tourism',
            'UNE': 'Unemployment',
            'URB': 'Urban Development',
            'UTE': 'Utilities',
            'VET': 'Veterans',
            'WAS': 'Waste (Hazardous/Solid)',
            'WTE': 'Water',
            'WTO': 'WTO/GATT'
        }

    def _calculate_total_expenditures(self, data: Dict) -> float:
        """Calculate total lobbying expenditures"""
        return (
            self._calculate_inhouse_expenditures(data) +
            self._calculate_client_reimbursement(data)
        )

    def _calculate_inhouse_expenditures(self, data: Dict) -> float:
        """Calculate in-house lobbying expenditures"""
        total = 0

        for lobbyist in data.get('in_house_lobbyists', []):
            total += lobbyist.get('time_spent_hours', 0) * 200  # Assumption: $200/hour

        # Add other in-house costs
        total += data.get('in_house_other_costs', 0)

        return total

    def _calculate_client_reimbursement(self, data: Dict) -> float:
        """Calculate client reimbursements for lobbying"""
        total = 0

        for client in data.get('clients', []):
            total += client.get('reimbursement_amount', 0)

        return total

    def _extract_lobbied_issues(self, data: Dict) -> List[LobbiedIssue]:
        """Extract lobbied issue areas"""
        issues = []

        for issue in data.get('lobbied_issues', []):
            lobbied_issue = LobbiedIssue(
                issue_code=issue.get('code', 'MIA'),
                issue_description=issue.get('description', ''),
                amount_spent=issue.get('amount_spent', 0),
                specific_issues=issue.get('specific_issues', [])
            )
            issues.append(lobbied_issue)

        return issues
```

## Disclosure Architecture

### Multi-Jurisdiction Tracking System

```python
from typing import List, Dict

class LobbiedActivitiesTracker:
    """Tracks lobbying activities across jurisdictions"""

    def __init__(self, db_connection):
        self.db = db_connection
        self.jurisdictions = {}

    def log_lobbying_activity(self, activity: Dict) -> str:
        """Log a lobbying activity for tracking"""

        activity_record = {
            'activity_id': self._generate_activity_id(),
            'activity_date': activity.get('date', datetime.now()),
            'activity_type': activity.get('type'),  # 'meeting', 'phone_call', 'email', etc.
            'lobbyist': activity.get('lobbyist_name'),
            'client': activity.get('client_name'),
            'contacted_official': activity.get('official_name'),
            'contacted_entity': activity.get('entity'),  # House, Senate, agency, etc.
            'issue_codes': activity.get('issue_codes', []),
            'issue_description': activity.get('issue_description', ''),
            'location': activity.get('location', ''),
            'duration_minutes': activity.get('duration_minutes'),
            'participants': activity.get('participants', []),
            'expected_cost': activity.get('expected_cost', 0),
            'actual_cost': activity.get('actual_cost'),
            'notes': activity.get('notes', ''),
            'jurisdictions_affected': activity.get('jurisdictions', ['US-FEDERAL']),
            'created_at': datetime.now(),
            'reporting_periods': self._identify_reporting_periods(
                activity.get('date', datetime.now())
            )
        }

        self.db.insert_lobbying_activity(activity_record)
        return activity_record['activity_id']

    def get_activities_for_reporting_period(self, client_id: str,
                                           period: str) -> List[Dict]:
        """Get all lobbying activities for a specific reporting period"""

        activities = self.db.query("""
            SELECT * FROM lobbying_activities
            WHERE client_id = %s
            AND %s = ANY(reporting_periods)
            ORDER BY activity_date DESC
        """, [client_id, period])

        return activities

    def _generate_activity_id(self) -> str:
        """Generate unique activity ID"""
        import uuid
        return f"ACT-{uuid.uuid4().hex[:12].upper()}"

    def _identify_reporting_periods(self, activity_date: datetime) -> List[str]:
        """Identify which reporting periods include this activity"""
        periods = []

        # Federal quarters
        quarter = (activity_date.month - 1) // 3 + 1
        year = activity_date.year
        periods.append(f"Q{quarter}-{year}")

        return periods

class ExpenditureCalculator:
    """Calculates lobbying expenditures for disclosure"""

    def __init__(self):
        self.allocation_methods = {
            'direct': self._allocate_direct_cost,
            'pro_rata': self._allocate_pro_rata,
            'activity_based': self._allocate_activity_based,
            'time_based': self._allocate_time_based
        }

    def calculate_period_expenditures(self, activities: List[Dict],
                                     allocation_method: str = 'activity_based') -> float:
        """Calculate total expenditures for a reporting period"""

        total_expenditures = 0

        for activity in activities:
            if 'actual_cost' in activity and activity['actual_cost']:
                total_expenditures += activity['actual_cost']
            elif 'expected_cost' in activity and activity['expected_cost']:
                total_expenditures += activity['expected_cost']
            else:
                # Estimate cost based on activity type
                total_expenditures += self._estimate_activity_cost(activity)

        return round(total_expenditures, 2)

    def calculate_client_specific_expenditures(self, client_id: str,
                                              period: str,
                                              activities: List[Dict]) -> Dict:
        """Calculate expenditures allocable to specific client"""

        client_activities = [
            a for a in activities if a.get('client') == client_id
        ]

        # Calculate based on lobbyist time
        lobbyist_allocations = {}

        for activity in client_activities:
            lobbyist = activity.get('lobbyist')
            duration = activity.get('duration_minutes', 30)
            cost = activity.get('actual_cost', self._estimate_activity_cost(activity))

            if lobbyist not in lobbyist_allocations:
                lobbyist_allocations[lobbyist] = {
                    'time_minutes': 0,
                    'cost': 0
                }

            lobbyist_allocations[lobbyist]['time_minutes'] += duration
            lobbyist_allocations[lobbyist]['cost'] += cost

        return {
            'client_id': client_id,
            'reporting_period': period,
            'total_cost': sum(
                alloc['cost'] for alloc in lobbyist_allocations.values()
            ),
            'lobbyist_allocation': lobbyist_allocations
        }

    def _estimate_activity_cost(self, activity: Dict) -> float:
        """Estimate cost of activity if not provided"""

        activity_type = activity.get('activity_type', 'meeting')

        # Standard cost estimates
        cost_estimates = {
            'meeting': 500,
            'phone_call': 100,
            'email': 50,
            'event': 2000,
            'research': 300
        }

        base_cost = cost_estimates.get(activity_type, 200)

        # Adjust for duration
        duration_minutes = activity.get('duration_minutes', 30)
        duration_factor = max(1, duration_minutes / 30)

        return base_cost * duration_factor

    def _allocate_direct_cost(self, activity: Dict) -> float:
        """Direct cost allocation"""
        return activity.get('actual_cost', 0)

    def _allocate_pro_rata(self, activity: Dict, total_clients: int) -> float:
        """Pro-rata allocation across clients"""
        cost = activity.get('actual_cost', 0)
        return cost / total_clients if total_clients > 0 else 0

    def _allocate_activity_based(self, activity: Dict, activities: List[Dict]) -> float:
        """Allocate based on activity count"""
        cost = activity.get('actual_cost', 0)
        total_activities = len(activities)
        return cost / total_activities if total_activities > 0 else 0

    def _allocate_time_based(self, activity: Dict, total_time: int) -> float:
        """Allocate based on time spent"""
        cost = activity.get('actual_cost', 0)
        activity_time = activity.get('duration_minutes', 30)
        return (activity_time / total_time * cost) if total_time > 0 else 0
```

## Data Collection and Tracking

### Activity Logging System

```python
class LobbyingActivityLogger:
    """Comprehensive system for logging lobbying activities"""

    def __init__(self, db_connection):
        self.db = db_connection
        self.validators = ActivityValidator()

    def create_activity_log_entry(self, activity_data: Dict) -> str:
        """Create a new activity log entry"""

        # Validate input data
        validation_result = self.validators.validate_activity(activity_data)

        if not validation_result['valid']:
            raise ValueError(f"Invalid activity data: {validation_result['errors']}")

        # Normalize activity data
        normalized = self._normalize_activity_data(activity_data)

        # Generate entry
        entry = {
            'activity_id': self._generate_id(),
            'date_logged': datetime.now(),
            **normalized,
            'source': 'manual_entry',
            'verified': False,
            'verification_date': None
        }

        self.db.insert_activity(entry)
        return entry['activity_id']

    def bulk_import_activities(self, activities: List[Dict]) -> Dict:
        """Bulk import activities from various sources"""

        import_results = {
            'total_imported': 0,
            'successful': 0,
            'failed': 0,
            'errors': []
        }

        for activity in activities:
            try:
                activity_id = self.create_activity_log_entry(activity)
                import_results['successful'] += 1
            except Exception as e:
                import_results['failed'] += 1
                import_results['errors'].append({
                    'activity': activity,
                    'error': str(e)
                })

            import_results['total_imported'] += 1

        return import_results

    def _normalize_activity_data(self, activity_data: Dict) -> Dict:
        """Normalize activity data for consistent storage"""

        return {
            'activity_date': activity_data.get('date', datetime.now()),
            'activity_type': activity_data.get('type', 'meeting').lower(),
            'lobbyist_name': activity_data.get('lobbyist_name', '').strip(),
            'client_name': activity_data.get('client_name', '').strip(),
            'contacted_entity': activity_data.get('contacted_entity', '').upper(),
            'contacted_official': activity_data.get('official_name', '').strip(),
            'issue_codes': [c.upper() for c in activity_data.get('issue_codes', [])],
            'issue_description': activity_data.get('issue_description', '').strip(),
            'duration_minutes': int(activity_data.get('duration_minutes', 30)),
            'cost': float(activity_data.get('cost', 0)),
            'notes': activity_data.get('notes', '').strip()
        }

    def _generate_id(self) -> str:
        import uuid
        return f"LOG-{datetime.now().strftime('%Y%m%d')}-{uuid.uuid4().hex[:8].upper()}"

class ActivityValidator:
    """Validates lobbying activity data"""

    def validate_activity(self, activity: Dict) -> Dict:
        """Validate activity data for completeness and accuracy"""

        errors = []

        # Check required fields
        required_fields = ['date', 'type', 'lobbyist_name', 'client_name']

        for field in required_fields:
            if field not in activity or not activity[field]:
                errors.append(f"Missing required field: {field}")

        # Validate date
        if 'date' in activity:
            try:
                activity_date = activity['date']
                if isinstance(activity_date, str):
                    datetime.fromisoformat(activity_date)
            except ValueError:
                errors.append("Invalid date format")

        # Validate activity type
        valid_types = ['meeting', 'phone_call', 'email', 'event', 'research']
        if activity.get('type', '').lower() not in valid_types:
            errors.append(f"Invalid activity type: {activity.get('type')}")

        # Validate cost if provided
        if 'cost' in activity:
            try:
                float(activity['cost'])
            except ValueError:
                errors.append("Cost must be numeric")

        return {
            'valid': len(errors) == 0,
            'errors': errors
        }
```

## Calculation Methodologies

### Expenditure Reporting Methods

```python
class ExpenditureReportingMethods:
    """Different methods for calculating and reporting expenditures"""

    @staticmethod
    def calculate_threshold_expenditures(quarterly_data: List[float]) -> Dict:
        """Calculate quarterly and annual thresholds"""

        return {
            'q1': quarterly_data[0] if len(quarterly_data) > 0 else 0,
            'q2': quarterly_data[1] if len(quarterly_data) > 1 else 0,
            'q3': quarterly_data[2] if len(quarterly_data) > 2 else 0,
            'q4': quarterly_data[3] if len(quarterly_data) > 3 else 0,
            'annual_total': sum(quarterly_data),
            'above_threshold': sum(quarterly_data) > 10000
        }

    @staticmethod
    def estimate_salary_allocable_portion(salary: float, hours_lobbying: float,
                                         total_hours: float) -> float:
        """Calculate allocable portion of salary for lobbying"""

        if total_hours == 0:
            return 0

        hourly_rate = salary / 2080  # 2080 working hours per year
        allocable_amount = hourly_rate * hours_lobbying

        return allocable_amount

    @staticmethod
    def calculate_outside_firm_costs(base_retainer: float,
                                    hours_spent: float,
                                    hourly_rate: float,
                                    expenses: float) -> float:
        """Calculate costs for outside lobbying firms"""

        actual_services = hours_spent * hourly_rate
        total_cost = base_retainer + actual_services + expenses

        return total_cost

    @staticmethod
    def allocate_mixed_purpose_costs(total_cost: float,
                                    lobbying_percentage: float) -> float:
        """Calculate allocable cost for mixed-purpose activities"""

        return total_cost * (lobbying_percentage / 100)
```

## Filing Systems

### Multi-Jurisdiction Form Generator

```python
class MultiJurisdictionFormGenerator:
    """Generates disclosure forms for multiple jurisdictions"""

    def __init__(self, db_connection):
        self.db = db_connection
        self.regulations = DisclosureRegulation()

    def prepare_filings(self, organization_id: str,
                       reporting_period: str) -> Dict[str, object]:
        """Prepare filings for all applicable jurisdictions"""

        org_data = self.db.query_organization(organization_id)
        jurisdictions = self.regulations.get_applicable_jurisdictions(org_data)

        filings = {}

        for jurisdiction in jurisdictions:
            if jurisdiction.jurisdiction_type == JurisdictionType.FEDERAL:
                form = self._generate_federal_form(
                    organization_id,
                    reporting_period,
                    jurisdiction
                )
                filings['US-FEDERAL'] = form

            elif jurisdiction.jurisdiction_type == JurisdictionType.STATE:
                form = self._generate_state_form(
                    organization_id,
                    reporting_period,
                    jurisdiction
                )
                filings[jurisdiction.jurisdiction_id] = form

        return filings

    def _generate_federal_form(self, org_id: str, period: str,
                              jurisdiction: RegulatoryJurisdiction) -> LDAForm:
        """Generate federal LDA form"""

        reporting_data = self._compile_reporting_data(org_id, period)
        generator = FederalLDAGenerator(self.db)

        return generator.create_lda_form(reporting_data)

    def _generate_state_form(self, org_id: str, period: str,
                            jurisdiction: RegulatoryJurisdiction) -> Dict:
        """Generate state-specific disclosure form"""

        reporting_data = self._compile_reporting_data(org_id, period)

        state_form = {
            'form_type': f"STATE-LOBBYING-{jurisdiction.jurisdiction_id}",
            'jurisdiction': jurisdiction.jurisdiction_name,
            'reporting_period': period,
            'organization': reporting_data['organization_name'],
            'required_fields': {
                'lobbyist_names': jurisdiction.requires_lobbyist_names,
                'compensation': jurisdiction.requires_compensation_details,
                'issue_codes': jurisdiction.requires_issue_codes,
                'issue_descriptions': jurisdiction.requires_issue_descriptions,
                'client_revenue': jurisdiction.requires_client_revenue,
                'grassroots': jurisdiction.requires_grassroots_lobbying
            },
            'filing_deadline': self._calculate_deadline(period, jurisdiction),
            'data': reporting_data
        }

        return state_form

    def _compile_reporting_data(self, org_id: str, period: str) -> Dict:
        """Compile all reporting data for a period"""

        activities = self.db.query_activities(org_id, period)
        clients = self.db.query_clients(org_id)
        lobbyists = self.db.query_lobbyists(org_id)

        expenditure_calculator = ExpenditureCalculator()

        return {
            'organization_id': org_id,
            'organization_name': self.db.query_organization(org_id)['name'],
            'reporting_period': period,
            'activities': activities,
            'clients': clients,
            'lobbyists': lobbyists,
            'total_expenditures': expenditure_calculator.calculate_period_expenditures(
                activities
            ),
            'in_house_expenditures': self._calculate_inhouse(activities, lobbyists),
            'client_reimbursements': self._calculate_reimbursements(activities)
        }

    def _calculate_deadline(self, period: str,
                           jurisdiction: RegulatoryJurisdiction) -> date:
        """Calculate filing deadline for jurisdiction"""

        # Parse period (Q1-2024 format)
        parts = period.split('-')
        quarter = int(parts[0][1])
        year = int(parts[1])

        # Last day of quarter
        quarter_end_months = [3, 6, 9, 12]
        month = quarter_end_months[quarter - 1]
        last_day = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31][month - 1]

        period_end = date(year, month, last_day)

        # Add deadline days
        deadline = period_end + timedelta(days=jurisdiction.filing_deadline_days)

        return deadline
```

## Compliance Workflows

### Filing Workflow Orchestration

```python
class ComplianceFilingWorkflow:
    """Orchestrates the complete filing compliance workflow"""

    def __init__(self, db_connection, form_generator, filing_service):
        self.db = db_connection
        self.form_generator = form_generator
        self.filing_service = filing_service
        self.regulations = DisclosureRegulation()

    def initiate_filing_cycle(self, organization_id: str, period: str) -> str:
        """Initiate new filing cycle"""

        cycle_id = f"FC-{organization_id}-{period}"

        cycle_record = {
            'cycle_id': cycle_id,
            'organization_id': organization_id,
            'reporting_period': period,
            'status': 'initiated',
            'initiated_date': datetime.now(),
            'activities_deadline': self._calculate_activity_deadline(period),
            'filing_deadline': self._calculate_filing_deadline(period),
            'stages': {}
        }

        self.db.insert_filing_cycle(cycle_record)
        return cycle_id

    def execute_filing_workflow(self, cycle_id: str) -> Dict:
        """Execute complete filing workflow"""

        cycle = self.db.query_filing_cycle(cycle_id)

        workflow_results = {
            'cycle_id': cycle_id,
            'stages': {}
        }

        # Stage 1: Data Verification
        stage1_result = self._verify_activity_data(cycle)
        workflow_results['stages']['data_verification'] = stage1_result

        if not stage1_result['success']:
            return workflow_results

        # Stage 2: Form Generation
        stage2_result = self._generate_forms(cycle)
        workflow_results['stages']['form_generation'] = stage2_result

        # Stage 3: Internal Review
        stage3_result = self._conduct_review(cycle)
        workflow_results['stages']['internal_review'] = stage3_result

        # Stage 4: File with authorities
        if stage3_result['approved']:
            stage4_result = self._file_with_authorities(cycle)
            workflow_results['stages']['filing'] = stage4_result

        return workflow_results

    def _verify_activity_data(self, cycle: Dict) -> Dict:
        """Verify all activity data is complete and accurate"""

        org_id = cycle['organization_id']
        period = cycle['reporting_period']

        activities = self.db.query_activities(org_id, period)
        validator = ActivityValidator()

        verification_results = {
            'success': True,
            'total_activities': len(activities),
            'valid_activities': 0,
            'invalid_activities': 0,
            'issues': []
        }

        for activity in activities:
            result = validator.validate_activity(activity)

            if result['valid']:
                verification_results['valid_activities'] += 1
            else:
                verification_results['invalid_activities'] += 1
                verification_results['issues'].extend(result['errors'])
                verification_results['success'] = False

        return verification_results

    def _generate_forms(self, cycle: Dict) -> Dict:
        """Generate disclosure forms for all jurisdictions"""

        org_id = cycle['organization_id']
        period = cycle['reporting_period']

        forms = self.form_generator.prepare_filings(org_id, period)

        return {
            'forms_generated': len(forms),
            'jurisdictions': list(forms.keys()),
            'forms': forms,
            'generation_date': datetime.now()
        }

    def _conduct_review(self, cycle: Dict) -> Dict:
        """Conduct internal compliance review"""

        return {
            'approved': True,
            'reviewed_by': 'Compliance Officer',
            'review_date': datetime.now(),
            'notes': 'All requirements met'
        }

    def _file_with_authorities(self, cycle: Dict) -> Dict:
        """Submit filings to regulatory authorities"""

        org_id = cycle['organization_id']
        period = cycle['reporting_period']
        forms = cycle.get('forms', {})

        filing_results = {
            'submissions': [],
            'filing_date': datetime.now()
        }

        for jurisdiction, form in forms.items():
            submission_result = self.filing_service.submit_form(
                jurisdiction=jurisdiction,
                form=form,
                organization_id=org_id,
                period=period
            )

            filing_results['submissions'].append(submission_result)

        return filing_results
```

## Audit and Monitoring

### Compliance Audit System

```python
class ComplianceAuditSystem:
    """Conducts audits of lobbying disclosure compliance"""

    def __init__(self, db_connection):
        self.db = db_connection

    def conduct_comprehensive_audit(self, organization_id: str) -> Dict:
        """Conduct comprehensive compliance audit"""

        audit_report = {
            'audit_id': f"AUD-{organization_id}-{datetime.now().strftime('%Y%m%d')}",
            'organization_id': organization_id,
            'audit_date': datetime.now(),
            'audit_sections': {}
        }

        # Check federal compliance
        audit_report['audit_sections']['federal'] = self._audit_federal_compliance(organization_id)

        # Check state compliance
        audit_report['audit_sections']['state'] = self._audit_state_compliance(organization_id)

        # Check documentation
        audit_report['audit_sections']['documentation'] = self._audit_documentation(organization_id)

        # Check for missing filings
        audit_report['audit_sections']['filings'] = self._audit_filings(organization_id)

        # Generate findings
        audit_report['findings'] = self._compile_findings(audit_report)
        audit_report['overall_status'] = self._determine_status(audit_report)

        self.db.insert_audit_report(audit_report)
        return audit_report

    def _audit_federal_compliance(self, org_id: str) -> Dict:
        """Audit federal lobbying compliance"""

        org_data = self.db.query_organization(org_id)
        filings = self.db.query_federal_filings(org_id)

        compliance_checks = {
            'threshold_compliance': [],
            'filing_timeliness': [],
            'disclosure_completeness': [],
            'issues_found': []
        }

        for filing in filings:
            # Check if above threshold
            if filing['total_expenditures'] > 5000:  # Quarterly threshold
                compliance_checks['threshold_compliance'].append({
                    'period': filing['period'],
                    'above_threshold': True,
                    'amount': filing['total_expenditures']
                })

            # Check filing timeliness
            days_late = (filing['filed_date'] - filing['deadline']).days
            if days_late > 0:
                compliance_checks['filing_timeliness'].append({
                    'period': filing['period'],
                    'days_late': days_late
                })
                compliance_checks['issues_found'].append(
                    f"Filing {filing['period']} was {days_late} days late"
                )

        return compliance_checks

    def _audit_state_compliance(self, org_id: str) -> Dict:
        """Audit state lobbying compliance"""

        regulations = DisclosureRegulation()
        org_data = self.db.query_organization(org_id)
        states = org_data.get('operating_states', [])

        state_compliance = {}

        for state in states:
            if state in regulations.jurisdictions:
                state_reg = regulations.jurisdictions[state]
                filings = self.db.query_state_filings(org_id, state)

                state_compliance[state] = {
                    'jurisdiction': state_reg.jurisdiction_name,
                    'filing_frequency': state_reg.filing_frequency,
                    'expected_filings': self._calculate_expected_filings(state_reg),
                    'actual_filings': len(filings),
                    'missing_filings': max(
                        0,
                        self._calculate_expected_filings(state_reg) - len(filings)
                    )
                }

        return state_compliance

    def _audit_documentation(self, org_id: str) -> Dict:
        """Audit supporting documentation"""

        documentation_audit = {
            'activity_logs': self.db.count_activity_logs(org_id),
            'supporting_documents': self.db.count_supporting_docs(org_id),
            'approval_records': self.db.count_approvals(org_id),
            'compliance_certs': self.db.count_compliance_certifications(org_id),
            'completeness_score': 0.0
        }

        # Calculate completeness
        total_possible = 100
        score = 0

        if documentation_audit['activity_logs'] > 0:
            score += 25
        if documentation_audit['supporting_documents'] > 0:
            score += 25
        if documentation_audit['approval_records'] > 0:
            score += 25
        if documentation_audit['compliance_certs'] > 0:
            score += 25

        documentation_audit['completeness_score'] = score

        return documentation_audit
```

## Best Practices

### Excellence in Lobbying Disclosure

1. **Proactive Documentation**
   - Document all lobbying activities contemporaneously
   - Maintain detailed activity logs
   - Keep supporting materials for all filings
   - Establish data retention policies (minimum 3 years)

2. **Clear Allocation Methods**
   - Establish consistent cost allocation methodology
   - Document methodology in writing
   - Apply consistently across periods
   - Track time spent on each client/issue

3. **Robust Internal Controls**
   - Implement approval workflows
   - Require supervisory review of filings
   - Conduct regular self-audits
   - Maintain audit trails

4. **Timely Communication**
   - Notify team of disclosure requirements
   - Provide clear reporting procedures
   - Set internal deadlines before regulatory deadlines
   - Train staff on compliance

5. **Accurate Reporting**
   - Use consistent cost estimation methods
   - Round numbers consistently
   - Document assumptions
   - Provide complete disclosures

6. **Regulatory Relationships**
   - Monitor regulatory changes
   - Maintain relationships with filing authorities
   - Seek guidance on ambiguous items
   - Keep up with rule changes

## Conclusion

Lobbying disclosure compliance requires systematic data collection, accurate calculation of expenditures, and timely filing across multiple jurisdictions with varying requirements. Organizations that implement comprehensive tracking systems, clear allocation methodologies, and robust internal controls significantly reduce compliance risk and demonstrate good faith compliance efforts.
