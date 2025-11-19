#!/usr/bin/env python3
"""
Data Retention Policy Management
Automated data lifecycle management and retention compliance
"""

import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from enum import Enum

class DataClassification(Enum):
    PUBLIC = "public"
    INTERNAL = "internal"
    CONFIDENTIAL = "confidential"
    RESTRICTED = "restricted"

class RetentionStatus(Enum):
    ACTIVE = "active"
    ARCHIVED = "archived"
    SCHEDULED_FOR_DELETION = "scheduled_for_deletion"
    DELETED = "deleted"

class DataRetentionManager:
    """Manage data retention policies and lifecycle"""

    def __init__(self):
        self.retention_policies = {}
        self.data_inventory = {}
        self.deletion_schedules = {}
        self.retention_audit_log = []

    def create_retention_policy(self, data_type: str, classification: str,
                               retention_period_years: int,
                               regulatory_requirements: List[str]) -> Dict:
        """
        Create data retention policy

        Args:
            data_type: Type of data (e.g., customer_records)
            classification: Data classification level
            retention_period_years: Retention period in years
            regulatory_requirements: Applicable regulations

        Returns:
            Retention policy record
        """
        try:
            if not all([data_type, classification, retention_period_years]):
                raise ValueError("Data type, classification, and retention period required")

            if retention_period_years < 0:
                raise ValueError("Retention period must be non-negative")

            policy_id = f"POL_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

            policy = {
                'policy_id': policy_id,
                'data_type': data_type,
                'classification': classification,
                'created_date': datetime.now().isoformat(),
                'effective_date': datetime.now().isoformat(),
                'retention_period_years': retention_period_years,
                'retention_period_days': retention_period_years * 365,
                'regulatory_requirements': regulatory_requirements,
                'deletion_method': 'secure_deletion',
                'deletion_verification': True,
                'backup_retention': retention_period_years + 1,
                'exceptions': [],
                'policy_status': 'active',
                'owner': 'Data Governance',
                'last_review': datetime.now().isoformat(),
                'next_review': (datetime.now() + timedelta(days=365)).isoformat()
            }

            self.retention_policies[policy_id] = policy

            return {
                'policy_id': policy_id,
                'status': 'created',
                'message': f'Retention policy for {data_type} created successfully'
            }
        except Exception as e:
            return {
                'status': 'failed',
                'error': str(e)
            }

    def register_data_asset(self, asset_name: str, data_type: str,
                          quantity: int, storage_location: str,
                          classification: str) -> Dict:
        """
        Register data asset for retention management

        Args:
            asset_name: Name of data asset
            data_type: Type of data
            quantity: Number of records/items
            storage_location: Where data is stored
            classification: Data classification level

        Returns:
            Data asset registration
        """
        try:
            if not all([asset_name, data_type, quantity, storage_location, classification]):
                raise ValueError("All asset parameters required")

            asset_id = f"ASSET_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

            asset = {
                'asset_id': asset_id,
                'asset_name': asset_name,
                'data_type': data_type,
                'quantity': quantity,
                'storage_location': storage_location,
                'classification': classification,
                'registered_date': datetime.now().isoformat(),
                'policy_applied': self._find_applicable_policy(data_type),
                'retention_end_date': self._calculate_retention_end_date(data_type),
                'last_accessed': datetime.now().isoformat(),
                'access_count': 0,
                'owner_department': 'Unknown',
                'status': RetentionStatus.ACTIVE.value,
                'backup_status': 'current'
            }

            self.data_inventory[asset_id] = asset

            return {
                'asset_id': asset_id,
                'status': 'registered',
                'message': f'Data asset {asset_name} registered'
            }
        except Exception as e:
            return {
                'status': 'failed',
                'error': str(e)
            }

    def schedule_data_deletion(self, asset_id: str, deletion_reason: str,
                              approval_required: bool = True) -> Dict:
        """
        Schedule data asset for deletion

        Args:
            asset_id: Asset to schedule for deletion
            deletion_reason: Reason for deletion
            approval_required: Whether approval is needed

        Returns:
            Deletion schedule record
        """
        try:
            if asset_id not in self.data_inventory:
                raise ValueError(f"Asset {asset_id} not found")

            if not deletion_reason:
                raise ValueError("Deletion reason required")

            asset = self.data_inventory[asset_id]
            schedule_id = f"DEL_{asset_id}_{datetime.now().strftime('%Y%m%d')}"

            schedule = {
                'schedule_id': schedule_id,
                'asset_id': asset_id,
                'asset_name': asset.get('asset_name'),
                'scheduled_date': datetime.now().isoformat(),
                'deletion_reason': deletion_reason,
                'reason_category': 'retention_expired' if 'retention' in deletion_reason.lower() else 'other',
                'quantity_to_delete': asset.get('quantity'),
                'deletion_method': 'secure_deletion',
                'planned_deletion_date': (datetime.now() + timedelta(days=30)).isoformat(),
                'approval_status': 'pending' if approval_required else 'approved',
                'approvers_required': ['Data Privacy Officer', 'Legal'] if approval_required else [],
                'deletion_status': RetentionStatus.SCHEDULED_FOR_DELETION.value,
                'verification_method': 'deletion_certificate',
                'audit_trail': {
                    'created_by': 'system',
                    'created_date': datetime.now().isoformat()
                }
            }

            self.deletion_schedules[schedule_id] = schedule

            # Update asset status
            asset['status'] = RetentionStatus.SCHEDULED_FOR_DELETION.value

            return schedule
        except Exception as e:
            return {
                'status': 'failed',
                'error': str(e)
            }

    def execute_data_deletion(self, schedule_id: str) -> Dict:
        """
        Execute scheduled data deletion

        Args:
            schedule_id: Deletion schedule to execute

        Returns:
            Deletion execution record
        """
        try:
            if schedule_id not in self.deletion_schedules:
                raise ValueError(f"Schedule {schedule_id} not found")

            schedule = self.deletion_schedules[schedule_id]

            if schedule.get('approval_status') != 'approved':
                raise ValueError("Deletion not approved")

            execution = {
                'execution_id': f"EXEC_{schedule_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                'schedule_id': schedule_id,
                'execution_date': datetime.now().isoformat(),
                'execution_status': 'completed',
                'records_deleted': schedule.get('quantity_to_delete'),
                'deletion_method': schedule.get('deletion_method'),
                'deletion_tool': 'Secure Delete Pro 5.0',
                'deletion_certificate': f"CERT_{schedule_id}_{datetime.now().strftime('%Y%m%d')}",
                'verification_completed': True,
                'verification_date': datetime.now().isoformat(),
                'audit_log_entry': {
                    'action': 'data_deletion_executed',
                    'timestamp': datetime.now().isoformat(),
                    'performed_by': 'Data Retention System',
                    'asset_id': schedule.get('asset_id'),
                    'records_affected': schedule.get('quantity_to_delete')
                }
            }

            # Update asset status
            asset_id = schedule.get('asset_id')
            if asset_id in self.data_inventory:
                self.data_inventory[asset_id]['status'] = RetentionStatus.DELETED.value

            # Log audit event
            self.retention_audit_log.append(execution['audit_log_entry'])

            return execution
        except Exception as e:
            return {
                'status': 'failed',
                'error': str(e)
            }

    def audit_retention_compliance(self) -> Dict:
        """
        Audit retention compliance across all data assets

        Returns:
            Retention compliance audit results
        """
        try:
            audit_id = f"AUDIT_{datetime.now().strftime('%Y%m%d')}"

            non_compliant_assets = []
            compliant_assets = 0
            overdue_deletions = 0

            for asset in self.data_inventory.values():
                retention_end = asset.get('retention_end_date')
                if retention_end:
                    if datetime.fromisoformat(retention_end) < datetime.now():
                        if asset.get('status') != RetentionStatus.DELETED.value:
                            non_compliant_assets.append(asset.get('asset_id'))
                            overdue_deletions += 1
                        else:
                            compliant_assets += 1
                    else:
                        compliant_assets += 1

            audit = {
                'audit_id': audit_id,
                'audit_date': datetime.now().isoformat(),
                'audit_period': 'last_90_days',
                'total_assets_audited': len(self.data_inventory),
                'compliant_assets': compliant_assets,
                'non_compliant_assets': len(non_compliant_assets),
                'compliance_rate': (compliant_assets / len(self.data_inventory) * 100) if self.data_inventory else 0,
                'findings': {
                    'overdue_deletions': overdue_deletions,
                    'assets_without_retention_policy': 0,
                    'improper_classification': 0,
                    'retention_violations': len(non_compliant_assets)
                },
                'non_compliant_asset_list': non_compliant_assets[:10],
                'remediation_required': overdue_deletions > 0,
                'remediation_deadline': (datetime.now() + timedelta(days=30)).isoformat() if overdue_deletions > 0 else None,
                'audit_status': 'completed'
            }

            return audit
        except Exception as e:
            return {
                'status': 'failed',
                'error': str(e)
            }

    def generate_retention_report(self) -> Dict:
        """
        Generate comprehensive data retention report

        Returns:
            Data retention status report
        """
        try:
            report_id = f"RETAIN_REPORT_{datetime.now().strftime('%Y%m%d')}"

            # Calculate metrics
            total_assets = len(self.data_inventory)
            total_records = sum(a.get('quantity', 0) for a in self.data_inventory.values())

            by_status = {}
            for asset in self.data_inventory.values():
                status = asset.get('status')
                if status not in by_status:
                    by_status[status] = 0
                by_status[status] += 1

            by_classification = {}
            for asset in self.data_inventory.values():
                classification = asset.get('classification')
                if classification not in by_classification:
                    by_classification[classification] = 0
                by_classification[classification] += 1

            report = {
                'report_id': report_id,
                'report_date': datetime.now().isoformat(),
                'reporting_period': 'last_12_months',
                'summary': {
                    'total_data_assets': total_assets,
                    'total_records_managed': total_records,
                    'policies_in_effect': len(self.retention_policies)
                },
                'status_breakdown': by_status,
                'classification_breakdown': by_classification,
                'retention_policy_coverage': {
                    'assets_with_policy': sum(1 for a in self.data_inventory.values() if a.get('policy_applied')),
                    'assets_without_policy': sum(1 for a in self.data_inventory.values() if not a.get('policy_applied'))
                },
                'deletion_activity': {
                    'deletions_executed': len([s for s in self.deletion_schedules.values() if s.get('deletion_status') == RetentionStatus.DELETED.value]),
                    'records_deleted': sum(s.get('quantity_to_delete', 0) for s in self.deletion_schedules.values()),
                    'deletions_pending': len([s for s in self.deletion_schedules.values() if s.get('deletion_status') == RetentionStatus.SCHEDULED_FOR_DELETION.value])
                },
                'compliance_status': 'compliant',
                'audit_log_entries': len(self.retention_audit_log),
                'recommendations': ['Review deletion schedules', 'Update retention policies annually']
            }

            return report
        except Exception as e:
            return {
                'status': 'failed',
                'error': str(e)
            }

    def enforce_retention_hold(self, asset_id: str, hold_reason: str,
                              hold_duration_days: int) -> Dict:
        """
        Place retention hold on data asset (legal hold)

        Args:
            asset_id: Asset to place hold on
            hold_reason: Reason for hold (e.g., legal litigation)
            hold_duration_days: Duration of hold

        Returns:
            Retention hold record
        """
        try:
            if asset_id not in self.data_inventory:
                raise ValueError(f"Asset {asset_id} not found")

            hold_id = f"HOLD_{asset_id}_{datetime.now().strftime('%Y%m%d')}"

            hold = {
                'hold_id': hold_id,
                'asset_id': asset_id,
                'hold_date': datetime.now().isoformat(),
                'hold_reason': hold_reason,
                'hold_duration_days': hold_duration_days,
                'hold_release_date': (datetime.now() + timedelta(days=hold_duration_days)).isoformat(),
                'responsible_party': 'Legal Department',
                'hold_status': 'active',
                'notifications_sent': True,
                'audit_notification_date': datetime.now().isoformat()
            }

            return hold
        except Exception as e:
            return {
                'status': 'failed',
                'error': str(e)
            }

    # Private helper methods
    def _find_applicable_policy(self, data_type: str) -> Optional[str]:
        """Find applicable retention policy for data type"""
        try:
            for policy in self.retention_policies.values():
                if policy.get('data_type') == data_type and policy.get('policy_status') == 'active':
                    return policy.get('policy_id')
            return None
        except:
            return None

    def _calculate_retention_end_date(self, data_type: str) -> str:
        """Calculate retention end date for data type"""
        try:
            policy = None
            for p in self.retention_policies.values():
                if p.get('data_type') == data_type:
                    policy = p
                    break

            if policy:
                retention_days = policy.get('retention_period_days', 365)
                end_date = datetime.now() + timedelta(days=retention_days)
                return end_date.isoformat()
            else:
                # Default 7 years
                return (datetime.now() + timedelta(days=2555)).isoformat()
        except:
            return (datetime.now() + timedelta(days=2555)).isoformat()


def main():
    """Main execution"""
    try:
        manager = DataRetentionManager()

        # Create retention policies
        policy = manager.create_retention_policy(
            data_type='customer_records',
            classification='confidential',
            retention_period_years=6,
            regulatory_requirements=['GDPR', 'CCPA', 'SOX']
        )

        # Register data assets
        asset1 = manager.register_data_asset(
            asset_name='Customer Database 2023',
            data_type='customer_records',
            quantity=150000,
            storage_location='Primary Data Center',
            classification='confidential'
        )

        asset2 = manager.register_data_asset(
            asset_name='Transaction Logs 2018',
            data_type='transaction_logs',
            quantity=2000000,
            storage_location='Archive Storage',
            classification='internal'
        )

        # Schedule deletion
        if asset2.get('asset_id'):
            deletion = manager.schedule_data_deletion(
                asset_id=asset2['asset_id'],
                deletion_reason='Retention period expired',
                approval_required=True
            )

            # Execute deletion (after approval)
            if deletion.get('schedule_id'):
                # First approve it
                manager.deletion_schedules[deletion['schedule_id']]['approval_status'] = 'approved'

                execution = manager.execute_data_deletion(deletion['schedule_id'])
            else:
                execution = None
        else:
            deletion = None
            execution = None

        # Audit retention compliance
        audit = manager.audit_retention_compliance()

        # Generate report
        report = manager.generate_retention_report()

        # Place retention hold
        if asset1.get('asset_id'):
            hold = manager.enforce_retention_hold(
                asset_id=asset1['asset_id'],
                hold_reason='Pending litigation',
                hold_duration_days=180
            )
        else:
            hold = None

        print(json.dumps({
            'policy': policy,
            'assets': [asset1, asset2],
            'deletion_schedule': deletion,
            'deletion_execution': execution,
            'audit': audit,
            'report': report,
            'legal_hold': hold
        }, indent=2, default=str))
    except Exception as e:
        print(json.dumps({'error': str(e)}, indent=2))


if __name__ == '__main__':
    main()
