"""
USPTO API Client for Patent and Trademark Data Retrieval
Integrates with USPTO Patent Examination Data System (PEDS) and Trademark Search API
"""

import json
import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)


@dataclass
class PatentData:
    """Patent data structure"""
    patent_number: str
    title: str
    abstract: str
    filing_date: datetime
    issue_date: Optional[datetime]
    inventors: List[str]
    assignee: Optional[str]
    claims_count: int
    ipc_class: List[str]
    cpc_class: List[str]
    status: str
    citations: List[str]


@dataclass
class TrademarkData:
    """Trademark data structure"""
    serial_number: str
    mark: str
    mark_type: str
    filing_date: datetime
    registration_date: Optional[datetime]
    applicant_name: str
    goods_services: str
    status: str
    owner: str


class USPTOAPIClient(ABC):
    """Abstract base class for USPTO API clients"""

    @abstractmethod
    def authenticate(self) -> None:
        """Authenticate with the API"""
        pass

    @abstractmethod
    def search(self, query: str) -> List[Dict[str, Any]]:
        """Search for records"""
        pass


class PatentAPIClient(USPTOAPIClient):
    """Client for USPTO Patent data via PEDS and Open Data API"""

    def __init__(self, api_key: Optional[str] = None, timeout: int = 30):
        """
        Initialize Patent API Client

        Args:
            api_key: Optional USPTO API key for authenticated requests
            timeout: Request timeout in seconds
        """
        self.api_key = api_key
        self.timeout = timeout
        self.base_url = "https://developer.uspto.gov/ibd-api"
        self.opendata_url = "https://data.uspto.gov"

        # Configure session with retries
        self.session = self._create_session()

    def _create_session(self) -> requests.Session:
        """Create requests session with retry strategy"""
        session = requests.Session()
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        return session

    def authenticate(self) -> None:
        """Authenticate with USPTO API (key-based)"""
        if not self.api_key:
            logger.warning("No API key provided. Limited to public endpoints.")
            return

        self.session.headers.update({
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        })

    def search(self, query: str, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Search patents using USPTO Open Data API

        Args:
            query: Search query (CQL syntax supported)
            limit: Maximum results to return

        Returns:
            List of patent data dictionaries
        """
        try:
            # Using USPTO Open Data API (no authentication required)
            url = f"{self.opendata_url}/api/v1/patents"
            params = {
                "q": query,
                "fl": "patent_number,title,abstract,filing_date,issue_date,inventor_name",
                "rows": limit,
                "sort": "filing_date desc"
            }

            response = self.session.get(
                url,
                params=params,
                timeout=self.timeout
            )
            response.raise_for_status()

            data = response.json()
            return data.get("results", [])

        except requests.RequestException as e:
            logger.error(f"Patent search failed: {e}")
            raise

    def get_patent_by_number(self, patent_number: str) -> Optional[PatentData]:
        """
        Retrieve detailed patent information by patent number

        Args:
            patent_number: US patent number (with or without leading zeros)

        Returns:
            PatentData object or None if not found
        """
        try:
            # Search for specific patent
            results = self.search(f'patent_number:"{patent_number}"')

            if not results:
                logger.info(f"Patent {patent_number} not found")
                return None

            patent = results[0]

            return PatentData(
                patent_number=patent.get("patent_number", ""),
                title=patent.get("title", ""),
                abstract=patent.get("abstract", ""),
                filing_date=self._parse_date(patent.get("filing_date")),
                issue_date=self._parse_date(patent.get("issue_date")),
                inventors=patent.get("inventor_name", []),
                assignee=patent.get("assignee_name", ""),
                claims_count=int(patent.get("claims_count", 0)),
                ipc_class=patent.get("ipc_class", []),
                cpc_class=patent.get("cpc_class", []),
                status=patent.get("status", ""),
                citations=patent.get("cited_by", [])
            )

        except Exception as e:
            logger.error(f"Failed to retrieve patent {patent_number}: {e}")
            return None

    def _parse_date(self, date_str: Optional[str]) -> Optional[datetime]:
        """Parse date string in various formats"""
        if not date_str:
            return None

        formats = ["%Y-%m-%d", "%Y/%m/%d", "%m/%d/%Y"]
        for fmt in formats:
            try:
                return datetime.strptime(date_str, fmt)
            except ValueError:
                continue

        return None


class TrademarkAPIClient(USPTOAPIClient):
    """Client for USPTO Trademark data via TESS and Open Data API"""

    def __init__(self, api_key: Optional[str] = None, timeout: int = 30):
        """
        Initialize Trademark API Client

        Args:
            api_key: Optional USPTO API key
            timeout: Request timeout in seconds
        """
        self.api_key = api_key
        self.timeout = timeout
        self.tess_url = "https://ttsearch.uspto.gov/bin/gate.exe"
        self.opendata_url = "https://data.uspto.gov"
        self.session = self._create_session()

    def _create_session(self) -> requests.Session:
        """Create requests session with retry strategy"""
        session = requests.Session()
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        return session

    def authenticate(self) -> None:
        """Trademark API uses different auth mechanism"""
        pass

    def search(self, query: str, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Search trademarks using USPTO Open Data API

        Args:
            query: Search query
            limit: Maximum results to return

        Returns:
            List of trademark data dictionaries
        """
        try:
            url = f"{self.opendata_url}/api/v1/trademarks"
            params = {
                "q": query,
                "fl": "serial_number,mark,status,filing_date,registration_date",
                "rows": limit
            }

            response = self.session.get(
                url,
                params=params,
                timeout=self.timeout
            )
            response.raise_for_status()

            data = response.json()
            return data.get("results", [])

        except requests.RequestException as e:
            logger.error(f"Trademark search failed: {e}")
            raise

    def get_trademark_by_serial(self, serial_number: str) -> Optional[TrademarkData]:
        """
        Retrieve detailed trademark information by serial number

        Args:
            serial_number: Trademark serial number

        Returns:
            TrademarkData object or None if not found
        """
        try:
            results = self.search(f'serial_number:"{serial_number}"')

            if not results:
                logger.info(f"Trademark {serial_number} not found")
                return None

            tm = results[0]

            return TrademarkData(
                serial_number=tm.get("serial_number", ""),
                mark=tm.get("mark", ""),
                mark_type=tm.get("mark_type", ""),
                filing_date=self._parse_date(tm.get("filing_date")),
                registration_date=self._parse_date(tm.get("registration_date")),
                applicant_name=tm.get("applicant_name", ""),
                goods_services=tm.get("goods_services", ""),
                status=tm.get("status", ""),
                owner=tm.get("owner", "")
            )

        except Exception as e:
            logger.error(f"Failed to retrieve trademark {serial_number}: {e}")
            return None

    def _parse_date(self, date_str: Optional[str]) -> Optional[datetime]:
        """Parse date string"""
        if not date_str:
            return None

        formats = ["%Y-%m-%d", "%Y/%m/%d", "%m/%d/%Y"]
        for fmt in formats:
            try:
                return datetime.strptime(date_str, fmt)
            except ValueError:
                continue

        return None


class WIPOAPIClient:
    """Client for WIPO (World Intellectual Property Organization) data"""

    def __init__(self, timeout: int = 30):
        """
        Initialize WIPO API Client

        Args:
            timeout: Request timeout in seconds
        """
        self.timeout = timeout
        self.base_url = "https://www.wipo.int"
        self.session = self._create_session()

    def _create_session(self) -> requests.Session:
        """Create requests session"""
        session = requests.Session()
        session.headers.update({
            "User-Agent": "USPTOWIPOClient/1.0"
        })
        return session

    def search_pct_applications(self, query: str) -> List[Dict[str, Any]]:
        """
        Search PCT (Patent Cooperation Treaty) applications

        Args:
            query: Search query

        Returns:
            List of PCT application data
        """
        # WIPO provides data through various channels
        # This is a placeholder for WIPO integration
        logger.info(f"Searching PCT applications: {query}")
        return []

    def get_designated_states(self, pct_number: str) -> List[str]:
        """
        Get designated states/countries for a PCT application

        Args:
            pct_number: PCT application number

        Returns:
            List of designated state codes
        """
        logger.info(f"Retrieving designated states for {pct_number}")
        return []


def main():
    """Example usage"""
    # Patent search
    patent_client = PatentAPIClient(timeout=30)
    patent_results = patent_client.search("solar panel", limit=10)
    print(f"Found {len(patent_results)} patents")

    # Get specific patent
    if patent_results:
        patent_number = patent_results[0].get("patent_number")
        patent_data = patent_client.get_patent_by_number(patent_number)
        if patent_data:
            print(f"Patent: {patent_data.title}")

    # Trademark search
    tm_client = TrademarkAPIClient(timeout=30)
    tm_results = tm_client.search("APPLE", limit=10)
    print(f"Found {len(tm_results)} trademarks")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()
