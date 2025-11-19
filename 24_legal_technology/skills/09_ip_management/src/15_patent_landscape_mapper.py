"""
Patent Landscape Mapper Example
Maps technology landscape and innovation trends
"""

from typing import List, Dict, Set, Optional
from dataclasses import dataclass
from datetime import datetime
from collections import defaultdict

@dataclass
class PatentNode:
    """Represents a patent in the landscape"""
    patent_number: str
    title: str
    technology_area: str
    filing_year: int
    citations_received: int
    assignee: str

class PatentLandscapeMapper:
    """Map and analyze patent landscape"""

    def __init__(self):
        self.patents: Dict[str, PatentNode] = {}
        self.technology_areas: Set[str] = set()

    def add_patent(self, patent: PatentNode):
        """Add patent to landscape"""
        self.patents[patent.patent_number] = patent
        self.technology_areas.add(patent.technology_area)

    def build_landscape_map(self) -> Dict:
        """Build comprehensive landscape map"""
        if not self.patents:
            return {}

        landscape = {
            'total_patents': len(self.patents),
            'technology_areas': list(self.technology_areas),
            'filing_timeline': self._build_filing_timeline(),
            'technology_distribution': self._analyze_technology_distribution(),
            'assignee_distribution': self._analyze_assignee_distribution(),
            'citation_heatmap': self._build_citation_heatmap(),
            'innovation_clusters': self._identify_innovation_clusters(),
            'technology_maturity': self._assess_technology_maturity()
        }

        return landscape

    def _build_filing_timeline(self) -> Dict:
        """Build timeline of patent filings"""
        timeline = defaultdict(int)

        for patent in self.patents.values():
            timeline[patent.filing_year] += 1

        return dict(sorted(timeline.items()))

    def _analyze_technology_distribution(self) -> Dict:
        """Analyze distribution of patents by technology"""
        distribution = defaultdict(int)

        for patent in self.patents.values():
            distribution[patent.technology_area] += 1

        return dict(sorted(distribution.items(), key=lambda x: x[1], reverse=True))

    def _analyze_assignee_distribution(self) -> Dict:
        """Analyze patent distribution by assignee/company"""
        assignees = defaultdict(int)

        for patent in self.patents.values():
            assignees[patent.assignee] += 1

        # Sort by patent count
        sorted_assignees = sorted(assignees.items(), key=lambda x: x[1], reverse=True)

        return {
            'total_assignees': len(assignees),
            'top_assignees': dict(sorted_assignees[:10]),
            'patent_concentration': sorted_assignees[0][1] / len(self.patents) if self.patents else 0
        }

    def _build_citation_heatmap(self) -> Dict:
        """Build citation impact heatmap"""
        heatmap = {
            'highly_cited': [],
            'moderately_cited': [],
            'lightly_cited': [],
            'not_cited': []
        }

        if not self.patents:
            return heatmap

        # Calculate percentiles
        citation_counts = [p.citations_received for p in self.patents.values()]
        citation_counts.sort()

        # Define thresholds
        if citation_counts:
            p75 = citation_counts[int(len(citation_counts) * 0.75)]
            p50 = citation_counts[int(len(citation_counts) * 0.50)]
            p25 = citation_counts[int(len(citation_counts) * 0.25)]

            for patent in self.patents.values():
                if patent.citations_received >= p75:
                    heatmap['highly_cited'].append(patent.patent_number)
                elif patent.citations_received >= p50:
                    heatmap['moderately_cited'].append(patent.patent_number)
                elif patent.citations_received >= p25:
                    heatmap['lightly_cited'].append(patent.patent_number)
                else:
                    heatmap['not_cited'].append(patent.patent_number)

        return heatmap

    def _identify_innovation_clusters(self) -> List[Dict]:
        """Identify clusters of related innovation"""
        clusters = []

        # Group by technology area
        tech_clusters = defaultdict(list)
        for patent in self.patents.values():
            tech_clusters[patent.technology_area].append(patent)

        # Analyze each cluster
        for tech_area, patents in tech_clusters.items():
            if len(patents) >= 3:  # Only significant clusters
                # Calculate innovation metrics
                avg_citations = sum(p.citations_received for p in patents) / len(patents)
                year_range = (max(p.filing_year for p in patents) -
                            min(p.filing_year for p in patents))

                # Identify key players
                assignees = defaultdict(int)
                for patent in patents:
                    assignees[patent.assignee] += 1

                clusters.append({
                    'technology_area': tech_area,
                    'patent_count': len(patents),
                    'average_citation_impact': avg_citations,
                    'innovation_span_years': year_range,
                    'key_players': list(sorted(assignees.items(), key=lambda x: x[1], reverse=True)[:3]),
                    'growth_trend': "Growing" if year_range > 5 and len(patents) > 5 else "Established",
                    'maturity': self._assess_cluster_maturity(patents)
                })

        return clusters

    def _assess_cluster_maturity(self, patents: List[PatentNode]) -> str:
        """Assess maturity of technology cluster"""
        if not patents:
            return "Unknown"

        # Calculate average age
        current_year = datetime.now().year
        avg_age = sum(current_year - p.filing_year for p in patents) / len(patents)
        avg_citations = sum(p.citations_received for p in patents) / len(patents)

        if avg_age < 3 and avg_citations < 5:
            return "Emerging"
        elif avg_age < 8 and avg_citations < 20:
            return "Growth"
        elif avg_citations > 20:
            return "Mature and Influential"
        else:
            return "Mature"

    def _assess_technology_maturity(self) -> Dict:
        """Assess maturity of each technology area"""
        maturity = {}

        tech_groups = defaultdict(list)
        for patent in self.patents.values():
            tech_groups[patent.technology_area].append(patent)

        for tech_area, patents in tech_groups.items():
            if patents:
                # Calculate metrics
                current_year = datetime.now().year
                avg_age = sum(current_year - p.filing_year for p in patents) / len(patents)
                filing_rate_recent = sum(1 for p in patents if current_year - p.filing_year <= 5) / len(patents)

                # Determine maturity
                if avg_age < 3:
                    stage = "Emerging"
                elif filing_rate_recent > 0.6:
                    stage = "Growth"
                elif avg_age > 10:
                    stage = "Declining"
                else:
                    stage = "Mature"

                maturity[tech_area] = stage

        return maturity

    def forecast_trends(self) -> Dict:
        """Forecast future technology trends"""
        if not self.patents:
            return {}

        current_year = datetime.now().year
        recent_years = [current_year - i for i in range(5)]

        trends = {}
        for tech_area in self.technology_areas:
            tech_patents = [p for p in self.patents.values()
                          if p.technology_area == tech_area]

            # Count recent filings
            recent_filings = sum(1 for p in tech_patents
                               if p.filing_year in recent_years)

            # Trend analysis
            if recent_filings > len(tech_patents) * 0.4:
                trend = "Rising"
            elif recent_filings < len(tech_patents) * 0.2:
                trend = "Declining"
            else:
                trend = "Stable"

            # Calculate growth rate
            if recent_filings > 0:
                growth_rate = (recent_filings / len(tech_patents)) if tech_patents else 0
            else:
                growth_rate = 0

            trends[tech_area] = {
                'trend': trend,
                'recent_filing_ratio': recent_filings / len(tech_patents) if tech_patents else 0,
                'estimated_growth_rate': growth_rate,
                'forecast': "Expansion expected" if trend == "Rising" else "Decline expected" if trend == "Declining" else "Steady state"
            }

        return trends

    def identify_technology_gaps(self, reference_landscape: 'PatentLandscapeMapper') -> Dict:
        """Identify technology gaps vs. competitor landscape"""
        our_techs = set(self.technology_areas)
        their_techs = set(reference_landscape.technology_areas)

        gaps = {
            'our_exclusive_areas': list(our_techs - their_techs),
            'their_exclusive_areas': list(their_techs - our_techs),
            'shared_areas': list(our_techs & their_techs),
            'areas_where_they_lead': [],
            'areas_where_we_lead': []
        }

        # Analyze strength in shared areas
        for tech in gaps['shared_areas']:
            our_count = len([p for p in self.patents.values() if p.technology_area == tech])
            their_count = len([p for p in reference_landscape.patents.values() if p.technology_area == tech])

            if their_count > our_count * 1.5:
                gaps['areas_where_they_lead'].append(f"{tech} ({their_count} vs {our_count})")
            elif our_count > their_count * 1.5:
                gaps['areas_where_we_lead'].append(f"{tech} ({our_count} vs {their_count})")

        return gaps


# Example usage
if __name__ == "__main__":
    mapper = PatentLandscapeMapper()

    # Add patents
    mapper.add_patent(PatentNode(
        "US10000001", "ML Algorithm", "Machine Learning", 2018, 25, "TechCorp"
    ))
    mapper.add_patent(PatentNode(
        "US10000002", "Neural Network", "Machine Learning", 2019, 30, "InnovateCo"
    ))
    mapper.add_patent(PatentNode(
        "US10000003", "Blockchain System", "Blockchain", 2020, 5, "TechCorp"
    ))

    # Build landscape
    landscape = mapper.build_landscape_map()
    print(f"Total patents: {landscape['total_patents']}")
    print(f"Technology areas: {landscape['technology_areas']}")

    # Identify clusters
    clusters = mapper._identify_innovation_clusters()
    print(f"\nInnovation clusters found: {len(clusters)}")
    for cluster in clusters:
        print(f"  {cluster['technology_area']}: {cluster['patent_count']} patents, {cluster['maturity']}")
