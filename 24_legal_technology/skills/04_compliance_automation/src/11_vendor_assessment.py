#!/usr/bin/env python3
"""
Comprehensive Vendor Assessment System
Automated vendor performance and compliance assessment
"""

import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from enum import Enum

class AssessmentStatus(Enum):
    INITIATED = "initiated"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"

class PerformanceRating(Enum):
    EXCELLENT = 5
    GOOD = 4
    ACCEPTABLE = 3
    POOR = 2
    UNACCEPTABLE = 1

class VendorAssessmentEngine:
    """Comprehensive vendor assessment and performance evaluation"""

    def __init__(self, assessment_id: Optional[str] = None):
        self.assessment_id = assessment_id or f"VA_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.vendor_data = {}
        self.assessment_results = {}
        self.performance_metrics = {}
        self.compliance_findings = []
        self.assessment_status = AssessmentStatus.INITIATED

    def initiate_vendor_assessment(self, vendor_id: str, vendor_name: str,
                                   assessment_scope: List[str]) -> Dict:
        """
        Initiate comprehensive vendor assessment

        Args:
            vendor_id: Unique vendor identifier
            vendor_name: Vendor company name
            assessment_scope: List of assessment areas

        Returns:
            Assessment initiation confirmation
        """
        try:
            if not vendor_id or not vendor_name:
                raise ValueError("Vendor ID and name are required")

            if not assessment_scope or not isinstance(assessment_scope, list):
                raise ValueError("Assessment scope must be non-empty list")

            self.vendor_data = {
                'vendor_id': vendor_id,
                'vendor_name': vendor_name,
                'assessment_scope': assessment_scope,
                'initiated_date': datetime.now().isoformat(),
                'assessment_status': AssessmentStatus.INITIATED.value
            }

            self.assessment_status = AssessmentStatus.IN_PROGRESS

            return {
                'assessment_id': self.assessment_id,
                'vendor_id': vendor_id,
                'status': self.assessment_status.value,
                'initiated_date': self.vendor_data['initiated_date'],
                'scope': assessment_scope,
                'message': 'Vendor assessment initiated successfully'
            }
        except Exception as e:
            self.assessment_status = AssessmentStatus.FAILED
            return {
                'assessment_id': self.assessment_id,
                'status': self.assessment_status.value,
                'error': str(e),
                'message': 'Failed to initiate assessment'
            }

    def assess_financial_stability(self, financial_data: Dict) -> Dict:
        """
        Assess vendor financial stability and creditworthiness

        Args:
            financial_data: Dictionary with financial metrics

        Returns:
            Financial stability assessment
        """
        try:
            if not financial_data:
                raise ValueError("Financial data is required")

            assessment = {
                'assessment_type': 'financial_stability',
                'assessment_date': datetime.now().isoformat(),
                'metrics': {
                    'revenue': financial_data.get('revenue'),
                    'profit_margin': financial_data.get('profit_margin'),
                    'debt_ratio': financial_data.get('debt_ratio'),
                    'liquidity_ratio': financial_data.get('liquidity_ratio'),
                    'credit_rating': financial_data.get('credit_rating', 'Not Available')
                },
                'financial_health': self._evaluate_financial_health(financial_data),
                'risk_level': self._calculate_financial_risk(financial_data),
                'recommendations': self._generate_financial_recommendations(financial_data)
            }

            return assessment
        except Exception as e:
            return {
                'assessment_type': 'financial_stability',
                'error': str(e),
                'status': 'failed'
            }

    def evaluate_operational_performance(self, performance_data: Dict) -> Dict:
        """
        Evaluate vendor operational performance metrics

        Args:
            performance_data: Operational metrics data

        Returns:
            Operational performance assessment
        """
        try:
            if not performance_data:
                raise ValueError("Performance data is required")

            metrics = {
                'on_time_delivery_rate': performance_data.get('on_time_delivery', 0),
                'quality_score': performance_data.get('quality_score', 0),
                'incident_count': performance_data.get('incident_count', 0),
                'response_time_hours': performance_data.get('response_time', 0),
                'customer_satisfaction': performance_data.get('satisfaction_score', 0)
            }

            overall_rating = self._calculate_performance_rating(metrics)

            assessment = {
                'assessment_type': 'operational_performance',
                'assessment_date': datetime.now().isoformat(),
                'metrics': metrics,
                'overall_rating': overall_rating.name,
                'rating_score': overall_rating.value,
                'performance_trend': self._analyze_performance_trend(performance_data),
                'improvement_areas': self._identify_improvement_areas(metrics)
            }

            return assessment
        except Exception as e:
            return {
                'assessment_type': 'operational_performance',
                'error': str(e),
                'status': 'failed'
            }

    def assess_compliance_posture(self, compliance_data: Dict) -> Dict:
        """
        Assess vendor compliance posture and certifications

        Args:
            compliance_data: Compliance information

        Returns:
            Compliance assessment results
        """
        try:
            if not compliance_data:
                raise ValueError("Compliance data is required")

            certifications = compliance_data.get('certifications', [])
            audit_findings = compliance_data.get('audit_findings', {})
            violations = compliance_data.get('violations', [])

            assessment = {
                'assessment_type': 'compliance_posture',
                'assessment_date': datetime.now().isoformat(),
                'certifications': {
                    'iso_27001': 'ISO 27001' in certifications,
                    'soc_2': 'SOC 2' in certifications,
                    'iso_9001': 'ISO 9001' in certifications,
                    'industry_specific': [c for c in certifications if c not in ['ISO 27001', 'SOC 2', 'ISO 9001']]
                },
                'audit_findings': audit_findings,
                'critical_violations': len([v for v in violations if v.get('severity') == 'critical']),
                'open_non_conformances': len([v for v in violations if v.get('resolved') == False]),
                'compliance_score': self._calculate_compliance_score(compliance_data),
                'remediation_status': self._assess_remediation_status(violations)
            }

            return assessment
        except Exception as e:
            return {
                'assessment_type': 'compliance_posture',
                'error': str(e),
                'status': 'failed'
            }

    def review_service_level_agreements(self, sla_data: Dict) -> Dict:
        """
        Review vendor service level agreements and adherence

        Args:
            sla_data: SLA terms and performance data

        Returns:
            SLA review results
        """
        try:
            if not sla_data:
                raise ValueError("SLA data is required")

            sla_terms = sla_data.get('sla_terms', {})
            performance = sla_data.get('performance_data', {})

            adherence_analysis = {}
            for metric, target in sla_terms.items():
                actual = performance.get(metric, 0)
                adherence_analysis[metric] = {
                    'target': target,
                    'actual': actual,
                    'met': actual >= target if isinstance(target, (int, float)) else actual == target
                }

            review = {
                'assessment_type': 'sla_review',
                'assessment_date': datetime.now().isoformat(),
                'sla_terms': sla_terms,
                'adherence_analysis': adherence_analysis,
                'overall_compliance': all(a['met'] for a in adherence_analysis.values()),
                'breaches_count': sum(1 for a in adherence_analysis.values() if not a['met']),
                'pending_credits': self._calculate_sla_credits(adherence_analysis)
            }

            return review
        except Exception as e:
            return {
                'assessment_type': 'sla_review',
                'error': str(e),
                'status': 'failed'
            }

    def generate_vendor_scorecard(self, assessments: Dict) -> Dict:
        """
        Generate comprehensive vendor scorecard

        Args:
            assessments: Dictionary containing all assessment results

        Returns:
            Vendor scorecard with overall rating
        """
        try:
            if not assessments:
                raise ValueError("Assessments data is required")

            scorecard = {
                'scorecard_id': f"VS_{self.vendor_data.get('vendor_id', 'UNKNOWN')}_{datetime.now().strftime('%Y%m%d')}",
                'vendor_id': self.vendor_data.get('vendor_id'),
                'vendor_name': self.vendor_data.get('vendor_name'),
                'assessment_date': datetime.now().isoformat(),
                'assessments': assessments,
                'overall_score': self._calculate_overall_score(assessments),
                'recommendation': self._generate_vendor_recommendation(assessments),
                'next_assessment_date': (datetime.now() + timedelta(days=180)).isoformat(),
                'sign_off': {
                    'prepared_by': 'Compliance Team',
                    'reviewed_by': 'Vendor Manager',
                    'date': datetime.now().date().isoformat()
                }
            }

            return scorecard
        except Exception as e:
            return {
                'scorecard_id': f"VS_ERROR_{datetime.now().strftime('%Y%m%d')}",
                'error': str(e),
                'status': 'failed'
            }

    def create_improvement_action_plan(self, assessment_gaps: List[Dict]) -> Dict:
        """
        Create action plan for identified improvement areas

        Args:
            assessment_gaps: List of identified gaps

        Returns:
            Action plan with timelines and responsibilities
        """
        try:
            if not assessment_gaps or not isinstance(assessment_gaps, list):
                raise ValueError("Assessment gaps must be non-empty list")

            action_plan = {
                'plan_id': f"AP_{self.vendor_data.get('vendor_id', 'UNKNOWN')}_{datetime.now().strftime('%Y%m%d')}",
                'created_date': datetime.now().isoformat(),
                'target_completion': (datetime.now() + timedelta(days=90)).isoformat(),
                'actions': [],
                'review_checkpoints': []
            }

            for idx, gap in enumerate(assessment_gaps, 1):
                action = {
                    'action_id': f"ACT_{idx:03d}",
                    'description': gap.get('description'),
                    'priority': gap.get('priority', 'medium'),
                    'responsible_party': gap.get('owner'),
                    'target_date': (datetime.now() + timedelta(days=30 * (idx % 3 + 1))).isoformat(),
                    'status': 'pending',
                    'success_metrics': gap.get('success_metrics', [])
                }
                action_plan['actions'].append(action)

            # Add review checkpoints every 30 days
            for i in range(1, 4):
                action_plan['review_checkpoints'].append({
                    'checkpoint_id': f"CP_{i:02d}",
                    'checkpoint_date': (datetime.now() + timedelta(days=30 * i)).isoformat(),
                    'review_type': 'progress_review'
                })

            return action_plan
        except Exception as e:
            return {
                'plan_id': f"AP_ERROR_{datetime.now().strftime('%Y%m%d')}",
                'error': str(e),
                'status': 'failed'
            }

    # Private helper methods
    @staticmethod
    def _evaluate_financial_health(financial_data: Dict) -> str:
        """Evaluate overall financial health"""
        try:
            score = 0
            if financial_data.get('profit_margin', 0) > 0.15:
                score += 3
            if financial_data.get('debt_ratio', 1) < 0.5:
                score += 3
            if financial_data.get('liquidity_ratio', 0) > 1.5:
                score += 3

            if score >= 7:
                return 'Excellent'
            elif score >= 5:
                return 'Good'
            else:
                return 'Needs Improvement'
        except:
            return 'Unable to Assess'

    @staticmethod
    def _calculate_financial_risk(financial_data: Dict) -> str:
        """Calculate financial risk level"""
        try:
            debt_ratio = financial_data.get('debt_ratio', 1)
            profit_margin = financial_data.get('profit_margin', 0)

            if debt_ratio > 0.8 or profit_margin < 0.05:
                return 'High'
            elif debt_ratio > 0.5 or profit_margin < 0.10:
                return 'Medium'
            else:
                return 'Low'
        except:
            return 'Unknown'

    @staticmethod
    def _generate_financial_recommendations(financial_data: Dict) -> List[str]:
        """Generate financial recommendations"""
        recommendations = []
        try:
            if financial_data.get('debt_ratio', 0) > 0.7:
                recommendations.append('Monitor debt reduction progress')
            if financial_data.get('profit_margin', 0) < 0.10:
                recommendations.append('Track profitability improvements')
            if financial_data.get('liquidity_ratio', 0) < 1.0:
                recommendations.append('Monitor cash flow closely')
        except:
            pass
        return recommendations or ['No specific recommendations']

    @staticmethod
    def _calculate_performance_rating(metrics: Dict) -> PerformanceRating:
        """Calculate overall performance rating"""
        try:
            score = 0
            if metrics.get('on_time_delivery_rate', 0) >= 95:
                score += 1
            if metrics.get('quality_score', 0) >= 90:
                score += 1
            if metrics.get('incident_count', 999) < 5:
                score += 1
            if metrics.get('response_time_hours', 999) < 4:
                score += 1
            if metrics.get('customer_satisfaction', 0) >= 4.0:
                score += 1

            if score >= 5:
                return PerformanceRating.EXCELLENT
            elif score >= 4:
                return PerformanceRating.GOOD
            elif score >= 3:
                return PerformanceRating.ACCEPTABLE
            elif score >= 2:
                return PerformanceRating.POOR
            else:
                return PerformanceRating.UNACCEPTABLE
        except:
            return PerformanceRating.ACCEPTABLE

    @staticmethod
    def _analyze_performance_trend(performance_data: Dict) -> str:
        """Analyze performance trend direction"""
        try:
            previous = performance_data.get('previous_period', {})
            current = performance_data.get('current_period', {})

            if not previous or not current:
                return 'Insufficient data'

            improvement = sum(1 for k in current if current.get(k, 0) > previous.get(k, 0))
            decline = sum(1 for k in current if current.get(k, 0) < previous.get(k, 0))

            if improvement > decline:
                return 'Improving'
            elif decline > improvement:
                return 'Declining'
            else:
                return 'Stable'
        except:
            return 'Unknown'

    @staticmethod
    def _identify_improvement_areas(metrics: Dict) -> List[str]:
        """Identify areas needing improvement"""
        areas = []
        try:
            if metrics.get('on_time_delivery_rate', 100) < 90:
                areas.append('On-time delivery performance')
            if metrics.get('quality_score', 100) < 85:
                areas.append('Quality standards')
            if metrics.get('incident_count', 0) > 10:
                areas.append('Incident management')
            if metrics.get('customer_satisfaction', 5) < 3.5:
                areas.append('Customer satisfaction')
        except:
            pass
        return areas or ['No significant areas identified']

    @staticmethod
    def _calculate_compliance_score(compliance_data: Dict) -> int:
        """Calculate overall compliance score"""
        try:
            score = 100
            violations = compliance_data.get('violations', [])
            audit_findings = compliance_data.get('audit_findings', {})

            critical_count = len([v for v in violations if v.get('severity') == 'critical'])
            major_count = len([v for v in violations if v.get('severity') == 'major'])

            score -= (critical_count * 20)
            score -= (major_count * 10)

            return max(0, score)
        except:
            return 50

    @staticmethod
    def _assess_remediation_status(violations: List) -> str:
        """Assess remediation status of violations"""
        try:
            if not violations:
                return 'No violations'
            resolved = sum(1 for v in violations if v.get('resolved'))
            return f"{resolved}/{len(violations)} remediated"
        except:
            return 'Unable to assess'

    @staticmethod
    def _calculate_sla_credits(adherence: Dict) -> float:
        """Calculate SLA credits owed"""
        try:
            breaches = sum(1 for a in adherence.values() if not a['met'])
            return float(breaches) * 5.0
        except:
            return 0.0

    @staticmethod
    def _calculate_overall_score(assessments: Dict) -> float:
        """Calculate overall vendor score"""
        try:
            if not assessments:
                return 0.0

            scores = []
            if 'financial_stability' in assessments and 'risk_level' in assessments['financial_stability']:
                risk = assessments['financial_stability'].get('risk_level')
                score = 100 if risk == 'Low' else 60 if risk == 'Medium' else 20
                scores.append(score)

            if 'operational_performance' in assessments and 'rating_score' in assessments['operational_performance']:
                scores.append(assessments['operational_performance'].get('rating_score', 3) * 20)

            if 'compliance_posture' in assessments:
                scores.append(assessments['compliance_posture'].get('compliance_score', 50))

            return sum(scores) / len(scores) if scores else 50.0
        except:
            return 50.0

    @staticmethod
    def _generate_vendor_recommendation(assessments: Dict) -> str:
        """Generate vendor recommendation"""
        try:
            overall_score = VendorAssessmentEngine._calculate_overall_score(assessments)

            if overall_score >= 80:
                return 'Continue engagement - excellent vendor'
            elif overall_score >= 60:
                return 'Continue with monitoring - address gaps'
            else:
                return 'Review engagement - significant concerns'
        except:
            return 'Recommend further review'


def main():
    """Main execution"""
    try:
        engine = VendorAssessmentEngine()

        # Initiate assessment
        init_result = engine.initiate_vendor_assessment(
            vendor_id='VENDOR_123',
            vendor_name='Tech Solutions Inc',
            assessment_scope=['financial', 'operational', 'compliance', 'sla']
        )

        # Financial assessment
        financial = engine.assess_financial_stability({
            'revenue': 5000000,
            'profit_margin': 0.18,
            'debt_ratio': 0.35,
            'liquidity_ratio': 2.1,
            'credit_rating': 'A'
        })

        # Operational assessment
        operational = engine.evaluate_operational_performance({
            'on_time_delivery': 96.5,
            'quality_score': 92.0,
            'incident_count': 2,
            'response_time': 2,
            'satisfaction_score': 4.3
        })

        # Compliance assessment
        compliance = engine.assess_compliance_posture({
            'certifications': ['ISO 27001', 'SOC 2', 'ISO 9001'],
            'audit_findings': {'last_audit': '2024-03-15', 'findings': 0},
            'violations': []
        })

        # SLA review
        sla = engine.review_service_level_agreements({
            'sla_terms': {'availability': 99.5, 'response_time': 4},
            'performance_data': {'availability': 99.7, 'response_time': 2}
        })

        # Generate scorecard
        scorecard = engine.generate_vendor_scorecard({
            'financial_stability': financial,
            'operational_performance': operational,
            'compliance_posture': compliance,
            'sla_review': sla
        })

        # Action plan
        action_plan = engine.create_improvement_action_plan([])

        print(json.dumps({
            'assessment_id': engine.assessment_id,
            'initiation': init_result,
            'financial': financial,
            'operational': operational,
            'compliance': compliance,
            'sla': sla,
            'scorecard': scorecard,
            'action_plan': action_plan
        }, indent=2, default=str))
    except Exception as e:
        print(json.dumps({'error': str(e)}, indent=2))


if __name__ == '__main__':
    main()
