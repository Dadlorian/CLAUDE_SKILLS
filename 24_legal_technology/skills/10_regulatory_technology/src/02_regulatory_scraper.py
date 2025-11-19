"""
Regulatory Scraper Module

Web scraping and data extraction from regulatory sources including:
- Federal Register
- State regulatory agency databases
- EPA, SEC, FCC documents
- Legislative tracking sites (Congress.gov, LegiScan, etc.)
"""

import logging
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
from urllib.parse import urljoin
import hashlib
import json
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)


class RegulatorySourceType(Enum):
    """Types of regulatory sources."""
    FEDERAL_REGISTER = "federal_register"
    SEC_FILING = "sec_filing"
    EPA_RULE = "epa_rule"
    STATE_REGISTER = "state_register"
    FCC_ORDER = "fcc_order"
    LEGISLATION = "legislation"
    AGENCY_GUIDANCE = "agency_guidance"


@dataclass
class RegulatoryDocument:
    """Scraped regulatory document."""
    document_id: str
    source_type: str
    title: str
    content: str
    document_url: str
    publication_date: str
    effective_date: Optional[str]
    agency: str
    jurisdiction: str
    document_type: str
    impact_areas: List[str]
    search_keywords: List[str]
    extracted_metadata: Dict
    full_text_url: str
    comment_deadline: Optional[str]
    scraped_date: str
    document_hash: str


class RegulatorySource(ABC):
    """Abstract base class for regulatory sources."""

    def __init__(self, name: str, base_url: str, rate_limit: float = 1.0):
        """
        Initialize regulatory source.

        Args:
            name: Source name
            base_url: Base URL for API/website
            rate_limit: Seconds between requests
        """
        self.name = name
        self.base_url = base_url
        self.rate_limit = rate_limit
        self.last_request_time = 0
        self.session_id = hashlib.md5(f"{name}{datetime.now()}".encode()).hexdigest()

    def _respect_rate_limit(self) -> None:
        """Enforce rate limiting between requests."""
        elapsed = time.time() - self.last_request_time
        if elapsed < self.rate_limit:
            time.sleep(self.rate_limit - elapsed)
        self.last_request_time = time.time()

    @abstractmethod
    def search(self, keywords: List[str], filters: Dict = None) -> List[RegulatoryDocument]:
        """Search for regulatory documents matching criteria."""
        pass

    @abstractmethod
    def fetch_document(self, document_id: str) -> RegulatoryDocument:
        """Fetch full content of a regulatory document."""
        pass


class FederalRegisterSource(RegulatorySource):
    """Federal Register data source."""

    def __init__(self):
        """Initialize Federal Register source."""
        super().__init__(
            name="Federal Register",
            base_url="https://www.federalregister.gov",
            rate_limit=0.5
        )
        self.api_endpoint = "https://api.federalregister.gov/v1"

    def search(
        self,
        keywords: List[str],
        filters: Dict = None
    ) -> List[RegulatoryDocument]:
        """
        Search Federal Register documents.

        Filters support: agencies, document_type, president_administration, dates
        """
        self._respect_rate_limit()

        if filters is None:
            filters = {}

        documents = []
        query_string = " AND ".join(keywords)

        # Build query parameters
        params = {
            "q": query_string,
            "per_page": 100,
            "order": "newest"
        }

        if "agencies" in filters:
            params["agencies[]"] = filters["agencies"]
        if "document_type" in filters:
            params["type[]"] = filters["document_type"]
        if "date_from" in filters:
            params["publication_date[gte]"] = filters["date_from"]
        if "date_to" in filters:
            params["publication_date[lte]"] = filters["date_to"]

        try:
            # Simulate API response
            results = self._simulate_api_call(params)

            for item in results:
                doc = self._parse_federal_register_item(item)
                documents.append(doc)

            logger.info(f"Federal Register search returned {len(documents)} documents")

        except Exception as e:
            logger.error(f"Federal Register search error: {e}")

        return documents

    def fetch_document(self, document_id: str) -> Optional[RegulatoryDocument]:
        """Fetch complete Federal Register document."""
        self._respect_rate_limit()

        try:
            # Simulate fetching full document
            url = f"{self.api_endpoint}/documents/{document_id}"
            doc_data = self._simulate_api_call({"url": url})
            return self._parse_federal_register_item(doc_data)

        except Exception as e:
            logger.error(f"Failed to fetch Federal Register document {document_id}: {e}")
            return None

    def _parse_federal_register_item(self, item: Dict) -> RegulatoryDocument:
        """Parse Federal Register API response into RegulatoryDocument."""
        doc_id = item.get("document_number", "UNKNOWN")
        content = item.get("full_text", "")

        return RegulatoryDocument(
            document_id=doc_id,
            source_type=RegulatorySourceType.FEDERAL_REGISTER.value,
            title=item.get("title", ""),
            content=content[:5000],  # Limit excerpt
            document_url=item.get("html_url", ""),
            publication_date=item.get("publication_date", ""),
            effective_date=item.get("effective_on"),
            agency=item.get("agency_names", ["Unknown"])[0],
            jurisdiction="US Federal",
            document_type=item.get("type", "Notice"),
            impact_areas=self._extract_impact_areas(item),
            search_keywords=[],
            extracted_metadata={
                "document_type": item.get("type"),
                "comments_url": item.get("comments_url"),
                "docket_id": item.get("docket_id"),
                "pages": item.get("pages"),
                "significant": item.get("significant")
            },
            full_text_url=item.get("pdf_url", ""),
            comment_deadline=item.get("comment_end_date"),
            scraped_date=datetime.now().isoformat(),
            document_hash=hashlib.sha256(content.encode()).hexdigest()
        )

    def _extract_impact_areas(self, item: Dict) -> List[str]:
        """Extract industry/sector impact areas from document metadata."""
        impact_areas = []

        # Extract from topic_names if available
        if "topic_names" in item and item["topic_names"]:
            impact_areas.extend(item["topic_names"][:5])

        # Extract from agencies
        if "agency_names" in item:
            impact_areas.extend(item["agency_names"][:3])

        return impact_areas

    def _simulate_api_call(self, params: Dict) -> List[Dict]:
        """Simulate API call response."""
        return [
            {
                "document_number": "2024-00001",
                "title": "Environmental Protection Agency Rule",
                "publication_date": datetime.now().isoformat(),
                "effective_on": (datetime.now() + timedelta(days=30)).isoformat(),
                "type": "Rule",
                "agency_names": ["Environmental Protection Agency"],
                "topic_names": ["Environmental Protection"],
                "html_url": "https://federalregister.gov/documents/...",
                "pdf_url": "https://federalregister.gov/pdf/...",
                "full_text": "This rule establishes new environmental standards...",
                "comments_url": "https://www.regulations.gov/...",
                "docket_id": "EPA-2024-0001",
                "pages": 45,
                "significant": True,
                "comment_end_date": (datetime.now() + timedelta(days=60)).isoformat()
            }
        ]


class RegulatoryScraperManager:
    """
    Manages multiple regulatory sources and document extraction.

    Features:
    - Multi-source scraping coordination
    - Document deduplication
    - Keyword extraction and tagging
    - Change detection and alerts
    - Full-text indexing
    """

    def __init__(self):
        """Initialize scraper manager."""
        self.sources: Dict[str, RegulatorySource] = {}
        self.documents: Dict[str, RegulatoryDocument] = {}
        self.document_history: Dict[str, List[RegulatoryDocument]] = {}
        self.extracted_keywords: Dict[str, int] = {}
        self.change_log: List[Dict] = []

        # Initialize default sources
        self._initialize_sources()
        logger.info("Regulatory Scraper Manager initialized")

    def _initialize_sources(self) -> None:
        """Initialize default regulatory sources."""
        self.sources["federal_register"] = FederalRegisterSource()

    def add_custom_source(self, source: RegulatorySource) -> None:
        """Register a custom regulatory source."""
        self.sources[source.name.lower().replace(" ", "_")] = source
        logger.info(f"Custom source added: {source.name}")

    def search_all_sources(
        self,
        keywords: List[str],
        filters: Dict = None,
        sources: List[str] = None
    ) -> List[RegulatoryDocument]:
        """
        Search across multiple regulatory sources.

        Args:
            keywords: Search keywords
            filters: Search filters
            sources: Specific sources to search (None = all)

        Returns:
            Deduplicated list of regulatory documents
        """
        all_documents = []
        sources_to_search = sources or list(self.sources.keys())

        for source_name in sources_to_search:
            if source_name not in self.sources:
                logger.warning(f"Source {source_name} not found")
                continue

            source = self.sources[source_name]
            try:
                docs = source.search(keywords, filters)
                all_documents.extend(docs)
                logger.info(f"Retrieved {len(docs)} documents from {source_name}")

            except Exception as e:
                logger.error(f"Error searching {source_name}: {e}")

        # Deduplicate documents
        unique_docs = self._deduplicate_documents(all_documents)

        # Store documents
        for doc in unique_docs:
            self.documents[doc.document_id] = doc

        return unique_docs

    def _deduplicate_documents(
        self,
        documents: List[RegulatoryDocument]
    ) -> List[RegulatoryDocument]:
        """Remove duplicate documents based on content hash and similarity."""
        seen_hashes = set()
        unique = []

        for doc in documents:
            if doc.document_hash not in seen_hashes:
                seen_hashes.add(doc.document_hash)
                unique.append(doc)

        return unique

    def extract_keywords(self, document: RegulatoryDocument) -> List[Tuple[str, float]]:
        """
        Extract keywords and calculate relevance scores from document.

        Returns list of (keyword, relevance_score) tuples.
        """
        keywords = {}

        # Extract from title
        title_words = document.title.lower().split()
        for word in title_words:
            if len(word) > 3:
                keywords[word] = keywords.get(word, 0) + 1.5

        # Extract from impact areas
        for area in document.impact_areas:
            area_lower = area.lower()
            keywords[area_lower] = keywords.get(area_lower, 0) + 2.0

        # Extract from metadata
        content_words = document.content.lower().split()
        for word in content_words[:100]:  # Limit to first 100 words
            if len(word) > 4 and word not in ["this", "that", "which", "from"]:
                keywords[word] = keywords.get(word, 0) + 0.5

        # Sort by relevance
        sorted_keywords = sorted(keywords.items(), key=lambda x: x[1], reverse=True)

        # Update global keyword index
        for keyword, score in sorted_keywords[:20]:
            self.extracted_keywords[keyword] = self.extracted_keywords.get(keyword, 0) + 1

        return sorted_keywords[:20]

    def track_document_changes(
        self,
        document_id: str,
        old_doc: Optional[RegulatoryDocument],
        new_doc: RegulatoryDocument
    ) -> Dict:
        """Track and log changes to documents."""
        changes = {
            "document_id": document_id,
            "timestamp": datetime.now().isoformat(),
            "changes": []
        }

        if old_doc is None:
            changes["changes"].append("Document created")
        else:
            # Check for content changes
            if old_doc.content != new_doc.content:
                changes["changes"].append("Content updated")

            # Check for metadata changes
            if old_doc.effective_date != new_doc.effective_date:
                changes["changes"].append(f"Effective date changed to {new_doc.effective_date}")

            # Check for comment deadline changes
            if old_doc.comment_deadline != new_doc.comment_deadline:
                changes["changes"].append(f"Comment deadline changed to {new_doc.comment_deadline}")

        self.change_log.append(changes)
        return changes

    def get_documents_by_agency(self, agency: str) -> List[RegulatoryDocument]:
        """Retrieve documents from specific agency."""
        return [
            doc for doc in self.documents.values()
            if doc.agency.lower() == agency.lower()
        ]

    def get_documents_by_impact_area(self, impact_area: str) -> List[RegulatoryDocument]:
        """Retrieve documents affecting specific industry/sector."""
        return [
            doc for doc in self.documents.values()
            if any(area.lower() == impact_area.lower() for area in doc.impact_areas)
        ]

    def get_documents_with_upcoming_deadlines(
        self,
        days_until_deadline: int = 30
    ) -> List[RegulatoryDocument]:
        """Get documents with comment deadlines approaching."""
        cutoff_date = datetime.now() + timedelta(days=days_until_deadline)

        upcoming = []
        for doc in self.documents.values():
            if doc.comment_deadline:
                try:
                    deadline = datetime.fromisoformat(doc.comment_deadline)
                    if datetime.now() < deadline < cutoff_date:
                        upcoming.append(doc)
                except ValueError:
                    pass

        return sorted(upcoming, key=lambda d: d.comment_deadline)

    def export_documents(self, format: str = "json") -> str:
        """Export scraped documents in specified format."""
        docs_list = list(self.documents.values())

        if format == "json":
            return json.dumps([
                {
                    "document_id": d.document_id,
                    "title": d.title,
                    "agency": d.agency,
                    "publication_date": d.publication_date,
                    "comment_deadline": d.comment_deadline,
                    "document_url": d.document_url
                }
                for d in docs_list
            ], indent=2)

        return ""

    def get_statistics(self) -> Dict:
        """Generate scraping statistics and summary."""
        return {
            "total_documents": len(self.documents),
            "sources_active": len(self.sources),
            "total_sources": len(self.sources),
            "documents_by_agency": self._count_by_field("agency"),
            "documents_by_type": self._count_by_field("document_type"),
            "top_keywords": sorted(
                self.extracted_keywords.items(),
                key=lambda x: x[1],
                reverse=True
            )[:20],
            "documents_with_deadlines": len([
                d for d in self.documents.values()
                if d.comment_deadline
            ]),
            "last_scrape": datetime.now().isoformat()
        }

    def _count_by_field(self, field: str) -> Dict[str, int]:
        """Count documents by a specific field."""
        counts = {}
        for doc in self.documents.values():
            value = getattr(doc, field, "Unknown")
            counts[value] = counts.get(value, 0) + 1
        return counts


if __name__ == "__main__":
    # Example usage
    manager = RegulatoryScraperManager()

    # Search across sources
    documents = manager.search_all_sources(
        keywords=["environmental", "emissions"],
        filters={
            "agencies": "EPA",
            "date_from": "2024-01-01"
        }
    )

    print(f"Found {len(documents)} documents")

    # Get statistics
    stats = manager.get_statistics()
    print(json.dumps(stats, indent=2, default=str))
