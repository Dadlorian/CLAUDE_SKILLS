"""Sanctions and PEP Screening Service"""

import json
from difflib import SequenceMatcher
from dataclasses import dataclass
from typing import Dict, List, Optional

@dataclass
class ScreeningMatch:
    match_type: str  # EXACT, FUZZY, PEP
    confidence_score: float  # 0-1
    list_source: str  # OFAC, EU, UN, PEP
    matched_name: str
    customer_name: str
    recommendation: str  # BLOCK, MANUAL_REVIEW, CLEAR

class SanctionsChecker:
    """Real-time sanctions and PEP screening"""

    def __init__(self):
        # Mock sanctions data (in production, would be database)
        self.ofac_list = [
            {'name': 'Osama Bin Laden', 'dob': '1957-03-10', 'nationality': 'SA'},
            {'name': 'Ayman Al-Zawahiri', 'dob': '1951-06-19', 'nationality': 'EG'},
        ]
        self.pep_list = [
            {'name': 'Vladimir Putin', 'position': 'President', 'country': 'RU'},
            {'name': 'Xi Jinping', 'position': 'Chairman', 'country': 'CN'},
        ]
        self.eu_list = [
            {'name': 'Bashar Al-Assad', 'country': 'SY'},
            {'name': 'Maduro Nicolas', 'country': 'VE'},
        ]

    def screen_customer(self, name: str, country: str, dob: Optional[str] = None) -> Dict:
        """
        Screen customer against sanctions and PEP lists
        Returns screening result with recommendation
        """
        results = {
            'customer_name': name,
            'screening_timestamp': '2024-01-15T14:00:00Z',
            'matches': [],
            'recommendation': 'APPROVE',
            'risk_level': 'LOW'
        }

        # OFAC screening
        ofac_match = self._screen_ofac(name, dob)
        if ofac_match:
            results['matches'].append(ofac_match)
            results['recommendation'] = 'BLOCK'
            results['risk_level'] = 'CRITICAL'

        # PEP screening
        pep_match = self._screen_pep(name, country)
        if pep_match:
            results['matches'].append(pep_match)
            if results['recommendation'] != 'BLOCK':
                results['recommendation'] = 'MANUAL_REVIEW'
                results['risk_level'] = 'HIGH'

        # EU list screening
        eu_match = self._screen_eu_list(name, country)
        if eu_match:
            results['matches'].append(eu_match)
            results['recommendation'] = 'BLOCK'
            results['risk_level'] = 'CRITICAL'

        return results

    def _screen_ofac(self, name: str, dob: Optional[str]) -> Optional[ScreeningMatch]:
        """Screen against OFAC SDN list"""
        for entry in self.ofac_list:
            match_score = self._fuzzy_match(name, entry['name'])
            if match_score > 0.95:
                return ScreeningMatch(
                    match_type='EXACT',
                    confidence_score=match_score,
                    list_source='OFAC',
                    matched_name=entry['name'],
                    customer_name=name,
                    recommendation='BLOCK'
                )
            elif match_score > 0.85:
                return ScreeningMatch(
                    match_type='FUZZY',
                    confidence_score=match_score,
                    list_source='OFAC',
                    matched_name=entry['name'],
                    customer_name=name,
                    recommendation='MANUAL_REVIEW'
                )
        return None

    def _screen_pep(self, name: str, country: Optional[str]) -> Optional[ScreeningMatch]:
        """Screen against PEP list"""
        for entry in self.pep_list:
            match_score = self._fuzzy_match(name, entry['name'])
            if match_score > 0.95 and country == entry['country']:
                return ScreeningMatch(
                    match_type='PEP',
                    confidence_score=match_score,
                    list_source='PEP',
                    matched_name=entry['name'],
                    customer_name=name,
                    recommendation='MANUAL_REVIEW'
                )
        return None

    def _screen_eu_list(self, name: str, country: Optional[str]) -> Optional[ScreeningMatch]:
        """Screen against EU consolidated list"""
        for entry in self.eu_list:
            match_score = self._fuzzy_match(name, entry['name'])
            if match_score > 0.90:
                return ScreeningMatch(
                    match_type='EXACT',
                    confidence_score=match_score,
                    list_source='EU',
                    matched_name=entry['name'],
                    customer_name=name,
                    recommendation='BLOCK'
                )
        return None

    def _fuzzy_match(self, name1: str, name2: str) -> float:
        """Fuzzy string matching using sequence matcher"""
        matcher = SequenceMatcher(None, name1.lower(), name2.lower())
        return matcher.ratio()

    def batch_screen(self, customers: List[Dict]) -> List[Dict]:
        """Screen multiple customers"""
        results = []
        for customer in customers:
            result = self.screen_customer(
                customer['name'],
                customer.get('country'),
                customer.get('dob')
            )
            results.append(result)
        return results

    def update_sanctions_list(self, list_type: str, entries: List[Dict]):
        """Update sanctions list (mock implementation)"""
        if list_type == 'OFAC':
            self.ofac_list.extend(entries)
        elif list_type == 'PEP':
            self.pep_list.extend(entries)
        elif list_type == 'EU':
            self.eu_list.extend(entries)

    def get_screening_statistics(self) -> Dict:
        """Get screening database statistics"""
        return {
            'ofac_entries': len(self.ofac_list),
            'pep_entries': len(self.pep_list),
            'eu_entries': len(self.eu_list),
            'total_entries': len(self.ofac_list) + len(self.pep_list) + len(self.eu_list)
        }

# Example usage
if __name__ == "__main__":
    checker = SanctionsChecker()

    # Screen individual
    result = checker.screen_customer("John Doe", "US", "1980-01-15")
    print("Screening Result:", json.dumps(result, indent=2))

    # Batch screening
    customers = [
        {'name': 'Vladimir Putin', 'country': 'RU', 'dob': '1952-10-01'},
        {'name': 'Jane Smith', 'country': 'US', 'dob': '1985-05-15'},
        {'name': 'Bashar Assad', 'country': 'SY', 'dob': '1965-09-11'}
    ]
    batch_results = checker.batch_screen(customers)
    print("\nBatch Screening Results:")
    for r in batch_results:
        print(f"  {r['customer_name']}: {r['recommendation']}")

    # Statistics
    stats = checker.get_screening_statistics()
    print(f"\nScreening Database: {json.dumps(stats, indent=2)}")
