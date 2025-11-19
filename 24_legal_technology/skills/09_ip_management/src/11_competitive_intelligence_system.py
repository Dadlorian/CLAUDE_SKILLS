"""
Competitive Intelligence System Example
Tracks competitor IP strategies and innovation trends
"""

from typing import List, Dict, Optional
from dataclasses import dataclass
from datetime import datetime
from collections import defaultdict

@dataclass
class CompetitorPatent:
    """Represents a competitor's patent"""
    patent_number: str
    filing_date: str
    issue_date: Optional[str]
    title: str
    technology_area: str
    claim_count: int

@dataclass
class CompetitorProfile:
    """Profile of a competitor's IP activity"""
    company_name: str
    patents: List[CompetitorPatent]
    total_patents: int
    technology_focus: Dict[str, int]  # Tech area to count
    filing_rate_annual: float
    average_patent_age: float

class CompetitiveIntelligenceSystem:
    """Track and analyze competitor IP strategies"""

    def __init__(self):
        self.competitors: Dict[str, CompetitorProfile] = {}
        self.patent_database: Dict[str, CompetitorPatent] = {}
        self.technology_trends: Dict[str, List[int]] = defaultdict(list)

    def add_competitor(self, company_name: str):
        """Register a competitor for tracking"""
        self.competitors[company_name] = CompetitorProfile(
            company_name=company_name,
            patents=[],
            total_patents=0,
            technology_focus={},
            filing_rate_annual=0.0,
            average_patent_age=0.0
        )

    def add_patent_to_competitor(self, company_name: str, patent: CompetitorPatent):
        """Add a patent to competitor profile"""
        if company_name not in self.competitors:
            self.add_competitor(company_name)

        competitor = self.competitors[company_name]
        competitor.patents.append(patent)
        self.patent_database[patent.patent_number] = patent

        # Update technology focus
        tech_area = patent.technology_area
        competitor.technology_focus[tech_area] = competitor.technology_focus.get(tech_area, 0) + 1

    def analyze_competitor_portfolio(self, company_name: str) -> Dict:
        """Analyze a competitor's IP portfolio"""
        if company_name not in self.competitors:
            return {}

        competitor = self.competitors[company_name]
        patents = competitor.patents

        if not patents:
            return {'company': company_name, 'status': 'No patents found'}

        # Calculate statistics
        total_patents = len(patents)

        # Technology distribution
        tech_counts = defaultdict(int)
        for patent in patents:
            tech_counts[patent.technology_area] += 1

        # Calculate average patent age
        today = datetime.now()
        ages = []
        for patent in patents:
            if patent.issue_date:
                issue_date = datetime.strptime(patent.issue_date, '%Y-%m-%d')
                age_years = (today - issue_date).days / 365.25
                ages.append(age_years)

        average_age = sum(ages) / len(ages) if ages else 0

        # Find top technology areas
        top_techs = sorted(tech_counts.items(), key=lambda x: x[1], reverse=True)[:5]

        return {
            'company': company_name,
            'total_patents': total_patents,
            'average_patent_age': average_age,
            'technology_distribution': dict(top_techs),
            'primary_focus': top_techs[0][0] if top_techs else None,
            'portfolio_breadth': len(tech_counts),
            'patents': patents
        }

    def identify_technology_gaps(self, company_name: str, reference_company: str) -> Dict:
        """
        Identify technology areas where competitor may have advantage or gap

        Args:
            company_name: Company to analyze
            reference_company: Company to compare against

        Returns:
            Dictionary showing technology gaps
        """
        company_profile = self.competitors.get(company_name)
        reference_profile = self.competitors.get(reference_company)

        if not company_profile or not reference_profile:
            return {}

        company_techs = set(company_profile.technology_focus.keys())
        reference_techs = set(reference_profile.technology_focus.keys())

        # Find gaps
        competitor_gaps = reference_techs - company_techs
        our_advantages = company_techs - reference_techs

        return {
            'company': company_name,
            'competitor_advantage_areas': list(competitor_gaps),
            'our_advantage_areas': list(our_advantages),
            'shared_technology_areas': list(company_techs & reference_techs)
        }

    def track_innovation_velocity(self, company_name: str, years: int = 5) -> Dict:
        """
        Analyze how fast a competitor is innovating
        """
        if company_name not in self.competitors:
            return {}

        competitor = self.competitors[company_name]
        patents = competitor.patents

        # Group patents by year
        filing_by_year = defaultdict(int)
        today = datetime.now()

        for patent in patents:
            filing_date = datetime.strptime(patent.filing_date, '%Y-%m-%d')
            year = filing_date.year

            if year >= today.year - years:
                filing_by_year[year] += 1

        # Calculate trend
        yearly_filings = [filing_by_year[year] for year in sorted(filing_by_year.keys())]

        # Simple trend calculation
        trend = "Increasing" if len(yearly_filings) > 1 and yearly_filings[-1] > yearly_filings[0] else "Decreasing"

        return {
            'company': company_name,
            'filings_by_year': dict(sorted(filing_by_year.items())),
            'total_filings_period': sum(yearly_filings),
            'average_annual_filings': sum(yearly_filings) / len(yearly_filings) if yearly_filings else 0,
            'innovation_trend': trend
        }

    def identify_acquisition_candidates(self, technology_area: str) -> List[Dict]:
        """
        Identify potential acquisition candidates based on patent strength in specific tech area
        """
        candidates = []

        for company_name, competitor in self.competitors.items():
            if technology_area in competitor.technology_focus:
                strength = competitor.technology_focus[technology_area]

                candidates.append({
                    'company': company_name,
                    'technology_area': technology_area,
                    'patent_count': strength,
                    'score': strength  # Could be more sophisticated
                })

        # Sort by strength
        candidates.sort(key=lambda x: x['score'], reverse=True)

        return candidates

    def generate_competitive_landscape_report(self) -> Dict:
        """Generate overall competitive landscape report"""
        if not self.competitors:
            return {}

        report = {
            'timestamp': datetime.now().isoformat(),
            'total_competitors_tracked': len(self.competitors),
            'total_patents_tracked': len(self.patent_database),
            'competitor_profiles': [],
            'technology_distribution': defaultdict(int),
            'innovation_leaders': []
        }

        # Add each competitor's profile
        for company_name in self.competitors:
            profile = self.analyze_competitor_portfolio(company_name)
            if 'total_patents' in profile:
                report['competitor_profiles'].append(profile)

                # Track technology distribution
                for tech, count in profile.get('technology_distribution', {}).items():
                    report['technology_distribution'][tech] += count

        # Identify innovation leaders (by filing rate)
        for company_name in self.competitors:
            velocity = self.track_innovation_velocity(company_name)
            if 'average_annual_filings' in velocity:
                report['innovation_leaders'].append({
                    'company': company_name,
                    'annual_filings': velocity['average_annual_filings'],
                    'trend': velocity['innovation_trend']
                })

        # Sort innovation leaders
        report['innovation_leaders'].sort(key=lambda x: x['annual_filings'], reverse=True)

        return report


# Example usage
if __name__ == "__main__":
    intelligence = CompetitiveIntelligenceSystem()

    # Add competitors
    intelligence.add_competitor("TechCorp")
    intelligence.add_competitor("InnovateCo")

    # Add patents for TechCorp
    intelligence.add_patent_to_competitor("TechCorp", CompetitorPatent(
        "US10000001", "2020-01-01", "2022-01-01",
        "Machine Learning Algorithm", "Machine Learning", 25
    ))

    intelligence.add_patent_to_competitor("TechCorp", CompetitorPatent(
        "US10000002", "2020-06-01", "2022-06-01",
        "Deep Neural Network", "Machine Learning", 30
    ))

    # Analyze competitor
    portfolio = intelligence.analyze_competitor_portfolio("TechCorp")
    print(f"TechCorp Portfolio: {portfolio['total_patents']} patents")
    print(f"Primary Focus: {portfolio['primary_focus']}")

    # Generate landscape report
    report = intelligence.generate_competitive_landscape_report()
    print(f"\nTracking {report['total_competitors_tracked']} competitors")
    print(f"Total patents: {report['total_patents_tracked']}")
