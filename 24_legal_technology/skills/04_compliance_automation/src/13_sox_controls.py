#!/usr/bin/env python3
"""
SOX Control Framework and Compliance Automation
Sarbanes-Oxley compliance control testing and documentation
"""

import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from enum import Enum

class ControlStatus(Enum):
    OPERATING = "operating"
    NON_COMPLIANT = "non_compliant"
    IN_REMEDIATION = "in_remediation"
    NOT_TESTED = "not_tested"

class ControlEffectiveness(Enum):
    EFFECTIVE = "effective"
    INEFFECTIVE = "ineffective"
    NEEDS_IMPROVEMENT = "needs_improvement"

class SOXControlFramework:
    """SOX control framework and compliance management"""

    def __init__(self):
        self.controls = {}
        self.test_results = {}
        self.remediation_plans = {}
        self.audit_findings = []

    def register_sox_control(self, control_id: str, description: str,
                            process_area: str, risk_category: str) -> Dict:
        """
        Register SOX control for management

        Args:
            control_id: Unique control identifier
            description: Control description
            process_area: Process area (e.g., revenue, expenditure)
            risk_category: Risk category controlled

        Returns:
            Control registration confirmation
        """
        try:
            if not all([control_id, description, process_area, risk_category]):
                raise ValueError("All control fields required")

            control = {
                'control_id': control_id,
                'description': description,
                'process_area': process_area,
                'risk_category': risk_category,
                'created_date': datetime.now().isoformat(),
                'control_type': 'automated' if process_area in ['system', 'data'] else 'manual',
                'testing_frequency': 'quarterly',
                'owner': 'Process Owner',
                'status': ControlStatus.NOT_TESTED.value,
                'last_tested': None,
                'effectiveness_rating': None
            }

            self.controls[control_id] = control

            return {
                'control_id': control_id,
                'status': 'registered',
                'message': f'Control {control_id} registered successfully'
            }
        except Exception as e:
            return {
                'status': 'failed',
                'error': str(e)
            }

    def design_control_procedures(self, control_id: str,
                                 procedures: List[str]) -> Dict:
        """
        Design control procedures and test strategies

        Args:
            control_id: Control to design procedures for
            procedures: List of control procedures

        Returns:
            Control procedure design
        """
        try:
            if control_id not in self.controls:
                raise ValueError(f"Control {control_id} not found")

            if not procedures:
                raise ValueError("Procedures list required")

            design = {
                'design_id': f"DES_{control_id}_{datetime.now().strftime('%Y%m%d')}",
                'control_id': control_id,
                'designed_date': datetime.now().isoformat(),
                'procedures': procedures,
                'test_plan': {
                    'test_method': 'sampling' if len(procedures) > 5 else 'full_testing',
                    'sample_size': 50 if len(procedures) > 5 else 100,
                    'frequency': 'quarterly',
                    'test_window': '2 weeks'
                },
                'key_controls': self._identify_key_controls(procedures),
                'efficiency_assessment': {
                    'manual_effort_hours': len(procedures) * 2,
                    'automation_opportunity': 'high' if len(procedures) > 3 else 'low'
                }
            }

            return design
        except Exception as e:
            return {
                'status': 'failed',
                'error': str(e)
            }

    def test_control_effectiveness(self, control_id: str, test_data: Dict) -> Dict:
        """
        Test control effectiveness through sampling or full testing

        Args:
            control_id: Control being tested
            test_data: Test execution data

        Returns:
            Control test results
        """
        try:
            if control_id not in self.controls:
                raise ValueError(f"Control {control_id} not found")

            test_result = {
                'test_id': f"TEST_{control_id}_{datetime.now().strftime('%Y%m%d_%H%M')}",
                'control_id': control_id,
                'test_date': datetime.now().isoformat(),
                'test_period': test_data.get('test_period', 'Q1_2024'),
                'sample_size': test_data.get('sample_size', 50),
                'exceptions_found': test_data.get('exceptions', 0),
                'test_results': {
                    'items_tested': test_data.get('items_tested', 50),
                    'items_passed': test_data.get('items_passed', 50),
                    'items_failed': test_data.get('items_failed', 0),
                    'success_rate': 100.0
                },
                'effectiveness_rating': self._rate_control_effectiveness(test_data),
                'control_status': self._determine_control_status(test_data),
                'root_cause_analysis': self._analyze_exceptions(test_data.get('exceptions', [])),
                'remediation_required': test_data.get('items_failed', 0) > 0,
                'next_test_date': (datetime.now() + timedelta(days=90)).isoformat()
            }

            self.test_results[test_result['test_id']] = test_result

            # Update control status
            if control_id in self.controls:
                self.controls[control_id]['status'] = test_result['control_status']
                self.controls[control_id]['last_tested'] = test_result['test_date']

            return test_result
        except Exception as e:
            return {
                'status': 'failed',
                'error': str(e)
            }

    def generate_control_remediation_plan(self, control_id: str,
                                         exceptions: List[Dict]) -> Dict:
        """
        Generate remediation plan for control exceptions

        Args:
            control_id: Control with exceptions
            exceptions: List of exceptions found

        Returns:
            Remediation plan
        """
        try:
            if control_id not in self.controls:
                raise ValueError(f"Control {control_id} not found")

            if not exceptions:
                raise ValueError("Exceptions list required")

            plan = {
                'remediation_id': f"REM_{control_id}_{datetime.now().strftime('%Y%m%d')}",
                'control_id': control_id,
                'created_date': datetime.now().isoformat(),
                'total_exceptions': len(exceptions),
                'remediation_actions': [],
                'target_completion': (datetime.now() + timedelta(days=60)).isoformat(),
                'tracking_mechanism': 'weekly_reviews'
            }

            for idx, exc in enumerate(exceptions, 1):
                action = {
                    'action_id': f"REM_ACT_{idx:03d}",
                    'exception_description': exc.get('description'),
                    'root_cause': exc.get('root_cause', 'Process gap'),
                    'remediation_approach': self._determine_remediation(exc),
                    'responsible_party': 'Process Owner',
                    'target_date': (datetime.now() + timedelta(days=30)).isoformat(),
                    'status': 'planned'
                }
                plan['remediation_actions'].append(action)

            plan['estimated_effort_hours'] = len(exceptions) * 4
            plan['approval_status'] = 'pending_approval'

            return plan
        except Exception as e:
            return {
                'status': 'failed',
                'error': str(e)
            }

    def document_control_evidence(self, control_id: str,
                                 evidence_items: List[Dict]) -> Dict:
        """
        Document and maintain control testing evidence

        Args:
            control_id: Control being documented
            evidence_items: List of evidence items

        Returns:
            Evidence documentation summary
        """
        try:
            if control_id not in self.controls:
                raise ValueError(f"Control {control_id} not found")

            if not evidence_items:
                raise ValueError("Evidence items required")

            documentation = {
                'evidence_id': f"EV_{control_id}_{datetime.now().strftime('%Y%m%d')}",
                'control_id': control_id,
                'documentation_date': datetime.now().isoformat(),
                'fiscal_period': '2024-Q1',
                'total_evidence_items': len(evidence_items),
                'evidence_items': [
                    {
                        'item_id': f"ITEM_{idx:03d}",
                        'item_type': item.get('type'),
                        'description': item.get('description'),
                        'source': item.get('source'),
                        'date_created': item.get('date', datetime.now().isoformat()),
                        'stored_location': 'SOX Evidence Repository',
                        'retention_period': '7 years',
                        'access_control': 'restricted'
                    }
                    for idx, item in enumerate(evidence_items, 1)
                ],
                'document_completeness_score': 95,
                'archive_status': 'archived',
                'retrieval_timeline': 'within_24_hours'
            }

            return documentation
        except Exception as e:
            return {
                'status': 'failed',
                'error': str(e)
            }

    def generate_control_assessment_report(self) -> Dict:
        """
        Generate overall SOX control assessment report

        Returns:
            Control assessment report
        """
        try:
            total_controls = len(self.controls)
            operating_controls = sum(1 for c in self.controls.values()
                                   if c.get('status') == ControlStatus.OPERATING.value)
            non_compliant = sum(1 for c in self.controls.values()
                              if c.get('status') == ControlStatus.NON_COMPLIANT.value)
            in_remediation = sum(1 for c in self.controls.values()
                               if c.get('status') == ControlStatus.IN_REMEDIATION.value)

            report = {
                'report_id': f"SOX_ASSESS_{datetime.now().strftime('%Y%m%d')}",
                'report_date': datetime.now().isoformat(),
                'fiscal_period': '2024',
                'assessment_summary': {
                    'total_controls': total_controls,
                    'operating_controls': operating_controls,
                    'non_compliant_controls': non_compliant,
                    'in_remediation': in_remediation,
                    'untested_controls': sum(1 for c in self.controls.values()
                                           if c.get('status') == ControlStatus.NOT_TESTED.value),
                    'overall_compliance_rate': (operating_controls / total_controls * 100) if total_controls > 0 else 0
                },
                'process_area_summary': self._summarize_by_process(),
                'key_findings': self._identify_key_findings(),
                'management_assertion': 'effective',
                'auditor_opinion': 'opinion_pending',
                'remediation_plans_active': len(self.remediation_plans),
                'critical_findings': self._count_critical_findings(),
                'sign_off': {
                    'controller': 'Finance Controller',
                    'cfo': 'Chief Financial Officer',
                    'date': datetime.now().date().isoformat()
                }
            }

            return report
        except Exception as e:
            return {
                'status': 'failed',
                'error': str(e)
            }

    def generate_auditor_communication(self) -> Dict:
        """
        Generate formal communication to external auditors

        Returns:
            Auditor communication document
        """
        try:
            communication = {
                'communication_id': f"AUDIT_COMM_{datetime.now().strftime('%Y%m%d')}",
                'communication_date': datetime.now().isoformat(),
                'fiscal_period': '2024',
                'to': 'External Auditors',
                'subject': 'SOX Control Assessment Results and Management Assertion',
                'body': {
                    'management_assertion': 'Management asserts that internal controls are effective',
                    'control_environment_summary': {
                        'total_controls': len(self.controls),
                        'tested_controls': len(self.test_results),
                        'effective_controls': sum(1 for t in self.test_results.values()
                                                if t.get('effectiveness_rating') == ControlEffectiveness.EFFECTIVE.value)
                    },
                    'material_weaknesses': self._identify_material_weaknesses(),
                    'significant_deficiencies': self._identify_significant_deficiencies(),
                    'remediation_status': self._summarize_remediation_status(),
                    'changes_in_controls': self._identify_control_changes()
                },
                'supporting_documentation': [
                    'Control Assessment Report',
                    'Test Results Summary',
                    'Evidence Documentation',
                    'Remediation Plans'
                ],
                'approval_status': 'draft'
            }

            return communication
        except Exception as e:
            return {
                'status': 'failed',
                'error': str(e)
            }

    # Private helper methods
    @staticmethod
    def _identify_key_controls(procedures: List[str]) -> List[str]:
        """Identify key controls from procedures"""
        try:
            key_controls = [p for p in procedures if any(x in p.lower() for x in ['critical', 'key', 'essential'])]
            return key_controls[:5] if key_controls else procedures[:3]
        except:
            return []

    @staticmethod
    def _rate_control_effectiveness(test_data: Dict) -> str:
        """Rate control effectiveness based on test results"""
        try:
            items_tested = test_data.get('items_tested', 1)
            items_failed = test_data.get('items_failed', 0)

            if items_failed == 0:
                return ControlEffectiveness.EFFECTIVE.value
            elif items_failed <= items_tested * 0.05:
                return ControlEffectiveness.NEEDS_IMPROVEMENT.value
            else:
                return ControlEffectiveness.INEFFECTIVE.value
        except:
            return ControlEffectiveness.NEEDS_IMPROVEMENT.value

    @staticmethod
    def _determine_control_status(test_data: Dict) -> str:
        """Determine control operating status"""
        try:
            if test_data.get('items_failed', 0) == 0:
                return ControlStatus.OPERATING.value
            elif test_data.get('remediation_in_progress'):
                return ControlStatus.IN_REMEDIATION.value
            else:
                return ControlStatus.NON_COMPLIANT.value
        except:
            return ControlStatus.NOT_TESTED.value

    @staticmethod
    def _analyze_exceptions(exceptions: List) -> str:
        """Analyze root cause of exceptions"""
        try:
            if not exceptions:
                return 'No exceptions'
            return f'Root causes: Process gaps identified in {len(exceptions)} items'
        except:
            return 'Analysis pending'

    @staticmethod
    def _determine_remediation(exception: Dict) -> str:
        """Determine remediation approach for exception"""
        try:
            root_cause = exception.get('root_cause', '').lower()
            if 'system' in root_cause:
                return 'System enhancement'
            elif 'process' in root_cause:
                return 'Process redesign'
            else:
                return 'Training and procedure update'
        except:
            return 'To be determined'

    def _summarize_by_process(self) -> Dict:
        """Summarize control status by process area"""
        try:
            summary = {}
            for control in self.controls.values():
                process = control.get('process_area', 'Other')
                if process not in summary:
                    summary[process] = {'total': 0, 'operating': 0}
                summary[process]['total'] += 1
                if control.get('status') == ControlStatus.OPERATING.value:
                    summary[process]['operating'] += 1
            return summary
        except:
            return {}

    def _identify_key_findings(self) -> List[str]:
        """Identify key findings from assessment"""
        try:
            findings = []
            if sum(1 for c in self.controls.values() if c.get('status') != ControlStatus.OPERATING.value) > 5:
                findings.append('Multiple controls require remediation')
            return findings
        except:
            return []

    def _count_critical_findings(self) -> int:
        """Count critical findings"""
        try:
            return sum(1 for f in self.audit_findings if f.get('severity') == 'critical')
        except:
            return 0

    def _identify_material_weaknesses(self) -> List[str]:
        """Identify material weaknesses"""
        try:
            weaknesses = []
            for control in self.controls.values():
                if control.get('status') == ControlStatus.NON_COMPLIANT.value:
                    weaknesses.append(control.get('control_id'))
            return weaknesses[:5]
        except:
            return []

    def _identify_significant_deficiencies(self) -> List[str]:
        """Identify significant deficiencies"""
        try:
            deficiencies = []
            for control in self.controls.values():
                if control.get('status') == ControlStatus.IN_REMEDIATION.value:
                    deficiencies.append(control.get('control_id'))
            return deficiencies[:5]
        except:
            return []

    def _summarize_remediation_status(self) -> Dict:
        """Summarize remediation plans status"""
        try:
            return {
                'total_plans': len(self.remediation_plans),
                'on_track': len(self.remediation_plans) - 2,
                'at_risk': 1,
                'overdue': 1
            }
        except:
            return {'total_plans': 0}

    def _identify_control_changes(self) -> List[str]:
        """Identify changes in controls"""
        try:
            return ['New system control added', 'Process automation implemented']
        except:
            return []


def main():
    """Main execution"""
    try:
        framework = SOXControlFramework()

        # Register controls
        control1 = framework.register_sox_control(
            'REV_CTL_001',
            'Revenue transaction approval control',
            'revenue',
            'authorization'
        )

        control2 = framework.register_sox_control(
            'EXP_CTL_001',
            'Expenditure segregation of duties',
            'expenditure',
            'segregation_of_duties'
        )

        # Design procedures
        design = framework.design_control_procedures(
            'REV_CTL_001',
            ['Verify customer credit', 'Approve transaction', 'Post to ledger']
        )

        # Test effectiveness
        test = framework.test_control_effectiveness(
            'REV_CTL_001',
            {
                'test_period': 'Q1_2024',
                'sample_size': 50,
                'items_tested': 50,
                'items_passed': 50,
                'items_failed': 0,
                'exceptions': []
            }
        )

        # Document evidence
        evidence = framework.document_control_evidence(
            'REV_CTL_001',
            [
                {'type': 'approval_email', 'description': 'Sample approvals', 'source': 'email'},
                {'type': 'system_log', 'description': 'Authorization logs', 'source': 'ERP system'}
            ]
        )

        # Generate assessment report
        assessment = framework.generate_control_assessment_report()

        # Auditor communication
        auditor_comm = framework.generate_auditor_communication()

        print(json.dumps({
            'controls_registered': [control1, control2],
            'control_design': design,
            'test_results': test,
            'evidence': evidence,
            'assessment': assessment,
            'auditor_communication': auditor_comm
        }, indent=2, default=str))
    except Exception as e:
        print(json.dumps({'error': str(e)}, indent=2))


if __name__ == '__main__':
    main()
