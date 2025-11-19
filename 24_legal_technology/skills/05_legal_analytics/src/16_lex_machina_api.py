"""
Lex Machina API Integration Module

Provides integration with Lex Machina litigation analytics API for:
- Judge analytics and statistics
- Attorney statistics and performance
- Case outcome predictions
- Patent litigation analytics
- Judge propensity analysis
- Settlement prediction
"""

import requests
import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
import json
import warnings
from functools import lru_cache

warnings.filterwarnings('ignore')


class LexMachinaAPI:
    """Integration with Lex Machina litigation analytics API"""

    BASE_URL = "https://api.lexmachina.com/v1"

    def __init__(self, api_key: str, client_id: str = None, timeout: int = 30):
        """
        Initialize Lex Machina API client

        Args:
            api_key: Lex Machina API key
            client_id: Client ID for tracking
            timeout: Request timeout in seconds
        """
        self.api_key = api_key
        self.client_id = client_id
        self.timeout = timeout
        self.headers = self._build_headers()
        self.rate_limit_remaining = None
        self.rate_limit_reset = None

    def _build_headers(self) -> Dict:
        """Build HTTP headers for API requests"""
        headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json',
            'User-Agent': 'LexMachina-Analytics/1.0'
        }
        if self.client_id:
            headers['X-Client-ID'] = self.client_id
        return headers

    def _handle_rate_limit(self, response: requests.Response):
        """Handle rate limit headers"""
        if 'X-RateLimit-Remaining' in response.headers:
            self.rate_limit_remaining = int(response.headers['X-RateLimit-Remaining'])
        if 'X-RateLimit-Reset' in response.headers:
            self.rate_limit_reset = int(response.headers['X-RateLimit-Reset'])

    def _make_request(self, method: str, endpoint: str, params: Dict = None,
                     data: Dict = None) -> Dict:
        """Make API request with error handling"""
        url = f"{self.BASE_URL}{endpoint}"

        try:
            if method.upper() == 'GET':
                response = requests.get(url, headers=self.headers, params=params,
                                       timeout=self.timeout)
            elif method.upper() == 'POST':
                response = requests.post(url, headers=self.headers, json=data,
                                        timeout=self.timeout)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")

            self._handle_rate_limit(response)

            response.raise_for_status()
            return response.json()

        except requests.exceptions.RequestException as e:
            return {'error': str(e), 'status': 'failed'}

    def get_judge_analytics(self, judge_name: str, jurisdiction: str = None,
                           court: str = None) -> Dict:
        """Get judge analytics from Lex Machina"""
        params = {
            'name': judge_name,
            'jurisdiction': jurisdiction,
            'court': court
        }

        result = self._make_request('GET', '/judges/search', params=params)

        if 'error' not in result and 'judges' in result:
            judge_data = result['judges'][0] if result['judges'] else {}
            return {
                'judge_id': judge_data.get('id'),
                'name': judge_data.get('name'),
                'court': judge_data.get('court'),
                'jurisdiction': judge_data.get('jurisdiction'),
                'cases_analyzed': judge_data.get('caseCount'),
                'reversal_rate': judge_data.get('reversalRate'),
                'median_decision_time': judge_data.get('medianDecisionTime'),
                'plaintiff_win_rate': judge_data.get('plaintiffWinRate')
            }
        return result

    def get_attorney_statistics(self, attorney_name: str, firm: str = None) -> Dict:
        """Get attorney statistics from Lex Machina"""
        params = {
            'name': attorney_name,
            'firm': firm
        }

        result = self._make_request('GET', '/attorneys/search', params=params)

        if 'error' not in result and 'attorneys' in result:
            attorney_data = result['attorneys'][0] if result['attorneys'] else {}
            return {
                'attorney_id': attorney_data.get('id'),
                'name': attorney_data.get('name'),
                'firm': attorney_data.get('firm'),
                'cases_handled': attorney_data.get('caseCount'),
                'win_rate': attorney_data.get('winRate'),
                'average_recovery': attorney_data.get('avgRecovery'),
                'settlement_rate': attorney_data.get('settlementRate'),
                'average_settlement': attorney_data.get('avgSettlement')
            }
        return result

    def predict_case_outcome(self, case_data: Dict) -> Dict:
        """Predict case outcome using Lex Machina analytics"""
        prediction = self._make_request('POST', '/predictions/outcome', data=case_data)

        if 'error' not in prediction:
            return {
                'plaintiff_win_probability': prediction.get('plaintiffWinProb'),
                'defendant_win_probability': prediction.get('defendantWinProb'),
                'settlement_probability': prediction.get('settlementProb'),
                'confidence_score': prediction.get('confidence'),
                'reasoning': prediction.get('reasoning')
            }
        return prediction

    def analyze_patent_litigation(self, patent_number: str) -> Dict:
        """Get patent litigation analytics"""
        params = {'patentNumber': patent_number}

        result = self._make_request('GET', '/patents/litigation', params=params)

        if 'error' not in result:
            return {
                'patent_number': patent_number,
                'litigation_count': result.get('litigationCount'),
                'win_rate_patent_holder': result.get('holderWinRate'),
                'average_damages': result.get('avgDamages'),
                'average_litigation_duration': result.get('avgDuration'),
                'common_defendants': result.get('commonDefendants'),
                'technology_area': result.get('techArea')
            }
        return result

    def get_judge_propensity(self, judge_id: str, case_type: str = None) -> Dict:
        """Get judge propensity for specific case type"""
        params = {
            'judgeId': judge_id,
            'caseType': case_type
        }

        result = self._make_request('GET', '/judges/propensity', params=params)

        if 'error' not in result:
            return {
                'judge_id': judge_id,
                'case_type': case_type,
                'plaintiff_favorable': result.get('plaintiffFavorable'),
                'defendant_favorable': result.get('defendantFavorable'),
                'settlement_propensity': result.get('settlementPropensity'),
                'reversal_risk': result.get('reversalRisk'),
                'sample_size': result.get('sampleSize')
            }
        return result

    def predict_settlement_amount(self, case_data: Dict) -> Dict:
        """Predict settlement amount for case"""
        result = self._make_request('POST', '/predictions/settlement', data=case_data)

        if 'error' not in result:
            return {
                'predicted_settlement': result.get('expectedSettlement'),
                'settlement_range_low': result.get('rangeMin'),
                'settlement_range_high': result.get('rangeMax'),
                'confidence_interval': result.get('confidence'),
                'similar_cases': result.get('similarCases')
            }
        return result

    def get_law_firm_statistics(self, firm_name: str) -> Dict:
        """Get law firm statistics"""
        params = {'firm': firm_name}

        result = self._make_request('GET', '/firms/statistics', params=params)

        if 'error' not in result:
            return {
                'firm_name': firm_name,
                'total_cases': result.get('totalCases'),
                'win_rate': result.get('winRate'),
                'average_settlement': result.get('avgSettlement'),
                'practice_areas': result.get('practiceAreas'),
                'top_attorneys': result.get('topAttorneys'),
                'litigation_trend': result.get('trend')
            }
        return result

    def compare_judges(self, judge_ids: List[str], metrics: List[str] = None) -> pd.DataFrame:
        """Compare multiple judges across metrics"""
        if metrics is None:
            metrics = ['win_rate', 'settlement_rate', 'decision_time']

        comparison_data = []

        for judge_id in judge_ids:
            params = {'judgeId': judge_id, 'metrics': ','.join(metrics)}
            result = self._make_request('GET', '/judges/compare', params=params)

            if 'error' not in result:
                comparison_data.append(result)

        if comparison_data:
            return pd.DataFrame(comparison_data)
        return pd.DataFrame()

    def batch_judge_analysis(self, judge_names: List[str]) -> List[Dict]:
        """Batch analyze multiple judges"""
        results = []

        for judge_name in judge_names:
            result = self.get_judge_analytics(judge_name)
            results.append(result)

        return results

    def get_api_status(self) -> Dict:
        """Check API status and rate limits"""
        return {
            'status': 'available',
            'rate_limit_remaining': self.rate_limit_remaining,
            'rate_limit_reset': self.rate_limit_reset,
            'base_url': self.BASE_URL
        }


class LexMachinaAnalytics:
    """High-level analytics using Lex Machina data"""

    def __init__(self, api_client: LexMachinaAPI):
        """Initialize Lex Machina analytics"""
        self.client = api_client

    def analyze_judge_for_case(self, judge_name: str, case_type: str = None) -> Dict:
        """Comprehensive judge analysis for case"""
        judge_data = self.client.get_judge_analytics(judge_name)

        if 'error' in judge_data:
            return judge_data

        propensity = self.client.get_judge_propensity(
            judge_data.get('judge_id'),
            case_type
        )

        return {
            'judge_profile': judge_data,
            'propensity_analysis': propensity,
            'recommendation': self._generate_recommendation(judge_data, propensity)
        }

    def _generate_recommendation(self, judge_data: Dict, propensity: Dict) -> str:
        """Generate recommendation based on judge data"""
        if not judge_data or not propensity:
            return "Insufficient data"

        if propensity.get('plaintiff_favorable', 0) > 0.6:
            return "Judge favors plaintiffs - consider case strengths carefully"
        elif propensity.get('defendant_favorable', 0) > 0.6:
            return "Judge favors defendants - strong defense preparation needed"
        elif propensity.get('settlement_propensity', 0) > 0.6:
            return "Judge prefers settlements - develop settlement strategy"
        else:
            return "Judge shows balanced approach - standard litigation strategy"

    def create_judge_profile_report(self, judge_name: str) -> Dict:
        """Create comprehensive judge profile report"""
        judge_data = self.client.get_judge_analytics(judge_name)

        if 'error' in judge_data:
            return judge_data

        return {
            'judge_name': judge_data.get('name'),
            'court': judge_data.get('court'),
            'jurisdiction': judge_data.get('jurisdiction'),
            'cases_analyzed': judge_data.get('cases_analyzed'),
            'plaintiff_win_rate': f"{judge_data.get('plaintiff_win_rate', 0):.1f}%",
            'reversal_rate': f"{judge_data.get('reversal_rate', 0):.1f}%",
            'median_decision_time_days': judge_data.get('median_decision_time'),
            'key_insights': [
                f"Analyzed {judge_data.get('cases_analyzed')} cases",
                f"Plaintiff win rate: {judge_data.get('plaintiff_win_rate', 0):.1f}%",
                f"Reversal rate: {judge_data.get('reversal_rate', 0):.1f}%"
            ]
        }


def create_mock_data() -> Tuple[Dict, Dict, Dict]:
    """Create mock Lex Machina response data for testing"""
    judge_response = {
        'judges': [{
            'id': 'J123',
            'name': 'Judge John Smith',
            'court': 'US District Court - Northern District of California',
            'jurisdiction': 'Federal',
            'caseCount': 250,
            'reversalRate': 12.5,
            'medianDecisionTime': 85,
            'plaintiffWinRate': 55.0
        }]
    }

    attorney_response = {
        'attorneys': [{
            'id': 'A456',
            'name': 'Jane Doe',
            'firm': 'Smith & Associates',
            'caseCount': 120,
            'winRate': 72.5,
            'avgRecovery': 2500000,
            'settlementRate': 65.0,
            'avgSettlement': 1500000
        }]
    }

    case_prediction = {
        'plaintiffWinProb': 0.65,
        'defendantWinProb': 0.25,
        'settlementProb': 0.10,
        'confidence': 0.78,
        'reasoning': 'Strong plaintiff case based on precedent'
    }

    return judge_response, attorney_response, case_prediction


if __name__ == "__main__":
    # Mock API client for demonstration
    api_client = LexMachinaAPI(api_key='demo_key')

    # Get API status
    print("=" * 80)
    print("LEX MACHINA API INTEGRATION")
    print("=" * 80)

    print("\n1. API STATUS")
    print("-" * 80)
    status = api_client.get_api_status()
    print(f"API Status: {status['status']}")
    print(f"Base URL: {status['base_url']}")

    # Create sample data
    judge_resp, attorney_resp, prediction = create_mock_data()

    print("\n2. SAMPLE JUDGE DATA STRUCTURE")
    print("-" * 80)
    print(json.dumps(judge_resp['judges'][0], indent=2))

    print("\n3. SAMPLE ATTORNEY DATA STRUCTURE")
    print("-" * 80)
    print(json.dumps(attorney_resp['attorneys'][0], indent=2))

    print("\n4. SAMPLE CASE PREDICTION STRUCTURE")
    print("-" * 80)
    print(json.dumps(prediction, indent=2))

    print("\n5. EXPECTED API ENDPOINTS")
    print("-" * 80)
    endpoints = [
        "GET /judges/search - Search for judges",
        "GET /attorneys/search - Search for attorneys",
        "POST /predictions/outcome - Predict case outcome",
        "GET /patents/litigation - Patent litigation analytics",
        "GET /judges/propensity - Judge propensity analysis",
        "POST /predictions/settlement - Predict settlement amount",
        "GET /firms/statistics - Law firm statistics",
        "GET /judges/compare - Compare judges",
    ]
    for endpoint in endpoints:
        print(f"  {endpoint}")

    print("\n6. AUTHENTICATION")
    print("-" * 80)
    print("API Key: Bearer token in Authorization header")
    print("Rate Limit Headers: X-RateLimit-Remaining, X-RateLimit-Reset")
