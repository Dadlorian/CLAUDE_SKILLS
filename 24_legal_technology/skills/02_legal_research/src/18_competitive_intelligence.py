"""
Competitive Intelligence
Analyzes competitor legal strategies and litigation patterns
"""

from typing import List, Dict, Optional
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class CompetitiveIntelligence:
    """
    Analyzes competitor legal strategy
    """

    def __init__(self):
        """Initialize competitive intelligence engine"""
        self.companies = {}
        self.litigations = []
        self.litigation_history = {}

    def add_company(self, company_name: str, industry: str, description: str = ""):
        """
        Add company for analysis

        Args:
            company_name: Company name
            industry: Industry sector
            description: Company description
        """
        self.companies[company_name] = {
            "name": company_name,
            "industry": industry,
            "description": description,
            "lawsuits": [],
            "patents": [],
            "regulatory": []
        }
        logger.info(f"Added company: {company_name}")

    def add_litigation(self, company: str, case_data: Dict):
        """
        Add litigation record

        Args:
            company: Company name
            case_data: Case information
        """
        if company not in self.companies:
            self.add_company(company, "Unknown")

        litigation = {
            "company": company,
            "case_name": case_data.get("case_name"),
            "opponent": case_data.get("opponent"),
            "court": case_data.get("court"),
            "year": case_data.get("year"),
            "outcome": case_data.get("outcome"),
            "issue_area": case_data.get("issue_area")
        }

        self.companies[company]["lawsuits"].append(litigation)
        self.litigations.append(litigation)
        logger.info(f"Added litigation for {company}")

    def analyze_litigation_pattern(self, company: str) -> Dict:
        """
        Analyze litigation patterns

        Args:
            company: Company name

        Returns:
            Pattern analysis
        """
        if company not in self.companies:
            return {}

        lawsuits = self.companies[company]["lawsuits"]

        if not lawsuits:
            return {"company": company, "litigation_count": 0}

        # Analyze by issue area
        issue_areas = {}
        for lawsuit in lawsuits:
            area = lawsuit.get("issue_area", "Unknown")
            if area not in issue_areas:
                issue_areas[area] = 0
            issue_areas[area] += 1

        # Analyze outcomes
        outcomes = {}
        for lawsuit in lawsuits:
            outcome = lawsuit.get("outcome", "Unknown")
            outcomes[outcome] = outcomes.get(outcome, 0) + 1

        return {
            "company": company,
            "litigation_count": len(lawsuits),
            "by_issue_area": issue_areas,
            "by_outcome": outcomes,
            "most_litigated_area": max(issue_areas, key=issue_areas.get) if issue_areas else None
        }

    def identify_litigation_trends(self, industry: str) -> Dict:
        """
        Identify litigation trends in industry

        Args:
            industry: Industry name

        Returns:
            Trend analysis
        """
        industry_companies = [c for c in self.companies.values() if c["industry"] == industry]

        if not industry_companies:
            return {"industry": industry, "companies": 0}

        all_litigations = []
        for company in industry_companies:
            all_litigations.extend(company["lawsuits"])

        # Identify trends
        issue_frequency = {}
        for lit in all_litigations:
            area = lit.get("issue_area", "Unknown")
            issue_frequency[area] = issue_frequency.get(area, 0) + 1

        return {
            "industry": industry,
            "companies_analyzed": len(industry_companies),
            "total_litigations": len(all_litigations),
            "top_issues": sorted(issue_frequency.items(), key=lambda x: x[1], reverse=True)[:5]
        }

    def compare_strategies(self, company1: str, company2: str) -> Dict:
        """
        Compare litigation strategies

        Args:
            company1: First company
            company2: Second company

        Returns:
            Strategy comparison
        """
        pattern1 = self.analyze_litigation_pattern(company1)
        pattern2 = self.analyze_litigation_pattern(company2)

        return {
            "company1": company1,
            "company2": company2,
            "pattern1": pattern1,
            "pattern2": pattern2,
            "comparison": {
                "litigation_difference": abs(pattern1.get("litigation_count", 0) - pattern2.get("litigation_count", 0)),
                "similar_issues": self._find_similar_issues(pattern1, pattern2)
            }
        }

    @staticmethod
    def _find_similar_issues(pattern1: Dict, pattern2: Dict) -> List[str]:
        """Find similar issue areas between two patterns"""
        areas1 = set(pattern1.get("by_issue_area", {}).keys())
        areas2 = set(pattern2.get("by_issue_area", {}).keys())
        return list(areas1 & areas2)


# Usage example
if __name__ == "__main__":
    intelligence = CompetitiveIntelligence()

    # Add companies
    intelligence.add_company("TechCorp", "Technology")
    intelligence.add_company("InnovateLabs", "Technology")

    # Add litigation
    intelligence.add_litigation("TechCorp", {
        "case_name": "TechCorp v. Patent Troll Inc.",
        "opponent": "Patent Troll Inc.",
        "court": "9th Circuit",
        "year": 2023,
        "outcome": "won",
        "issue_area": "patent"
    })

    # Analyze patterns
    patterns = intelligence.analyze_litigation_pattern("TechCorp")
    print(f"Litigation Patterns: {patterns}")
