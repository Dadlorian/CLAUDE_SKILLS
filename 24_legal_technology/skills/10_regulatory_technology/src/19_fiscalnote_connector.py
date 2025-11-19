"""
FiscalNote Connector - Integration with FiscalNote policy intelligence platform.
Provides real-time legislative tracking, bill analysis, and political intelligence.
"""

import requests
from typing import List, Dict, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class FiscalNoteBill:
    """Represents a bill from FiscalNote."""

    def __init__(self, data: Dict):
        """Initialize bill from FiscalNote API response."""
        self.fiscalnote_id = data.get("id")
        self.bill_id = data.get("bill_id")
        self.bill_number = data.get("bill_number")
        self.title = data.get("title")
        self.summary = data.get("summary")
        self.chamber = data.get("chamber")
        self.state = data.get("state")
        self.status = data.get("status")
        self.introduced_date = data.get("introduced_date")
        self.last_action_date = data.get("last_action_date")
        self.sponsor = data.get("sponsor")
        self.cosponsors = data.get("cosponsors", [])
        self.bill_text_url = data.get("bill_text_url")
        self.fiscal_impact = data.get("fiscal_impact")
        self.industry_tags = data.get("industry_tags", [])
        self.hearing_date = data.get("hearing_date")
        self.priority_score = data.get("priority_score")


class FiscalNoteAnalysis:
    """Represents FiscalNote bill analysis."""

    def __init__(self, data: Dict):
        """Initialize analysis from FiscalNote."""
        self.analysis_id = data.get("id")
        self.bill_id = data.get("bill_id")
        self.fiscal_impact = data.get("fiscal_impact")
        self.estimated_cost = data.get("estimated_cost")
        self.beneficiaries = data.get("beneficiaries", [])
        self.affected_industries = data.get("affected_industries", [])
        self.federal_state_impact = data.get("federal_state_impact")
        self.employment_impact = data.get("employment_impact")
        self.regulatory_implications = data.get("regulatory_implications")
        self.analysis_text = data.get("analysis_text")
        self.data_sources = data.get("data_sources", [])
        self.confidence_score = data.get("confidence_score")


class FiscalNoteAlert:
    """Represents an alert from FiscalNote."""

    def __init__(self, data: Dict):
        """Initialize alert from FiscalNote."""
        self.alert_id = data.get("id")
        self.bill_id = data.get("bill_id")
        self.alert_type = data.get("alert_type")
        self.alert_message = data.get("alert_message")
        self.created_date = data.get("created_date")
        self.related_bills = data.get("related_bills", [])
        self.action_items = data.get("action_items", [])
        self.priority = data.get("priority")


class FiscalNoteConnector:
    """Integration with FiscalNote policy intelligence platform."""

    BASE_URL = "https://api.fiscalnote.com/v1"

    def __init__(self, api_key: str):
        """Initialize FiscalNote connector."""
        self.api_key = api_key
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        })
        self.tracked_bills = {}

    def search_bills(
        self,
        keywords: str = None,
        state: str = None,
        status: str = None,
        industry: str = None,
        limit: int = 50
    ) -> List[FiscalNoteBill]:
        """
        Search for bills using FiscalNote.

        Args:
            keywords: Search keywords
            state: State code
            status: Bill status
            industry: Industry tag
            limit: Result limit
        """
        try:
            params = {
                "limit": limit,
                "sort": "date_desc"
            }

            if keywords:
                params["q"] = keywords
            if state:
                params["state"] = state
            if status:
                params["status"] = status
            if industry:
                params["industry"] = industry

            response = self.session.get(
                f"{self.BASE_URL}/bills/search",
                params=params,
                timeout=10
            )
            response.raise_for_status()

            bills = [FiscalNoteBill(b) for b in response.json()["results"]]
            logger.info(f"Found {len(bills)} bills in FiscalNote")
            return bills

        except requests.RequestException as e:
            logger.error(f"Error searching FiscalNote bills: {e}")
            return []

    def get_bill_analysis(self, bill_id: str) -> Optional[FiscalNoteAnalysis]:
        """Get FiscalNote analysis for a bill."""
        try:
            response = self.session.get(
                f"{self.BASE_URL}/bills/{bill_id}/analysis",
                timeout=10
            )
            response.raise_for_status()

            return FiscalNoteAnalysis(response.json())

        except requests.RequestException as e:
            logger.error(f"Error fetching bill analysis: {e}")
            return None

    def get_related_bills(self, bill_id: str) -> List[FiscalNoteBill]:
        """Get bills related to a specific bill."""
        try:
            response = self.session.get(
                f"{self.BASE_URL}/bills/{bill_id}/related",
                timeout=10
            )
            response.raise_for_status()

            bills = [FiscalNoteBill(b) for b in response.json()["results"]]
            return bills

        except requests.RequestException as e:
            logger.error(f"Error fetching related bills: {e}")
            return []

    def search_by_industry(self, industry: str, limit: int = 50) -> List[FiscalNoteBill]:
        """Search bills affecting a specific industry."""
        try:
            params = {
                "industry": industry,
                "limit": limit,
                "sort": "priority_score_desc"
            }

            response = self.session.get(
                f"{self.BASE_URL}/bills/search",
                params=params,
                timeout=10
            )
            response.raise_for_status()

            bills = [FiscalNoteBill(b) for b in response.json()["results"]]
            logger.info(f"Found {len(bills)} bills for industry: {industry}")
            return bills

        except requests.RequestException as e:
            logger.error(f"Error searching by industry: {e}")
            return []

    def get_fiscal_impact_summary(self, bill_id: str) -> Optional[Dict]:
        """Get fiscal impact summary for a bill."""
        try:
            analysis = self.get_bill_analysis(bill_id)
            if not analysis:
                return None

            return {
                "bill_id": bill_id,
                "estimated_cost": analysis.estimated_cost,
                "beneficiaries": analysis.beneficiaries,
                "affected_industries": analysis.affected_industries,
                "employment_impact": analysis.employment_impact,
                "confidence_score": analysis.confidence_score
            }

        except Exception as e:
            logger.error(f"Error getting fiscal impact: {e}")
            return None

    def track_bill(self, bill_id: str, notification_settings: Dict = None) -> bool:
        """Start tracking a bill for alerts."""
        try:
            data = {
                "bill_id": bill_id,
                "notifications": notification_settings or {
                    "status_change": True,
                    "hearing_scheduled": True,
                    "analysis_updated": True
                }
            }

            response = self.session.post(
                f"{self.BASE_URL}/tracking/bills",
                json=data,
                timeout=10
            )
            response.raise_for_status()

            self.tracked_bills[bill_id] = data
            logger.info(f"Tracking bill: {bill_id}")
            return True

        except requests.RequestException as e:
            logger.error(f"Error tracking bill: {e}")
            return False

    def untrack_bill(self, bill_id: str) -> bool:
        """Stop tracking a bill."""
        try:
            response = self.session.delete(
                f"{self.BASE_URL}/tracking/bills/{bill_id}",
                timeout=10
            )
            response.raise_for_status()

            if bill_id in self.tracked_bills:
                del self.tracked_bills[bill_id]

            logger.info(f"Stopped tracking bill: {bill_id}")
            return True

        except requests.RequestException as e:
            logger.error(f"Error untracking bill: {e}")
            return False

    def get_alerts(self, limit: int = 50) -> List[FiscalNoteAlert]:
        """Get recent alerts from FiscalNote."""
        try:
            params = {
                "limit": limit,
                "sort": "date_desc"
            }

            response = self.session.get(
                f"{self.BASE_URL}/alerts",
                params=params,
                timeout=10
            )
            response.raise_for_status()

            alerts = [FiscalNoteAlert(a) for a in response.json()["results"]]
            logger.info(f"Retrieved {len(alerts)} alerts")
            return alerts

        except requests.RequestException as e:
            logger.error(f"Error fetching alerts: {e}")
            return []

    def get_bill_history(self, bill_id: str) -> List[Dict]:
        """Get full action history for a bill."""
        try:
            response = self.session.get(
                f"{self.BASE_URL}/bills/{bill_id}/actions",
                timeout=10
            )
            response.raise_for_status()

            return response.json()["results"]

        except requests.RequestException as e:
            logger.error(f"Error fetching bill history: {e}")
            return []

    def get_hearing_schedule(self, state: str = None) -> List[Dict]:
        """Get scheduled committee hearings."""
        try:
            params = {}
            if state:
                params["state"] = state

            response = self.session.get(
                f"{self.BASE_URL}/hearings/schedule",
                params=params,
                timeout=10
            )
            response.raise_for_status()

            return response.json()["results"]

        except requests.RequestException as e:
            logger.error(f"Error fetching hearing schedule: {e}")
            return []

    def create_report(
        self,
        bills: List[str],
        report_title: str,
        include_analysis: bool = True
    ) -> Optional[Dict]:
        """Create a report on multiple bills."""
        try:
            data = {
                "title": report_title,
                "bill_ids": bills,
                "include_analysis": include_analysis
            }

            response = self.session.post(
                f"{self.BASE_URL}/reports/create",
                json=data,
                timeout=10
            )
            response.raise_for_status()

            return response.json()

        except requests.RequestException as e:
            logger.error(f"Error creating report: {e}")
            return None

    def get_legislative_calendar(self, state: str) -> Optional[Dict]:
        """Get legislative calendar for a state."""
        try:
            response = self.session.get(
                f"{self.BASE_URL}/calendars/{state}",
                timeout=10
            )
            response.raise_for_status()

            return response.json()

        except requests.RequestException as e:
            logger.error(f"Error fetching legislative calendar: {e}")
            return None
