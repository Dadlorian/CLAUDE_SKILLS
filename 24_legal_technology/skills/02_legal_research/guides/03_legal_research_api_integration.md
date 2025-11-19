# Legal Research API Integration Guide

## Overview

This guide provides practical instructions for integrating legal research platform APIs into custom applications, practice management systems, and automated workflows.

## Supported Legal Research APIs

### Westlaw Edge API

**Base URL**: `https://api.westlaw.com`
**Authentication**: OAuth 2.0
**Rate Limits**: Tier-based (10-100 requests/second)

**Key Endpoints**:
```
/search/v1/query - Full-text search
/document/v1/retrieve - Get specific document
/keycite/v1/validate - Citation validation
/keycite/v1/citing-references - Get citing cases
/metadata/v1/jurisdictions - Jurisdiction metadata
```

**Authentication Flow**:
```python
import requests

class WestlawAPI:
    def __init__(self, client_id, client_secret):
        self.client_id = client_id
        self.client_secret = client_secret
        self.access_token = None
        self.token_url = "https://signin.westlaw.com/oauth/token"
        self.api_base = "https://api.westlaw.com"

    def authenticate(self):
        """Get OAuth 2.0 access token"""
        data = {
            "grant_type": "client_credentials",
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "scope": "search keycite document"
        }

        response = requests.post(self.token_url, data=data)
        response.raise_for_status()

        self.access_token = response.json()["access_token"]
        return self.access_token

    def search(self, query, database="ALLCASES", limit=50):
        """Execute search query"""
        if not self.access_token:
            self.authenticate()

        endpoint = f"{self.api_base}/search/v1/query"
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }

        payload = {
            "query": query,
            "database": database,
            "fields": ["citation", "title", "court", "date", "snippet"],
            "limit": limit
        }

        response = requests.post(endpoint, json=payload, headers=headers)
        response.raise_for_status()

        return response.json()["results"]

    def keycite(self, citation):
        """Validate citation with KeyCite"""
        if not self.access_token:
            self.authenticate()

        endpoint = f"{self.api_base}/keycite/v1/validate"
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }

        payload = {"citations": [citation]}

        response = requests.post(endpoint, json=payload, headers=headers)
        response.raise_for_status()

        return response.json()["results"][0]

# Usage example
api = WestlawAPI("your_client_id", "your_client_secret")
results = api.search("negligence /s medical")
for result in results[:5]:
    print(f"{result['citation']}: {result['title']}")

# KeyCite check
status = api.keycite("505 U.S. 144")
print(f"Status: {status['status']}")
```

### LexisNexis API

**Base URL**: `https://api.lexisnexis.com`
**Authentication**: API Key
**Rate Limits**: 5-50 requests/second

**Key Endpoints**:
```
/search/v1 - Search cases, statutes
/document/v1 - Retrieve documents
/shepards/v1/citation - Shepardize citations
/analytics/v1/judge - Judge analytics
```

**Implementation**:
```python
class LexisNexisAPI:
    def __init__(self, api_key):
        self.api_key = api_key
        self.api_base = "https://api.lexisnexis.com"

    def search(self, query, sources=["Federal Cases, Combined"], limit=50):
        """Search LexisNexis"""
        endpoint = f"{self.api_base}/search/v1"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        payload = {
            "query": query,
            "sources": sources,
            "limit": limit,
            "sortBy": "relevance"
        }

        response = requests.post(endpoint, json=payload, headers=headers)
        response.raise_for_status()

        return response.json()["documents"]

    def shepardize(self, citation):
        """Shepardize citation"""
        endpoint = f"{self.api_base}/shepards/v1/citation"
        headers = {"Authorization": f"Bearer {self.api_key}"}

        params = {
            "citation": citation,
            "analysis": "full"
        }

        response = requests.get(endpoint, params=params, headers=headers)
        response.raise_for_status()

        return response.json()

# Usage
lexis = LexisNexisAPI("your_api_key")
results = lexis.search("breach AND contract")
shepards = lexis.shepardize("410 U.S. 113")
```

### CourtListener API (Free)

**Base URL**: `https://www.courtlistener.com/api/rest/v3/`
**Authentication**: Token (free registration)
**Rate Limits**: Generous (free tier)

**Implementation**:
```python
class CourtListenerAPI:
    def __init__(self, api_token):
        self.api_token = api_token
        self.api_base = "https://www.courtlistener.com/api/rest/v3/"

    def search_opinions(self, query, court=None, date_filed_after=None):
        """Search case law (free!)"""
        endpoint = f"{self.api_base}search/"
        headers = {"Authorization": f"Token {self.api_token}"}

        params = {
            "q": query,
            "type": "o",  # opinions
            "format": "json",
            "order_by": "score desc"
        }

        if court:
            params["court"] = court

        if date_filed_after:
            params["filed_after"] = date_filed_after

        response = requests.get(endpoint, params=params, headers=headers)
        response.raise_for_status()

        return response.json()["results"]

    def get_opinion(self, opinion_id):
        """Retrieve specific opinion"""
        endpoint = f"{self.api_base}opinions/{opinion_id}/"
        headers = {"Authorization": f"Token {self.api_token}"}

        response = requests.get(endpoint, headers=headers)
        response.raise_for_status()

        return response.json()

# Usage
cl = CourtListenerAPI("your_token")
scotus_cases = cl.search_opinions("patent", court="scotus")
```

## Integration Patterns

### Pattern 1: Research Automation Pipeline

```python
class LegalResearchPipeline:
    """Automated research workflow"""

    def __init__(self):
        self.westlaw = WestlawAPI(WL_CLIENT_ID, WL_CLIENT_SECRET)
        self.lexis = LexisNexisAPI(LEXIS_API_KEY)
        self.courtlistener = CourtListenerAPI(CL_TOKEN)

    def comprehensive_research(self, legal_issue, jurisdiction):
        """Execute multi-platform research"""
        results = {
            "westlaw": self.westlaw.search(legal_issue),
            "lexis": self.lexis.search(legal_issue),
            "courtlistener": self.courtlistener.search_opinions(legal_issue)
        }

        # Deduplicate across platforms
        unique_cases = self.deduplicate_citations(results)

        # Validate citations
        validated = self.validate_all_citations(unique_cases)

        # Rank by relevance and authority
        ranked = self.rank_results(validated, jurisdiction)

        return {
            "total_sources": len(unique_cases),
            "top_authorities": ranked[:20],
            "research_date": datetime.now(),
            "platforms_searched": ["Westlaw", "LexisNexis", "CourtListener"]
        }

    def validate_all_citations(self, citations):
        """Validate citations across platforms"""
        validated = []

        for citation in citations:
            # KeyCite check
            kc = self.westlaw.keycite(citation)

            # Shepard's check
            shep = self.lexis.shepardize(citation)

            validated.append({
                "citation": citation,
                "keycite_status": kc["status"],
                "shepards_signal": shep["signal"],
                "good_law": self.determine_good_law(kc, shep)
            })

        return validated

# Usage
pipeline = LegalResearchPipeline()
research_results = pipeline.comprehensive_research(
    "summary judgment standard",
    "federal"
)
```

### Pattern 2: Practice Management Integration

```python
class PracticeManagementIntegration:
    """Integrate research APIs with practice management system"""

    def __init__(self, pm_system):
        self.pm_system = pm_system  # Clio, MyCase, etc.
        self.westlaw = WestlawAPI(WL_CLIENT_ID, WL_CLIENT_SECRET)

    def matter_based_research(self, matter_id, research_query):
        """Link research to specific matter"""
        # Get matter details from PM system
        matter = self.pm_system.get_matter(matter_id)

        # Execute research
        research_results = self.westlaw.search(research_query)

        # Store research in matter
        research_memo = self.create_research_memo(
            matter_id,
            research_query,
            research_results
        )

        # Save to PM system
        self.pm_system.add_document(matter_id, research_memo)

        # Log time
        self.pm_system.log_time(
            matter_id=matter_id,
            activity="Legal Research",
            time=calculate_research_time(research_results),
            description=f"Researched: {research_query}"
        )

        return research_memo

    def automated_citation_monitoring(self, matter_id):
        """Monitor citations used in matter"""
        # Extract citations from matter documents
        citations = self.pm_system.extract_citations_from_matter(matter_id)

        # Set up monitoring
        for citation in citations:
            # Create alert
            alert = self.westlaw.create_keycite_alert(citation)

            # Store alert reference
            self.pm_system.add_matter_note(
                matter_id,
                f"KeyCite alert created for {citation}"
            )

        return {"citations_monitored": len(citations)}
```

### Pattern 3: Document Assembly Integration

```python
class DocumentAssemblyIntegration:
    """Integrate research APIs with document automation"""

    def __init__(self, document_system):
        self.document_system = document_system
        self.westlaw = WestlawAPI(WL_CLIENT_ID, WL_CLIENT_SECRET)

    def auto_cite_validation_on_save(self, document):
        """Validate citations when document saved"""
        # Extract citations from document
        citations = self.extract_citations_from_document(document)

        # Validate each citation
        validation_results = []

        for citation in citations:
            status = self.westlaw.keycite(citation)

            if status["status"] in ["red_flag", "yellow_flag"]:
                validation_results.append({
                    "citation": citation,
                    "status": status["status"],
                    "action": "FLAG_FOR_REVIEW"
                })

                # Highlight in document
                self.document_system.highlight_text(
                    document,
                    citation,
                    color="red" if status["status"] == "red_flag" else "yellow"
                )

        # Alert user if problematic citations found
        if validation_results:
            self.document_system.show_alert(
                f"{len(validation_results)} citations require review"
            )

        return validation_results
```

## Best Practices for API Integration

### 1. Error Handling

```python
import time
from requests.exceptions import HTTPError, Timeout, ConnectionError

class RobustAPIClient:
    """API client with robust error handling"""

    def __init__(self, api):
        self.api = api
        self.max_retries = 3
        self.backoff_factor = 2

    def execute_with_retry(self, api_call, *args, **kwargs):
        """Execute API call with exponential backoff retry"""
        for attempt in range(self.max_retries):
            try:
                return api_call(*args, **kwargs)

            except HTTPError as e:
                if e.response.status_code == 429:  # Rate limit
                    wait_time = self.backoff_factor ** attempt
                    print(f"Rate limited. Waiting {wait_time}s...")
                    time.sleep(wait_time)
                elif e.response.status_code >= 500:  # Server error
                    if attempt < self.max_retries - 1:
                        time.sleep(self.backoff_factor ** attempt)
                    else:
                        raise
                else:
                    raise  # Client error, don't retry

            except Timeout:
                if attempt < self.max_retries - 1:
                    time.sleep(self.backoff_factor ** attempt)
                else:
                    raise

            except ConnectionError:
                if attempt < self.max_retries - 1:
                    time.sleep(self.backoff_factor ** attempt)
                else:
                    raise

        raise Exception(f"Failed after {self.max_retries} attempts")

# Usage
robust_client = RobustAPIClient(westlaw_api)
results = robust_client.execute_with_retry(
    westlaw_api.search,
    "negligence"
)
```

### 2. Caching

```python
import hashlib
import json
from functools import lru_cache

class CachedAPIClient:
    """API client with caching to reduce costs"""

    def __init__(self, api, cache_ttl=3600):
        self.api = api
        self.cache = {}
        self.cache_ttl = cache_ttl  # seconds

    def cached_search(self, query, database="ALLCASES"):
        """Search with caching"""
        # Generate cache key
        cache_key = self.generate_cache_key(query, database)

        # Check cache
        if cache_key in self.cache:
            cached_data, timestamp = self.cache[cache_key]
            if (datetime.now() - timestamp).seconds < self.cache_ttl:
                print("Returning cached results")
                return cached_data

        # Execute API call
        results = self.api.search(query, database)

        # Store in cache
        self.cache[cache_key] = (results, datetime.now())

        return results

    def generate_cache_key(self, *args):
        """Generate cache key from arguments"""
        key_string = json.dumps(args, sort_keys=True)
        return hashlib.md5(key_string.encode()).hexdigest()
```

### 3. Rate Limiting

```python
import time
from collections import deque

class RateLimitedAPIClient:
    """API client with rate limiting"""

    def __init__(self, api, max_requests_per_second=10):
        self.api = api
        self.max_requests_per_second = max_requests_per_second
        self.request_times = deque()

    def rate_limited_call(self, api_method, *args, **kwargs):
        """Execute API call with rate limiting"""
        current_time = time.time()

        # Remove requests older than 1 second
        while self.request_times and current_time - self.request_times[0] > 1:
            self.request_times.popleft()

        # Check if at rate limit
        if len(self.request_times) >= self.max_requests_per_second:
            sleep_time = 1 - (current_time - self.request_times[0])
            if sleep_time > 0:
                time.sleep(sleep_time)

        # Execute request
        result = api_method(*args, **kwargs)

        # Record request time
        self.request_times.append(time.time())

        return result
```

### 4. Logging and Monitoring

```python
import logging

class MonitoredAPIClient:
    """API client with comprehensive logging"""

    def __init__(self, api):
        self.api = api
        self.logger = logging.getLogger(__name__)
        self.metrics = {
            "total_requests": 0,
            "successful_requests": 0,
            "failed_requests": 0,
            "total_latency": 0
        }

    def monitored_search(self, query):
        """Search with monitoring"""
        start_time = time.time()

        try:
            self.logger.info(f"Executing search: {query}")

            results = self.api.search(query)

            latency = time.time() - start_time

            # Update metrics
            self.metrics["total_requests"] += 1
            self.metrics["successful_requests"] += 1
            self.metrics["total_latency"] += latency

            self.logger.info(
                f"Search completed in {latency:.2f}s. Results: {len(results)}"
            )

            return results

        except Exception as e:
            self.metrics["total_requests"] += 1
            self.metrics["failed_requests"] += 1

            self.logger.error(f"Search failed: {str(e)}")
            raise

    def get_metrics(self):
        """Get performance metrics"""
        return {
            **self.metrics,
            "avg_latency": self.metrics["total_latency"] / self.metrics["total_requests"]
                            if self.metrics["total_requests"] > 0 else 0,
            "success_rate": self.metrics["successful_requests"] / self.metrics["total_requests"]
                            if self.metrics["total_requests"] > 0 else 0
        }
```

---

*Legal research API integration enables automation, cost savings, and enhanced research capabilities when implemented with proper error handling, caching, and monitoring.*
