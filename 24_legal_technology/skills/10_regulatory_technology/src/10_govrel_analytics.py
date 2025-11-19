"""
Government Relations Analytics Module

Analytics and insights for government relations activities including:
- Legislative activity tracking and trends
- Stakeholder influence analysis
- Advocacy effectiveness measurement
- Policy outcome prediction
- ROI analysis for advocacy spend
- Sentiment and position tracking
"""

import logging
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field, asdict
from enum import Enum
import statistics

logger = logging.getLogger(__name__)


class AnalyticsMetric(Enum):
    """Key government relations metrics."""
    BILLS_INTRODUCED = "bills_introduced"
    BILLS_PASSED = "bills_passed"
    COMMITTEE_APPEARANCES = "committee_appearances"
    LEGISLATIVE_CONTACTS = "legislative_contacts"
    MEDIA_MENTIONS = "media_mentions"
    POLICY_INFLUENCE_SCORE = "policy_influence_score"
    ADVOCACY_REACH = "advocacy_reach"
    RELATIONSHIP_STRENGTH = "relationship_strength"


class TrendDirection(Enum):
    """Direction of trend."""
    INCREASING = "increasing"
    DECREASING = "decreasing"
    STABLE = "stable"


@dataclass
class AnalyticsDataPoint:
    """Individual data point for analysis."""
    metric_name: str
    value: float
    date: str
    context: Dict = field(default_factory=dict)
    source: str = "unknown"


@dataclass
class LegislativeMetrics:
    """Metrics related to legislative activity."""
    period: str  # Week, Month, Quarter, Year
    bills_introduced: int
    bills_passed: int
    bills_failed: int
    committee_hearings: int
    favorable_mentions: int
    unfavorable_mentions: int
    neutral_mentions: int
    key_votes_count: int
    favorable_votes: int
    unfavorable_votes: int


@dataclass
class StakeholderInfluenceScore:
    """Influence score for stakeholder."""
    stakeholder_id: str
    stakeholder_name: str
    organization: str
    influence_score: float  # 0-100
    reach_score: float  # Audience reach
    activity_score: float  # Recent activity level
    collaboration_score: float  # Willingness to collaborate
    position_alignment: float  # -100 to +100 alignment with organization
    trend: str  # increasing, decreasing, stable
    data_points_count: int
    last_updated: str


@dataclass
class AdvocacyEffectivenessAnalysis:
    """Analysis of advocacy campaign effectiveness."""
    campaign_id: str
    campaign_name: str
    campaign_type: str
    start_date: str
    end_date: str
    total_spend: float
    revenue_influenced: Optional[float]
    policy_outcomes_achieved: List[str]
    target_legislators_engaged: int
    legislators_converted: int
    media_impressions: int
    social_media_engagement: int
    roi_estimate: Optional[float]
    effectiveness_rating: float  # 1-10
    key_success_factors: List[str]
    improvement_areas: List[str]


@dataclass
class PolicyOutcomePredictor:
    """Prediction of policy outcome."""
    policy_id: str
    policy_name: str
    prediction_date: str
    passage_probability: float  # 0-1
    timeline_months: int
    key_supporting_factors: List[str]
    key_opposing_factors: List[str]
    critical_decision_makers: List[str]
    recommended_actions: List[str]
    confidence_level: float  # 0-1
    sensitivity_analysis: Dict  # Factor -> impact on probability


class GovernmentRelationsAnalytics:
    """
    Analytics engine for government relations activities.

    Features:
    - Activity and trend analysis
    - Stakeholder influence scoring
    - Advocacy effectiveness measurement
    - Policy outcome prediction
    - ROI and impact analysis
    - Comparative analysis
    """

    def __init__(self):
        """Initialize analytics engine."""
        self.data_points: Dict[str, List[AnalyticsDataPoint]] = {}
        self.legislative_metrics: Dict[str, LegislativeMetrics] = {}
        self.influence_scores: Dict[str, StakeholderInfluenceScore] = {}
        self.effectiveness_analyses: Dict[str, AdvocacyEffectivenessAnalysis] = {}
        self.predictions: Dict[str, PolicyOutcomePredictor] = {}
        logger.info("Government Relations Analytics initialized")

    def track_metric(
        self,
        metric_name: str,
        value: float,
        context: Dict = None,
        source: str = "manual"
    ) -> None:
        """Track analytics metric."""
        if metric_name not in self.data_points:
            self.data_points[metric_name] = []

        data_point = AnalyticsDataPoint(
            metric_name=metric_name,
            value=value,
            date=datetime.now().isoformat(),
            context=context or {},
            source=source
        )

        self.data_points[metric_name].append(data_point)
        logger.info(f"Metric tracked: {metric_name} = {value}")

    def calculate_trend(
        self,
        metric_name: str,
        days: int = 90
    ) -> Dict:
        """Calculate trend for metric."""
        if metric_name not in self.data_points:
            return {"metric": metric_name, "trend": "insufficient_data"}

        cutoff_date = (datetime.now() - timedelta(days=days)).isoformat()
        recent_points = [
            p for p in self.data_points[metric_name]
            if p.date >= cutoff_date
        ]

        if len(recent_points) < 2:
            return {
                "metric": metric_name,
                "trend": "insufficient_data",
                "data_points": len(recent_points)
            }

        values = [p.value for p in sorted(recent_points, key=lambda x: x.date)]

        # Simple linear trend
        if values[-1] > values[0]:
            trend = TrendDirection.INCREASING.value
        elif values[-1] < values[0]:
            trend = TrendDirection.DECREASING.value
        else:
            trend = TrendDirection.STABLE.value

        percent_change = ((values[-1] - values[0]) / values[0] * 100) if values[0] != 0 else 0

        return {
            "metric": metric_name,
            "period_days": days,
            "trend": trend,
            "current_value": values[-1],
            "previous_value": values[0],
            "percent_change": percent_change,
            "data_points": len(recent_points),
            "average": statistics.mean(values),
            "std_dev": statistics.stdev(values) if len(values) > 1 else 0
        }

    def record_legislative_metrics(
        self,
        period: str,
        metrics: LegislativeMetrics
    ) -> None:
        """Record legislative activity metrics."""
        period_key = f"{period}_{datetime.now().isoformat()[:10]}"
        self.legislative_metrics[period_key] = metrics
        logger.info(f"Legislative metrics recorded for {period}")

    def calculate_influence_score(
        self,
        stakeholder_id: str,
        stakeholder_name: str,
        organization: str,
        activity_data: Dict
    ) -> StakeholderInfluenceScore:
        """Calculate influence score for stakeholder."""
        # Component scores
        reach_score = min(100.0, activity_data.get("audience_reach", 0) / 1000)
        activity_score = min(
            100.0,
            activity_data.get("recent_activities", 0) * 10
        )

        collaboration_score = activity_data.get("collaboration_willingness", 50.0)

        position_alignment = activity_data.get("position_alignment", 0)

        # Weighted composite score
        influence_score = (
            reach_score * 0.3 +
            activity_score * 0.4 +
            collaboration_score * 0.2 +
            abs(position_alignment) * 0.1
        )

        recent_trend = TrendDirection.STABLE.value

        # Determine trend from recent data
        if stakeholder_id in self.influence_scores:
            previous_score = self.influence_scores[stakeholder_id].influence_score
            if influence_score > previous_score * 1.1:
                recent_trend = TrendDirection.INCREASING.value
            elif influence_score < previous_score * 0.9:
                recent_trend = TrendDirection.DECREASING.value

        score = StakeholderInfluenceScore(
            stakeholder_id=stakeholder_id,
            stakeholder_name=stakeholder_name,
            organization=organization,
            influence_score=min(100.0, influence_score),
            reach_score=reach_score,
            activity_score=activity_score,
            collaboration_score=collaboration_score,
            position_alignment=position_alignment,
            trend=recent_trend,
            data_points_count=activity_data.get("data_points", 1),
            last_updated=datetime.now().isoformat()
        )

        self.influence_scores[stakeholder_id] = score
        return score

    def analyze_advocacy_effectiveness(
        self,
        campaign_id: str,
        campaign_name: str,
        campaign_type: str,
        start_date: str,
        end_date: str,
        total_spend: float,
        outcomes_achieved: List[str],
        engagement_metrics: Dict
    ) -> AdvocacyEffectivenessAnalysis:
        """Analyze effectiveness of advocacy campaign."""
        legislators_engaged = engagement_metrics.get("legislators_engaged", 0)
        legislators_converted = engagement_metrics.get("legislators_converted", 0)
        media_impressions = engagement_metrics.get("media_impressions", 0)
        social_engagement = engagement_metrics.get("social_media_engagement", 0)
        revenue_influenced = engagement_metrics.get("revenue_influenced")

        # Calculate effectiveness rating
        conversion_rate = (
            legislators_converted / legislators_engaged
            if legislators_engaged > 0 else 0
        )

        effectiveness_rating = (
            (len(outcomes_achieved) / max(1, legislators_engaged)) * 10 +
            min(10, conversion_rate * 20) +
            min(10, media_impressions / 100000)
        ) / 3

        # Calculate ROI
        roi_estimate = None
        if revenue_influenced and total_spend > 0:
            roi_estimate = ((revenue_influenced - total_spend) / total_spend) * 100

        analysis = AdvocacyEffectivenessAnalysis(
            campaign_id=campaign_id,
            campaign_name=campaign_name,
            campaign_type=campaign_type,
            start_date=start_date,
            end_date=end_date,
            total_spend=total_spend,
            revenue_influenced=revenue_influenced,
            policy_outcomes_achieved=outcomes_achieved,
            target_legislators_engaged=legislators_engaged,
            legislators_converted=legislators_converted,
            media_impressions=media_impressions,
            social_media_engagement=social_engagement,
            roi_estimate=roi_estimate,
            effectiveness_rating=min(10.0, effectiveness_rating),
            key_success_factors=[],
            improvement_areas=[]
        )

        self.effectiveness_analyses[campaign_id] = analysis
        return analysis

    def predict_policy_outcome(
        self,
        policy_id: str,
        policy_name: str,
        supporting_factors: List[Tuple[str, float]],  # Factor, weight 0-1
        opposing_factors: List[Tuple[str, float]],
        decision_makers: List[str],
        current_indicators: Dict
    ) -> PolicyOutcomePredictor:
        """Predict policy outcome probability."""
        # Calculate base probability from factors
        support_score = sum(weight for _, weight in supporting_factors)
        opposition_score = sum(weight for _, weight in opposing_factors)

        base_probability = support_score / (support_score + opposition_score) if (support_score + opposition_score) > 0 else 0.5

        # Adjust based on decision maker engagement
        decision_makers_engaged = current_indicators.get("decision_makers_engaged", 0)
        decision_maker_adjustment = min(0.3, decision_makers_engaged / len(decision_makers) * 0.3) if decision_makers else 0

        # Adjust based on momentum
        momentum_score = current_indicators.get("momentum_score", 0)  # -1 to 1
        momentum_adjustment = momentum_score * 0.2

        # Final probability
        final_probability = min(
            0.99,
            max(0.01, base_probability + decision_maker_adjustment + momentum_adjustment)
        )

        # Estimate timeline
        timeline_months = current_indicators.get("estimated_timeline_months", 6)

        predictor = PolicyOutcomePredictor(
            policy_id=policy_id,
            policy_name=policy_name,
            prediction_date=datetime.now().isoformat(),
            passage_probability=final_probability,
            timeline_months=timeline_months,
            key_supporting_factors=[f[0] for f in supporting_factors],
            key_opposing_factors=[f[0] for f in opposing_factors],
            critical_decision_makers=decision_makers,
            recommended_actions=[],
            confidence_level=current_indicators.get("confidence_level", 0.6),
            sensitivity_analysis={}
        )

        self.predictions[policy_id] = predictor
        return predictor

    def get_high_influence_stakeholders(
        self,
        limit: int = 10,
        min_score: float = 60.0
    ) -> List[StakeholderInfluenceScore]:
        """Get highest influence stakeholders."""
        qualified = [
            s for s in self.influence_scores.values()
            if s.influence_score >= min_score
        ]

        return sorted(
            qualified,
            key=lambda x: x.influence_score,
            reverse=True
        )[:limit]

    def get_advocacy_roi_analysis(
        self,
        time_period_months: int = 12
    ) -> Dict:
        """Analyze ROI across advocacy campaigns."""
        cutoff_date = (datetime.now() - timedelta(days=time_period_months * 30)).isoformat()

        relevant_analyses = [
            a for a in self.effectiveness_analyses.values()
            if a.end_date >= cutoff_date
        ]

        if not relevant_analyses:
            return {"campaigns_analyzed": 0}

        total_spend = sum(a.total_spend for a in relevant_analyses)
        total_revenue_influenced = sum(a.revenue_influenced or 0 for a in relevant_analyses)

        campaigns_with_roi = [
            a for a in relevant_analyses
            if a.roi_estimate is not None
        ]

        average_roi = (
            statistics.mean([c.roi_estimate for c in campaigns_with_roi])
            if campaigns_with_roi else 0
        )

        return {
            "campaigns_analyzed": len(relevant_analyses),
            "period_months": time_period_months,
            "total_advocacy_spend": total_spend,
            "total_revenue_influenced": total_revenue_influenced,
            "net_value_created": total_revenue_influenced - total_spend,
            "average_campaign_roi": average_roi,
            "campaigns_by_effectiveness": sorted(
                [
                    {
                        "campaign_name": a.campaign_name,
                        "effectiveness": a.effectiveness_rating,
                        "roi": a.roi_estimate
                    }
                    for a in relevant_analyses
                ],
                key=lambda x: x["effectiveness"],
                reverse=True
            ),
            "analysis_date": datetime.now().isoformat()
        }

    def generate_comprehensive_report(self) -> Dict:
        """Generate comprehensive government relations analytics report."""
        return {
            "report_date": datetime.now().isoformat(),
            "metrics_tracked": len(self.data_points),
            "stakeholder_profiles": len(self.influence_scores),
            "campaigns_analyzed": len(self.effectiveness_analyses),
            "predictions": len(self.predictions),
            "key_metrics": {
                m: self.calculate_trend(m, 90)
                for m in list(self.data_points.keys())[:5]
            },
            "top_influencers": [
                asdict(s) for s in self.get_high_influence_stakeholders(5)
            ],
            "roi_analysis": self.get_advocacy_roi_analysis(12),
            "summary": {
                "total_data_points": sum(len(p) for p in self.data_points.values()),
                "most_recent_update": datetime.now().isoformat()
            }
        }

    def export_analytics(self, format: str = "json") -> str:
        """Export analytics report."""
        if format == "json":
            report = self.generate_comprehensive_report()
            return json.dumps(report, indent=2, default=str)

        return ""


if __name__ == "__main__":
    # Example usage
    analytics = GovernmentRelationsAnalytics()

    # Track metrics
    analytics.track_metric("bills_passed", 3, {"session": "2024-01"})
    analytics.track_metric("bills_passed", 5, {"session": "2024-02"})
    analytics.track_metric("bills_passed", 7, {"session": "2024-03"})

    # Calculate trend
    trend = analytics.calculate_trend("bills_passed", 90)
    print(f"Bills Passed Trend: {json.dumps(trend, indent=2)}")

    # Calculate influence score
    influence = analytics.calculate_influence_score(
        "STAKE_001",
        "Rep. John Smith",
        "House of Representatives",
        {
            "audience_reach": 50000,
            "recent_activities": 8,
            "collaboration_willingness": 85.0,
            "position_alignment": 45.0
        }
    )

    print(f"\nInfluence Score: {influence.influence_score:.1f}")

    # Analyze advocacy effectiveness
    effectiveness = analytics.analyze_advocacy_effectiveness(
        "CAMP_001",
        "Data Privacy Campaign",
        "Legislative",
        "2024-01-01",
        "2024-06-30",
        500000,
        ["Bill introduced", "Committee hearing held"],
        {
            "legislators_engaged": 45,
            "legislators_converted": 15,
            "media_impressions": 500000,
            "social_media_engagement": 25000,
            "revenue_influenced": 2000000
        }
    )

    print(f"\nCampaign Effectiveness Rating: {effectiveness.effectiveness_rating:.1f}/10")
    print(f"Estimated ROI: {effectiveness.roi_estimate:.1f}%")

    # Generate report
    report = analytics.generate_comprehensive_report()
    print(f"\nReport: {json.dumps(report, indent=2, default=str)}")
