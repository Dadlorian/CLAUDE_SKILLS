"""
Threat Intelligence Aggregator
Collect and analyze threat intelligence from multiple sources
"""

from typing import Dict, List, Set
from dataclasses import dataclass
from datetime import datetime
import hashlib


@dataclass
class ThreatIndicator:
    """Threat indicator (IOC)"""
    ioc_type: str  # ip, domain, hash, url
    value: str
    threat_type: str  # malware, phishing, c2, etc.
    confidence: int  # 1-100
    first_seen: datetime
    last_seen: datetime
    sources: List[str]


class ThreatIntelligence:
    """
    Threat Intelligence Platform

    Features:
    - IOC collection and normalization
    - Threat correlation
    - Risk scoring
    - Alert generation
    - STIX/TAXII integration (simulated)
    """

    def __init__(self):
        self.indicators: Dict[str, ThreatIndicator] = {}
        self.threat_actors: Dict[str, Dict] = {}
        self.campaigns: Dict[str, Dict] = {}

    def add_indicator(self, indicator: ThreatIndicator):
        """Add threat indicator"""
        key = f"{indicator.ioc_type}:{indicator.value}"

        if key in self.indicators:
            # Update existing indicator
            existing = self.indicators[key]
            existing.last_seen = indicator.last_seen
            existing.sources.extend(indicator.sources)
            existing.sources = list(set(existing.sources))
            # Average confidence scores
            existing.confidence = (existing.confidence + indicator.confidence) // 2
        else:
            self.indicators[key] = indicator

    def check_ioc(self, ioc_type: str, value: str) -> bool:
        """Check if IOC is known threat"""
        key = f"{ioc_type}:{value}"
        return key in self.indicators

    def get_threat_score(self, ioc_type: str, value: str) -> int:
        """Get threat score for IOC"""
        key = f"{ioc_type}:{value}"
        if key in self.indicators:
            indicator = self.indicators[key]
            # Calculate score based on confidence and recency
            days_old = (datetime.now() - indicator.last_seen).days
            recency_factor = max(0, 100 - days_old * 2)  # Decay over time
            return (indicator.confidence + recency_factor) // 2
        return 0

    def correlate_threats(self, ioc_list: List[tuple]) -> Dict:
        """Correlate multiple IOCs to identify campaigns"""
        correlation = {
            'related_indicators': [],
            'threat_types': set(),
            'confidence': 0,
            'recommendation': ''
        }

        matched_indicators = []
        for ioc_type, value in ioc_list:
            key = f"{ioc_type}:{value}"
            if key in self.indicators:
                matched_indicators.append(self.indicators[key])

        if matched_indicators:
            # Aggregate threat types
            for indicator in matched_indicators:
                correlation['threat_types'].add(indicator.threat_type)

            # Calculate average confidence
            avg_confidence = sum(i.confidence for i in matched_indicators) // len(matched_indicators)
            correlation['confidence'] = avg_confidence
            correlation['related_indicators'] = [i.value for i in matched_indicators]

            # Generate recommendation
            if avg_confidence >= 80:
                correlation['recommendation'] = 'BLOCK - High confidence threat'
            elif avg_confidence >= 50:
                correlation['recommendation'] = 'ALERT - Investigate further'
            else:
                correlation['recommendation'] = 'MONITOR - Low confidence'

        correlation['threat_types'] = list(correlation['threat_types'])
        return correlation

    def enrich_ioc(self, ioc_type: str, value: str) -> Dict:
        """Enrich IOC with additional context"""
        key = f"{ioc_type}:{value}"

        if key not in self.indicators:
            return {'status': 'unknown'}

        indicator = self.indicators[key]

        enrichment = {
            'status': 'known_threat',
            'ioc_type': indicator.ioc_type,
            'value': indicator.value,
            'threat_type': indicator.threat_type,
            'confidence': indicator.confidence,
            'first_seen': indicator.first_seen.isoformat(),
            'last_seen': indicator.last_seen.isoformat(),
            'sources': indicator.sources,
            'age_days': (datetime.now() - indicator.first_seen).days,
            'threat_score': self.get_threat_score(ioc_type, value)
        }

        return enrichment

    def generate_threat_report(self) -> Dict:
        """Generate threat intelligence report"""
        threat_types = {}
        high_confidence_threats = []

        for indicator in self.indicators.values():
            # Count by threat type
            if indicator.threat_type not in threat_types:
                threat_types[indicator.threat_type] = 0
            threat_types[indicator.threat_type] += 1

            # Collect high confidence threats
            if indicator.confidence >= 80:
                high_confidence_threats.append({
                    'type': indicator.ioc_type,
                    'value': indicator.value,
                    'threat_type': indicator.threat_type,
                    'confidence': indicator.confidence
                })

        return {
            'report_date': datetime.now().isoformat(),
            'total_indicators': len(self.indicators),
            'threat_types': threat_types,
            'high_confidence_threats': high_confidence_threats[:10]  # Top 10
        }


if __name__ == "__main__":
    ti = ThreatIntelligence()

    # Add sample indicators
    malware_ip = ThreatIndicator(
        ioc_type="ip",
        value="192.0.2.1",
        threat_type="malware_c2",
        confidence=95,
        first_seen=datetime.now(),
        last_seen=datetime.now(),
        sources=["AlienVault", "VirusTotal"]
    )

    ti.add_indicator(malware_ip)

    # Check IOC
    is_threat = ti.check_ioc("ip", "192.0.2.1")
    print(f"Is threat: {is_threat}")

    # Enrich IOC
    enrichment = ti.enrich_ioc("ip", "192.0.2.1")
    print(f"Threat score: {enrichment['threat_score']}")
