#!/usr/bin/env python3
"""
Terminology Service Integration
SNOMED CT, LOINC, RxNorm code lookup and mapping
"""

import requests
from typing import Dict, List, Optional
import logging
from functools import lru_cache

logger = logging.getLogger(__name__)

class SNOMEDService:
    """SNOMED CT terminology service"""

    def __init__(self, base_url: str = "https://browser.ihtsdotools.org/snowstorm/snomed-ct"):
        self.base_url = base_url

    def lookup_concept(self, code: str) -> Optional[Dict]:
        """Look up SNOMED concept"""
        try:
            url = f"{self.base_url}/browser/concepts/{code}"
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"SNOMED lookup failed: {e}")
            return None

    def search_concepts(self, term: str, limit: int = 50) -> List[Dict]:
        """Search for SNOMED concepts"""
        try:
            url = f"{self.base_url}/browser/concepts"
            params = {'term': term, 'returnLimit': limit}
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()

            data = response.json()
            return data.get('items', [])
        except Exception as e:
            logger.error(f"SNOMED search failed: {e}")
            return []

    def get_parent_concepts(self, code: str) -> List[Dict]:
        """Get parent concepts"""
        try:
            concept = self.lookup_concept(code)
            if concept and 'parents' in concept:
                return concept['parents']
            return []
        except Exception as e:
            logger.error(f"Parent lookup failed: {e}")
            return []


class LOINCService:
    """LOINC terminology service"""

    def __init__(self, api_key: Optional[str] = None):
        self.base_url = "https://loinc.org/api/search"
        self.api_key = api_key

    def search_loinc(self, search_term: str) -> List[Dict]:
        """Search for LOINC codes"""
        try:
            params = {'q': search_term}
            if self.api_key:
                params['api_key'] = self.api_key

            response = requests.get(self.base_url, params=params, timeout=10)
            response.raise_for_status()

            data = response.json()
            return data.get('documents', [])
        except Exception as e:
            logger.error(f"LOINC search failed: {e}")
            return []

    def get_loinc_details(self, loinc_code: str) -> Optional[Dict]:
        """Get LOINC code details"""
        try:
            url = f"https://loinc.org/api/{loinc_code}"
            params = {}
            if self.api_key:
                params['api_key'] = self.api_key

            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"LOINC details failed: {e}")
            return None


class RxNormService:
    """RxNorm terminology service"""

    def __init__(self):
        self.base_url = "https://rxnav.nlm.nih.gov/REST"

    def search_by_name(self, drug_name: str) -> List[str]:
        """Search for drug by name"""
        try:
            url = f"{self.base_url}/rxcui"
            params = {'name': drug_name}

            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()

            data = response.json()
            if "idGroup" in data and data["idGroup"]["rxUris"]:
                return [uri.split("/")[-1] for uri in data["idGroup"]["rxUris"]]

            return []
        except Exception as e:
            logger.error(f"RxNorm search failed: {e}")
            return []

    def get_drug_info(self, rxcui: str) -> Optional[Dict]:
        """Get drug information"""
        try:
            url = f"{self.base_url}/rxcui/{rxcui}/properties"
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            return response.json().get('properties', {})
        except Exception as e:
            logger.error(f"RxNorm info failed: {e}")
            return None

    def check_interactions(self, rxcui_list: List[str]) -> Dict:
        """Check drug interactions"""
        try:
            url = f"{self.base_url}/interaction"
            params = {'rxcuis': '+'.join(rxcui_list)}

            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Interaction check failed: {e}")
            return {}

    def find_alternatives(self, rxcui: str) -> List[Dict]:
        """Find alternative medications"""
        try:
            url = f"{self.base_url}/rxcui/{rxcui}/allrelatives"
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            return response.json().get('allRelatives', [])
        except Exception as e:
            logger.error(f"Alternative search failed: {e}")
            return []


class CodeMappingService:
    """Code mapping between terminology systems"""

    def __init__(self, db_session):
        self.db = db_session
        self.snomed = SNOMEDService()
        self.loinc = LOINCService()
        self.rxnorm = RxNormService()

    def map_code(self, source_code: str, source_system: str,
                 target_system: str) -> Optional[Dict]:
        """Map code between systems"""
        # Check cache
        cached = self._get_cached_mapping(source_code, source_system, target_system)
        if cached:
            return cached

        # Attempt dynamic mapping
        result = self._perform_mapping(source_code, source_system, target_system)

        if result:
            self._cache_mapping(source_code, source_system, target_system, result)

        return result

    def validate_code(self, code: str, system: str) -> bool:
        """Validate code against terminology system"""
        if system.lower() == 'snomed':
            return self.snomed.lookup_concept(code) is not None
        elif system.lower() == 'loinc':
            return self.loinc.get_loinc_details(code) is not None
        elif system.lower() == 'rxnorm':
            return self.rxnorm.get_drug_info(code) is not None

        return False

    def _perform_mapping(self, source_code: str, source_system: str,
                        target_system: str) -> Optional[Dict]:
        """Perform actual code mapping"""
        # This would implement actual mapping logic
        # For now, return None (would need real mapping data)

        if source_system == 'local' and target_system == 'snomed':
            results = self.snomed.search_concepts(source_code)
            if results:
                return {
                    'code': results[0]['id'],
                    'display': results[0]['term']
                }

        return None

    def _get_cached_mapping(self, source_code: str, source_system: str,
                           target_system: str) -> Optional[Dict]:
        """Get mapping from cache"""
        # Query database cache
        # Implementation depends on database schema
        return None

    def _cache_mapping(self, source_code: str, source_system: str,
                      target_system: str, result: Dict):
        """Cache mapping result"""
        # Store in database
        # Implementation depends on database schema
        pass


if __name__ == '__main__':
    # Example usage
    snomed = SNOMEDService()
    concept = snomed.lookup_concept("80891009")
    print(f"SNOMED: {concept}")

    loinc = LOINCService()
    glucose_tests = loinc.search_loinc("glucose")
    print(f"LOINC results: {len(glucose_tests)}")

    rxnorm = RxNormService()
    drugs = rxnorm.search_by_name("metformin")
    print(f"RxNorm results: {drugs}")
