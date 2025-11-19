"""
IP Portfolio Visualizer
Creates visualizations and analytics for IP portfolios
"""

import logging
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
from collections import defaultdict

logger = logging.getLogger(__name__)


class VisualizationType(Enum):
    """Types of portfolio visualizations"""
    TIMELINE = "timeline"
    HEATMAP = "heatmap"
    DISTRIBUTION = "distribution"
    NETWORK = "network"
    SCATTER = "scatter"
    BAR_CHART = "bar_chart"
    PIE_CHART = "pie_chart"


@dataclass
class PortfolioMetrics:
    """Portfolio metrics"""
    total_patents: int = 0
    total_trademarks: int = 0
    total_copyrights: int = 0
    total_value: float = 0.0
    avg_patent_age: float = 0.0
    patent_grant_rate: float = 0.0
    geographic_distribution: Dict[str, int] = None
    technology_distribution: Dict[str, int] = None
    status_distribution: Dict[str, int] = None

    def __post_init__(self):
        if self.geographic_distribution is None:
            self.geographic_distribution = {}
        if self.technology_distribution is None:
            self.technology_distribution = {}
        if self.status_distribution is None:
            self.status_distribution = {}


class TimelineAnalyzer:
    """Analyze portfolio timeline"""

    def __init__(self):
        """Initialize timeline analyzer"""
        pass

    def generate_filing_timeline(self, patents: List[Dict[str, Any]]) -> Dict[str, any]:
        """
        Generate filing timeline

        Args:
            patents: List of patent data

        Returns:
            Timeline data structure
        """
        timeline = defaultdict(int)

        for patent in patents:
            filing_date = patent.get("filing_date")
            if filing_date:
                if isinstance(filing_date, str):
                    year = int(filing_date[:4])
                else:
                    year = filing_date.year

                timeline[year] += 1

        return dict(sorted(timeline.items()))

    def generate_expiration_timeline(self, patents: List[Dict[str, Any]]) -> Dict[str, any]:
        """
        Generate expiration timeline

        Args:
            patents: List of patent data

        Returns:
            Expiration timeline
        """
        timeline = defaultdict(int)

        for patent in patents:
            expiration_date = patent.get("expiration_date")
            if expiration_date:
                if isinstance(expiration_date, str):
                    year = int(expiration_date[:4])
                else:
                    year = expiration_date.year

                timeline[year] += 1

        return dict(sorted(timeline.items()))


class GeographicAnalyzer:
    """Analyze geographic distribution of IP"""

    def __init__(self):
        """Initialize geographic analyzer"""
        self.country_codes = self._load_country_codes()

    def analyze_distribution(self, patents: List[Dict[str, Any]]) -> Dict[str, int]:
        """
        Analyze geographic distribution

        Args:
            patents: List of patent data

        Returns:
            Distribution by country/region
        """
        distribution = defaultdict(int)

        for patent in patents:
            jurisdiction = patent.get("jurisdiction", "US")
            distribution[jurisdiction] += 1

        return dict(distribution)

    def get_top_jurisdictions(
        self,
        patents: List[Dict[str, Any]],
        top_n: int = 10
    ) -> List[Tuple[str, int]]:
        """
        Get top jurisdictions

        Args:
            patents: List of patents
            top_n: Number of top jurisdictions

        Returns:
            List of (jurisdiction, count) tuples
        """
        distribution = self.analyze_distribution(patents)
        sorted_dist = sorted(distribution.items(), key=lambda x: x[1], reverse=True)
        return sorted_dist[:top_n]

    def calculate_geographic_concentration(self, patents: List[Dict[str, Any]]) -> float:
        """
        Calculate geographic concentration (Herfindahl index)

        Args:
            patents: List of patents

        Returns:
            Concentration index (0-1)
        """
        distribution = self.analyze_distribution(patents)

        if not distribution:
            return 0.0

        total = sum(distribution.values())
        concentration = sum((count / total) ** 2 for count in distribution.values())

        return concentration

    def _load_country_codes(self) -> Dict[str, str]:
        """Load country code mappings"""
        return {
            "US": "United States",
            "EP": "Europe",
            "JP": "Japan",
            "CN": "China",
            "GB": "United Kingdom",
            "DE": "Germany",
            "FR": "France",
            "CA": "Canada",
            "AU": "Australia",
            "KR": "South Korea",
        }


class TechnologyAnalyzer:
    """Analyze technology distribution"""

    def __init__(self):
        """Initialize technology analyzer"""
        self.tech_categories = self._load_tech_categories()

    def analyze_technology_distribution(
        self,
        patents: List[Dict[str, Any]]
    ) -> Dict[str, int]:
        """
        Analyze technology distribution

        Args:
            patents: List of patents

        Returns:
            Distribution by technology
        """
        distribution = defaultdict(int)

        for patent in patents:
            # Get primary technology from classification
            classifications = patent.get("classifications", [])
            if classifications:
                tech = self._classify_technology(classifications[0])
                distribution[tech] += 1
            else:
                distribution["Unknown"] += 1

        return dict(distribution)

    def get_top_technologies(
        self,
        patents: List[Dict[str, Any]],
        top_n: int = 10
    ) -> List[Tuple[str, int]]:
        """Get top technology areas"""
        distribution = self.analyze_technology_distribution(patents)
        sorted_dist = sorted(distribution.items(), key=lambda x: x[1], reverse=True)
        return sorted_dist[:top_n]

    def _classify_technology(self, classification: str) -> str:
        """Classify patent by IPC/CPC code"""
        if not classification:
            return "Unknown"

        # Get first character (section)
        section = classification[0]

        tech_map = {
            "A": "Human Necessities",
            "B": "Performing Operations; Transporting",
            "C": "Chemistry; Metallurgy",
            "D": "Textiles; Paper",
            "E": "Fixed Structures",
            "F": "Mechanical Engineering",
            "G": "Physics; Computing",
            "H": "Electricity",
        }

        return tech_map.get(section, "Unknown")

    def _load_tech_categories(self) -> Dict[str, str]:
        """Load technology category mappings"""
        return {
            "solar": "Solar & Renewable Energy",
            "battery": "Energy Storage",
            "semiconductor": "Semiconductors",
            "telecom": "Telecommunications",
            "software": "Software & IT",
        }


class PortfolioAnalyzer:
    """Analyze overall portfolio metrics"""

    def __init__(self):
        """Initialize portfolio analyzer"""
        self.timeline = TimelineAnalyzer()
        self.geographic = GeographicAnalyzer()
        self.technology = TechnologyAnalyzer()

    def calculate_portfolio_metrics(
        self,
        patents: List[Dict[str, Any]],
        trademarks: Optional[List[Dict[str, Any]]] = None,
        copyrights: Optional[List[Dict[str, Any]]] = None
    ) -> PortfolioMetrics:
        """
        Calculate comprehensive portfolio metrics

        Args:
            patents: List of patents
            trademarks: List of trademarks (optional)
            copyrights: List of copyrights (optional)

        Returns:
            PortfolioMetrics object
        """
        metrics = PortfolioMetrics()

        if patents:
            metrics.total_patents = len(patents)
            metrics.avg_patent_age = self._calculate_avg_age(patents)
            metrics.patent_grant_rate = self._calculate_grant_rate(patents)
            metrics.geographic_distribution = self.geographic.analyze_distribution(patents)
            metrics.technology_distribution = self.technology.analyze_technology_distribution(patents)
            metrics.status_distribution = self._analyze_status_distribution(patents)

        if trademarks:
            metrics.total_trademarks = len(trademarks)

        if copyrights:
            metrics.total_copyrights = len(copyrights)

        metrics.total_value = self._estimate_portfolio_value(
            patents,
            trademarks,
            copyrights
        )

        return metrics

    def get_portfolio_summary(
        self,
        patents: List[Dict[str, Any]]
    ) -> Dict[str, any]:
        """
        Get portfolio summary

        Args:
            patents: List of patents

        Returns:
            Summary data
        """
        summary = {
            "total_patents": len(patents),
            "filing_timeline": self.timeline.generate_filing_timeline(patents),
            "expiration_timeline": self.timeline.generate_expiration_timeline(patents),
            "top_jurisdictions": self.geographic.get_top_jurisdictions(patents),
            "top_technologies": self.technology.get_top_technologies(patents),
            "geographic_concentration": self.geographic.calculate_geographic_concentration(patents),
        }

        return summary

    def _calculate_avg_age(self, patents: List[Dict[str, Any]]) -> float:
        """Calculate average patent age"""
        if not patents:
            return 0.0

        today = datetime.now()
        total_age = 0

        for patent in patents:
            filing_date = patent.get("filing_date")
            if filing_date:
                if isinstance(filing_date, str):
                    filing_date = datetime.fromisoformat(filing_date)

                age_days = (today - filing_date).days
                total_age += age_days

        return total_age / len(patents) / 365.25

    def _calculate_grant_rate(self, patents: List[Dict[str, Any]]) -> float:
        """Calculate patent grant rate"""
        if not patents:
            return 0.0

        granted = sum(1 for p in patents if p.get("status") == "granted")
        return granted / len(patents)

    def _analyze_status_distribution(self, patents: List[Dict[str, Any]]) -> Dict[str, int]:
        """Analyze status distribution"""
        distribution = defaultdict(int)

        for patent in patents:
            status = patent.get("status", "unknown")
            distribution[status] += 1

        return dict(distribution)

    def _estimate_portfolio_value(
        self,
        patents: Optional[List[Dict[str, Any]]],
        trademarks: Optional[List[Dict[str, Any]]],
        copyrights: Optional[List[Dict[str, Any]]]
    ) -> float:
        """
        Estimate portfolio value (simplified)

        Args:
            patents: List of patents
            trademarks: List of trademarks
            copyrights: List of copyrights

        Returns:
            Estimated value in USD
        """
        value = 0.0

        # Average patent value estimates
        if patents:
            value += len(patents) * 50000  # ~$50k per patent

        if trademarks:
            value += len(trademarks) * 5000  # ~$5k per trademark

        if copyrights:
            value += len(copyrights) * 1000  # ~$1k per copyright

        return value


class PortfolioVisualization:
    """Generate portfolio visualization data"""

    def __init__(self, analyzer: PortfolioAnalyzer):
        """
        Initialize visualizer

        Args:
            analyzer: PortfolioAnalyzer instance
        """
        self.analyzer = analyzer

    def generate_filing_chart_data(
        self,
        patents: List[Dict[str, Any]]
    ) -> Dict[str, any]:
        """Generate data for filing timeline chart"""
        timeline = self.analyzer.timeline.generate_filing_timeline(patents)

        return {
            "type": "bar_chart",
            "title": "Patent Filings by Year",
            "data": {
                "labels": list(timeline.keys()),
                "values": list(timeline.values()),
            }
        }

    def generate_jurisdiction_chart_data(
        self,
        patents: List[Dict[str, Any]]
    ) -> Dict[str, any]:
        """Generate data for jurisdiction distribution chart"""
        top_jurisdictions = self.analyzer.geographic.get_top_jurisdictions(patents, top_n=10)

        return {
            "type": "pie_chart",
            "title": "Patent Distribution by Jurisdiction",
            "data": {
                "labels": [j[0] for j in top_jurisdictions],
                "values": [j[1] for j in top_jurisdictions],
            }
        }

    def generate_technology_chart_data(
        self,
        patents: List[Dict[str, Any]]
    ) -> Dict[str, any]:
        """Generate data for technology distribution chart"""
        top_tech = self.analyzer.technology.get_top_technologies(patents, top_n=10)

        return {
            "type": "bar_chart",
            "title": "Patents by Technology Area",
            "data": {
                "labels": [t[0] for t in top_tech],
                "values": [t[1] for t in top_tech],
            }
        }

    def generate_status_chart_data(
        self,
        patents: List[Dict[str, Any]]
    ) -> Dict[str, any]:
        """Generate data for status distribution"""
        metrics = self.analyzer.calculate_portfolio_metrics(patents)

        return {
            "type": "pie_chart",
            "title": "Patents by Status",
            "data": {
                "labels": list(metrics.status_distribution.keys()),
                "values": list(metrics.status_distribution.values()),
            }
        }

    def generate_dashboard(
        self,
        patents: List[Dict[str, Any]]
    ) -> Dict[str, any]:
        """Generate complete dashboard data"""
        metrics = self.analyzer.calculate_portfolio_metrics(patents)
        summary = self.analyzer.get_portfolio_summary(patents)

        dashboard = {
            "generated": datetime.now().isoformat(),
            "metrics": {
                "total_patents": metrics.total_patents,
                "avg_age_years": round(metrics.avg_patent_age, 1),
                "grant_rate": f"{metrics.patent_grant_rate * 100:.1f}%",
                "estimated_value": f"${metrics.total_value:,.0f}",
            },
            "charts": {
                "filings": self.generate_filing_chart_data(patents),
                "jurisdictions": self.generate_jurisdiction_chart_data(patents),
                "technologies": self.generate_technology_chart_data(patents),
                "status": self.generate_status_chart_data(patents),
            },
            "timeline": summary["filing_timeline"],
            "concentration": summary["geographic_concentration"],
        }

        return dashboard


def main():
    """Example usage"""
    # Sample patent data
    patents = [
        {
            "patent_number": "10000001",
            "filing_date": "2020-01-15",
            "issue_date": "2022-06-20",
            "jurisdiction": "US",
            "classifications": ["H02S30/20"],
            "status": "granted"
        },
        {
            "patent_number": "10000002",
            "filing_date": "2021-06-15",
            "issue_date": "2023-03-20",
            "jurisdiction": "EP",
            "classifications": ["H01L31/00"],
            "status": "granted"
        },
        {
            "patent_number": "10000003",
            "filing_date": "2022-01-10",
            "jurisdiction": "JP",
            "classifications": ["H02S40/40"],
            "status": "pending"
        },
    ]

    # Create analyzer and visualizer
    analyzer = PortfolioAnalyzer()
    visualizer = PortfolioVisualization(analyzer)

    # Generate dashboard
    dashboard = visualizer.generate_dashboard(patents)

    print("Portfolio Dashboard:")
    print(f"  Total Patents: {dashboard['metrics']['total_patents']}")
    print(f"  Average Age: {dashboard['metrics']['avg_age_years']} years")
    print(f"  Grant Rate: {dashboard['metrics']['grant_rate']}")
    print(f"  Estimated Value: {dashboard['metrics']['estimated_value']}")

    print(f"\nTop Jurisdictions:")
    for jurisdiction, count in analyzer.geographic.get_top_jurisdictions(patents):
        print(f"  {jurisdiction}: {count}")

    print(f"\nTop Technologies:")
    for tech, count in analyzer.technology.get_top_technologies(patents):
        print(f"  {tech}: {count}")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()
