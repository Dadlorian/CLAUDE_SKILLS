"""
Quorum API Integration - Integrate with Quorum's government relations data platform.
Provides access to legislative intelligence, lobbying data, and politician profiles.
"""

import requests
from typing import List, Dict, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class QuorumPolitician:
    """Represents a politician from Quorum."""

    def __init__(self, data: Dict):
        """Initialize politician from Quorum API response."""
        self.quorum_id = data.get("id")
        self.name = data.get("name")
        self.title = data.get("title")
        self.state = data.get("state")
        self.district = data.get("district")
        self.party = data.get("party")
        self.phone = data.get("phone")
        self.email = data.get("email")
        self.office_address = data.get("office_address")
        self.committees = data.get("committees", [])
        self.bills_sponsored = data.get("bills_sponsored", [])
        self.social_accounts = data.get("social_accounts", {})


class QuorumBill:
    """Represents a bill from Quorum."""

    def __init__(self, data: Dict):
        """Initialize bill from Quorum API response."""
        self.quorum_id = data.get("id")
        self.bill_number = data.get("bill_number")
        self.title = data.get("title")
        self.description = data.get("description")
        self.chamber = data.get("chamber")  # House or Senate
        self.introduced_date = data.get("introduced_date")
        self.current_status = data.get("current_status")
        self.sponsor = data.get("sponsor")
        self.cosponsors = data.get("cosponsors", [])
        self.committees = data.get("committees", [])
        self.votes = data.get("votes", [])
        self.current_text = data.get("current_text")
        self.keywords = data.get("keywords", [])
        self.impact_score = data.get("impact_score")


class QuorumLobbyingRecord:
    """Represents a lobbying disclosure record."""

    def __init__(self, data: Dict):
        """Initialize lobbying record from Quorum."""
        self.record_id = data.get("id")
        self.lobbyist_name = data.get("lobbyist_name")
        self.client = data.get("client")
        self.lobbying_issues = data.get("lobbying_issues", [])
        self.lobbying_activities = data.get("lobbying_activities", [])
        self.reported_expenses = data.get("reported_expenses")
        self.reporting_period = data.get("reporting_period")
        self.legislators_contacted = data.get("legislators_contacted", [])
        self.agencies_contacted = data.get("agencies_contacted", [])


class QuorumIntegration:
    """Integration with Quorum government relations API."""

    BASE_URL = "https://api.quorum.us/api/v1"

    def __init__(self, api_key: str):
        """Initialize Quorum API integration."""
        self.api_key = api_key
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        })
        self.cache = {}

    def search_bills(
        self,
        keywords: str = None,
        state: str = None,
        chamber: str = None,
        status: str = None,
        limit: int = 50
    ) -> List[QuorumBill]:
        """
        Search for bills in Quorum database.

        Args:
            keywords: Search terms
            state: State abbreviation
            chamber: "house" or "senate"
            status: Bill status
            limit: Result limit
        """
        try:
            params = {
                "limit": limit
            }

            if keywords:
                params["q"] = keywords
            if state:
                params["state"] = state
            if chamber:
                params["chamber"] = chamber
            if status:
                params["status"] = status

            response = self.session.get(
                f"{self.BASE_URL}/bills",
                params=params,
                timeout=10
            )
            response.raise_for_status()

            bills = [QuorumBill(bill_data) for bill_data in response.json()["results"]]
            logger.info(f"Found {len(bills)} bills")
            return bills

        except requests.RequestException as e:
            logger.error(f"Error searching bills: {e}")
            return []

    def get_bill_details(self, bill_id: str) -> Optional[QuorumBill]:
        """Get detailed information about a specific bill."""
        try:
            response = self.session.get(
                f"{self.BASE_URL}/bills/{bill_id}",
                timeout=10
            )
            response.raise_for_status()

            return QuorumBill(response.json())

        except requests.RequestException as e:
            logger.error(f"Error fetching bill details: {e}")
            return None

    def search_politicians(
        self,
        name: str = None,
        state: str = None,
        title: str = None,
        limit: int = 50
    ) -> List[QuorumPolitician]:
        """
        Search for politicians in Quorum database.

        Args:
            name: Politician name
            state: State abbreviation
            title: "Senator", "Representative", etc.
            limit: Result limit
        """
        try:
            params = {
                "limit": limit
            }

            if name:
                params["name"] = name
            if state:
                params["state"] = state
            if title:
                params["title"] = title

            response = self.session.get(
                f"{self.BASE_URL}/politicians",
                params=params,
                timeout=10
            )
            response.raise_for_status()

            politicians = [
                QuorumPolitician(p_data)
                for p_data in response.json()["results"]
            ]
            logger.info(f"Found {len(politicians)} politicians")
            return politicians

        except requests.RequestException as e:
            logger.error(f"Error searching politicians: {e}")
            return []

    def get_politician_details(self, politician_id: str) -> Optional[QuorumPolitician]:
        """Get detailed information about a specific politician."""
        try:
            response = self.session.get(
                f"{self.BASE_URL}/politicians/{politician_id}",
                timeout=10
            )
            response.raise_for_status()

            return QuorumPolitician(response.json())

        except requests.RequestException as e:
            logger.error(f"Error fetching politician details: {e}")
            return None

    def get_politician_bills(self, politician_id: str) -> List[QuorumBill]:
        """Get bills sponsored or cosponsored by a politician."""
        try:
            response = self.session.get(
                f"{self.BASE_URL}/politicians/{politician_id}/bills",
                timeout=10
            )
            response.raise_for_status()

            bills = [QuorumBill(b) for b in response.json()["results"]]
            return bills

        except requests.RequestException as e:
            logger.error(f"Error fetching politician bills: {e}")
            return []

    def search_lobbying_records(
        self,
        client: str = None,
        lobbyist: str = None,
        issue: str = None,
        from_date: str = None,
        to_date: str = None,
        limit: int = 50
    ) -> List[QuorumLobbyingRecord]:
        """
        Search lobbying disclosure records.

        Args:
            client: Client name
            lobbyist: Lobbyist name
            issue: Lobbying issue
            from_date: Start date (YYYY-MM-DD)
            to_date: End date (YYYY-MM-DD)
            limit: Result limit
        """
        try:
            params = {
                "limit": limit
            }

            if client:
                params["client"] = client
            if lobbyist:
                params["lobbyist"] = lobbyist
            if issue:
                params["issue"] = issue
            if from_date:
                params["from_date"] = from_date
            if to_date:
                params["to_date"] = to_date

            response = self.session.get(
                f"{self.BASE_URL}/lobbying",
                params=params,
                timeout=10
            )
            response.raise_for_status()

            records = [
                QuorumLobbyingRecord(r_data)
                for r_data in response.json()["results"]
            ]
            logger.info(f"Found {len(records)} lobbying records")
            return records

        except requests.RequestException as e:
            logger.error(f"Error searching lobbying records: {e}")
            return []

    def get_bill_impact_analysis(self, bill_id: str) -> Optional[Dict]:
        """Get impact analysis for a bill."""
        try:
            response = self.session.get(
                f"{self.BASE_URL}/bills/{bill_id}/impact",
                timeout=10
            )
            response.raise_for_status()

            return response.json()

        except requests.RequestException as e:
            logger.error(f"Error fetching impact analysis: {e}")
            return None

    def get_committee_schedule(self, committee_id: str) -> Optional[List[Dict]]:
        """Get upcoming committee meetings and hearings."""
        try:
            response = self.session.get(
                f"{self.BASE_URL}/committees/{committee_id}/schedule",
                timeout=10
            )
            response.raise_for_status()

            return response.json()["results"]

        except requests.RequestException as e:
            logger.error(f"Error fetching committee schedule: {e}")
            return None

    def track_bill(self, bill_id: str) -> bool:
        """Subscribe to updates for a specific bill."""
        try:
            data = {
                "bill_id": bill_id,
                "subscribe": True
            }

            response = self.session.post(
                f"{self.BASE_URL}/tracking/bills",
                json=data,
                timeout=10
            )
            response.raise_for_status()

            logger.info(f"Added bill tracking: {bill_id}")
            return True

        except requests.RequestException as e:
            logger.error(f"Error tracking bill: {e}")
            return False

    def get_tracked_updates(self) -> List[Dict]:
        """Get updates for tracked bills."""
        try:
            response = self.session.get(
                f"{self.BASE_URL}/tracking/updates",
                timeout=10
            )
            response.raise_for_status()

            return response.json()["results"]

        except requests.RequestException as e:
            logger.error(f"Error fetching tracked updates: {e}")
            return []
