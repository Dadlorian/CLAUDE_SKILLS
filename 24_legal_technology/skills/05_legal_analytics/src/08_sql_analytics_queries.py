"""
SQL Analytics Queries Module
Provides SQL query templates for legal analytics on databases
"""

import pandas as pd
from typing import Dict, List


class SQLAnalyticsQueries:
    """Collection of SQL queries for legal analytics."""

    # Legal spend analysis queries
    TOTAL_SPEND_BY_FIRM = """
    SELECT
        law_firm,
        COUNT(DISTINCT invoice_id) as invoice_count,
        SUM(invoice_amount) as total_spend,
        AVG(invoice_amount) as avg_invoice,
        SUM(hours_billed) as total_hours,
        SUM(invoice_amount) / SUM(hours_billed) as blended_rate
    FROM invoices
    WHERE invoice_date >= DATE_SUB(CURDATE(), INTERVAL 12 MONTH)
    GROUP BY law_firm
    ORDER BY total_spend DESC;
    """

    SPEND_BY_PRACTICE_AREA = """
    SELECT
        practice_area,
        COUNT(DISTINCT invoice_id) as invoice_count,
        SUM(invoice_amount) as total_spend,
        AVG(invoice_amount) as avg_invoice,
        SUM(hours_billed) as total_hours,
        ROUND(SUM(invoice_amount) / SUM(hours_billed), 2) as hourly_rate
    FROM invoices
    WHERE invoice_date >= DATE_SUB(CURDATE(), INTERVAL 12 MONTH)
    GROUP BY practice_area
    ORDER BY total_spend DESC;
    """

    MONTHLY_SPEND_TRENDS = """
    SELECT
        DATE_TRUNC(invoice_date, MONTH) as month,
        COUNT(*) as invoice_count,
        SUM(invoice_amount) as total_spend,
        AVG(invoice_amount) as avg_invoice,
        MAX(invoice_amount) as max_invoice,
        MIN(invoice_amount) as min_invoice,
        SUM(hours_billed) as total_hours
    FROM invoices
    GROUP BY DATE_TRUNC(invoice_date, MONTH)
    ORDER BY month DESC;
    """

    COST_PER_MATTER = """
    SELECT
        matter_id,
        COUNT(DISTINCT invoice_id) as invoice_count,
        COUNT(DISTINCT law_firm) as firm_count,
        SUM(invoice_amount) as total_cost,
        AVG(invoice_amount) as avg_invoice,
        SUM(hours_billed) as total_hours,
        ROUND(SUM(invoice_amount) / SUM(hours_billed), 2) as cost_per_hour,
        MIN(invoice_date) as start_date,
        MAX(invoice_date) as end_date,
        DATEDIFF(DAY, MIN(invoice_date), MAX(invoice_date)) as duration_days
    FROM invoices
    GROUP BY matter_id
    HAVING SUM(invoice_amount) > 100000
    ORDER BY total_cost DESC;
    """

    # Rate analysis queries
    RATE_ANALYSIS_BY_SENIORITY = """
    SELECT
        attorney_seniority,
        COUNT(*) as num_entries,
        ROUND(AVG(hourly_rate), 2) as avg_rate,
        ROUND(MEDIAN(hourly_rate), 2) as median_rate,
        ROUND(MIN(hourly_rate), 2) as min_rate,
        ROUND(MAX(hourly_rate), 2) as max_rate,
        ROUND(STDDEV(hourly_rate), 2) as rate_variance,
        ROUND(AVG(hours_billed), 2) as avg_hours_per_invoice
    FROM time_entries
    WHERE invoice_date >= DATE_SUB(CURDATE(), INTERVAL 12 MONTH)
    GROUP BY attorney_seniority
    ORDER BY avg_rate DESC;
    """

    RATE_BENCHMARKING = """
    SELECT
        law_firm,
        attorney_seniority,
        ROUND(AVG(hourly_rate), 2) as benchmark_rate,
        COUNT(*) as num_entries,
        ROUND(MIN(hourly_rate), 2) as min_rate,
        ROUND(MAX(hourly_rate), 2) as max_rate,
        ROUND(STDDEV(hourly_rate), 2) as variance
    FROM time_entries
    WHERE invoice_date >= DATE_SUB(CURDATE(), INTERVAL 24 MONTH)
    GROUP BY law_firm, attorney_seniority
    ORDER BY law_firm, attorney_seniority;
    """

    # Settlement and litigation queries
    SETTLEMENT_RECOVERY_RATE = """
    SELECT
        claim_type,
        COUNT(*) as num_settlements,
        ROUND(AVG(original_claim_amount), 0) as avg_claim,
        ROUND(AVG(final_settlement_amount), 0) as avg_settlement,
        ROUND(AVG(final_settlement_amount) / AVG(original_claim_amount) * 100, 2) as recovery_rate,
        ROUND(AVG(negotiation_duration_months), 1) as avg_duration,
        ROUND(AVG(defense_cost), 0) as avg_defense_cost,
        ROUND(AVG(final_settlement_amount - defense_cost), 0) as net_recovery
    FROM settlements
    WHERE settlement_outcome = 'Settled'
    GROUP BY claim_type
    ORDER BY recovery_rate DESC;
    """

    LITIGATION_COST_BY_TYPE = """
    SELECT
        case_type,
        COUNT(*) as num_cases,
        ROUND(AVG(claim_amount), 0) as avg_claim,
        ROUND(AVG(defense_cost), 0) as avg_defense_cost,
        ROUND(AVG(recovery_amount), 0) as avg_recovery,
        ROUND(AVG(litigation_duration_months), 1) as avg_duration,
        ROUND(AVG(defense_cost) / AVG(litigation_duration_months), 0) as cost_per_month,
        ROUND(AVG(num_depositions), 1) as avg_depositions,
        ROUND(AVG(num_experts), 1) as avg_experts
    FROM litigation_cases
    GROUP BY case_type
    ORDER BY avg_defense_cost DESC;
    """

    # Outside counsel performance queries
    COUNSEL_PERFORMANCE_SCORECARD = """
    SELECT
        law_firm,
        COUNT(DISTINCT matter_id) as matter_count,
        ROUND(SUM(matter_cost), 0) as total_cost,
        ROUND(AVG(matter_cost), 0) as avg_cost,
        ROUND(AVG(budget_variance_pct), 2) as avg_variance_pct,
        ROUND(AVG(client_satisfaction_score), 2) as satisfaction_score,
        ROUND(SUM(CASE WHEN on_time_delivery = 1 THEN 1 ELSE 0 END) * 100 / COUNT(*), 2) as on_time_pct,
        ROUND(AVG(quality_issues_count), 2) as avg_quality_issues
    FROM counsel_performance
    GROUP BY law_firm
    ORDER BY satisfaction_score DESC;
    """

    # Budget variance queries
    BUDGET_VARIANCE_ANALYSIS = """
    SELECT
        practice_area,
        COUNT(DISTINCT matter_id) as matter_count,
        ROUND(SUM(matter_budget), 0) as total_budget,
        ROUND(SUM(matter_cost), 0) as total_cost,
        ROUND(SUM(matter_cost) - SUM(matter_budget), 0) as variance_amount,
        ROUND((SUM(matter_cost) - SUM(matter_budget)) / SUM(matter_budget) * 100, 2) as variance_pct,
        SUM(CASE WHEN matter_cost > matter_budget THEN 1 ELSE 0 END) as overbudget_count,
        SUM(CASE WHEN matter_cost < matter_budget THEN 1 ELSE 0 END) as underbudget_count
    FROM matters
    WHERE matter_status IN ('Closed', 'Active')
    GROUP BY practice_area
    ORDER BY variance_pct DESC;
    """

    # Matter complexity analysis
    MATTER_COMPLEXITY_METRICS = """
    SELECT
        matter_id,
        COUNT(DISTINCT law_firm) as firm_count,
        COUNT(DISTINCT attorney_id) as attorney_count,
        SUM(hours_billed) as total_hours,
        COUNT(DISTINCT MONTH(invoice_date)) as months_active,
        SUM(invoice_amount) as total_cost,
        CASE
            WHEN SUM(hours_billed) > 500 THEN 'High Complexity'
            WHEN SUM(hours_billed) > 250 THEN 'Medium Complexity'
            ELSE 'Low Complexity'
        END as complexity_tier
    FROM invoices
    GROUP BY matter_id
    ORDER BY total_hours DESC;
    """

    # Attorney utilization
    ATTORNEY_UTILIZATION = """
    SELECT
        attorney_id,
        attorney_name,
        attorney_seniority,
        law_firm,
        COUNT(DISTINCT matter_id) as matters_worked,
        SUM(hours_billed) as total_hours_billed,
        COUNT(DISTINCT CAST(invoice_date AS DATE)) as billable_days,
        ROUND(SUM(hours_billed) / NULLIF(COUNT(DISTINCT CAST(invoice_date AS DATE)), 0), 2) as hours_per_day,
        ROUND(SUM(invoice_amount), 0) as total_billings,
        ROUND(AVG(hourly_rate), 2) as avg_hourly_rate
    FROM time_entries
    WHERE invoice_date >= DATE_SUB(CURDATE(), INTERVAL 12 MONTH)
    GROUP BY attorney_id, attorney_name, attorney_seniority, law_firm
    ORDER BY total_hours_billed DESC;
    """

    @staticmethod
    def get_all_queries() -> Dict[str, str]:
        """Return all available queries."""
        return {
            'total_spend_by_firm': SQLAnalyticsQueries.TOTAL_SPEND_BY_FIRM,
            'spend_by_practice_area': SQLAnalyticsQueries.SPEND_BY_PRACTICE_AREA,
            'monthly_trends': SQLAnalyticsQueries.MONTHLY_SPEND_TRENDS,
            'cost_per_matter': SQLAnalyticsQueries.COST_PER_MATTER,
            'rate_by_seniority': SQLAnalyticsQueries.RATE_ANALYSIS_BY_SENIORITY,
            'rate_benchmarking': SQLAnalyticsQueries.RATE_BENCHMARKING,
            'settlement_recovery': SQLAnalyticsQueries.SETTLEMENT_RECOVERY_RATE,
            'litigation_costs': SQLAnalyticsQueries.LITIGATION_COST_BY_TYPE,
            'counsel_scorecard': SQLAnalyticsQueries.COUNSEL_PERFORMANCE_SCORECARD,
            'budget_variance': SQLAnalyticsQueries.BUDGET_VARIANCE_ANALYSIS,
            'matter_complexity': SQLAnalyticsQueries.MATTER_COMPLEXITY_METRICS,
            'attorney_utilization': SQLAnalyticsQueries.ATTORNEY_UTILIZATION
        }

    @staticmethod
    def print_query(query_name: str) -> None:
        """Print a specific query."""
        queries = SQLAnalyticsQueries.get_all_queries()
        if query_name in queries:
            print(f"\n=== {query_name.upper()} ===\n")
            print(queries[query_name])
        else:
            print(f"Query '{query_name}' not found.")
            print(f"Available queries: {', '.join(queries.keys())}")

    @staticmethod
    def list_all_queries() -> List[str]:
        """List all available query names."""
        return list(SQLAnalyticsQueries.get_all_queries().keys())


# Example usage
if __name__ == "__main__":
    print("=== LEGAL ANALYTICS SQL QUERIES ===\n")

    # List all available queries
    print("Available queries:")
    for query_name in SQLAnalyticsQueries.list_all_queries():
        print(f"  - {query_name}")

    # Print specific query examples
    print("\n" + "="*50)
    SQLAnalyticsQueries.print_query('total_spend_by_firm')

    print("\n" + "="*50)
    SQLAnalyticsQueries.print_query('settlement_recovery')

    print("\n" + "="*50)
    SQLAnalyticsQueries.print_query('counsel_scorecard')
