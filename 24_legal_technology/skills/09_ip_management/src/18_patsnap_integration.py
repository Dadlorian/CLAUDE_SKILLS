"""
Patsnap Integration Example
Integrates with Patsnap API for patent intelligence
"""

from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
import json


class PatentStatus(Enum):
    """Patent status from Patsnap"""
    PENDING = "pending"
    GRANTED = "granted"
    EXPIRED = "expired"
    ABANDONED = "abandoned"


@dataclass
class PatsnapsearchResult:
    """Patsnap search result"""
    patent_id: str
    title: str
    abstract: str
    assignee: str
    filing_date: datetime
    publication_date: datetime
    patent_status: PatentStatus
    relevance_score: float
    jurisdiction: str
    ipc_classes: List[str]
    claims_count: int
    citations_count: int


@dataclass
class PatentData:
    """Full patent data from Patsnap"""
    patent_id: str
    title: str
    abstract: str
    claims: List[str]
    assignee: str
    inventors: List[str]
    filing_date: datetime
    publication_date: datetime
    grant_date: Optional[datetime]
    claims_count: int
    citations_received: int
    citations_made: int
    legal_status: str
    family_members: List[str]


class PatsnapsearchAPI:
    """Interface to Patsnap API"""

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.patsnap.com/v1"
        self.search_cache = {}

    def search_patents(self, query: str, limit: int = 50) -> List[PatsnapsearchResult]:
        """
        Search patents by query

        Args:
            query: Search query
            limit: Max results

        Returns:
            List of search results
        """
        # Simulated API call
        cache_key = f"{query}_{limit}"
        if cache_key in self.search_cache:
            return self.search_cache[cache_key]

        results = []
        # In real implementation, would call actual Patsnap API
        # results = requests.get(
        #     f"{self.base_url}/patent/search",
        #     headers={'Authorization': f'Bearer {self.api_key}'},
        #     params={'q': query, 'limit': limit}
        # ).json()

        self.search_cache[cache_key] = results
        return results

    def get_patent_details(self, patent_id: str) -> Optional[PatentData]:
        """
        Get full patent details

        Args:
            patent_id: Patent ID

        Returns:
            Patent details
        """
        # Simulated API call
        # In real implementation:
        # response = requests.get(
        #     f"{self.base_url}/patent/{patent_id}",
        #     headers={'Authorization': f'Bearer {self.api_key}'}
        # ).json()

        return None

    def search_by_ipc(self, ipc_class: str) -> List[PatsnapsearchResult]:
        """
        Search patents by IPC classification

        Args:
            ipc_class: IPC classification

        Returns:
            Patents in classification
        """
        query = f"IPC:{ipc_class}"
        return self.search_patents(query)

    def search_by_assignee(self, assignee: str) -> List[PatsnapsearchResult]:
        """
        Search patents by assignee

        Args:
            assignee: Assignee name

        Returns:
            Patents assigned to company
        """
        query = f"Assignee:{assignee}"
        return self.search_patents(query)

    def get_patent_family(self, patent_id: str) -> List[PatsnapsearchResult]:
        """
        Get patent family members

        Args:
            patent_id: Patent ID

        Returns:
            List of family patents
        """
        query = f"FamilyID:{patent_id}"
        return self.search_patents(query)


class PatsnapsearchAnalytics:
    """Analytics using Patsnap data"""

    def __init__(self, api: PatsnapsearchAPI):
        self.api = api
        self.patents_cache = {}

    def analyze_competitor_portfolio(self, competitor_name: str) -> Dict:
        """
        Analyze competitor IP portfolio

        Args:
            competitor_name: Competitor company name

        Returns:
            Portfolio analysis
        """
        patents = self.api.search_by_assignee(competitor_name)

        # Analyze portfolio
        total_patents = len(patents)
        granted = sum(1 for p in patents if p.patent_status == PatentStatus.GRANTED)
        pending = sum(1 for p in patents if p.patent_status == PatentStatus.PENDING)
        expired = sum(1 for p in patents if p.patent_status == PatentStatus.EXPIRED)

        # Geographic distribution
        jurisdictions = {}
        for patent in patents:
            jurisdictions[patent.jurisdiction] = jurisdictions.get(patent.jurisdiction, 0) + 1

        # Technology distribution
        technologies = {}
        for patent in patents:
            for ipc in patent.ipc_classes:
                technologies[ipc] = technologies.get(ipc, 0) + 1

        # Citation impact
        total_citations = sum(p.citations_count for p in patents)
        avg_citations = total_citations / total_patents if total_patents > 0 else 0

        return {
            'competitor': competitor_name,
            'portfolio_size': total_patents,
            'granted_patents': granted,
            'pending_patents': pending,
            'expired_patents': expired,
            'grant_rate': (granted / total_patents * 100) if total_patents > 0 else 0,
            'geographic_distribution': jurisdictions,
            'technology_focus': sorted(technologies.items(), key=lambda x: x[1], reverse=True)[:10],
            'citation_impact': {
                'total_citations': int(total_citations),
                'average_citations_per_patent': avg_citations,
                'highly_cited_patents': sum(1 for p in patents if p.citations_count > 10)
            }
        }

    def monitor_technology_area(self, technology: str, last_n_months: int = 12) -> Dict:
        """
        Monitor filings in technology area

        Args:
            technology: Technology area (IPC or search term)
            last_n_months: Months to monitor

        Returns:
            Filing activity analysis
        """
        patents = self.api.search_patents(technology)

        # Filter recent filings
        from datetime import timedelta
        cutoff_date = datetime.now() - timedelta(days=last_n_months*30)
        recent = [p for p in patents if p.filing_date >= cutoff_date]

        # Group by assignee
        assignee_activity = {}
        for patent in recent:
            if patent.assignee not in assignee_activity:
                assignee_activity[patent.assignee] = []
            assignee_activity[patent.assignee].append(patent)

        # Sort by activity
        top_filers = sorted(assignee_activity.items(),
                           key=lambda x: len(x[1]),
                           reverse=True)[:10]

        return {
            'technology': technology,
            'period_months': last_n_months,
            'total_recent_filings': len(recent),
            'top_assignees': [
                {
                    'name': assignee,
                    'filing_count': len(patents),
                    'avg_citations': sum(p.citations_count for p in patents) / len(patents) if patents else 0
                }
                for assignee, patents in top_filers
            ],
            'filing_trend': 'increasing' if len(recent) > len(patents) / 2 else 'stable'
        }

    def prior_art_search(self, keywords: str, ipc_classes: List[str] = None) -> Dict:
        """
        Conduct prior art search

        Args:
            keywords: Search keywords
            ipc_classes: Optional IPC classifications

        Returns:
            Prior art search results
        """
        # Conduct keyword search
        keyword_results = self.api.search_patents(keywords)

        # Add IPC filters if provided
        all_results = keyword_results
        if ipc_classes:
            ipc_results = []
            for ipc in ipc_classes:
                ipc_results.extend(self.api.search_by_ipc(ipc))
            # Combine and deduplicate
            all_ids = set(p.patent_id for p in keyword_results + ipc_results)
            all_results = [p for p in keyword_results + ipc_results
                          if p.patent_id in all_ids]

        # Score by relevance
        scored_results = [
            {
                'patent_id': p.patent_id,
                'title': p.title,
                'relevance': p.relevance_score,
                'assignee': p.assignee,
                'filing_date': p.filing_date.isoformat(),
                'status': p.patent_status.value,
                'citations': p.citations_count
            }
            for p in sorted(all_results, key=lambda x: x.relevance_score, reverse=True)[:20]
        ]

        return {
            'search_keywords': keywords,
            'ipc_filters': ipc_classes or [],
            'total_results_found': len(all_results),
            'top_results': scored_results,
            'critical_prior_art': [r for r in scored_results if r['relevance'] > 0.8]
        }

    def track_patent_family(self, patent_id: str) -> Dict:
        """
        Track patent family across jurisdictions

        Args:
            patent_id: Patent ID

        Returns:
            Family tracking information
        """
        family = self.api.get_patent_family(patent_id)

        # Analyze family
        jurisdictions = {}
        statuses = {}
        filing_dates = []

        for patent in family:
            jurisdictions[patent.jurisdiction] = jurisdictions.get(patent.jurisdiction, 0) + 1
            statuses[patent.patent_status.value] = statuses.get(patent.patent_status.value, 0) + 1
            filing_dates.append(patent.filing_date)

        return {
            'root_patent_id': patent_id,
            'family_size': len(family),
            'jurisdictions_covered': jurisdictions,
            'status_distribution': statuses,
            'first_filing_date': min(filing_dates).isoformat() if filing_dates else None,
            'last_filing_date': max(filing_dates).isoformat() if filing_dates else None,
            'family_members': [p.patent_id for p in family]
        }

    def competitive_threat_analysis(self, our_technologies: List[str],
                                    competitor_ids: List[str]) -> Dict:
        """
        Analyze competitive threats

        Args:
            our_technologies: Our technology areas
            competitor_ids: Competitor company names

        Returns:
            Threat analysis
        """
        threats = []

        for competitor in competitor_ids:
            portfolio = self.analyze_competitor_portfolio(competitor)

            # Find overlaps with our technologies
            competitor_techs = [tech[0] for tech in portfolio['technology_focus']]
            overlaps = set(our_technologies) & set(competitor_techs)

            if overlaps:
                threat_score = len(overlaps) * (portfolio['portfolio_size'] / 1000)
                threats.append({
                    'competitor': competitor,
                    'overlapping_technologies': list(overlaps),
                    'threat_score': threat_score,
                    'competitor_portfolio_size': portfolio['portfolio_size'],
                    'threat_level': 'high' if threat_score > 5 else 'medium' if threat_score > 2 else 'low'
                })

        return {
            'our_technologies': our_technologies,
            'competitors_analyzed': competitor_ids,
            'threats_identified': sorted(threats, key=lambda x: x['threat_score'], reverse=True)
        }

    def generate_market_intelligence_report(self, technology_area: str,
                                          competitors: List[str]) -> Dict:
        """
        Generate comprehensive market intelligence report

        Args:
            technology_area: Technology to analyze
            competitors: Competitors to track

        Returns:
            Complete market intelligence report
        """
        return {
            'report_date': datetime.now().isoformat(),
            'technology_area': technology_area,
            'technology_monitor': self.monitor_technology_area(technology_area),
            'competitor_profiles': [
                self.analyze_competitor_portfolio(comp) for comp in competitors
            ],
            'competitive_threats': self.competitive_threat_analysis(
                [technology_area],
                competitors
            )
        }


# Example usage
if __name__ == "__main__":
    # Initialize API
    api = PatsnapsearchAPI("dummy_api_key")

    # Initialize analytics
    analytics = PatsnapsearchAnalytics(api)

    # Analyze technology area
    monitor = analytics.monitor_technology_area("G06F", 12)
    print("Technology Area Monitoring")
    print(f"Recent Filings: {monitor['total_recent_filings']}")

    # Prior art search
    prior_art = analytics.prior_art_search(
        "machine learning artificial intelligence",
        ["G06F", "G06N"]
    )
    print(f"\nPrior Art Search Results: {prior_art['total_results_found']}")
