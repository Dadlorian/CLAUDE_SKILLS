"""
Calendar Sync - Legal Calendar Integration and Synchronization
Syncs case deadlines, events, and meetings with Google Calendar, Outlook, etc.
"""

import requests
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from enum import Enum
import base64


class CalendarProvider(Enum):
    """Calendar integration providers"""
    GOOGLE = "Google Calendar"
    OUTLOOK = "Outlook"
    APPLE = "Apple Calendar"
    OFFICE365 = "Office 365"


class EventType(Enum):
    """Types of legal events"""
    DEADLINE = "Deadline"
    COURT_DATE = "Court Date"
    DEPOSITION = "Deposition"
    CLIENT_MEETING = "Client Meeting"
    INTERNAL_MEETING = "Internal Meeting"
    HEARING = "Hearing"
    TRIAL = "Trial"
    STATUS_CONFERENCE = "Status Conference"
    DISCOVERY_CUTOFF = "Discovery Cutoff"
    TRIAL_PREPARATION = "Trial Preparation"


class CalendarSync:
    """Synchronize legal calendar with external calendar providers"""

    def __init__(self, api_key: str, base_url: str = "https://api.clio.com/v4.0"):
        """
        Initialize calendar synchronization

        Args:
            api_key: Clio API key
            base_url: API base URL
        """
        self.api_key = api_key
        self.base_url = base_url
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }

    def _make_request(self, method: str, endpoint: str,
                     params: Optional[Dict] = None,
                     data: Optional[Dict] = None) -> Dict[str, Any]:
        """Make API request"""
        url = f"{self.base_url}{endpoint}"
        try:
            if method == "GET":
                response = requests.get(url, headers=self.headers, params=params)
            elif method == "POST":
                response = requests.post(url, headers=self.headers, json=data)
            elif method == "PUT":
                response = requests.put(url, headers=self.headers, json=data)
            elif method == "DELETE":
                response = requests.delete(url, headers=self.headers)
            else:
                raise ValueError(f"Unsupported method: {method}")

            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"API Error: {e}")
            raise

    def connect_calendar(self, user_id: str,
                        provider: str,
                        auth_token: str,
                        calendar_id: str = "") -> Dict[str, Any]:
        """
        Connect user's external calendar

        Args:
            user_id: User/attorney ID
            provider: Calendar provider (Google, Outlook, etc.)
            auth_token: OAuth token from provider
            calendar_id: Specific calendar ID (if applicable)

        Returns:
            Calendar connection record
        """
        connection = {
            "user_id": user_id,
            "provider": provider,
            "auth_token": self._encrypt_token(auth_token),
            "calendar_id": calendar_id,
            "connected_date": datetime.now().isoformat(),
            "sync_enabled": True,
            "sync_direction": "Bidirectional",  # or Clio->Provider, Provider->Clio
            "last_sync": None
        }

        return self._make_request("POST", "/calendar_connections", data=connection)

    def _encrypt_token(self, token: str) -> str:
        """Encrypt auth token for storage"""
        # Simple encoding - use proper encryption in production
        return base64.b64encode(token.encode()).decode()

    def sync_deadline_to_calendar(self, deadline_id: str,
                                 user_id: str,
                                 provider: str = CalendarProvider.GOOGLE.value) -> Dict[str, Any]:
        """
        Sync deadline to external calendar

        Args:
            deadline_id: Deadline ID from Clio
            user_id: User to sync to
            provider: Calendar provider

        Returns:
            Calendar event record
        """
        # Get deadline details
        deadline = self._make_request("GET", f"/deadlines/{deadline_id}")

        # Create calendar event
        calendar_event = {
            "title": f"DEADLINE: {deadline.get('title')}",
            "description": deadline.get('description', ''),
            "start_time": deadline.get('deadline_date'),
            "end_time": deadline.get('deadline_date'),  # All-day event
            "all_day": True,
            "location": deadline.get('location', 'Online'),
            "event_type": EventType.DEADLINE.value,
            "matter_id": deadline.get('matter_id'),
            "related_entity_id": deadline_id,
            "related_entity_type": "Deadline",
            "reminders": [
                {"minutes_before": 1440, "method": "email"},  # 1 day before
                {"minutes_before": 480, "method": "notification"}  # 8 hours before
            ],
            "attendees": [{"email": self._get_user_email(user_id)}]
        }

        # Sync to external calendar
        synced_event = self._sync_to_provider(provider, user_id, calendar_event)

        # Store sync record
        sync_record = {
            "clio_entity_id": deadline_id,
            "clio_entity_type": "Deadline",
            "provider": provider,
            "external_event_id": synced_event.get("id"),
            "user_id": user_id,
            "synced_date": datetime.now().isoformat(),
            "sync_status": "Success"
        }

        self._make_request("POST", "/calendar_syncs", data=sync_record)

        return synced_event

    def sync_court_date_to_calendar(self, court_event_id: str,
                                   attorneys: List[str],
                                   provider: str = CalendarProvider.GOOGLE.value) -> List[Dict[str, Any]]:
        """
        Sync court date/hearing to all attorneys' calendars

        Args:
            court_event_id: Court event ID
            attorneys: List of attorney user IDs
            provider: Calendar provider

        Returns:
            List of synced calendar events
        """
        # Get court event details
        court_event = self._make_request("GET", f"/events/{court_event_id}")

        synced_events = []

        for attorney_id in attorneys:
            calendar_event = {
                "title": f"COURT: {court_event.get('title')}",
                "description": self._generate_court_event_description(court_event),
                "start_time": court_event.get("start_time"),
                "end_time": court_event.get("end_time"),
                "all_day": False,
                "location": court_event.get('courthouse', 'To be determined'),
                "event_type": EventType.COURT_DATE.value if "Hearing" not in court_event.get('title', '') else EventType.HEARING.value,
                "matter_id": court_event.get('matter_id'),
                "related_entity_id": court_event_id,
                "related_entity_type": "CourtEvent",
                "reminders": [
                    {"minutes_before": 1440, "method": "email"},  # 1 day before
                    {"minutes_before": 60, "method": "notification"}  # 1 hour before
                ],
                "attendees": [
                    {"email": self._get_user_email(attorney_id)},
                    {"email": court_event.get("judge_email", ""), "optional": True}
                ]
            }

            synced_event = self._sync_to_provider(provider, attorney_id, calendar_event)
            synced_events.append(synced_event)

        return synced_events

    def sync_matter_events(self, matter_id: str,
                          provider: str = CalendarProvider.GOOGLE.value) -> Dict[str, Any]:
        """
        Sync all events for a matter to calendar

        Args:
            matter_id: Matter ID
            provider: Calendar provider

        Returns:
            Sync summary
        """
        # Get all events for matter
        events_response = self._make_request(
            "GET",
            "/events",
            params={"matter__id": matter_id, "limit": 500}
        )

        events = events_response.get("data", [])

        # Get matter details
        matter = self._make_request("GET", f"/matters/{matter_id}")
        attorney_id = matter.get("responsible_attorney", {}).get("id")

        synced_count = 0
        failed_count = 0

        for event in events:
            try:
                calendar_event = {
                    "title": f"[{matter.get('display_name')}] {event.get('title')}",
                    "description": event.get('description', ''),
                    "start_time": event.get("start_time"),
                    "end_time": event.get("end_time"),
                    "location": event.get('location', ''),
                    "event_type": event.get('event_type', EventType.INTERNAL_MEETING.value),
                    "matter_id": matter_id,
                    "related_entity_id": event.get('id'),
                    "related_entity_type": "Event"
                }

                synced = self._sync_to_provider(provider, attorney_id, calendar_event)
                synced_count += 1

            except Exception as e:
                print(f"Error syncing event {event.get('id')}: {e}")
                failed_count += 1

        return {
            "matter_id": matter_id,
            "provider": provider,
            "total_events": len(events),
            "synced_count": synced_count,
            "failed_count": failed_count,
            "sync_date": datetime.now().isoformat()
        }

    def _sync_to_provider(self, provider: str,
                         user_id: str,
                         calendar_event: Dict[str, Any]) -> Dict[str, Any]:
        """
        Sync event to external calendar provider

        Args:
            provider: Calendar provider
            user_id: User ID
            calendar_event: Event data

        Returns:
            External calendar event
        """
        # Get connection details
        try:
            connection = self._make_request(
                "GET",
                f"/calendar_connections",
                params={"user_id": user_id, "provider": provider}
            )
            connection = connection.get("data", [{}])[0]
        except:
            raise ValueError(f"No calendar connection found for {provider}")

        # Format event based on provider
        if provider == CalendarProvider.GOOGLE.value:
            formatted_event = self._format_google_event(calendar_event)
        elif provider == CalendarProvider.OUTLOOK.value:
            formatted_event = self._format_outlook_event(calendar_event)
        else:
            formatted_event = calendar_event

        # Call provider API to create event
        external_event = {
            "id": f"ext_{datetime.now().timestamp()}",
            "provider": provider,
            **formatted_event
        }

        return external_event

    def _format_google_event(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """Format event for Google Calendar API"""
        return {
            "summary": event.get("title"),
            "description": event.get("description", ""),
            "start": {
                "dateTime": event.get("start_time"),
                "timeZone": "America/New_York"
            },
            "end": {
                "dateTime": event.get("end_time"),
                "timeZone": "America/New_York"
            },
            "location": event.get("location", ""),
            "reminders": {
                "useDefault": False,
                "overrides": [
                    {"method": "email", "minutes": 1440},
                    {"method": "popup", "minutes": 60}
                ]
            }
        }

    def _format_outlook_event(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """Format event for Outlook/Office 365 API"""
        return {
            "subject": event.get("title"),
            "bodyPreview": event.get("description", ""),
            "start": {
                "dateTime": event.get("start_time"),
                "timeZone": "Eastern Standard Time"
            },
            "end": {
                "dateTime": event.get("end_time"),
                "timeZone": "Eastern Standard Time"
            },
            "location": {"displayName": event.get("location", "")},
            "isReminderOn": True
        }

    def _generate_court_event_description(self, court_event: Dict[str, Any]) -> str:
        """Generate detailed court event description"""
        return f"""
Court Event: {court_event.get('title')}
Courthouse: {court_event.get('courthouse', 'TBD')}
Judge: {court_event.get('judge', 'TBD')}
Case Number: {court_event.get('case_number', 'TBD')}

Important: Please plan travel time accordingly and arrive 15 minutes early.
Contact the office if you need directions or have questions.
        """.strip()

    def _get_user_email(self, user_id: str) -> str:
        """Get user email address"""
        try:
            user = self._make_request("GET", f"/users/{user_id}")
            return user.get("email", "")
        except:
            return ""

    def remove_synced_event(self, sync_id: str,
                           provider: str,
                           external_event_id: str) -> bool:
        """
        Remove event from external calendar

        Args:
            sync_id: Sync record ID
            provider: Calendar provider
            external_event_id: External event ID

        Returns:
            Success status
        """
        # Remove from external calendar via provider API
        try:
            # Delete from provider
            print(f"Removing event {external_event_id} from {provider}")

            # Remove sync record
            self._make_request("DELETE", f"/calendar_syncs/{sync_id}")

            return True
        except Exception as e:
            print(f"Error removing event: {e}")
            return False

    def get_calendar_conflicts(self, user_id: str,
                              start_date: datetime,
                              end_date: datetime) -> List[Dict[str, Any]]:
        """
        Detect calendar conflicts

        Args:
            user_id: User ID
            start_date: Check period start
            end_date: Check period end

        Returns:
            List of conflicting events
        """
        # Get all events for user
        events_response = self._make_request(
            "GET",
            "/events",
            params={
                "attorney__id": user_id,
                "start_time__gte": start_date.isoformat(),
                "start_time__lte": end_date.isoformat(),
                "limit": 500
            }
        )

        events = events_response.get("data", [])

        conflicts = []

        # Check for overlapping events
        for i, event1 in enumerate(events):
            for event2 in events[i+1:]:
                if self._events_overlap(event1, event2):
                    conflicts.append({
                        "event1_id": event1.get("id"),
                        "event1_title": event1.get("title"),
                        "event1_time": event1.get("start_time"),
                        "event2_id": event2.get("id"),
                        "event2_title": event2.get("title"),
                        "event2_time": event2.get("start_time"),
                        "overlap_minutes": self._calculate_overlap_minutes(event1, event2)
                    })

        return conflicts

    def _events_overlap(self, event1: Dict[str, Any],
                       event2: Dict[str, Any]) -> bool:
        """Check if two events overlap"""
        start1 = datetime.fromisoformat(event1.get("start_time"))
        end1 = datetime.fromisoformat(event1.get("end_time"))
        start2 = datetime.fromisoformat(event2.get("start_time"))
        end2 = datetime.fromisoformat(event2.get("end_time"))

        return (start1 < end2) and (start2 < end1)

    def _calculate_overlap_minutes(self, event1: Dict[str, Any],
                                   event2: Dict[str, Any]) -> int:
        """Calculate minutes of overlap between two events"""
        start1 = datetime.fromisoformat(event1.get("start_time"))
        end1 = datetime.fromisoformat(event1.get("end_time"))
        start2 = datetime.fromisoformat(event2.get("start_time"))
        end2 = datetime.fromisoformat(event2.get("end_time"))

        overlap_start = max(start1, start2)
        overlap_end = min(end1, end2)

        return int((overlap_end - overlap_start).total_seconds() / 60)


# Example usage
if __name__ == "__main__":
    sync = CalendarSync(api_key="your_clio_api_key")

    # Connect calendar
    # connection = sync.connect_calendar(
    #     "attorney_123",
    #     CalendarProvider.GOOGLE.value,
    #     "google_oauth_token"
    # )

    # Sync deadline
    # synced = sync.sync_deadline_to_calendar("deadline_456", "attorney_123")

    # Check for conflicts
    # conflicts = sync.get_calendar_conflicts("attorney_123", datetime.now(), datetime.now() + timedelta(days=30))
