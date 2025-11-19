"""
Research Cost Tracker
Tracks and optimizes legal research costs
"""

from typing import List, Dict, Optional
from dataclasses import dataclass
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class ResearchSession:
    """A research session with associated costs"""
    session_id: str
    researcher: str
    start_time: datetime
    end_time: Optional[datetime]
    database: str  # Westlaw, Lexis, etc.
    searches_performed: int
    cost_per_search: float
    total_cost: float
    matter_id: str


class ResearchCostTracker:
    """
    Tracks and optimizes research costs
    """

    def __init__(self):
        """Initialize cost tracker"""
        self.sessions = []
        self.rates = {
            "westlaw": 0.50,
            "lexis": 0.45,
            "google_scholar": 0.0,
            "courtlistener": 0.0,
            "custom_db": 1.00
        }

    def start_session(self, researcher: str, database: str, matter_id: str) -> str:
        """
        Start research session

        Args:
            researcher: Researcher name
            database: Database being used
            matter_id: Matter ID

        Returns:
            Session ID
        """
        session_id = f"session_{len(self.sessions)}_{datetime.now().timestamp()}"

        session = ResearchSession(
            session_id=session_id,
            researcher=researcher,
            start_time=datetime.now(),
            end_time=None,
            database=database,
            searches_performed=0,
            cost_per_search=self.rates.get(database.lower(), 0.50),
            total_cost=0.0,
            matter_id=matter_id
        )

        self.sessions.append(session)
        logger.info(f"Started session: {session_id}")
        return session_id

    def log_search(self, session_id: str):
        """
        Log a search in the session

        Args:
            session_id: Session ID
        """
        for session in self.sessions:
            if session.session_id == session_id and session.end_time is None:
                session.searches_performed += 1
                session.total_cost = session.searches_performed * session.cost_per_search
                logger.info(f"Logged search in {session_id}, cost: ${session.total_cost:.2f}")
                return

    def end_session(self, session_id: str) -> Dict:
        """
        End research session

        Args:
            session_id: Session ID

        Returns:
            Session summary
        """
        for session in self.sessions:
            if session.session_id == session_id:
                session.end_time = datetime.now()
                duration = (session.end_time - session.start_time).total_seconds() / 60

                logger.info(f"Ended session: {session_id}, Total cost: ${session.total_cost:.2f}")

                return {
                    "session_id": session_id,
                    "researcher": session.researcher,
                    "database": session.database,
                    "searches": session.searches_performed,
                    "duration_minutes": duration,
                    "total_cost": session.total_cost,
                    "cost_per_search": session.cost_per_search
                }

    def get_matter_costs(self, matter_id: str) -> Dict:
        """
        Get all costs for a matter

        Args:
            matter_id: Matter ID

        Returns:
            Cost summary for matter
        """
        matter_sessions = [s for s in self.sessions if s.matter_id == matter_id]

        if not matter_sessions:
            return {"matter_id": matter_id, "total_cost": 0.0, "sessions": []}

        total_cost = sum(s.total_cost for s in matter_sessions)
        total_searches = sum(s.searches_performed for s in matter_sessions)

        return {
            "matter_id": matter_id,
            "total_cost": total_cost,
            "total_searches": total_searches,
            "num_sessions": len(matter_sessions),
            "avg_cost_per_search": total_cost / total_searches if total_searches > 0 else 0,
            "by_database": self._summarize_by_database(matter_sessions)
        }

    @staticmethod
    def _summarize_by_database(sessions: List[ResearchSession]) -> Dict:
        """Summarize costs by database"""
        summary = {}
        for session in sessions:
            if session.database not in summary:
                summary[session.database] = {"cost": 0.0, "searches": 0}
            summary[session.database]["cost"] += session.total_cost
            summary[session.database]["searches"] += session.searches_performed
        return summary

    def get_optimization_suggestions(self, matter_id: str) -> List[str]:
        """
        Get suggestions to optimize research costs

        Args:
            matter_id: Matter ID

        Returns:
            List of optimization suggestions
        """
        costs = self.get_matter_costs(matter_id)
        suggestions = []

        if costs["total_cost"] > 1000:
            suggestions.append("Consider using Google Scholar for free case law searching")
            suggestions.append("Review research strategy to eliminate redundant searches")

        # Check database efficiency
        by_db = costs.get("by_database", {})
        for db, data in by_db.items():
            if db not in ["google_scholar", "courtlistener"]:
                suggestions.append(f"Consider free alternatives to {db}")

        if costs["avg_cost_per_search"] > 0.75:
            suggestions.append("Refine search queries to be more specific")

        return suggestions

    def get_monthly_summary(self) -> Dict:
        """
        Get monthly cost summary

        Args:
            None

        Returns:
            Monthly summary
        """
        total_cost = sum(s.total_cost for s in self.sessions)
        total_searches = sum(s.searches_performed for s in self.sessions)

        return {
            "period": "Current Month",
            "total_cost": total_cost,
            "total_searches": total_searches,
            "num_sessions": len(self.sessions),
            "num_researchers": len(set(s.researcher for s in self.sessions)),
            "avg_session_cost": total_cost / len(self.sessions) if self.sessions else 0
        }


# Usage example
if __name__ == "__main__":
    tracker = ResearchCostTracker()

    # Start session
    session_id = tracker.start_session("John Doe", "westlaw", "matter_001")

    # Log searches
    for _ in range(5):
        tracker.log_search(session_id)

    # End session
    summary = tracker.end_session(session_id)
    print(f"Session Summary: {summary}")

    # Get matter costs
    costs = tracker.get_matter_costs("matter_001")
    print(f"Matter Costs: {costs}")
