#!/usr/bin/env python3
"""
Compliance Training Tracker
Automated tracking and management of mandatory compliance training
"""

import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional

class ComplianceTrainingTracker:
    """Track mandatory compliance training completion and effectiveness"""

    def __init__(self, organization_name: str):
        self.organization_name = organization_name
        self.training_programs = {}
        self.employee_records = {}
        self.training_schedule = []

    def create_training_program(self, program_name: str, program_type: str,
                               mandatory: bool, frequency: str, duration_minutes: int,
                               target_audience: List[str]) -> str:
        """Create a new compliance training program"""
        program_id = f"PROG_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        program = {
            'program_id': program_id,
            'name': program_name,
            'type': program_type,  # gdpr, data_protection, privacy, anti_corruption, etc.
            'mandatory': mandatory,
            'frequency': frequency,  # annual, biennial, upon_hire, etc.
            'duration_minutes': duration_minutes,
            'target_audience': target_audience,
            'created_date': datetime.now().isoformat(),
            'content_modules': [],
            'assessment': None,
            'certification': False,
            'completion_requirement': 100,  # % for mandatory, 80 for optional
            'training_platform': 'LMS',
            'status': 'active'
        }

        self.training_programs[program_id] = program
        return program_id

    def add_training_module(self, program_id: str, module_name: str,
                          topics: List[str], duration_minutes: int) -> None:
        """Add module to training program"""
        if program_id not in self.training_programs:
            raise ValueError(f"Program {program_id} not found")

        module = {
            'module_id': f"MOD_{len(self.training_programs[program_id]['content_modules']) + 1}",\n            'name': module_name,
            'topics': topics,
            'duration_minutes': duration_minutes,
            'module_order': len(self.training_programs[program_id]['content_modules']) + 1
        }

        self.training_programs[program_id]['content_modules'].append(module)

    def enroll_employee(self, employee_id: str, employee_name: str,
                       department: str, job_title: str, training_requirements: List[str]) -> str:
        """Enroll employee in required training programs"""
        enrollment = {
            'employee_id': employee_id,
            'name': employee_name,
            'department': department,
            'job_title': job_title,
            'enrollment_date': datetime.now().isoformat(),
            'training_requirements': training_requirements,
            'completion_status': {}
        }

        # Initialize completion status for each required training
        for req in training_requirements:
            enrollment['completion_status'][req] = {
                'status': 'not_started',
                'enrollment_date': datetime.now().isoformat(),
                'due_date': (datetime.now() + timedelta(days=60)).isoformat(),
                'completion_date': None,
                'score': None,
                'passed': False,
                'certificate': None
            }

        self.employee_records[employee_id] = enrollment
        return employee_id

    def record_training_completion(self, employee_id: str, program_id: str,
                                  score: int, completion_time_minutes: int) -> Dict:
        """Record employee training completion"""
        if employee_id not in self.employee_records:
            raise ValueError(f"Employee {employee_id} not found")

        employee = self.employee_records[employee_id]
        program = self.training_programs.get(program_id)

        completion_record = {
            'completion_id': f"COMP_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            'employee_id': employee_id,
            'program_id': program_id,
            'completion_date': datetime.now().isoformat(),
            'score': score,
            'passed': score >= (program['completion_requirement'] if program else 80),
            'time_taken_minutes': completion_time_minutes,
            'assessment_type': 'quiz',
            'certificate_issued': score >= (program['completion_requirement'] if program else 80),
            'next_renewal_date': (datetime.now() + self._get_renewal_timedelta(program['frequency'] if program else 'annual')).isoformat()
        }

        # Update employee record
        if program_id in employee['completion_status']:
            employee['completion_status'][program_id].update({
                'status': 'completed',
                'completion_date': completion_record['completion_date'],
                'score': score,
                'passed': completion_record['passed'],
                'certificate': completion_record['certificate_issued']
            })

        return completion_record

    def generate_compliance_training_report(self) -> Dict:
        """Generate organization-wide training compliance report"""
        total_employees = len(self.employee_records)
        if total_employees == 0:
            return {'error': 'No employees enrolled'}

        training_status_summary = {}
        completion_rates = {}
        overdue_training = []

        for emp_id, employee in self.employee_records.items():
            for training_id, status in employee['completion_status'].items():
                if training_id not in training_status_summary:
                    training_status_summary[training_id] = {
                        'completed': 0,
                        'pending': 0,
                        'overdue': 0,
                        'failed': 0
                    }

                if status['status'] == 'completed' and status['passed']:
                    training_status_summary[training_id]['completed'] += 1
                elif status['status'] == 'completed' and not status['passed']:
                    training_status_summary[training_id]['failed'] += 1
                else:
                    # Check if overdue
                    due_date = datetime.fromisoformat(status['due_date'])
                    if due_date < datetime.now():
                        training_status_summary[training_id]['overdue'] += 1
                        overdue_training.append({
                            'employee_id': emp_id,
                            'employee_name': employee['name'],
                            'training': training_id,
                            'days_overdue': (datetime.now() - due_date).days
                        })
                    else:
                        training_status_summary[training_id]['pending'] += 1

        # Calculate completion rates
        for training_id, summary in training_status_summary.items():
            total = summary['completed'] + summary['pending'] + summary['overdue'] + summary['failed']
            completion_rates[training_id] = (summary['completed'] / total * 100) if total > 0 else 0

        return {
            'report_date': datetime.now().isoformat(),
            'organization': self.organization_name,
            'total_employees': total_employees,
            'training_programs': len(self.training_programs),
            'compliance_metrics': {
                'average_completion_rate': sum(completion_rates.values()) / len(completion_rates) if completion_rates else 0,
                'training_status_summary': training_status_summary,
                'completion_rates': completion_rates
            },
            'overdue_training': overdue_training,
            'overdue_count': len(overdue_training),
            'recommendations': self._get_training_recommendations(overdue_training),
            'next_renewal_schedule': self._get_renewal_schedule()
        }

    def identify_training_gaps(self, department: Optional[str] = None) -> Dict:
        \"\"\"Identify training gaps by department or organization-wide\"\"\"\n        gaps = {\n            'identified_date': datetime.now().isoformat(),\n            'gaps_by_training': {},\n            'gaps_by_employee': {}\n        }\n\n        for emp_id, employee in self.employee_records.items():\n            if department and employee['department'] != department:\n                continue\n\n            employee_gaps = []\n            for training_id, status in employee['completion_status'].items():\n                if status['status'] != 'completed' or not status['passed']:\n                    employee_gaps.append({\n                        'training_id': training_id,\n                        'due_date': status['due_date'],\n                        'days_until_due': (datetime.fromisoformat(status['due_date']) - datetime.now()).days\n                    })\n\n            if employee_gaps:\n                gaps['gaps_by_employee'][emp_id] = {\n                    'employee_name': employee['name'],\n                    'department': employee['department'],\n                    'gaps': employee_gaps\n                }\n\n        return gaps\n\n    def generate_training_schedule(self, training_period: str = 'quarterly') -> Dict:\n        \"\"\"Generate training schedule for upcoming period\"\"\"\n        schedule_id = f\"SCHED_{datetime.now().strftime('%Y%m%d')}\"\n\n        return {\n            'schedule_id': schedule_id,\n            'schedule_period': training_period,\n            'generated_date': datetime.now().isoformat(),\n            'scheduled_trainings': [\n                {\n                    'program_id': prog_id,\n                    'program_name': prog['name'],\n                    'target_audience': prog['target_audience'],\n                    'start_date': (datetime.now() + timedelta(days=7)).isoformat(),\n                    'deadline': (datetime.now() + timedelta(days=60)).isoformat(),\n                    'expected_participants': len([e for e in self.employee_records.values() if prog_id in e['training_requirements']]),\n                    'training_format': 'online',\n                    'duration_hours': prog['duration_minutes'] / 60\n                }\n                for prog_id, prog in self.training_programs.items()\n            ]\n        }\n\n    def generate_training_certificate(self, employee_id: str, program_id: str, score: int) -> Dict:\n        \"\"\"Generate training completion certificate\"\"\"\n        if employee_id not in self.employee_records:\n            raise ValueError(f\"Employee {employee_id} not found\")\n\n        employee = self.employee_records[employee_id]\n        program = self.training_programs.get(program_id)\n\n        return {\n            'certificate_id': f\"CERT_{employee_id}_{program_id}_{datetime.now().strftime('%Y%m%d')}\",\n            'employee_name': employee['name'],\n            'employee_id': employee_id,\n            'program_name': program['name'] if program else 'Unknown',\n            'program_id': program_id,\n            'completion_date': datetime.now().date().isoformat(),\n            'score': score,\n            'valid_until': (datetime.now() + timedelta(days=365)).date().isoformat(),\n            'issued_by': self.organization_name,\n            'certificate_number': f\"CERT_{datetime.now().timestamp()}\",\n            'digital_signature': 'SIGNED',\n            'can_be_printed': True\n        }\n\n    # Private helper methods\n    @staticmethod\n    def _get_renewal_timedelta(frequency: str) -> timedelta:\n        \"\"\"Get renewal period based on frequency\"\"\"\n        renewal_periods = {\n            'annual': timedelta(days=365),\n            'biennial': timedelta(days=730),\n            'upon_hire': timedelta(days=999999),  # No renewal\n            'quarterly': timedelta(days=90),\n            'semi_annual': timedelta(days=180)\n        }\n        return renewal_periods.get(frequency, timedelta(days=365))\n\n    @staticmethod\n    def _get_training_recommendations(overdue_training: List[Dict]) -> List[str]:\n        \"\"\"Get recommendations based on training compliance\"\"\"\n        recommendations = []\n        if len(overdue_training) > 20:\n            recommendations.append('High volume of overdue training - implement reminder campaign')\n        if len(overdue_training) > 0:\n            recommendations.append('Issue compliance notices to overdue employees')\n        recommendations.append('Schedule makeup training sessions for failed participants')\n        return recommendations\n\n    def _get_renewal_schedule(self) -> List[Dict]:\n        \"\"\"Get upcoming renewal schedule\"\"\"\n        return [\n            {\n                'training_name': prog['name'],\n                'current_renewals_due': sum(1 for emp in self.employee_records.values()\n                                          if emp['completion_status'].get(prog_id, {}).get('status') == 'completed' and\n                                          datetime.fromisoformat(emp['completion_status'].get(prog_id, {}).get('next_renewal_date', datetime.now().isoformat())) <= datetime.now() + timedelta(days=30))\n            }\n            for prog_id, prog in self.training_programs.items()\n        ]\n\n\ndef main():\n    tracker = ComplianceTrainingTracker('TechCorp Inc')\n\n    # Create training programs\n    gdpr_prog = tracker.create_training_program(\n        'GDPR Fundamentals',\n        'data_protection',\n        mandatory=True,\n        frequency='annual',\n        duration_minutes=60,\n        target_audience=['all_employees']\n    )\n\n    # Add modules\n    tracker.add_training_module(gdpr_prog, 'GDPR Overview', ['principles', 'rights'], 20)\n    tracker.add_training_module(gdpr_prog, 'Data Protection in Practice', ['implementation', 'best_practices'], 40)\n\n    # Enroll employees\n    emp1 = tracker.enroll_employee('EMP001', 'John Smith', 'IT', 'Developer', [gdpr_prog])\n    emp2 = tracker.enroll_employee('EMP002', 'Jane Doe', 'HR', 'Manager', [gdpr_prog])\n\n    # Record completion\n    completion = tracker.record_training_completion(emp1, gdpr_prog, 95, 58)\n    cert = tracker.generate_training_certificate(emp1, gdpr_prog, 95)\n\n    # Generate report\n    report = tracker.generate_compliance_training_report()\n    schedule = tracker.generate_training_schedule()\n\n    print(json.dumps({\n        'completion_record': completion,\n        'certificate': cert,\n        'compliance_report': report,\n        'training_schedule': schedule\n    }, indent=2, default=str))\n\n\nif __name__ == '__main__':\n    main()\n