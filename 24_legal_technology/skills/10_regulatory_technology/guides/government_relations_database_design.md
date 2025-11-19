# Government Relations Database Design Guide

## Table of Contents
1. [Overview](#overview)
2. [Database Architecture](#database-architecture)
3. [Core Entity Models](#core-entity-models)
4. [Schema Design](#schema-design)
5. [Relationship Management](#relationship-management)
6. [Query Optimization](#query-optimization)
7. [Data Warehouse](#data-warehouse)
8. [Security and Access Control](#security-and-access-control)
9. [Implementation Workflow](#implementation-workflow)
10. [Best Practices](#best-practices)

## Overview

A government relations database serves as the central repository for all information related to legislative tracking, regulatory compliance, lobbying disclosure, and stakeholder management. This guide provides a comprehensive approach to designing and implementing such systems.

### Key Objectives
- Centralize government relations data across the organization
- Enable rapid access to legislative and regulatory information
- Support compliance reporting and auditing
- Provide analytics and business intelligence
- Maintain data integrity and security
- Scale to enterprise volumes

### Success Metrics
- Query response time: <500ms for standard queries
- System uptime: 99.5%+
- Data accuracy: 99%+
- User adoption: 80%+
- Compliance audit pass rate: 100%

## Database Architecture

### Three-Tier Architecture

```
┌───────────────────────────────────────────────────────┐
│          Presentation Layer                           │
│  (Web UI, APIs, Reports, Dashboards)                 │
├───────────────────────────────────────────────────────┤
│          Application Layer                            │
│  (Business Logic, Compliance Engine, Analytics)      │
├───────────────────────────────────────────────────────┤
│          Data Layer                                   │
│  ┌──────────────┐  ┌──────────────┐  ┌────────────┐ │
│  │  Operational │  │  Data        │  │  Cache    │ │
│  │  Database    │  │  Warehouse   │  │  Layer    │ │
│  │  (OLTP)      │  │  (OLAP)      │  │  (Redis)  │ │
│  └──────────────┘  └──────────────┘  └────────────┘ │
└───────────────────────────────────────────────────────┘
```

### Database Selection

```python
class DatabaseArchitecture:
    """
    Operational Database (OLTP):
    - Primary: PostgreSQL
    - Purpose: Day-to-day operations
    - Characteristics: Normalized, ACID-compliant
    - Usage: Real-time transactions, updates
    - Scale: 1-10GB typical

    Analytical Database (OLAP):
    - Primary: Snowflake or BigQuery
    - Purpose: Historical analysis, BI
    - Characteristics: Denormalized, columnar
    - Usage: Reporting, analytics
    - Scale: 100GB-PB

    Cache Layer:
    - Primary: Redis
    - Purpose: Query acceleration
    - Characteristics: In-memory, fast
    - Usage: Frequent queries, session data
    - TTL: 1 hour typical

    Search Engine:
    - Primary: Elasticsearch
    - Purpose: Full-text search
    - Characteristics: Distributed, indexed
    - Usage: Bill text, regulation search
    - Real-time: Yes
    """
    pass
```

## Core Entity Models

### Government Official Representation

```python
from dataclasses import dataclass
from enum import Enum
from datetime import datetime, date
from typing import Optional, List

class OfficialType(Enum):
    SENATOR = "senator"
    REPRESENTATIVE = "representative"
    STATE_LEGISLATOR = "state_legislator"
    LOCAL_OFFICIAL = "local_official"
    EXECUTIVE_BRANCH = "executive_branch"
    AGENCY_OFFICIAL = "agency_official"
    STAFF = "staff"

class PartyAffiliation(Enum):
    DEMOCRAT = "D"
    REPUBLICAN = "R"
    INDEPENDENT = "I"
    OTHER = "O"

@dataclass
class GovernmentOfficial:
    """Represents a government official"""

    official_id: str
    first_name: str
    last_name: str
    middle_name: Optional[str]
    title: str
    official_type: OfficialType
    jurisdiction: str
    party: PartyAffiliation

    # Contact information
    office_address: str
    office_phone: str
    office_email: Optional[str]
    website: Optional[str]
    twitter_handle: Optional[str]
    district_number: Optional[int]

    # Tenure information
    term_start_date: date
    term_end_date: Optional[date]
    previous_positions: List[str]
    biographical_info: Optional[str]

    # Committee assignments
    committee_memberships: List['CommitteeAssignment']

    # Relationship tracking
    contact_history: List['ContactRecord']
    notes: List['InternalNote']

    created_at: datetime
    last_updated: datetime
    data_quality_score: float

@dataclass
class GovernmentOffice:
    """Represents government offices and agencies"""

    office_id: str
    office_name: str
    office_type: str  # 'Legislative', 'Executive', 'Agency', etc.
    jurisdiction: str
    agency_code: Optional[str]

    # Leadership
    director_official_id: Optional[str]
    deputy_director_official_id: Optional[str]

    # Contact information
    main_address: str
    phone_number: str
    email: Optional[str]
    website: Optional[str]

    # Organization
    department_of: Optional[str]
    sub_offices: List['GovernmentOffice']
    staff_count: Optional[int]

    # Specializations
    policy_areas: List[str]
    jurisdiction_areas: List[str]

    regulatory_authority: Optional[str]
    created_at: datetime
    last_updated: datetime

@dataclass
class CommitteeAssignment:
    """Committee assignments for officials"""

    assignment_id: str
    official_id: str
    committee_id: str
    committee_name: str
    jurisdiction: str

    # Role details
    role: str  # 'Chair', 'Ranking', 'Member'
    assignment_start: date
    assignment_end: Optional[date]
    is_current: bool

    # Significance
    priority_level: int  # 1-5, where 1 is most significant
    relevance_score: float

    created_at: datetime
    last_updated: datetime
```

### Relationship and Interaction Tracking

```python
@dataclass
class RelationshipRecord:
    """Tracks relationship between org and government actor"""

    relationship_id: str
    contact_type: str  # 'Official', 'Office', 'Agency', 'Committee'
    contact_id: str
    contact_name: str

    # Relationship details
    relationship_start_date: date
    relationship_end_date: Optional[date]
    relationship_status: str  # 'active', 'dormant', 'ended'
    relationship_strength: int  # 1-10 scale

    # Primary contacts
    primary_contact_name: Optional[str]
    primary_contact_email: Optional[str]
    primary_contact_phone: Optional[str]

    # Secondary contacts
    secondary_contacts: List[Dict]

    # Relationship basis
    shared_interests: List[str]
    connection_method: str
    connection_date: date

    # Activity metrics
    last_contact_date: date
    contact_frequency: str  # 'monthly', 'quarterly', 'annual'
    next_planned_contact: Optional[date]

    # Supporting information
    background_info: str
    internal_notes: List[str]

    created_at: datetime
    last_updated: datetime
    owner_user_id: str

@dataclass
class ContactRecord:
    """Individual contact/interaction record"""

    contact_id: str
    relationship_id: str
    contact_date: datetime
    contact_type: str  # 'meeting', 'call', 'email', 'event'
    contact_location: Optional[str]

    # Participants
    organization_participants: List[str]
    government_participants: List[str]

    # Content
    subjects_discussed: List[str]
    issues_discussed: List['IssueReference']
    outcomes: List[str]
    action_items: List['ActionItem']

    # Metadata
    initiated_by: str  # 'org' or 'government'
    contact_notes: str
    follow_up_required: bool
    follow_up_date: Optional[date]

    # Classification
    sentiment: str  # 'positive', 'neutral', 'negative'
    importance_level: int  # 1-5

    created_by: str
    created_at: datetime
    last_updated: datetime

class RelationshipManager:
    """Manages government relationships"""

    def __init__(self, db_connection):
        self.db = db_connection

    def track_contact(self, relationship_id: str, contact_data: Dict) -> str:
        """Record a new contact interaction"""

        contact = ContactRecord(
            contact_id=self._generate_id('CONT'),
            relationship_id=relationship_id,
            contact_date=contact_data.get('date', datetime.now()),
            contact_type=contact_data.get('type', 'meeting'),
            contact_location=contact_data.get('location'),
            organization_participants=contact_data.get('org_participants', []),
            government_participants=contact_data.get('gov_participants', []),
            subjects_discussed=contact_data.get('subjects', []),
            issues_discussed=contact_data.get('issues', []),
            outcomes=contact_data.get('outcomes', []),
            action_items=contact_data.get('action_items', []),
            initiated_by=contact_data.get('initiated_by', 'org'),
            contact_notes=contact_data.get('notes', ''),
            follow_up_required=contact_data.get('follow_up_required', False),
            follow_up_date=contact_data.get('follow_up_date'),
            sentiment=contact_data.get('sentiment', 'neutral'),
            importance_level=contact_data.get('importance', 3),
            created_by=contact_data.get('created_by', 'Unknown'),
            created_at=datetime.now(),
            last_updated=datetime.now()
        )

        # Update relationship
        self.db.update_relationship(
            relationship_id,
            {'last_contact_date': contact.contact_date}
        )

        # Store contact
        self.db.insert_contact(contact)

        return contact.contact_id

    def get_relationship_history(self, relationship_id: str,
                                days_back: int = 365) -> List[ContactRecord]:
        """Get contact history for a relationship"""

        start_date = datetime.now() - timedelta(days=days_back)

        return self.db.query("""
            SELECT * FROM contacts
            WHERE relationship_id = %s
            AND contact_date >= %s
            ORDER BY contact_date DESC
        """, [relationship_id, start_date])

    def identify_dormant_relationships(self, days_without_contact: int = 90) -> List[str]:
        """Identify relationships that need attention"""

        threshold_date = datetime.now() - timedelta(days=days_without_contact)

        dormant = self.db.query("""
            SELECT relationship_id FROM relationships
            WHERE relationship_status = 'active'
            AND last_contact_date < %s
            AND relationship_end_date IS NULL
        """, [threshold_date])

        return [r['relationship_id'] for r in dormant]
```

## Schema Design

### PostgreSQL Schema Definition

```sql
-- Government Officials Table
CREATE TABLE government_officials (
    official_id VARCHAR(50) PRIMARY KEY,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    middle_name VARCHAR(100),
    title VARCHAR(255) NOT NULL,
    official_type VARCHAR(50) NOT NULL,
    jurisdiction VARCHAR(50) NOT NULL,
    party_affiliation VARCHAR(10),
    office_address TEXT,
    office_phone VARCHAR(20),
    office_email VARCHAR(255),
    website VARCHAR(255),
    twitter_handle VARCHAR(100),
    district_number INTEGER,
    term_start_date DATE,
    term_end_date DATE,
    biographical_info TEXT,
    data_quality_score DECIMAL(3,2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_jurisdiction_type (jurisdiction, official_type),
    INDEX idx_last_name (last_name),
    FULLTEXT KEY idx_name_search (first_name, last_name)
);

-- Government Offices/Agencies
CREATE TABLE government_offices (
    office_id VARCHAR(50) PRIMARY KEY,
    office_name VARCHAR(255) NOT NULL,
    office_type VARCHAR(100) NOT NULL,
    jurisdiction VARCHAR(50) NOT NULL,
    agency_code VARCHAR(50),
    director_official_id VARCHAR(50),
    main_address TEXT,
    phone_number VARCHAR(20),
    email VARCHAR(255),
    website VARCHAR(255),
    department_of VARCHAR(50),
    parent_office_id VARCHAR(50),
    policy_areas JSON,
    regulatory_authority VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_jurisdiction_type (jurisdiction, office_type),
    INDEX idx_parent_office (parent_office_id),
    FOREIGN KEY (director_official_id) REFERENCES government_officials(official_id)
);

-- Relationships
CREATE TABLE relationships (
    relationship_id VARCHAR(50) PRIMARY KEY,
    contact_type VARCHAR(50) NOT NULL,
    contact_id VARCHAR(50) NOT NULL,
    contact_name VARCHAR(255) NOT NULL,
    relationship_status VARCHAR(50) NOT NULL,
    relationship_strength INTEGER,
    primary_contact_name VARCHAR(255),
    primary_contact_email VARCHAR(255),
    primary_contact_phone VARCHAR(20),
    shared_interests JSON,
    connection_method VARCHAR(100),
    connection_date DATE,
    last_contact_date DATE,
    contact_frequency VARCHAR(50),
    next_planned_contact DATE,
    relationship_start_date DATE NOT NULL,
    relationship_end_date DATE,
    background_info TEXT,
    owner_user_id VARCHAR(50) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_contact_type (contact_type, contact_id),
    INDEX idx_status (relationship_status),
    INDEX idx_owner (owner_user_id),
    INDEX idx_last_contact (last_contact_date)
);

-- Contact Records
CREATE TABLE contacts (
    contact_id VARCHAR(50) PRIMARY KEY,
    relationship_id VARCHAR(50) NOT NULL,
    contact_date TIMESTAMP NOT NULL,
    contact_type VARCHAR(50) NOT NULL,
    contact_location VARCHAR(255),
    organization_participants JSON,
    government_participants JSON,
    subjects_discussed JSON,
    outcomes JSON,
    initiated_by VARCHAR(50),
    contact_notes TEXT,
    follow_up_required BOOLEAN DEFAULT FALSE,
    follow_up_date DATE,
    sentiment VARCHAR(50),
    importance_level INTEGER,
    created_by VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_relationship (relationship_id),
    INDEX idx_contact_date (contact_date),
    INDEX idx_contact_type (contact_type),
    FOREIGN KEY (relationship_id) REFERENCES relationships(relationship_id) ON DELETE CASCADE
);

-- Committee Assignments
CREATE TABLE committee_assignments (
    assignment_id VARCHAR(50) PRIMARY KEY,
    official_id VARCHAR(50) NOT NULL,
    committee_id VARCHAR(50) NOT NULL,
    committee_name VARCHAR(255) NOT NULL,
    jurisdiction VARCHAR(50) NOT NULL,
    role VARCHAR(100),
    assignment_start DATE NOT NULL,
    assignment_end DATE,
    is_current BOOLEAN DEFAULT TRUE,
    priority_level INTEGER,
    relevance_score DECIMAL(3,2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_official (official_id),
    INDEX idx_committee (committee_id),
    INDEX idx_is_current (is_current),
    FOREIGN KEY (official_id) REFERENCES government_officials(official_id) ON DELETE CASCADE
);

-- Issues and Legislation Tracking
CREATE TABLE issues (
    issue_id VARCHAR(50) PRIMARY KEY,
    issue_name VARCHAR(255) NOT NULL,
    issue_category VARCHAR(100) NOT NULL,
    description TEXT,
    status VARCHAR(50),
    priority_level INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_category (issue_category),
    FULLTEXT KEY idx_issue_search (issue_name, description)
);

-- Relationship to Issues (many-to-many)
CREATE TABLE relationship_issues (
    relationship_id VARCHAR(50) NOT NULL,
    issue_id VARCHAR(50) NOT NULL,
    importance_level INTEGER,
    stance VARCHAR(50),  -- 'support', 'oppose', 'monitor'
    added_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (relationship_id, issue_id),
    FOREIGN KEY (relationship_id) REFERENCES relationships(relationship_id) ON DELETE CASCADE,
    FOREIGN KEY (issue_id) REFERENCES issues(issue_id) ON DELETE CASCADE
);
```

## Relationship Management

### Advanced Relationship Querying

```python
class RelationshipQueries:
    """Complex queries for government relationship analysis"""

    def __init__(self, db_connection):
        self.db = db_connection

    def find_key_decision_makers(self, issue_id: str) -> List[Dict]:
        """Find key decision makers on an issue"""

        query = """
            SELECT DISTINCT
                go.official_id,
                go.first_name,
                go.last_name,
                go.title,
                go.jurisdiction,
                ca.committee_name,
                ca.role,
                COUNT(DISTINCT c.contact_id) as contact_count,
                MAX(c.contact_date) as last_contact
            FROM government_officials go
            LEFT JOIN committee_assignments ca ON go.official_id = ca.official_id
                AND ca.is_current = TRUE
            LEFT JOIN relationships r ON go.official_id = r.contact_id
            LEFT JOIN contacts c ON r.relationship_id = c.relationship_id
            LEFT JOIN relationship_issues ri ON r.relationship_id = ri.relationship_id
            WHERE (
                ca.committee_id IN (
                    SELECT DISTINCT bi.committee_id
                    FROM bill_impacts bi
                    WHERE bi.issue_id = %s
                )
                OR ri.issue_id = %s
            )
            GROUP BY go.official_id, ca.committee_name, ca.role
            ORDER BY contact_count DESC, last_contact DESC
            LIMIT 50
        """

        return self.db.query(query, [issue_id, issue_id])

    def identify_influence_networks(self, official_id: str,
                                   depth: int = 2) -> Dict:
        """Identify network of influential relationships"""

        # Start with direct relationships
        direct = self.db.query("""
            SELECT * FROM relationships
            WHERE contact_id = %s
            AND relationship_status = 'active'
        """, [official_id])

        network = {
            'center': official_id,
            'depth': depth,
            'direct_relationships': len(direct),
            'relationship_network': direct
        }

        if depth > 1:
            # Find secondary relationships
            related_ids = [r['contact_id'] for r in direct]

            secondary = self.db.query(f"""
                SELECT * FROM relationships
                WHERE contact_id IN ({','.join(['%s'] * len(related_ids))})
                AND relationship_status = 'active'
                AND contact_id != %s
            """, related_ids + [official_id])

            network['secondary_relationships'] = len(secondary)
            network['secondary_network'] = secondary

        return network

    def get_engagement_timeline(self, relationship_id: str,
                               months_back: int = 12) -> List[Dict]:
        """Get engagement timeline for a relationship"""

        start_date = datetime.now() - timedelta(days=months_back*30)

        timeline = self.db.query("""
            SELECT
                DATE_TRUNC('month', contact_date) as month,
                COUNT(*) as contact_count,
                COUNT(DISTINCT contact_type) as unique_contact_types,
                GROUP_CONCAT(DISTINCT contact_type) as contact_types,
                AVG(importance_level) as avg_importance
            FROM contacts
            WHERE relationship_id = %s
            AND contact_date >= %s
            GROUP BY DATE_TRUNC('month', contact_date)
            ORDER BY month DESC
        """, [relationship_id, start_date])

        return timeline

    def find_allies_and_opponents(self, issue_id: str) -> Dict:
        """Identify allies and opponents on an issue"""

        allies_query = """
            SELECT DISTINCT
                r.contact_id,
                go.first_name,
                go.last_name,
                go.title,
                go.jurisdiction,
                ri.stance,
                COUNT(DISTINCT c.contact_id) as engagement_level
            FROM relationships r
            JOIN government_officials go ON r.contact_id = go.official_id
            LEFT JOIN relationship_issues ri ON r.relationship_id = ri.relationship_id
            LEFT JOIN contacts c ON r.relationship_id = c.relationship_id
            WHERE ri.issue_id = %s
            AND ri.stance = 'support'
            AND r.relationship_status = 'active'
            GROUP BY r.contact_id, go.first_name, go.last_name, go.title, go.jurisdiction, ri.stance
        """

        opponents_query = """
            SELECT DISTINCT
                r.contact_id,
                go.first_name,
                go.last_name,
                go.title,
                go.jurisdiction,
                ri.stance,
                COUNT(DISTINCT c.contact_id) as engagement_level
            FROM relationships r
            JOIN government_officials go ON r.contact_id = go.official_id
            LEFT JOIN relationship_issues ri ON r.relationship_id = ri.relationship_id
            LEFT JOIN contacts c ON r.relationship_id = c.relationship_id
            WHERE ri.issue_id = %s
            AND ri.stance = 'oppose'
            AND r.relationship_status = 'active'
            GROUP BY r.contact_id, go.first_name, go.last_name, go.title, go.jurisdiction, ri.stance
        """

        return {
            'allies': self.db.query(allies_query, [issue_id]),
            'opponents': self.db.query(opponents_query, [issue_id])
        }
```

## Query Optimization

### Indexing Strategy

```python
class IndexingStrategy:
    """Defines optimal indexing for government relations database"""

    PRIMARY_INDEXES = [
        # Official lookups
        "CREATE INDEX idx_officials_jurisdiction_type ON government_officials(jurisdiction, official_type)",
        "CREATE INDEX idx_officials_district ON government_officials(jurisdiction, district_number)",
        "CREATE INDEX idx_officials_party ON government_officials(party_affiliation)",

        # Relationship lookups
        "CREATE INDEX idx_relationships_contact ON relationships(contact_type, contact_id)",
        "CREATE INDEX idx_relationships_status ON relationships(relationship_status)",
        "CREATE INDEX idx_relationships_owner ON relationships(owner_user_id)",
        "CREATE INDEX idx_relationships_contact_date ON relationships(last_contact_date)",

        # Contact history
        "CREATE INDEX idx_contacts_relationship ON contacts(relationship_id)",
        "CREATE INDEX idx_contacts_date ON contacts(contact_date DESC)",
        "CREATE INDEX idx_contacts_type ON contacts(contact_type)",

        # Committee assignments
        "CREATE INDEX idx_committees_official ON committee_assignments(official_id)",
        "CREATE INDEX idx_committees_current ON committee_assignments(is_current, jurisdiction)",
        "CREATE INDEX idx_committees_priority ON committee_assignments(priority_level)",

        # Issue relationships
        "CREATE INDEX idx_issue_relationships ON relationship_issues(issue_id, relationship_id)"
    ]

    FULL_TEXT_INDEXES = [
        "CREATE FULLTEXT INDEX idx_officials_fulltext ON government_officials(first_name, last_name)",
        "CREATE FULLTEXT INDEX idx_offices_fulltext ON government_offices(office_name)",
        "CREATE FULLTEXT INDEX idx_issues_fulltext ON issues(issue_name, description)"
    ]

    COMPOSITE_INDEXES = [
        "CREATE INDEX idx_officials_jurisdiction_active ON government_officials(jurisdiction, term_end_date)",
        "CREATE INDEX idx_contacts_relationship_date ON contacts(relationship_id, contact_date DESC)",
        "CREATE INDEX idx_relationships_status_date ON relationships(relationship_status, last_contact_date)"
    ]

class QueryOptimization:
    """Query optimization techniques"""

    @staticmethod
    def explain_query_plan(db_connection, query: str, params: List) -> Dict:
        """Analyze query execution plan"""

        explain = db_connection.query(f"EXPLAIN ANALYZE {query}", params)
        return {
            'query': query,
            'plan': explain,
            'analysis': QueryOptimization._analyze_plan(explain)
        }

    @staticmethod
    def _analyze_plan(plan: List) -> Dict:
        """Analyze execution plan for optimization opportunities"""

        analysis = {
            'uses_indexes': False,
            'sequential_scans': 0,
            'recommended_indexes': [],
            'estimated_rows': 0
        }

        for line in plan:
            if 'Index' in str(line):
                analysis['uses_indexes'] = True
            if 'Seq Scan' in str(line):
                analysis['sequential_scans'] += 1

        return analysis
```

## Data Warehouse

### Analytics Schema

```python
class DataWarehouseSchema:
    """Schema for analytical database (OLAP)"""

    FACT_TABLES = {
        'fact_contacts': """
            CREATE TABLE fact_contacts (
                contact_id VARCHAR(50),
                relationship_key VARCHAR(50),
                official_key VARCHAR(50),
                office_key VARCHAR(50),
                date_key INTEGER,  -- YYYYMMDD
                contact_type VARCHAR(50),
                importance_level INTEGER,
                contact_count INTEGER,
                sentiment VARCHAR(50),
                created_at TIMESTAMP
            )
            PARTITION BY RANGE(date_key)
        """,

        'fact_relationships': """
            CREATE TABLE fact_relationships (
                relationship_key VARCHAR(50),
                official_key VARCHAR(50),
                office_key VARCHAR(50),
                start_date_key INTEGER,
                end_date_key INTEGER,
                relationship_length_days INTEGER,
                contact_frequency_code VARCHAR(10),
                relationship_strength INTEGER,
                total_contacts INTEGER
            )
        """,

        'fact_issues': """
            CREATE TABLE fact_issues (
                issue_key VARCHAR(50),
                relationship_key VARCHAR(50),
                date_key INTEGER,
                stance VARCHAR(50),
                issue_priority INTEGER,
                engagement_level INTEGER
            )
        """
    }

    DIMENSION_TABLES = {
        'dim_officials': """
            CREATE TABLE dim_officials (
                official_key VARCHAR(50) PRIMARY KEY,
                official_id VARCHAR(50),
                full_name VARCHAR(255),
                title VARCHAR(255),
                official_type VARCHAR(50),
                jurisdiction VARCHAR(50),
                party VARCHAR(10),
                committees JSON,
                is_current BOOLEAN,
                created_at TIMESTAMP,
                updated_at TIMESTAMP
            )
        """,

        'dim_organizations': """
            CREATE TABLE dim_organizations (
                organization_key VARCHAR(50) PRIMARY KEY,
                organization_id VARCHAR(50),
                organization_name VARCHAR(255),
                industry VARCHAR(100),
                headquarters_state VARCHAR(2),
                is_active BOOLEAN
            )
        """,

        'dim_dates': """
            CREATE TABLE dim_dates (
                date_key INTEGER PRIMARY KEY,
                full_date DATE,
                year INTEGER,
                quarter INTEGER,
                month INTEGER,
                day INTEGER,
                day_of_week VARCHAR(10)
            )
        """,

        'dim_issues': """
            CREATE TABLE dim_issues (
                issue_key VARCHAR(50) PRIMARY KEY,
                issue_id VARCHAR(50),
                issue_name VARCHAR(255),
                category VARCHAR(100),
                priority_level INTEGER
            )
        """
    }
```

## Security and Access Control

### Role-Based Access Control

```python
from enum import Enum

class AccessLevel(Enum):
    VIEWER = 1
    EDITOR = 2
    MANAGER = 3
    ADMINISTRATOR = 4

class DataSecurityModel:
    """Implements security for government relations data"""

    ROLE_PERMISSIONS = {
        AccessLevel.VIEWER: {
            'can_view_contacts': True,
            'can_view_relationships': True,
            'can_view_officials': True,
            'can_edit_contacts': False,
            'can_delete_contacts': False,
            'can_view_reports': True,
            'can_export_data': False,
            'can_manage_users': False
        },
        AccessLevel.EDITOR: {
            'can_view_contacts': True,
            'can_view_relationships': True,
            'can_view_officials': True,
            'can_edit_contacts': True,
            'can_delete_contacts': False,
            'can_view_reports': True,
            'can_export_data': True,
            'can_manage_users': False
        },
        AccessLevel.MANAGER: {
            'can_view_contacts': True,
            'can_view_relationships': True,
            'can_view_officials': True,
            'can_edit_contacts': True,
            'can_delete_contacts': True,
            'can_view_reports': True,
            'can_export_data': True,
            'can_manage_users': True
        },
        AccessLevel.ADMINISTRATOR: {
            'can_view_contacts': True,
            'can_view_relationships': True,
            'can_view_officials': True,
            'can_edit_contacts': True,
            'can_delete_contacts': True,
            'can_view_reports': True,
            'can_export_data': True,
            'can_manage_users': True,
            'can_manage_database': True,
            'can_manage_backups': True
        }
    }

class AccessControl:
    """Manages access to government relations data"""

    def __init__(self, db_connection, authentication_service):
        self.db = db_connection
        self.auth = authentication_service

    def check_access(self, user_id: str, resource_type: str,
                    action: str, resource_id: str = None) -> bool:
        """Check if user has access to perform action"""

        user = self.auth.get_user(user_id)
        access_level = user.get('access_level')

        # Get permissions for user's role
        permissions = self.ROLE_PERMISSIONS.get(access_level)

        # Check action permission
        permission_key = f"can_{action}_{resource_type}"
        if permission_key not in permissions:
            return False

        if not permissions[permission_key]:
            return False

        # Check resource-level access
        if resource_id:
            return self._check_resource_access(user_id, resource_type, resource_id)

        return True

    def _check_resource_access(self, user_id: str, resource_type: str,
                               resource_id: str) -> bool:
        """Check access to specific resource"""

        if resource_type == 'relationship':
            # User can only access relationships they own or are shared with them
            relationship = self.db.query_one(
                "SELECT owner_user_id FROM relationships WHERE relationship_id = %s",
                [resource_id]
            )

            if relationship['owner_user_id'] == user_id:
                return True

            # Check if shared
            shared = self.db.query(
                "SELECT * FROM relationship_shares WHERE relationship_id = %s AND user_id = %s",
                [resource_id, user_id]
            )

            return len(shared) > 0

        return True

    def encrypt_sensitive_data(self, data: Dict, fields: List[str]) -> Dict:
        """Encrypt sensitive fields in data"""

        encrypted = data.copy()

        for field in fields:
            if field in encrypted:
                encrypted[field] = self._encrypt(encrypted[field])

        return encrypted

    def _encrypt(self, value: str) -> str:
        """Encrypt a value"""

        from cryptography.fernet import Fernet

        # Use database encryption key
        key = self._get_encryption_key()
        cipher = Fernet(key)

        return cipher.encrypt(value.encode()).decode()
```

## Implementation Workflow

### Database Implementation Process

```python
class DatabaseImplementation:
    """Manages database implementation and deployment"""

    def __init__(self):
        self.migration_status = {}

    def create_initial_schema(self, db_connection) -> Dict:
        """Create initial database schema"""

        steps = [
            {
                'step': 'Create base tables',
                'tables': [
                    'government_officials',
                    'government_offices',
                    'relationships',
                    'contacts'
                ]
            },
            {
                'step': 'Create supporting tables',
                'tables': [
                    'committee_assignments',
                    'issues',
                    'relationship_issues'
                ]
            },
            {
                'step': 'Create indexes',
                'operations': IndexingStrategy.PRIMARY_INDEXES
            },
            {
                'step': 'Create full-text indexes',
                'operations': IndexingStrategy.FULL_TEXT_INDEXES
            }
        ]

        results = []

        for step in steps:
            result = {
                'step': step['step'],
                'success': True,
                'details': []
            }

            if 'tables' in step:
                for table in step['tables']:
                    try:
                        # Execute table creation
                        result['details'].append(f"Created table: {table}")
                    except Exception as e:
                        result['success'] = False
                        result['details'].append(f"Failed to create {table}: {str(e)}")

            if 'operations' in step:
                for operation in step['operations']:
                    try:
                        # Execute operation
                        result['details'].append(f"Executed: {operation[:50]}...")
                    except Exception as e:
                        result['success'] = False
                        result['details'].append(f"Failed: {str(e)}")

            results.append(result)

        return {
            'status': 'completed' if all(r['success'] for r in results) else 'failed',
            'steps': results
        }

    def migrate_legacy_data(self, db_connection, legacy_source: str) -> Dict:
        """Migrate data from legacy system"""

        migration_plan = {
            'source': legacy_source,
            'start_time': datetime.now(),
            'tables_migrated': [],
            'records_migrated': 0,
            'errors': []
        }

        # Import officials
        try:
            official_count = self._import_officials(db_connection, legacy_source)
            migration_plan['tables_migrated'].append('government_officials')
            migration_plan['records_migrated'] += official_count
        except Exception as e:
            migration_plan['errors'].append(f"Officials import failed: {str(e)}")

        # Import relationships
        try:
            rel_count = self._import_relationships(db_connection, legacy_source)
            migration_plan['tables_migrated'].append('relationships')
            migration_plan['records_migrated'] += rel_count
        except Exception as e:
            migration_plan['errors'].append(f"Relationships import failed: {str(e)}")

        # Import contacts
        try:
            contact_count = self._import_contacts(db_connection, legacy_source)
            migration_plan['tables_migrated'].append('contacts')
            migration_plan['records_migrated'] += contact_count
        except Exception as e:
            migration_plan['errors'].append(f"Contacts import failed: {str(e)}")

        migration_plan['end_time'] = datetime.now()
        migration_plan['duration_seconds'] = (
            migration_plan['end_time'] - migration_plan['start_time']
        ).total_seconds()

        return migration_plan
```

## Best Practices

### Database Excellence

1. **Schema Design**
   - Normalize for OLTP operations
   - Denormalize for analytical queries
   - Use surrogate keys for flexibility
   - Document relationships clearly

2. **Indexing Strategy**
   - Index foreign keys
   - Index frequently searched columns
   - Use composite indexes for common queries
   - Monitor index usage and eliminate unused indexes

3. **Query Performance**
   - Use EXPLAIN ANALYZE to understand query plans
   - Optimize JOIN operations
   - Use appropriate WHERE clauses
   - Cache frequently accessed data

4. **Data Quality**
   - Implement data validation rules
   - Use constraints to prevent invalid data
   - Establish data governance policies
   - Conduct regular data quality audits

5. **Backup and Recovery**
   - Implement daily backups
   - Test recovery procedures regularly
   - Maintain backup copies off-site
   - Document recovery time objectives (RTO)

6. **Security**
   - Encrypt sensitive data at rest
   - Use SSL/TLS for data in transit
   - Implement role-based access control
   - Audit all data access

7. **Scalability**
   - Design for horizontal scaling
   - Use partitioning for large tables
   - Implement read replicas for analytics
   - Monitor performance metrics

## Conclusion

A well-designed government relations database provides the foundation for effective regulatory tracking, relationship management, and compliance. Key success factors include:

1. Clear data models representing government structure and relationships
2. Efficient schema design supporting both operational and analytical needs
3. Robust security ensuring data privacy and access control
4. Performance optimization enabling fast queries and reporting
5. Scalable architecture supporting growth

Organizations that invest in building comprehensive, well-designed government relations databases gain competitive advantages in regulatory navigation and stakeholder engagement.
