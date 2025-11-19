"""
State Legislation Tracker - Monitor state-level legislative activities.
Tracks bill introductions, amendments, and status changes across all 50 states.
"""

import requests
from datetime import datetime
from typing import List, Dict, Optional
from enum import Enum
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)


class BillStatus(Enum):
    """Bill status enumeration."""
    INTRODUCED = "introduced"
    COMMITTEE = "in_committee"
    FLOOR = "on_floor"
    PASSED = "passed"
    FAILED = "failed"
    SIGNED = "signed"
    VETOED = "vetoed"


@dataclass
class StateBill:
    """Represents a state legislative bill."""
    bill_id: str
    state: str
    session: str
    title: str
    description: str
    status: BillStatus
    sponsors: List[str]
    introduced_date: datetime
    last_action_date: datetime
    committees: List[str]
    action_history: List[Dict]
    vote_counts: Optional[Dict]
    full_text_url: str


class StateLegislationTracker:
    """Track state-level legislation across all 50 states."""

    def __init__(self):
        """Initialize the state legislation tracker."""
        self.tracked_states = []
        self.tracked_keywords = []
        self.bill_cache = {}
        self.base_urls = {
            "open_states": "https://openstates.org/api/v3",
            "legiscan": "https://legiscan.com/api"
        }

    def search_bills(
        self,
        states: List[str],
        keywords: str = None,
        status: BillStatus = None,
        session: str = None
    ) -> List[StateBill]:
        """
        Search for bills across multiple states.

        Args:
            states: List of state abbreviations
            keywords: Search keywords
            status: Filter by bill status
            session: Specific legislative session
        """
        bills = []

        for state in states:
            state_bills = self._search_state_bills(
                state=state,
                keywords=keywords,
                status=status,
                session=session
            )
            bills.extend(state_bills)

        return bills

    def _search_state_bills(
        self,
        state: str,
        keywords: str = None,
        status: BillStatus = None,
        session: str = None
    ) -> List[StateBill]:
        """Search bills in a specific state."""
        try:
            params = {
                "state": state,
                "per_page": 100
            }

            if keywords:
                params["q"] = keywords
            if status:
                params["status"] = status.value
            if session:
                params["session"] = session

            response = requests.get(
                f"{self.base_urls['open_states']}/bills",
                params=params,
                timeout=10
            )
            response.raise_for_status()

            bills = []
            for bill_data in response.json()["results"]:
                bill = self._parse_bill(bill_data, state)
                bills.append(bill)
                self._cache_bill(bill)

            return bills
        except requests.RequestException as e:
            logger.error(f"Error searching bills in {state}: {e}")
            return []

    def _parse_bill(self, bill_data: Dict, state: str) -> StateBill:
        """Parse raw API response into StateBill."""
        action_history = []
        for action in bill_data.get("actions", []):
            action_history.append({
                "date": action.get("date"),
                "description": action.get("description"),
                "actor": action.get("actor")
            })

        vote_counts = None
        votes = bill_data.get("votes", [])
        if votes:
            latest_vote = votes[-1]
            vote_counts = {
                "yes": latest_vote.get("yes_count", 0),
                "no": latest_vote.get("no_count", 0),
                "absent": latest_vote.get("absent_count", 0)
            }

        return StateBill(
            bill_id=bill_data["id"],
            state=state,
            session=bill_data.get("session", ""),
            title=bill_data.get("title", ""),
            description=bill_data.get("summary", ""),
            status=BillStatus(bill_data.get("status", "introduced")),
            sponsors=[s.get("name", "") for s in bill_data.get("sponsors", [])],
            introduced_date=datetime.fromisoformat(bill_data.get("introduced_date", "1970-01-01")),
            last_action_date=datetime.fromisoformat(bill_data.get("updated_at", "1970-01-01")),
            committees=[c.get("name", "") for c in bill_data.get("committees", [])],
            action_history=action_history,
            vote_counts=vote_counts,
            full_text_url=bill_data.get("sources", [{}])[0].get("url", "")
        )

    def _cache_bill(self, bill: StateBill):
        """Cache bill for deduplication."""
        cache_key = f"{bill.state}_{bill.bill_id}"
        self.bill_cache[cache_key] = bill

    def track_state(self, state: str):
        """Add a state to tracking list."""
        if state not in self.tracked_states:
            self.tracked_states.append(state)

    def track_keyword(self, keyword: str):
        """Add a keyword to tracking list."""
        if keyword not in self.tracked_keywords:
            self.tracked_keywords.append(keyword)

    def get_tracked_bills(self) -> List[StateBill]:
        """Get all bills matching tracked states and keywords."""
        all_bills = []
        for state in self.tracked_states:
            for keyword in self.tracked_keywords:
                bills = self.search_bills(
                    states=[state],
                    keywords=keyword
                )
                all_bills.extend(bills)
        return all_bills

    def get_bills_by_sponsor(self, sponsor_name: str, state: str = None) -> List[StateBill]:
        """Get bills sponsored by specific legislator."""
        states = [state] if state else self.tracked_states
        all_bills = self.search_bills(states=states)
        return [b for b in all_bills if sponsor_name in b.sponsors]

    def get_bills_in_committee(self, committee_name: str) -> List[StateBill]:
        """Get bills currently in specific committee."""
        all_bills = self.search_bills(
            states=self.tracked_states,
            status=BillStatus.COMMITTEE
        )
        return [b for b in all_bills if committee_name in b.committees]
