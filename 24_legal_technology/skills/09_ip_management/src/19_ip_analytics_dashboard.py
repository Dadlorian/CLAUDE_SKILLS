"""
IP Analytics Dashboard Example
Generates comprehensive IP analytics and dashboard metrics
"""

from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta
from collections import defaultdict
import statistics


@dataclass
class PortfolioMetrics:
    """IP portfolio metrics"""
    total_assets: int
    total_patents: int
    total_trademarks: int
    total_copyrights: int
    granted_patents: int
    pending_patents: int
    expired_assets: int
    avg_asset_age_years: float
    geographic_coverage: int


@dataclass
class FinancialMetrics:
    """Financial metrics for IP"""
    total_asset_value: float
    annual_investment: float
    maintenance_costs_annual: float
    roi_percent: float
    cost_per_asset: float
    value_per_asset: float


@dataclass
class PerformanceMetrics:
    """Performance metrics"""
    prosecution_success_rate: float
    avg_prosecution_time_days: int
    enforcement_actions_count: int
    licensing_revenue: float
    litigation_count: int


class IPAnalyticsDashboard:
    """Generate IP analytics and dashboard data"""

    def __init__(self):
        self.portfolio_data = {}
        self.financial_data = {}
        self.performance_data = {}
        self.benchmark_data = defaultdict(dict)

    def calculate_portfolio_metrics(self, assets: List[Dict]) -> PortfolioMetrics:
        """
        Calculate portfolio metrics

        Args:
            assets: List of IP assets

        Returns:
            Portfolio metrics
        """
        total = len(assets)
        patents = sum(1 for a in assets if a.get('type') == 'patent')
        trademarks = sum(1 for a in assets if a.get('type') == 'trademark')
        copyrights = sum(1 for a in assets if a.get('type') == 'copyright')

        granted = sum(1 for a in assets if a.get('status') == 'granted')
        pending = sum(1 for a in assets if a.get('status') == 'pending')
        expired = sum(1 for a in assets if a.get('status') == 'expired')

        # Calculate average asset age
        ages = []
        for asset in assets:
            if 'creation_date' in asset:
                age = (datetime.now() - asset['creation_date']).days / 365.25
                ages.append(age)

        avg_age = statistics.mean(ages) if ages else 0

        # Count jurisdictions
        jurisdictions = set()
        for asset in assets:
            if 'jurisdictions' in asset:
                jurisdictions.update(asset['jurisdictions'])

        return PortfolioMetrics(
            total_assets=total,
            total_patents=patents,
            total_trademarks=trademarks,
            total_copyrights=copyrights,
            granted_patents=granted,
            pending_patents=pending,
            expired_assets=expired,
            avg_asset_age_years=avg_age,
            geographic_coverage=len(jurisdictions)
        )

    def calculate_financial_metrics(self, assets: List[Dict],
                                   financials: Dict) -> FinancialMetrics:
        """
        Calculate financial metrics

        Args:
            assets: List of IP assets
            financials: Financial data

        Returns:
            Financial metrics
        """
        total_value = financials.get('total_asset_value', 0)
        annual_investment = financials.get('annual_investment', 0)
        maintenance_costs = financials.get('maintenance_costs_annual', 0)
        licensing_revenue = financials.get('licensing_revenue', 0)

        total_assets = len(assets)

        # Calculate ROI
        if annual_investment > 0:
            roi = ((licensing_revenue + (total_value * 0.05) - maintenance_costs) / annual_investment) * 100
        else:
            roi = 0

        cost_per_asset = annual_investment / total_assets if total_assets > 0 else 0
        value_per_asset = total_value / total_assets if total_assets > 0 else 0

        return FinancialMetrics(
            total_asset_value=total_value,
            annual_investment=annual_investment,
            maintenance_costs_annual=maintenance_costs,
            roi_percent=roi,
            cost_per_asset=cost_per_asset,
            value_per_asset=value_per_asset
        )

    def calculate_performance_metrics(self, prosecution_history: List[Dict],
                                     enforcement_data: Dict) -> PerformanceMetrics:
        """
        Calculate performance metrics

        Args:
            prosecution_history: Patent prosecution history
            enforcement_data: Enforcement and litigation data

        Returns:
            Performance metrics
        """
        # Prosecution success rate
        successful = sum(1 for p in prosecution_history if p.get('status') == 'allowed')
        total_prosecutions = len(prosecution_history)
        success_rate = (successful / total_prosecutions * 100) if total_prosecutions > 0 else 0

        # Average prosecution time
        prosecution_times = []
        for p in prosecution_history:
            if 'filing_date' in p and 'grant_date' in p:
                time = (p['grant_date'] - p['filing_date']).days
                prosecution_times.append(time)

        avg_prosecution_time = statistics.mean(prosecution_times) if prosecution_times else 0

        # Enforcement metrics
        enforcement_actions = enforcement_data.get('enforcement_actions', 0)
        licensing_revenue = enforcement_data.get('licensing_revenue', 0)
        litigation_count = enforcement_data.get('litigation_count', 0)

        return PerformanceMetrics(
            prosecution_success_rate=success_rate,
            avg_prosecution_time_days=int(avg_prosecution_time),
            enforcement_actions_count=enforcement_actions,
            licensing_revenue=licensing_revenue,
            litigation_count=litigation_count
        )

    def generate_portfolio_dashboard(self, assets: List[Dict]) -> Dict:
        """
        Generate portfolio dashboard

        Args:
            assets: IP assets

        Returns:
            Dashboard data
        """
        metrics = self.calculate_portfolio_metrics(assets)

        # Breakdown by type
        type_breakdown = {}
        for asset in assets:
            asset_type = asset.get('type', 'unknown')
            type_breakdown[asset_type] = type_breakdown.get(asset_type, 0) + 1

        # Breakdown by status
        status_breakdown = {}
        for asset in assets:
            status = asset.get('status', 'unknown')
            status_breakdown[status] = status_breakdown.get(status, 0) + 1

        # Breakdown by jurisdiction
        jurisdiction_breakdown = defaultdict(int)
        for asset in assets:
            for jurisdiction in asset.get('jurisdictions', []):
                jurisdiction_breakdown[jurisdiction] += 1

        return {
            'portfolio_summary': {
                'total_assets': metrics.total_assets,
                'patents': metrics.total_patents,
                'trademarks': metrics.total_trademarks,
                'copyrights': metrics.total_copyrights,
                'avg_age_years': round(metrics.avg_asset_age_years, 1),
                'geographic_reach': metrics.geographic_coverage
            },
            'breakdown_by_type': type_breakdown,
            'breakdown_by_status': status_breakdown,
            'breakdown_by_jurisdiction': dict(jurisdiction_breakdown),
            'key_metrics': {
                'grant_rate': (metrics.granted_patents / metrics.total_patents * 100) if metrics.total_patents > 0 else 0,
                'pending_rate': (metrics.pending_patents / metrics.total_patents * 100) if metrics.total_patents > 0 else 0,
                'expiration_rate': (metrics.expired_assets / metrics.total_assets * 100) if metrics.total_assets > 0 else 0
            }
        }

    def generate_financial_dashboard(self, assets: List[Dict],
                                    financials: Dict) -> Dict:
        """
        Generate financial dashboard

        Args:
            assets: IP assets
            financials: Financial data

        Returns:
            Financial dashboard data
        """
        metrics = self.calculate_financial_metrics(assets, financials)

        # Value distribution
        value_distribution = {
            'patents': sum(a.get('estimated_value', 0) for a in assets if a.get('type') == 'patent'),
            'trademarks': sum(a.get('estimated_value', 0) for a in assets if a.get('type') == 'trademark'),
            'copyrights': sum(a.get('estimated_value', 0) for a in assets if a.get('type') == 'copyright')
        }

        # Cost analysis
        cost_per_asset = metrics.annual_investment / len(assets) if assets else 0

        return {
            'financial_summary': {
                'total_portfolio_value': f"${metrics.total_asset_value:,.0f}",
                'annual_investment': f"${metrics.annual_investment:,.0f}",
                'maintenance_costs': f"${metrics.maintenance_costs_annual:,.0f}",
                'avg_cost_per_asset': f"${cost_per_asset:,.0f}",
                'avg_value_per_asset': f"${metrics.value_per_asset:,.0f}",
                'roi_percent': f"{metrics.roi_percent:.1f}%"
            },
            'value_distribution': value_distribution,
            'investment_efficiency': {
                'roi': metrics.roi_percent,
                'value_to_cost_ratio': metrics.total_asset_value / metrics.annual_investment if metrics.annual_investment > 0 else 0,
                'licensing_revenue': financials.get('licensing_revenue', 0)
            }
        }

    def generate_performance_dashboard(self, prosecution_history: List[Dict],
                                      enforcement_data: Dict) -> Dict:
        """
        Generate performance dashboard

        Args:
            prosecution_history: Prosecution history
            enforcement_data: Enforcement data

        Returns:
            Performance dashboard data
        """
        metrics = self.calculate_performance_metrics(prosecution_history, enforcement_data)

        # Prosecution trends
        trends = self._calculate_prosecution_trends(prosecution_history)

        return {
            'performance_summary': {
                'prosecution_success_rate': f"{metrics.prosecution_success_rate:.1f}%",
                'avg_prosecution_months': round(metrics.avg_prosecution_time_days / 30, 1),
                'enforcement_actions': metrics.enforcement_actions_count,
                'active_litigation': metrics.litigation_count,
                'licensing_revenue': f"${metrics.licensing_revenue:,.0f}"
            },
            'prosecution_analysis': {
                'success_rate': metrics.prosecution_success_rate,
                'avg_time_days': metrics.avg_prosecution_time_days,
                'trends': trends
            },
            'enforcement_metrics': {
                'total_actions': metrics.enforcement_actions_count,
                'litigation_cases': metrics.litigation_count,
                'licensing_revenue': metrics.licensing_revenue
            }
        }

    def _calculate_prosecution_trends(self, history: List[Dict]) -> Dict:
        """Calculate prosecution trends"""
        if not history:
            return {}

        by_year = defaultdict(list)
        for item in history:
            if 'filing_date' in item:
                year = item['filing_date'].year
                by_year[year].append(item)

        trends = {}
        for year in sorted(by_year.keys()):
            items = by_year[year]
            successful = sum(1 for i in items if i.get('status') == 'allowed')
            trends[str(year)] = {
                'total': len(items),
                'successful': successful,
                'success_rate': (successful / len(items) * 100) if items else 0
            }

        return trends

    def generate_executive_dashboard(self, assets: List[Dict],
                                    financials: Dict,
                                    prosecution_history: List[Dict],
                                    enforcement_data: Dict) -> Dict:
        """
        Generate executive-level dashboard

        Args:
            assets: IP assets
            financials: Financial data
            prosecution_history: Prosecution history
            enforcement_data: Enforcement data

        Returns:
            Executive dashboard
        """
        portfolio = self.generate_portfolio_dashboard(assets)
        financial = self.generate_financial_dashboard(assets, financials)
        performance = self.generate_performance_dashboard(prosecution_history, enforcement_data)

        # Health score calculation
        portfolio_health = self._calculate_portfolio_health(portfolio)
        financial_health = self._calculate_financial_health(financial)
        performance_health = self._calculate_performance_health(performance)

        overall_health = (portfolio_health + financial_health + performance_health) / 3

        return {
            'dashboard_date': datetime.now().isoformat(),
            'portfolio': portfolio,
            'financial': financial,
            'performance': performance,
            'health_metrics': {
                'portfolio_health_score': portfolio_health,
                'financial_health_score': financial_health,
                'performance_health_score': performance_health,
                'overall_portfolio_health': overall_health,
                'status': 'excellent' if overall_health >= 80 else 'good' if overall_health >= 60 else 'fair' if overall_health >= 40 else 'needs_attention'
            },
            'key_recommendations': self._generate_recommendations(portfolio, financial, performance)
        }

    @staticmethod
    def _calculate_portfolio_health(dashboard: Dict) -> float:
        """Calculate portfolio health score (0-100)"""
        score = 50

        # Positive factors
        if dashboard['key_metrics']['grant_rate'] > 70:
            score += 20
        elif dashboard['key_metrics']['grant_rate'] > 50:
            score += 10

        if dashboard['portfolio_summary']['geographic_reach'] >= 3:
            score += 15
        elif dashboard['portfolio_summary']['geographic_reach'] >= 2:
            score += 8

        # Negative factors
        if dashboard['key_metrics']['expiration_rate'] > 20:
            score -= 15

        return min(100, max(0, score))

    @staticmethod
    def _calculate_financial_health(dashboard: Dict) -> float:
        """Calculate financial health score (0-100)"""
        score = 50

        # Positive factors
        investment_efficiency = dashboard['investment_efficiency']['value_to_cost_ratio']
        if investment_efficiency > 5:
            score += 25
        elif investment_efficiency > 2:
            score += 12

        # Negative factors
        if investment_efficiency < 1:
            score -= 20

        return min(100, max(0, score))

    @staticmethod
    def _calculate_performance_health(dashboard: Dict) -> float:
        """Calculate performance health score (0-100)"""
        score = 50

        # Positive factors
        prosecution_rate = float(
            dashboard['prosecution_analysis']['success_rate']
        ) if 'success_rate' in dashboard['prosecution_analysis'] else 50
        if prosecution_rate > 80:
            score += 25
        elif prosecution_rate > 60:
            score += 12

        return min(100, max(0, score))

    @staticmethod
    def _generate_recommendations(portfolio: Dict, financial: Dict,
                                 performance: Dict) -> List[str]:
        """Generate recommendations based on dashboard data"""
        recommendations = []

        # Portfolio recommendations
        if portfolio['key_metrics'].get('expiration_rate', 0) > 15:
            recommendations.append("High expiration rate - consider renewal strategy")

        if portfolio['portfolio_summary']['geographic_reach'] < 2:
            recommendations.append("Limited geographic coverage - expand to key markets")

        # Financial recommendations
        inv_efficiency = financial['investment_efficiency'].get('value_to_cost_ratio', 0)
        if inv_efficiency < 2:
            recommendations.append("Low ROI - review portfolio composition and maintenance")

        # Performance recommendations
        prosecution_rate = performance['prosecution_analysis'].get('success_rate', 0)
        if prosecution_rate < 70:
            recommendations.append("Prosecution success rate below target - review examination strategy")

        return recommendations[:3]  # Return top 3 recommendations


# Example usage
if __name__ == "__main__":
    dashboard = IPAnalyticsDashboard()

    # Sample data
    assets = [
        {
            'type': 'patent',
            'status': 'granted',
            'jurisdictions': ['US', 'EU'],
            'creation_date': datetime.now() - timedelta(days=365*5),
            'estimated_value': 150000
        },
        {
            'type': 'trademark',
            'status': 'registered',
            'jurisdictions': ['US'],
            'creation_date': datetime.now() - timedelta(days=365*3),
            'estimated_value': 50000
        }
    ]

    financials = {
        'total_asset_value': 500000,
        'annual_investment': 50000,
        'maintenance_costs_annual': 15000,
        'licensing_revenue': 100000
    }

    prosecution = [
        {'status': 'allowed', 'filing_date': datetime.now() - timedelta(days=365*2), 'grant_date': datetime.now() - timedelta(days=365)}
    ]

    enforcement = {
        'enforcement_actions': 2,
        'litigation_count': 1,
        'licensing_revenue': 100000
    }

    # Generate executive dashboard
    exec_dashboard = dashboard.generate_executive_dashboard(assets, financials, prosecution, enforcement)
    print("IP Analytics Executive Dashboard")
    print(f"Overall Health Score: {exec_dashboard['health_metrics']['overall_portfolio_health']:.1f}/100")
    print(f"Status: {exec_dashboard['health_metrics']['status']}")
    print(f"Total Assets: {exec_dashboard['portfolio']['portfolio_summary']['total_assets']}")
