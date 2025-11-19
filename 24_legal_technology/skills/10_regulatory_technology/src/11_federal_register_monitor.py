"""
Federal Register Monitor - Real-time monitoring of federal regulatory changes.
Tracks proposed rules, notices, and documents published in the Federal Register.
"""

import requests
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import hashlib
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)


@dataclass
class FederalRegisterDocument:
    """Represents a Federal Register document entry."""
    document_id: str
    title: str
    agency: str
    document_type: str
    publication_date: datetime
    comment_deadline: Optional[datetime]
    abstract: str
    url: str
    cfr_references: List[str]


class FederalRegisterMonitor:
    """Monitor and track Federal Register publications for regulatory changes."""

    BASE_URL = "https://www.federalregister.gov/api/v1"

    def __init__(self, api_key: str = None):
        """Initialize the Federal Register monitor."""
        self.api_key = api_key
        self.session = requests.Session()
        self.last_check = None
        self.tracked_agencies = set()
        self.document_cache = {}

    def search_documents(
        self,
        agency: str = None,
        document_type: str = None,
        days_back: int = 7,
        keywords: str = None
    ) -> List[FederalRegisterDocument]:
        """
        Search Federal Register documents with filters.

        Args:
            agency: Filter by agency code
            document_type: Filter by document type (RULE, NOTICE, PROPOSED_RULE)
            days_back: Number of days to search back
            keywords: Search keywords
        """
        params = {
            "per_page": 100,
            "order": "newest"
        }

        if agency:
            params["agencies"] = agency
        if document_type:
            params["type"] = document_type
        if keywords:
            params["conditions[term]"] = keywords

        # Date range
        start_date = datetime.now() - timedelta(days=days_back)
        params["conditions[publication_date][gte]"] = start_date.strftime("%Y-%m-%d")

        try:
            response = self.session.get(
                f"{self.BASE_URL}/documents",
                params=params,
                timeout=10
            )
            response.raise_for_status()

            documents = []
            for doc in response.json()["results"]:
                fed_doc = self._parse_document(doc)
                documents.append(fed_doc)
                self._cache_document(fed_doc)

            return documents
        except requests.RequestException as e:
            logger.error(f"Error searching Federal Register: {e}")
            return []

    def _parse_document(self, doc_data: Dict) -> FederalRegisterDocument:
        """Parse raw API response into FederalRegisterDocument."""
        comment_deadline = None
        if doc_data.get("comments_close_on"):
            comment_deadline = datetime.fromisoformat(
                doc_data["comments_close_on"].replace("Z", "+00:00")
            )

        publication_date = datetime.fromisoformat(
            doc_data["publication_date"]
        )

        cfr_refs = []
        for cfr in doc_data.get("cfr_references", []):
            cfr_refs.append(f"{cfr['title']} CFR {cfr['part']}")

        return FederalRegisterDocument(
            document_id=doc_data["document_number"],
            title=doc_data["title"],
            agency=doc_data["agency_names"][0] if doc_data.get("agency_names") else "",
            document_type=doc_data["type"],
            publication_date=publication_date,
            comment_deadline=comment_deadline,
            abstract=doc_data.get("abstract", ""),
            url=doc_data["html_url"],
            cfr_references=cfr_refs
        )

    def _cache_document(self, doc: FederalRegisterDocument):
        """Cache document for deduplication."""
        doc_hash = hashlib.md5(doc.document_id.encode()).hexdigest()
        self.document_cache[doc_hash] = doc

    def track_agency(self, agency_code: str):
        """Add an agency to tracking list."""
        self.tracked_agencies.add(agency_code)

    def get_new_documents(self) -> List[FederalRegisterDocument]:
        """Get all new documents since last check."""
        documents = []
        for agency in self.tracked_agencies:
            docs = self.search_documents(agency=agency, days_back=1)
            documents.extend(docs)

        self.last_check = datetime.now()
        return documents

    def get_documents_by_agency(self, agency_code: str) -> List[FederalRegisterDocument]:
        """Get all recent documents from specific agency."""
        return self.search_documents(agency=agency_code)

    def get_comment_deadline_documents(self, days_until: int = 7) -> List[FederalRegisterDocument]:
        """Get documents with upcoming comment deadlines."""
        all_docs = self.search_documents(days_back=90)
        upcoming = []

        now = datetime.now()
        cutoff = now + timedelta(days=days_until)

        for doc in all_docs:
            if doc.comment_deadline and now < doc.comment_deadline <= cutoff:
                upcoming.append(doc)

        return sorted(upcoming, key=lambda x: x.comment_deadline)
