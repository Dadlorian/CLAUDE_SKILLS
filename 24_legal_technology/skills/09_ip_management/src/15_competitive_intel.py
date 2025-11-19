"""
Competitive Intelligence System Example
Analyzes competitor IP portfolios and market positioning
"""

from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from collections import defaultdict, Counter
import statistics


@dataclass
class CompetitorActivity:
    """Competitor patent/trademark activity"""
    competitor_id: str
    activity_type: str  # 'patent_filing', 'patent_grant', 'trademark_filing'
    count: int
    date: datetime
    technology_classes: List[str] = field(default_factory=list)
    jurisdictions: List[str] = field(default_factory=list)


@dataclass
class CompetitorProfile:
    """Competitive profile of a company"""
    competitor_name: str
    competitor_id: str
    headquarters: str
    industry: str
    patent_count: int
    trademark_count: int
    technology_focus: List[str]
    geographic_focus: List[str]
    annual_filing_rate: float
    market_share_estimate: float


class CompetitiveIntelligenceSystem:
    """Analyze competitive IP landscape"""

    def __init__(self):
        self.competitors: Dict[str, CompetitorProfile] = {}
        self.activities: List[CompetitorActivity] = []
        self.market_data = defaultdict(list)

    def add_competitor(self, profile: CompetitorProfile):
        """Add competitor to system"""
        self.competitors[profile.competitor_id] = profile

    def add_activity(self, activity: CompetitorActivity):
        """Add competitor activity"""
        self.activities.append(activity)
        self.market_data[activity.competitor_id].append(activity)

    def analyze_filing_velocity(self, competitor_id: str, months_lookback: int = 24) -> Dict:
        """
        Analyze patent/trademark filing velocity

        Args:
            competitor_id: Competitor ID
            months_lookback: Months to analyze

        Returns:
            Filing velocity metrics
        """
        cutoff_date = datetime.now() - timedelta(days=months_lookback*30)
        recent_activities = [
            a for a in self.activities
            if a.competitor_id == competitor_id and a.date >= cutoff_date
        ]

        # Count by type
        filing_counts = Counter(a.activity_type for a in recent_activities)

        # Calculate monthly trend
        activities_by_month = defaultdict(int)
        for activity in recent_activities:
            month_key = activity.date.strftime("%Y-%m")
            activities_by_month[month_key] += activity.count

        sorted_months = sorted(activities_by_month.items())

        # Calculate velocity trend
        if len(sorted_months) > 1:
            early_avg = statistics.mean(v for _, v in sorted_months[:len(sorted_months)//2])
            recent_avg = statistics.mean(v for _, v in sorted_months[len(sorted_months)//2:])
            velocity_trend = ((recent_avg - early_avg) / early_avg) * 100 if early_avg > 0 else 0
        else:
            velocity_trend = 0

        total_activities = sum(a.count for a in recent_activities)

        return {
            'competitor_id': competitor_id,
            'months_analyzed': months_lookback,
            'total_filings': total_activities,
            'filings_by_type': dict(filing_counts),
            'monthly_trend': dict(sorted_months),
            'avg_monthly_filings': total_activities / months_lookback,
            'velocity_trend_percent': velocity_trend,
            'trend_direction': 'accelerating' if velocity_trend > 10 else 'decelerating' if velocity_trend < -10 else 'stable'
        }

    def analyze_technology_focus(self, competitor_id: str) -> Dict:
        """
        Analyze competitor technology focus areas

        Args:
            competitor_id: Competitor ID

        Returns:
            Technology focus analysis
        """
        tech_classes = defaultdict(int)
        jurisdictions = defaultdict(int)

        for activity in self.activities:
            if activity.competitor_id == competitor_id:
                for tech_class in activity.technology_classes:
                    tech_classes[tech_class] += activity.count
                for jurisdiction in activity.jurisdictions:
                    jurisdictions[jurisdiction] += activity.count

        # Calculate Herfindahl index for concentration
        total_filings = sum(tech_classes.values())
        if total_filings > 0:
            concentration = sum((count / total_filings) ** 2 for count in tech_classes.values())
            diversification_score = 1 - concentration
        else:
            diversification_score = 0

        top_technologies = sorted(tech_classes.items(), key=lambda x: x[1], reverse=True)[:10]
        top_jurisdictions = sorted(jurisdictions.items(), key=lambda x: x[1], reverse=True)[:10]

        return {
            'competitor_id': competitor_id,
            'total_filings_analyzed': total_filings,
            'unique_technologies': len(tech_classes),
            'top_technologies': top_technologies,
            'unique_jurisdictions': len(jurisdictions),
            'top_jurisdictions': top_jurisdictions,
            'technology_diversification_score': diversification_score,
            'concentration_risk': 1 - diversification_score
        }

    def compare_competitors(self, competitor_ids: List[str]) -> Dict:
        """
        Compare multiple competitors

        Args:
            competitor_ids: List of competitor IDs to compare

        Returns:
            Competitive comparison matrix
        """
        comparison = {
            'competitors': competitor_ids,
            'metrics': {}
        }

        for comp_id in competitor_ids:
            if comp_id in self.competitors:
                profile = self.competitors[comp_id]
                filing_analysis = self.analyze_filing_velocity(comp_id)
                tech_analysis = self.analyze_technology_focus(comp_id)

                comparison['metrics'][comp_id] = {
                    'name': profile.competitor_name,
                    'patent_count': profile.patent_count,
                    'trademark_count': profile.trademark_count,
                    'annual_filing_rate': profile.annual_filing_rate,
                    'market_share_estimate': profile.market_share_estimate,
                    'filing_velocity_trend': filing_analysis['velocity_trend_percent'],
                    'technology_diversification': tech_analysis['technology_diversification_score'],
                    'geographic_reach': len(tech_analysis['top_jurisdictions']),
                    'technology_focus_count': len(tech_analysis['top_technologies'])
                }

        return comparison

    def identify_competitive_threats(self, watch_technologies: List[str]) -> List[Dict]:
        """
        Identify competitive threats in watch technologies

        Args:
            watch_technologies: Technology areas to monitor

        Returns:
            List of threats identified
        """
        threats = []

        for activity in self.activities:
            for watch_tech in watch_technologies:
                if watch_tech in activity.technology_classes:
                    # Check filing velocity
                    filing_analysis = self.analyze_filing_velocity(activity.competitor_id)

                    if filing_analysis['trend_direction'] in ['accelerating', 'stable'] and filing_analysis['avg_monthly_filings'] > 2:
                        threats.append({
                            'competitor_id': activity.competitor_id,
                            'competitor_name': self.competitors[activity.competitor_id].competitor_name if activity.competitor_id in self.competitors else 'Unknown',
                            'threat_technology': watch_tech,
                            'filing_count_12mo': activity.count,
                            'velocity_trend': filing_analysis['velocity_trend_percent'],
                            'threat_level': self._calculate_threat_level(filing_analysis, activity.count),
                            'last_activity_date': activity.date.isoformat()
                        })

        return sorted(threats, key=lambda x: x['threat_level'], reverse=True)

    def _calculate_threat_level(self, filing_analysis: Dict, recent_filings: int) -> str:
        """Calculate threat level based on filing metrics"""
        score = 0

        # Velocity contribution
        if filing_analysis['velocity_trend_percent'] > 25:
            score += 3
        elif filing_analysis['velocity_trend_percent'] > 10:
            score += 2
        elif filing_analysis['velocity_trend_percent'] > 0:
            score += 1

        # Volume contribution
        if filing_analysis['avg_monthly_filings'] > 5:
            score += 3
        elif filing_analysis['avg_monthly_filings'] > 3:
            score += 2
        elif filing_analysis['avg_monthly_filings'] > 1:
            score += 1

        # Recent activity contribution
        if recent_filings > 10:
            score += 2
        elif recent_filings > 5:
            score += 1

        if score >= 6:
            return "critical"
        elif score >= 4:
            return "high"
        elif score >= 2:
            return "medium"
        else:
            return "low"

    def estimate_market_position(self, our_company_metrics: Dict) -> Dict:
        """
        Estimate market position relative to competitors

        Args:
            our_company_metrics: Dictionary with our company metrics

        Returns:
            Market positioning analysis
        """
        all_metrics = {'our_company': our_company_metrics}
        all_metrics.update({
            cid: {
                'patent_count': self.competitors[cid].patent_count,
                'filing_rate': self.competitors[cid].annual_filing_rate
            }
            for cid in self.competitors
        })

        # Patent portfolio rank
        patent_counts = [(k, v['patent_count']) for k, v in all_metrics.items()]
        patent_ranks = sorted(patent_counts, key=lambda x: x[1], reverse=True)
        our_patent_rank = next((i+1 for i, (k, v) in enumerate(patent_ranks) if k == 'our_company'), None)

        # Filing velocity rank
        filing_rates = [(k, v['filing_rate']) for k, v in all_metrics.items()]
        filing_ranks = sorted(filing_rates, key=lambda x: x[1], reverse=True)
        our_filing_rank = next((i+1 for i, (k, v) in enumerate(filing_ranks) if k == 'our_company'), None)

        total_competitors = len(self.competitors)

        return {
            'our_patent_portfolio_rank': our_patent_rank,
            'total_competitors': total_competitors,
            'patent_portfolio_percentile': ((total_competitors - our_patent_rank + 1) / total_competitors * 100) if our_patent_rank else 0,
            'filing_velocity_rank': our_filing_rank,
            'filing_velocity_percentile': ((total_competitors - our_filing_rank + 1) / total_competitors * 100) if our_filing_rank else 0,
            'market_position_summary': self._summarize_position(our_patent_rank, our_filing_rank, total_competitors)
        }

    @staticmethod
    def _summarize_position(patent_rank: Optional[int], filing_rank: Optional[int], total: int) -> str:
        """Summarize market position"""
        if patent_rank and patent_rank <= total // 3:
            return "Leader"
        elif patent_rank and patent_rank <= total * 2 // 3:
            return "Challenger"
        else:
            return "Emerging"

    def generate_competitive_report(self, watch_technologies: List[str]) -> Dict:
        """
        Generate comprehensive competitive intelligence report

        Returns:
            Complete competitive analysis
        """
        return {
            'report_date': datetime.now().isoformat(),
            'total_competitors_tracked': len(self.competitors),
            'threats_identified': self.identify_competitive_threats(watch_technologies),
            'competitor_comparison': self.compare_competitors(list(self.competitors.keys())),
            'analysis_period_months': 24
        }


# Example usage
if __name__ == "__main__":
    intel_system = CompetitiveIntelligenceSystem()

    # Add competitors
    for i in range(3):
        profile = CompetitorProfile(
            competitor_name=f"CompanyTech {i}",
            competitor_id=f"COMP{i}",
            headquarters="US",
            industry="Software",
            patent_count=500 + i*100,
            trademark_count=50 + i*10,
            technology_focus=["AI", "Cloud", "Security"],
            geographic_focus=["US", "EU", "APAC"],
            annual_filing_rate=50 + i*10,
            market_share_estimate=0.15 + i*0.1
        )
        intel_system.add_competitor(profile)

    # Add sample activities
    for i in range(10):
        activity = CompetitorActivity(
            competitor_id=f"COMP{i%3}",
            activity_type="patent_filing",
            count=5,
            date=datetime.now() - timedelta(days=i*30),
            technology_classes=["G06F", "H04L"],
            jurisdictions=["US", "EU"]
        )
        intel_system.add_activity(activity)

    report = intel_system.generate_competitive_report(["G06F", "H04L"])
    print("Competitive Intelligence Report")
    print(f"Competitors Tracked: {report['total_competitors_tracked']}")
    print(f"Threats Identified: {len(report['threats_identified'])}")
    for threat in report['threats_identified']:
        if threat['threat_level'] in ['critical', 'high']:
            print(f"  - {threat['competitor_name']}: {threat['threat_level']} threat")
