# Legislative Tracking Implementation Guide

## Table of Contents
1. [Executive Overview](#executive-overview)
2. [Core Architecture](#core-architecture)
3. [Data Collection Systems](#data-collection-systems)
4. [Processing Pipeline](#processing-pipeline)
5. [Storage and Indexing](#storage-and-indexing)
6. [Alert Mechanisms](#alert-mechanisms)
7. [Implementation Workflow](#implementation-workflow)
8. [Integration Points](#integration-points)
9. [Monitoring and Optimization](#monitoring-and-optimization)
10. [Best Practices](#best-practices)

## Executive Overview

Legislative tracking systems monitor legislative activity across federal, state, and local governments. Organizations use these systems to identify bills that may impact their business, operations, or regulatory obligations. This guide provides a comprehensive implementation approach for building a production-grade legislative tracking system.

### Key Objectives
- Automated collection of legislative data from government sources
- Real-time processing and analysis of bill content and status
- Intelligent filtering and relevance scoring
- Timely alerts for stakeholders
- Historical tracking and trend analysis
- Multi-jurisdictional support

### Success Metrics
- Coverage: Tracking 85%+ of relevant bills
- Latency: Bill updates within 24 hours of publication
- Accuracy: 95%+ relevance accuracy for alerts
- Availability: 99.5% system uptime
- User engagement: 70%+ alert open rate

## Core Architecture

### System Components

```
┌─────────────────────────────────────────────────────────────┐
│                    Legislative Tracking System               │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐       │
│  │ Data Sources │  │ APIs/Scrapers│  │ Manual Entry │       │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘       │
│         │                 │                 │                │
│         └─────────────────┼─────────────────┘                │
│                           │                                  │
│                    ┌──────▼────────┐                         │
│                    │ Ingestion Tier│                         │
│                    └──────┬────────┘                         │
│                           │                                  │
│         ┌─────────────────┼─────────────────┐               │
│         │                 │                 │               │
│  ┌──────▼─────┐  ┌─────────▼──────┐  ┌───────▼──────┐     │
│  │  Normalize  │  │   Deduplicate  │  │   Enrich     │     │
│  │    Data     │  │   & Validate   │  │    Content   │     │
│  └──────┬─────┘  └─────────┬──────┘  └───────┬──────┘     │
│         │                  │                  │             │
│         └──────────────────┼──────────────────┘             │
│                            │                               │
│                    ┌───────▼────────┐                      │
│                    │ Analysis Engine│                      │
│                    └───────┬────────┘                      │
│                            │                               │
│         ┌──────────────────┼──────────────────┐            │
│         │                  │                  │            │
│  ┌──────▼──────┐  ┌────────▼───────┐  ┌──────▼─────┐     │
│  │ Relevance   │  │ Classification │  │ Extraction │     │
│  │  Scoring    │  │                 │  │            │     │
│  └──────┬──────┘  └────────┬───────┘  └──────┬─────┘     │
│         │                  │                  │            │
│         └──────────────────┼──────────────────┘            │
│                            │                               │
│                    ┌───────▼────────┐                      │
│                    │  Storage Layer │                      │
│                    └───────┬────────┘                      │
│                            │                               │
│         ┌──────────────────┼──────────────────┐            │
│         │                  │                  │            │
│  ┌──────▼──────┐  ┌────────▼───────┐  ┌──────▼─────┐     │
│  │   Primary   │  │   Search       │  │   Cache    │     │
│  │   Database  │  │   Engine       │  │   Layer    │     │
│  └──────┬──────┘  └────────┬───────┘  └──────┬─────┘     │
│         │                  │                  │            │
│         └──────────────────┼──────────────────┘            │
│                            │                               │
│                    ┌───────▼────────┐                      │
│                    │  Alert Engine  │                      │
│                    └───────┬────────┘                      │
│                            │                               │
│         ┌──────────────────┼──────────────────┐            │
│         │                  │                  │            │
│  ┌──────▼──────┐  ┌────────▼───────┐  ┌──────▼─────┐     │
│  │ Email/SMS   │  │  Dashboard     │  │  API       │     │
│  │  Delivery   │  │  Notifications │  │  Webhooks  │     │
│  └─────────────┘  └────────────────┘  └────────────┘     │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### Technology Stack

```
Data Collection:
  - Web Scraping: Scrapy, Selenium for dynamic content
  - APIs: Federal (Congress.gov), State (State Legislature APIs)
  - Message Queue: RabbitMQ, Kafka for streaming

Processing:
  - Language Processing: spaCy, NLTK for NLP analysis
  - Data Processing: Apache Spark, Pandas
  - Containerization: Docker for scalable processing

Storage:
  - Primary: PostgreSQL with full-text search
  - Document Store: Elasticsearch for advanced search
  - Cache: Redis for frequent queries
  - Archive: S3 for historical data

Delivery:
  - Message Queue: RabbitMQ for notification dispatch
  - Email: SendGrid or SMTP service
  - SMS: Twilio for alerts
  - Webhooks: Custom REST APIs
```

## Data Collection Systems

### Federal Legislative Sources

#### Congress.gov API

```python
import requests
import json
from datetime import datetime
from typing import List, Dict

class CongressGovCollector:
    """Collects data from Congress.gov API"""

    BASE_URL = "https://api.congress.gov/v3"

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'LegislativeTracker/1.0'
        })

    def fetch_bills(self, congress_number: int, limit: int = 250) -> List[Dict]:
        """
        Fetch bills for a specific Congress session

        Args:
            congress_number: Congress number (e.g., 118 for 2023-2024)
            limit: Number of bills to fetch per request (max 250)

        Returns:
            List of bill dictionaries
        """
        bills = []
        offset = 0

        while True:
            endpoint = f"{self.BASE_URL}/bill/{congress_number}/"
            params = {
                'api_key': self.api_key,
                'limit': limit,
                'offset': offset,
                'sort': '-introduced-date'
            }

            response = self.session.get(endpoint, params=params)
            response.raise_for_status()

            data = response.json()
            bills.extend(data.get('bills', []))

            # Check if more results available
            if len(data.get('bills', [])) < limit:
                break

            offset += limit

        return bills

    def fetch_bill_details(self, bill_type: str, number: int,
                          congress_number: int) -> Dict:
        """
        Fetch detailed information for a specific bill

        Args:
            bill_type: Type of bill (HR, S, HJ, SJ, etc.)
            number: Bill number
            congress_number: Congress number

        Returns:
            Detailed bill dictionary
        """
        endpoint = f"{self.BASE_URL}/bill/{congress_number}/{bill_type.lower()}/{number}/"
        params = {'api_key': self.api_key}

        response = self.session.get(endpoint, params=params)
        response.raise_for_status()

        return response.json()['bill']

    def fetch_bill_amendments(self, bill_type: str, number: int,
                             congress_number: int) -> List[Dict]:
        """Fetch amendments to a bill"""
        endpoint = f"{self.BASE_URL}/bill/{congress_number}/{bill_type.lower()}/{number}/amendments/"
        params = {'api_key': self.api_key, 'limit': 250}

        amendments = []
        offset = 0

        while True:
            params['offset'] = offset
            response = self.session.get(endpoint, params=params)
            response.raise_for_status()

            data = response.json()
            amendments.extend(data.get('amendments', []))

            if len(data.get('amendments', [])) < 250:
                break

            offset += 250

        return amendments

    def fetch_bill_actions(self, bill_type: str, number: int,
                          congress_number: int) -> List[Dict]:
        """Fetch all actions taken on a bill"""
        endpoint = f"{self.BASE_URL}/bill/{congress_number}/{bill_type.lower()}/{number}/actions/"
        params = {'api_key': self.api_key, 'limit': 250}

        actions = []
        offset = 0

        while True:
            params['offset'] = offset
            response = self.session.get(endpoint, params=params)
            response.raise_for_status()

            data = response.json()
            actions.extend(data.get('actions', []))

            if len(data.get('actions', [])) < 250:
                break

            offset += 250

        return actions
```

#### State Legislative APIs

```python
from abc import ABC, abstractmethod
from enum import Enum

class StateLegislativeAPI(ABC):
    """Abstract base class for state legislative APIs"""

    @abstractmethod
    def fetch_bills(self, session_year: int) -> List[Dict]:
        """Fetch bills for a legislative session"""
        pass

    @abstractmethod
    def fetch_bill_details(self, bill_id: str) -> Dict:
        """Fetch detailed bill information"""
        pass

class CaliforniaLegislativeCollector(StateLegislativeAPI):
    """California Legislative Information API collector"""

    BASE_URL = "https://api.leginfo.legislature.ca.gov/v3"

    def fetch_bills(self, session_year: int) -> List[Dict]:
        """
        Fetch bills from California Legislature

        California uses a two-year session model
        """
        bills = []

        # California bills organized by year
        bill_types = ['AB', 'SB']  # Assembly Bills, Senate Bills

        for bill_type in bill_types:
            endpoint = f"{self.BASE_URL}/bills/{session_year}/{bill_type}/"

            response = requests.get(endpoint)
            response.raise_for_status()

            data = response.json()
            bills.extend(data.get('bills', []))

        return bills

    def fetch_bill_details(self, bill_id: str) -> Dict:
        """Fetch detailed information for a California bill"""
        endpoint = f"{self.BASE_URL}/bills/{bill_id}"

        response = requests.get(endpoint)
        response.raise_for_status()

        return response.json()

class TexasLegislativeCollector(StateLegislativeAPI):
    """Texas Legislative Online API collector"""

    BASE_URL = "https://api.legis.texas.gov/api/v1"

    def fetch_bills(self, session_year: int) -> List[Dict]:
        """Fetch bills from Texas Legislature"""
        bills = []
        bill_types = ['HB', 'SB']  # House Bills, Senate Bills

        for bill_type in bill_types:
            endpoint = f"{self.BASE_URL}/bills/{bill_type}/"
            params = {'legislature': session_year}

            response = requests.get(endpoint, params=params)
            response.raise_for_status()

            data = response.json()
            bills.extend(data)

        return bills

    def fetch_bill_details(self, bill_id: str) -> Dict:
        """Fetch detailed information for a Texas bill"""
        endpoint = f"{self.BASE_URL}/bills/{bill_id}"

        response = requests.get(endpoint)
        response.raise_for_status()

        return response.json()
```

### Web Scraping for Non-API Sources

```python
import scrapy
from scrapy.crawler import CrawlerProcess
from datetime import datetime

class LegislativeScraperSpider(scrapy.Spider):
    """Web scraper for legislative information from websites"""

    name = 'legislative_scraper'
    start_urls = []

    def __init__(self, urls: List[str], *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.start_urls = urls

    def parse(self, response):
        """Parse legislative page"""
        # Extract bill information
        bills = response.css('tr.bill-row')

        for bill in bills:
            yield {
                'bill_id': bill.css('td.bill-id::text').get(),
                'title': bill.css('td.bill-title::text').get(),
                'summary': bill.css('td.bill-summary::text').get(),
                'introduced_date': bill.css('td.introduced-date::text').get(),
                'sponsor': bill.css('td.sponsor::text').get(),
                'status': bill.css('td.status::text').get(),
                'url': bill.css('a::attr(href)').get(),
                'fetched_at': datetime.now().isoformat()
            }

class LegislativeDataCollector:
    """Coordinates collection from multiple sources"""

    def __init__(self):
        self.congress_collector = None
        self.state_collectors = {}

    def collect_federal_bills(self, congress_number: int):
        """Collect federal bills from Congress.gov"""
        bills = self.congress_collector.fetch_bills(congress_number)
        return bills

    def collect_state_bills(self, state_code: str, session_year: int):
        """Collect state bills"""
        if state_code not in self.state_collectors:
            raise ValueError(f"No collector configured for {state_code}")

        collector = self.state_collectors[state_code]
        bills = collector.fetch_bills(session_year)
        return bills

    def collect_all_jurisdictions(self, session_year: int):
        """Orchestrate collection across all jurisdictions"""
        federal_bills = self.collect_federal_bills(session_year)

        state_bills = {}
        for state_code in self.state_collectors.keys():
            state_bills[state_code] = self.collect_state_bills(state_code, session_year)

        return {
            'federal': federal_bills,
            'states': state_bills,
            'collected_at': datetime.now().isoformat()
        }
```

## Processing Pipeline

### Data Normalization

```python
from dataclasses import dataclass
from enum import Enum
from typing import Optional
from datetime import datetime

class BillStatus(Enum):
    INTRODUCED = "Introduced"
    IN_COMMITTEE = "In Committee"
    PASSED_CHAMBER = "Passed Chamber"
    IN_OTHER_CHAMBER = "In Other Chamber"
    PASSED_BOTH = "Passed Both Chambers"
    SIGNED = "Signed into Law"
    VETOED = "Vetoed"
    POCKET_VETOED = "Pocket Vetoed"
    FAILED = "Failed"

@dataclass
class NormalizedBill:
    """Standard bill representation across jurisdictions"""

    # Identifiers
    bill_id: str
    jurisdiction: str  # 'federal', 'CA', 'TX', etc.
    original_source: str
    source_url: str

    # Basic Information
    type: str  # 'HR', 'S', 'HB', 'SB', etc.
    number: int
    title: str
    summary: Optional[str]
    full_text_url: Optional[str]

    # Sponsorship
    primary_sponsor: str
    primary_sponsor_party: Optional[str]
    co_sponsors: List[str]

    # Dates
    introduced_date: datetime
    last_updated: datetime
    expected_vote_date: Optional[datetime]

    # Status
    current_status: BillStatus
    current_location: str  # Committee name, chamber, etc.

    # Content Analysis
    keywords: List[str]
    topics: List[str]
    affected_industries: List[str]

    # Legislative Progress
    actions: List[Dict]  # Historical actions
    amendments: List[Dict]
    votes: List[Dict]

    # Metadata
    data_quality_score: float  # 0-1
    processed_at: datetime

class BillNormalizer:
    """Normalizes bills from different sources"""

    def normalize_federal_bill(self, congress_bill: Dict) -> NormalizedBill:
        """Normalize a Congress.gov bill"""
        bill_data = congress_bill['bill']

        return NormalizedBill(
            bill_id=f"US-{bill_data['type']}{bill_data['number']}",
            jurisdiction='federal',
            original_source='congress.gov',
            source_url=bill_data.get('url', ''),
            type=bill_data['type'],
            number=bill_data['number'],
            title=bill_data['title'],
            summary=bill_data.get('summary', {}).get('text'),
            full_text_url=bill_data.get('textVersions', [{}])[0].get('formats', [{}])[0].get('url'),
            primary_sponsor=bill_data.get('sponsors', [{}])[0].get('name', 'Unknown'),
            primary_sponsor_party=bill_data.get('sponsors', [{}])[0].get('party'),
            co_sponsors=[s['name'] for s in bill_data.get('sponsors', [])[1:]],
            introduced_date=datetime.fromisoformat(
                bill_data.get('introducedDate', datetime.now().isoformat())
            ),
            last_updated=datetime.fromisoformat(
                bill_data.get('latestAction', {}).get('actionDate', datetime.now().isoformat())
            ),
            current_status=self._map_bill_status(
                bill_data.get('latestAction', {}).get('actionDescriptor', 'Introduced')
            ),
            current_location=bill_data.get('latestAction', {}).get('text', 'Unknown'),
            actions=bill_data.get('actions', []),
            amendments=bill_data.get('amendments', []),
            votes=bill_data.get('votes', []),
            keywords=[],
            topics=[],
            affected_industries=[],
            data_quality_score=0.9,
            processed_at=datetime.now()
        )

    def _map_bill_status(self, action_text: str) -> BillStatus:
        """Map action text to standard bill status"""
        action_lower = action_text.lower()

        if 'signed' in action_lower:
            return BillStatus.SIGNED
        elif 'vetoed' in action_lower:
            return BillStatus.VETOED
        elif 'passed' in action_lower:
            return BillStatus.PASSED_BOTH if 'both' in action_lower else BillStatus.PASSED_CHAMBER
        elif 'committee' in action_lower:
            return BillStatus.IN_COMMITTEE
        else:
            return BillStatus.INTRODUCED
```

## Storage and Indexing

### PostgreSQL Schema

```sql
-- Main bills table
CREATE TABLE bills (
    id BIGSERIAL PRIMARY KEY,
    bill_id VARCHAR(50) UNIQUE NOT NULL,
    jurisdiction VARCHAR(20) NOT NULL,
    bill_type VARCHAR(10) NOT NULL,
    bill_number INTEGER NOT NULL,
    title TEXT NOT NULL,
    summary TEXT,
    full_text_url TEXT,
    introduced_date TIMESTAMP NOT NULL,
    last_updated TIMESTAMP NOT NULL,
    current_status VARCHAR(50) NOT NULL,
    current_location TEXT,
    primary_sponsor VARCHAR(255),
    data_quality_score DECIMAL(3,2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(jurisdiction, bill_type, bill_number)
);

-- Bill keywords and topics
CREATE TABLE bill_keywords (
    id BIGSERIAL PRIMARY KEY,
    bill_id BIGINT NOT NULL REFERENCES bills(id) ON DELETE CASCADE,
    keyword VARCHAR(255) NOT NULL,
    relevance_score DECIMAL(3,2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_bill_keyword (bill_id, keyword)
);

-- Bill actions/history
CREATE TABLE bill_actions (
    id BIGSERIAL PRIMARY KEY,
    bill_id BIGINT NOT NULL REFERENCES bills(id) ON DELETE CASCADE,
    action_date TIMESTAMP NOT NULL,
    action_text TEXT NOT NULL,
    action_type VARCHAR(50),
    actor VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_bill_action_date (bill_id, action_date)
);

-- Sponsors information
CREATE TABLE bill_sponsors (
    id BIGSERIAL PRIMARY KEY,
    bill_id BIGINT NOT NULL REFERENCES bills(id) ON DELETE CASCADE,
    sponsor_name VARCHAR(255) NOT NULL,
    party VARCHAR(50),
    is_primary BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_bill_sponsor (bill_id)
);

-- Full-text search index
CREATE FULLTEXT INDEX idx_bill_text_search ON bills(title, summary);
```

### Elasticsearch Configuration

```python
from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk

class BillSearchIndex:
    """Manages Elasticsearch index for bills"""

    def __init__(self, hosts: List[str]):
        self.es = Elasticsearch(hosts)
        self.index_name = 'bills'

    def create_index(self):
        """Create bills index with mappings"""
        mappings = {
            "mappings": {
                "properties": {
                    "bill_id": {"type": "keyword"},
                    "jurisdiction": {"type": "keyword"},
                    "bill_type": {"type": "keyword"},
                    "bill_number": {"type": "integer"},
                    "title": {
                        "type": "text",
                        "analyzer": "standard",
                        "fields": {
                            "keyword": {"type": "keyword"}
                        }
                    },
                    "summary": {
                        "type": "text",
                        "analyzer": "standard"
                    },
                    "keywords": {"type": "keyword"},
                    "topics": {"type": "keyword"},
                    "affected_industries": {"type": "keyword"},
                    "introduced_date": {"type": "date"},
                    "current_status": {"type": "keyword"},
                    "primary_sponsor": {"type": "text"},
                    "co_sponsors": {"type": "keyword"},
                    "processed_at": {"type": "date"}
                }
            }
        }

        self.es.indices.create(index=self.index_name, body=mappings, ignore=400)

    def index_bill(self, bill: NormalizedBill):
        """Index a single bill"""
        doc = {
            "bill_id": bill.bill_id,
            "jurisdiction": bill.jurisdiction,
            "bill_type": bill.type,
            "bill_number": bill.number,
            "title": bill.title,
            "summary": bill.summary,
            "keywords": bill.keywords,
            "topics": bill.topics,
            "affected_industries": bill.affected_industries,
            "introduced_date": bill.introduced_date,
            "current_status": bill.current_status.value,
            "primary_sponsor": bill.primary_sponsor,
            "co_sponsors": bill.co_sponsors,
            "processed_at": bill.processed_at
        }

        self.es.index(index=self.index_name, id=bill.bill_id, body=doc)

    def bulk_index(self, bills: List[NormalizedBill]):
        """Bulk index multiple bills"""
        actions = []

        for bill in bills:
            doc = {
                "bill_id": bill.bill_id,
                "jurisdiction": bill.jurisdiction,
                "bill_type": bill.type,
                "bill_number": bill.number,
                "title": bill.title,
                "summary": bill.summary,
                "keywords": bill.keywords,
                "topics": bill.topics,
                "affected_industries": bill.affected_industries,
                "introduced_date": bill.introduced_date,
                "current_status": bill.current_status.value,
                "primary_sponsor": bill.primary_sponsor,
                "co_sponsors": bill.co_sponsors,
                "processed_at": bill.processed_at
            }

            actions.append({
                "_index": self.index_name,
                "_id": bill.bill_id,
                "_source": doc
            })

        bulk(self.es, actions)

    def search_bills(self, query: str, filters: Dict = None) -> Dict:
        """Search bills with optional filters"""
        search_body = {
            "query": {
                "bool": {
                    "must": [
                        {
                            "multi_match": {
                                "query": query,
                                "fields": ["title^2", "summary", "keywords"]
                            }
                        }
                    ]
                }
            }
        }

        if filters:
            search_body["query"]["bool"]["filter"] = filters

        return self.es.search(index=self.index_name, body=search_body)
```

## Alert Mechanisms

### Relevance Scoring

```python
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

class RelevanceScorer:
    """Scores bills for relevance to user interests"""

    def __init__(self):
        self.vectorizer = TfidfVectorizer(max_features=5000)
        self.user_profiles = {}

    def score_bill_relevance(self, bill: NormalizedBill,
                            user_interests: List[str]) -> float:
        """
        Calculate relevance score for a bill

        Uses multiple signals:
        - Keyword matching (keywords, topics)
        - Text similarity (title, summary)
        - Sponsor history (known advocates/opponents)
        - Geographic scope

        Returns:
            Relevance score between 0 and 1
        """
        scores = []
        weights = {
            'keyword_match': 0.4,
            'text_similarity': 0.3,
            'sponsor_history': 0.2,
            'scope_match': 0.1
        }

        # Keyword matching
        bill_keywords = set(bill.keywords + bill.topics)
        interest_keywords = set(user_interests)
        keyword_overlap = len(bill_keywords & interest_keywords)
        keyword_score = min(keyword_overlap / max(len(interest_keywords), 1), 1.0)
        scores.append(('keyword_match', keyword_score))

        # Text similarity
        combined_text = f"{bill.title} {bill.summary}"
        interest_text = " ".join(user_interests)

        vectorizer = TfidfVectorizer()
        tfidf_matrix = vectorizer.fit_transform([combined_text, interest_text])
        text_similarity = cosine_similarity(tfidf_matrix)[0][1]
        scores.append(('text_similarity', text_similarity))

        # Sponsor history (would integrate with user's tracked sponsors)
        sponsor_score = 0.5  # Placeholder
        scores.append(('sponsor_history', sponsor_score))

        # Calculate weighted score
        total_score = sum(
            score * weights[signal_type]
            for signal_type, score in scores
        )

        return total_score

    def batch_score_bills(self, bills: List[NormalizedBill],
                         user_interests: List[str]) -> List[tuple]:
        """Score multiple bills and return sorted by relevance"""
        scored_bills = [
            (bill, self.score_bill_relevance(bill, user_interests))
            for bill in bills
        ]

        return sorted(scored_bills, key=lambda x: x[1], reverse=True)
```

### Alert Generation and Delivery

```python
from enum import Enum
from dataclasses import dataclass
from typing import List

class AlertPriority(Enum):
    CRITICAL = 1
    HIGH = 2
    MEDIUM = 3
    LOW = 4

@dataclass
class UserAlert:
    user_id: str
    bill_id: str
    alert_type: str  # 'new_bill', 'status_update', 'sponsor_action'
    priority: AlertPriority
    relevance_score: float
    subject: str
    message: str
    bill_url: str
    created_at: datetime
    delivery_methods: List[str]  # ['email', 'sms', 'webhook']

class AlertEngine:
    """Generates and delivers alerts"""

    def __init__(self, db_connection, email_service, sms_service):
        self.db = db_connection
        self.email = email_service
        self.sms = sms_service

    def generate_new_bill_alerts(self, bill: NormalizedBill):
        """Generate alerts for newly introduced bills"""

        # Find matching users
        matching_users = self.db.query("""
            SELECT u.id, u.email, u.phone,
                   json_agg(i.interest) as interests
            FROM users u
            JOIN user_interests i ON u.id = i.user_id
            WHERE u.is_active = true
            GROUP BY u.id
        """)

        alerts = []

        for user in matching_users:
            scorer = RelevanceScorer()
            relevance = scorer.score_bill_relevance(
                bill,
                user['interests']
            )

            if relevance > 0.5:  # Threshold
                alert = UserAlert(
                    user_id=user['id'],
                    bill_id=bill.bill_id,
                    alert_type='new_bill',
                    priority=self._determine_priority(relevance),
                    relevance_score=relevance,
                    subject=f"New {bill.jurisdiction} Bill: {bill.title}",
                    message=self._format_alert_message(bill),
                    bill_url=bill.source_url,
                    created_at=datetime.now(),
                    delivery_methods=user.get('delivery_methods', ['email'])
                )
                alerts.append(alert)

        return alerts

    def deliver_alerts(self, alerts: List[UserAlert]):
        """Deliver generated alerts"""
        for alert in alerts:
            # Save to database
            self.db.insert_alert(alert)

            # Deliver via selected methods
            if 'email' in alert.delivery_methods:
                self.email.send(
                    to=alert.user_id,
                    subject=alert.subject,
                    body=alert.message
                )

            if 'sms' in alert.delivery_methods:
                self.sms.send(
                    to=alert.user_id,
                    message=self._format_sms_message(alert)
                )

    def _determine_priority(self, relevance_score: float) -> AlertPriority:
        """Determine priority based on relevance"""
        if relevance_score >= 0.9:
            return AlertPriority.CRITICAL
        elif relevance_score >= 0.8:
            return AlertPriority.HIGH
        elif relevance_score >= 0.6:
            return AlertPriority.MEDIUM
        else:
            return AlertPriority.LOW
```

## Implementation Workflow

### Deployment Pipeline

```yaml
# Kubernetes deployment manifest
apiVersion: apps/v1
kind: Deployment
metadata:
  name: legislative-tracker
  labels:
    app: legislative-tracker
spec:
  replicas: 3
  selector:
    matchLabels:
      app: legislative-tracker
  template:
    metadata:
      labels:
        app: legislative-tracker
    spec:
      containers:
      - name: collector
        image: legislative-tracker:latest
        env:
        - name: CONGRESS_API_KEY
          valueFrom:
            secretKeyRef:
              name: api-keys
              key: congress-api-key
        resources:
          requests:
            memory: "512Mi"
            cpu: "500m"
          limits:
            memory: "2Gi"
            cpu: "2000m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
---
apiVersion: batch/v1
kind: CronJob
metadata:
  name: legislative-tracker-collection
spec:
  schedule: "0 */6 * * *"  # Every 6 hours
  jobTemplate:
    spec:
      template:
        spec:
          containers:
          - name: collector
            image: legislative-tracker:latest
            command: ["python", "collect_bills.py"]
          restartPolicy: OnFailure
```

## Integration Points

### Webhook API

```python
from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/webhooks/bill-update', methods=['POST'])
def bill_update_webhook():
    """Receive bill updates from external sources"""
    data = request.json

    # Validate signature
    if not verify_webhook_signature(request):
        return {'error': 'Invalid signature'}, 401

    # Process update
    bill = normalize_bill(data)
    update_bill_in_database(bill)
    generate_relevant_alerts(bill)

    return {'status': 'processed'}, 200

@app.route('/api/bills/search', methods=['GET'])
def search_bills():
    """Search bills API"""
    query = request.args.get('q', '')
    jurisdiction = request.args.get('jurisdiction', 'federal')
    limit = int(request.args.get('limit', 50))

    results = search_index.search_bills(
        query=query,
        filters={'jurisdiction': jurisdiction}
    )

    return jsonify({
        'query': query,
        'results_count': len(results['hits']['hits']),
        'bills': [hit['_source'] for hit in results['hits']['hits'][:limit]]
    })
```

## Monitoring and Optimization

### Performance Metrics

```python
from prometheus_client import Counter, Histogram, Gauge
from datetime import datetime, timedelta

# Metrics
bills_collected = Counter('bills_collected_total', 'Total bills collected')
collection_errors = Counter('collection_errors_total', 'Collection errors')
bills_processed = Counter('bills_processed_total', 'Bills processed')
alerts_generated = Counter('alerts_generated_total', 'Alerts generated')
alerts_delivered = Counter('alerts_delivered_total', 'Alerts delivered')

collection_time = Histogram('collection_duration_seconds', 'Time to collect bills')
processing_time = Histogram('processing_duration_seconds', 'Time to process bills')
alert_latency = Histogram('alert_latency_seconds', 'Alert generation latency')

bills_in_system = Gauge('bills_total', 'Total bills in system')
stale_bills = Gauge('bills_stale_total', 'Bills not updated in 30 days')

class PerformanceMonitor:
    """Tracks system performance"""

    def __init__(self):
        self.metrics_start_time = datetime.now()

    def get_system_health(self) -> Dict:
        """Get overall system health metrics"""
        return {
            'uptime_hours': (datetime.now() - self.metrics_start_time).total_seconds() / 3600,
            'bills_collected_today': self._bills_collected_today(),
            'collection_success_rate': self._collection_success_rate(),
            'average_processing_time': self._average_processing_time(),
            'alert_delivery_rate': self._alert_delivery_rate(),
            'database_latency_ms': self._database_latency(),
            'search_index_health': self._search_index_health()
        }

    def _collection_success_rate(self) -> float:
        """Calculate success rate of data collection"""
        # Query metrics
        total = bills_collected._value.get() + collection_errors._value.get()
        if total == 0:
            return 1.0
        return bills_collected._value.get() / total
```

## Best Practices

### Data Quality Assurance

1. **Validation Checks**
   - Validate all bill data against schema
   - Check for missing required fields
   - Verify date formats and ranges
   - Confirm URL accessibility

2. **Deduplication**
   - Use bill IDs and numbers as primary uniqueness keys
   - Compare with existing data before insertion
   - Merge amendments and related bills

3. **Content Enrichment**
   - Extract key concepts from bill text
   - Identify affected legislation
   - Tag with relevant industry sectors
   - Extract financial impacts

### Security Considerations

1. **API Security**
   - Implement rate limiting
   - Use API keys for external services
   - Validate all inputs
   - Log all access

2. **Data Protection**
   - Encrypt sensitive user data
   - Use HTTPS for all communications
   - Implement proper access controls
   - Regular security audits

3. **Compliance**
   - GDPR compliance for EU users
   - CCPA compliance for California users
   - Data retention policies
   - User consent management

### Scalability Guidelines

1. **Database Optimization**
   - Implement proper indexing
   - Use partitioning for large tables
   - Archive historical data
   - Regular maintenance (VACUUM, ANALYZE)

2. **Caching Strategy**
   - Cache popular searches
   - Cache bill details
   - Implement TTL policies
   - Monitor cache hit rates

3. **Horizontal Scaling**
   - Containerize services
   - Use load balancers
   - Implement service discovery
   - Monitor resource utilization

### Testing Strategy

```python
import pytest
from unittest.mock import Mock, patch

class TestLegislativeTracking:
    """Test suite for legislative tracking system"""

    @pytest.fixture
    def congress_collector(self):
        return CongressGovCollector(api_key='test_key')

    def test_fetch_bills_success(self, congress_collector):
        """Test successful bill fetching"""
        with patch('requests.Session.get') as mock_get:
            mock_response = Mock()
            mock_response.json.return_value = {
                'bills': [{'type': 'HR', 'number': 1}]
            }
            mock_get.return_value = mock_response

            bills = congress_collector.fetch_bills(118)
            assert len(bills) > 0

    def test_bill_normalization(self):
        """Test bill normalization"""
        normalizer = BillNormalizer()
        test_bill = {
            'bill': {
                'type': 'HR',
                'number': 1234,
                'title': 'Test Bill',
                'url': 'http://example.com',
                'introducedDate': '2023-01-01'
            }
        }

        normalized = normalizer.normalize_federal_bill(test_bill)
        assert normalized.bill_id == 'US-HR1234'
        assert normalized.jurisdiction == 'federal'

    def test_relevance_scoring(self):
        """Test relevance scoring"""
        scorer = RelevanceScorer()
        bill = NormalizedBill(
            bill_id='test',
            keywords=['climate', 'energy'],
            topics=['environment'],
            # ... other fields
        )

        score = scorer.score_bill_relevance(bill, ['climate'])
        assert 0 <= score <= 1
```

### Operational Runbooks

#### Daily Operations
1. Monitor data collection pipeline
2. Review alert delivery logs
3. Check system health metrics
4. Verify database backups

#### Weekly Operations
1. Review data quality metrics
2. Analyze search patterns
3. Update documentation
4. Performance tuning

#### Monthly Operations
1. Generate usage reports
2. Audit access logs
3. Update legislative jurisdictions
4. Security patching

## Conclusion

This guide provides a comprehensive framework for implementing a production-grade legislative tracking system. Key takeaways:

1. **Multi-source data collection** is essential for comprehensive coverage
2. **Real-time processing** enables timely alerts
3. **Relevance scoring** filters noise for user value
4. **Scalable architecture** supports growing data volumes
5. **Continuous monitoring** ensures reliability

Success requires balancing data comprehensiveness, processing speed, and alert relevance while maintaining system reliability and security.
