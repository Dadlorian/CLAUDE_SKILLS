"""
SimpleLegal Integration Module

Provides integration with SimpleLegal legal spend management platform for:
- Invoice and spend data retrieval
- Matter cost tracking
- Vendor spend analytics
- Budget vs. actual analysis
- Cost allocation and distribution
- Spend forecasting
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
import requests
import json
import warnings

warnings.filterwarnings('ignore')


class SimpleLegalAPI:
    """Integration with SimpleLegal spend management API"""

    BASE_URL = "https://api.simplelegal.com/v2"

    def __init__(self, api_key: str, account_id: str, timeout: int = 30):
        """
        Initialize SimpleLegal API client

        Args:
            api_key: SimpleLegal API key
            account_id: SimpleLegal account ID
            timeout: Request timeout in seconds
        """
        self.api_key = api_key
        self.account_id = account_id
        self.timeout = timeout
        self.headers = self._build_headers()

    def _build_headers(self) -> Dict:
        """Build HTTP headers for API requests"""
        return {
            'Authorization': f'Bearer {self.api_key}',
            'X-Account-ID': self.account_id,
            'Content-Type': 'application/json',
            'User-Agent': 'SimpleLegal-Analytics/1.0'
        }

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

            response.raise_for_status()
            return response.json()

        except requests.exceptions.RequestException as e:
            return {'error': str(e), 'status': 'failed'}

    def get_invoices(self, start_date: str, end_date: str,
                    vendor_id: str = None, status: str = None) -> pd.DataFrame:
        """Retrieve invoices for specified period"""
        params = {
            'startDate': start_date,
            'endDate': end_date
        }

        if vendor_id:
            params['vendorId'] = vendor_id
        if status:
            params['status'] = status

        result = self._make_request('GET', '/invoices', params=params)

        if 'error' not in result and 'invoices' in result:
            return pd.DataFrame(result['invoices'])
        return pd.DataFrame()

    def get_matters(self, active_only: bool = True) -> pd.DataFrame:
        """Retrieve all matters"""
        params = {'activeOnly': active_only}

        result = self._make_request('GET', '/matters', params=params)

        if 'error' not in result and 'matters' in result:
            return pd.DataFrame(result['matters'])
        return pd.DataFrame()

    def get_vendors(self) -> pd.DataFrame:
        """Retrieve all vendors"""
        result = self._make_request('GET', '/vendors')

        if 'error' not in result and 'vendors' in result:
            return pd.DataFrame(result['vendors'])
        return pd.DataFrame()

    def get_matter_spend(self, matter_id: str) -> Dict:
        """Get total spend for specific matter"""
        result = self._make_request('GET', f'/matters/{matter_id}/spend')

        if 'error' not in result:
            return {
                'matter_id': matter_id,
                'total_spend': result.get('totalSpend'),
                'budget': result.get('budget'),
                'budget_variance': result.get('budgetVariance'),
                'budget_variance_percent': result.get('budgetVariancePercent'),
                'projected_spend': result.get('projectedSpend'),
                'vendors_count': result.get('vendorsCount')
            }
        return result

    def get_vendor_performance(self, vendor_id: str) -> Dict:
        """Get performance metrics for specific vendor"""
        result = self._make_request('GET', f'/vendors/{vendor_id}/performance')

        if 'error' not in result:
            return {
                'vendor_id': vendor_id,
                'vendor_name': result.get('vendorName'),
                'total_spend': result.get('totalSpend'),
                'invoice_count': result.get('invoiceCount'),
                'avg_invoice_amount': result.get('avgInvoiceAmount'),
                'on_time_payment_rate': result.get('onTimePaymentRate'),
                'avg_invoice_processing_days': result.get('avgProcessingDays'),
                'compliance_score': result.get('complianceScore')
            }
        return result

    def get_spend_by_vendor(self, start_date: str, end_date: str) -> pd.DataFrame:
        """Get spend aggregated by vendor"""
        params = {
            'startDate': start_date,
            'endDate': end_date,
            'groupBy': 'vendor'
        }

        result = self._make_request('GET', '/analytics/spend', params=params)

        if 'error' not in result and 'data' in result:
            return pd.DataFrame(result['data'])
        return pd.DataFrame()

    def get_spend_by_matter(self, start_date: str, end_date: str) -> pd.DataFrame:
        """Get spend aggregated by matter"""
        params = {
            'startDate': start_date,
            'endDate': end_date,
            'groupBy': 'matter'
        }

        result = self._make_request('GET', '/analytics/spend', params=params)

        if 'error' not in result and 'data' in result:
            return pd.DataFrame(result['data'])
        return pd.DataFrame()

    def get_budget_vs_actual(self, period: str = 'monthly') -> pd.DataFrame:
        """Get budget vs actual analysis"""
        params = {'period': period}

        result = self._make_request('GET', '/analytics/budget-analysis', params=params)

        if 'error' not in result and 'data' in result:
            return pd.DataFrame(result['data'])
        return pd.DataFrame()

    def forecast_spend(self, months_ahead: int = 3) -> Dict:
        """Forecast future spend based on trends"""
        params = {'monthsAhead': months_ahead}

        result = self._make_request('GET', '/analytics/forecast', params=params)

        if 'error' not in result:
            return {
                'forecast_period_months': months_ahead,
                'forecasted_monthly_spend': result.get('monthlyForecast'),
                'total_forecasted_spend': result.get('totalForecast'),
                'confidence_level': result.get('confidence'),
                'key_drivers': result.get('drivers')
            }
        return result

    def get_cost_allocation(self, allocation_method: str = 'proportional') -> Dict:
        """Get cost allocation analysis"""
        params = {'method': allocation_method}

        result = self._make_request('GET', '/analytics/cost-allocation', params=params)

        return result if 'error' not in result else {}

    def create_budget(self, matter_id: str, budget_amount: float,
                     fiscal_year: str) -> Dict:
        """Create budget for matter"""
        data = {
            'matterId': matter_id,
            'budgetAmount': budget_amount,
            'fiscalYear': fiscal_year
        }

        result = self._make_request('POST', '/budgets', data=data)

        return result if 'error' not in result else {}


class SimpleLegalAnalytics:
    """High-level analytics using SimpleLegal data"""

    def __init__(self, api_client: SimpleLegalAPI):
        """Initialize SimpleLegal analytics"""
        self.client = api_client

    def analyze_spend_trends(self, months: int = 12) -> Dict:
        """Analyze spend trends over time"""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=30 * months)

        spend_by_period = self.client.get_spend_by_vendor(
            start_date.strftime('%Y-%m-%d'),
            end_date.strftime('%Y-%m-%d')
        )

        if spend_by_period.empty:
            return {'error': 'No spend data available'}

        # Calculate trends
        total_spend = spend_by_period['spend'].sum() if 'spend' in spend_by_period else 0
        avg_monthly_spend = total_spend / months if months > 0 else 0

        return {
            'total_spend': total_spend,
            'average_monthly_spend': avg_monthly_spend,
            'month_count': months,
            'top_vendors': spend_by_period.nlargest(5, 'spend').to_dict('records') if 'spend' in spend_by_period else []
        }

    def identify_budget_overruns(self, threshold_percent: float = 110) -> List[Dict]:
        """Identify matters exceeding budget"""
        budget_analysis = self.client.get_budget_vs_actual()

        if budget_analysis.empty:
            return []

        overruns = budget_analysis[
            budget_analysis['variance_percent'] > threshold_percent
        ].to_dict('records')

        return overruns

    def vendor_performance_report(self) -> pd.DataFrame:
        """Generate vendor performance report"""
        vendors = self.client.get_vendors()

        if vendors.empty:
            return pd.DataFrame()

        performance_data = []
        for vendor_id in vendors['vendor_id'].unique():
            perf = self.client.get_vendor_performance(vendor_id)
            performance_data.append(perf)

        return pd.DataFrame(performance_data)

    def spend_forecasting_report(self) -> Dict:
        """Generate spend forecasting report"""
        forecast = self.client.forecast_spend(months_ahead=6)

        return {
            'forecast': forecast,
            'summary': f"Forecasted 6-month spend: ${forecast.get('total_forecasted_spend', 0):,.0f}",
            'confidence': f"{forecast.get('confidence_level', 0):.0f}%"
        }


class SimpleLegalDataTransform:
    """Transform SimpleLegal data for analytics"""

    @staticmethod
    def calculate_matter_profitability(invoices_df: pd.DataFrame,
                                      matters_df: pd.DataFrame) -> pd.DataFrame:
        """Calculate profitability by merging invoice and matter data"""
        if invoices_df.empty or matters_df.empty:
            return pd.DataFrame()

        # Merge and aggregate
        merged = invoices_df.merge(matters_df, left_on='matter_id', right_on='matter_id')

        profitability = merged.groupby('matter_id').agg({
            'amount': 'sum',
            'budget': 'first'
        }).reset_index()

        profitability['variance'] = profitability['budget'] - profitability['amount']
        profitability['variance_percent'] = (
            profitability['variance'] / profitability['budget'] * 100
        )

        return profitability

    @staticmethod
    def identify_cost_drivers(invoices_df: pd.DataFrame) -> pd.DataFrame:
        """Identify top cost drivers"""
        if invoices_df.empty:
            return pd.DataFrame()

        cost_drivers = invoices_df.groupby('vendor_id')['amount'].sum().sort_values(ascending=False)

        return cost_drivers.to_frame().reset_index().head(10)


def create_mock_spend_data() -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Create mock SimpleLegal data for testing"""
    np.random.seed(42)

    # Mock invoices
    invoices = pd.DataFrame({
        'invoice_id': [f'INV{i:06d}' for i in range(1, 201)],
        'vendor_id': [f'V{np.random.randint(1, 21):03d}' for _ in range(200)],
        'matter_id': [f'M{np.random.randint(1, 51):05d}' for _ in range(200)],
        'amount': np.random.uniform(5000, 50000, 200),
        'invoice_date': pd.date_range('2023-01-01', periods=200, freq='2D'),
        'status': np.random.choice(['Paid', 'Pending', 'Approved'], 200)
    })

    # Mock matters
    matters = pd.DataFrame({
        'matter_id': [f'M{i:05d}' for i in range(1, 51)],
        'matter_name': [f'Matter {i}' for i in range(1, 51)],
        'budget': np.random.uniform(100000, 500000, 50)
    })

    # Mock vendors
    vendors = pd.DataFrame({
        'vendor_id': [f'V{i:03d}' for i in range(1, 21)],
        'vendor_name': [f'Vendor {i}' for i in range(1, 21)],
        'vendor_type': np.random.choice(['Outside Counsel', 'Court Reporter', 'Expert'], 20)
    })

    return invoices, matters, vendors


if __name__ == "__main__":
    # Create mock data
    invoices_df, matters_df, vendors_df = create_mock_spend_data()

    print("=" * 80)
    print("SIMPLELEGAL INTEGRATION")
    print("=" * 80)

    print("\n1. MOCK INVOICES DATA")
    print("-" * 80)
    print(invoices_df.head(10).to_string(index=False))

    print("\n2. MOCK MATTERS DATA")
    print("-" * 80)
    print(matters_df.head(10).to_string(index=False))

    print("\n3. MOCK VENDORS DATA")
    print("-" * 80)
    print(vendors_df.to_string(index=False))

    print("\n4. COST DRIVERS ANALYSIS")
    print("-" * 80)
    cost_drivers = SimpleLegalDataTransform.identify_cost_drivers(invoices_df)
    if not cost_drivers.empty:
        print(cost_drivers.to_string(index=False))

    print("\n5. MATTER PROFITABILITY")
    print("-" * 80)
    profitability = SimpleLegalDataTransform.calculate_matter_profitability(invoices_df, matters_df)
    print(profitability.head(10).to_string(index=False))

    print("\n6. EXPECTED API ENDPOINTS")
    print("-" * 80)
    endpoints = [
        "GET /invoices - Retrieve invoices",
        "GET /matters - Retrieve matters",
        "GET /vendors - Retrieve vendors",
        "GET /matters/{id}/spend - Get matter spend",
        "GET /vendors/{id}/performance - Get vendor performance",
        "GET /analytics/spend - Spend analytics",
        "GET /analytics/budget-analysis - Budget vs actual",
        "GET /analytics/forecast - Spend forecasting",
        "POST /budgets - Create budget",
    ]
    for endpoint in endpoints:
        print(f"  {endpoint}")
