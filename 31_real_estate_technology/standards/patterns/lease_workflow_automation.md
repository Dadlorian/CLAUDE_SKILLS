# Lease Workflow Automation Pattern

**Version:** 2.0
**Last Updated:** 2025-01-15
**Status:** Active Standard
**References:** AWS Step Functions, Temporal.io, Camunda, Yardi Voyager Workflows

## Table of Contents

1. [Overview](#overview)
2. [State Machine Design](#state-machine-design)
3. [Automated Rent Posting](#automated-rent-posting)
4. [Lease Renewal Workflows](#lease-renewal-workflows)
5. [Move-In/Move-Out Automation](#move-in-move-out-automation)
6. [Event-Driven Patterns](#event-driven-patterns)
7. [Integration with Accounting](#integration-with-accounting)
8. [Approval Chains](#approval-chains)

## Overview

Lease lifecycle automation reduces manual intervention, ensures consistency, and improves operational efficiency through workflow orchestration.

### Lease Lifecycle Stages

```
Application → Screening → Approval → Lease Signing → Move-In → 
Active Tenancy → Rent Collection → Renewal Decision → 
Move-Out → Final Accounting → Archive
```

## State Machine Design

### Lease State Transitions

```python
from enum import Enum
from datetime import datetime, timedelta

class LeaseStatus(Enum):
    DRAFT = "draft"
    PENDING_SIGNATURES = "pending_signatures"
    ACTIVE = "active"
    EXPIRING_SOON = "expiring_soon"
    PENDING_RENEWAL = "pending_renewal"
    RENEWED = "renewed"
    NOTICE_GIVEN = "notice_given"
    EXPIRED = "expired"
    TERMINATED = "terminated"

class LeaseStateMachine:
    """
    Lease state machine with transition rules
    """

    ALLOWED_TRANSITIONS = {
        LeaseStatus.DRAFT: [LeaseStatus.PENDING_SIGNATURES],
        LeaseStatus.PENDING_SIGNATURES: [LeaseStatus.ACTIVE, LeaseStatus.DRAFT],
        LeaseStatus.ACTIVE: [
            LeaseStatus.EXPIRING_SOON,
            LeaseStatus.NOTICE_GIVEN,
            LeaseStatus.TERMINATED
        ],
        LeaseStatus.EXPIRING_SOON: [
            LeaseStatus.PENDING_RENEWAL,
            LeaseStatus.NOTICE_GIVEN,
            LeaseStatus.EXPIRED
        ],
        LeaseStatus.PENDING_RENEWAL: [
            LeaseStatus.RENEWED,
            LeaseStatus.NOTICE_GIVEN,
            LeaseStatus.EXPIRED
        ],
        LeaseStatus.NOTICE_GIVEN: [LeaseStatus.EXPIRED],
        LeaseStatus.EXPIRED: [],
        LeaseStatus.TERMINATED: [],
        LeaseStatus.RENEWED: []
    }

    def can_transition(self, from_status: LeaseStatus, to_status: LeaseStatus) -> bool:
        """
        Check if transition is allowed
        """
        allowed = self.ALLOWED_TRANSITIONS.get(from_status, [])
        return to_status in allowed

    def transition(self, lease, new_status: LeaseStatus, reason: str = None):
        """
        Transition lease to new status
        """
        if not self.can_transition(lease.status, new_status):
            raise ValueError(
                f"Invalid transition from {lease.status} to {new_status}"
            )

        # Record state change
        self.record_state_change(
            lease_id=lease.id,
            from_status=lease.status,
            to_status=new_status,
            reason=reason,
            timestamp=datetime.utcnow()
        )

        # Update lease status
        lease.status = new_status
        lease.updated_at = datetime.utcnow()

        # Trigger post-transition actions
        self.execute_post_transition_actions(lease, new_status)

    def execute_post_transition_actions(self, lease, new_status):
        """
        Execute actions after state transition
        """
        actions = {
            LeaseStatus.ACTIVE: self.on_lease_activated,
            LeaseStatus.EXPIRING_SOON: self.on_lease_expiring_soon,
            LeaseStatus.NOTICE_GIVEN: self.on_notice_given,
            LeaseStatus.EXPIRED: self.on_lease_expired
        }

        action = actions.get(new_status)
        if action:
            action(lease)

    def on_lease_activated(self, lease):
        """
        Actions when lease becomes active
        """
        # Post first month's rent
        self.post_rent_charge(lease)

        # Schedule recurring rent charges
        self.schedule_monthly_rent(lease)

        # Send welcome email to tenant
        self.send_welcome_email(lease)

        # Update unit status to occupied
        self.update_unit_status(lease.unit_id, "occupied")

    def on_lease_expiring_soon(self, lease):
        """
        Actions when lease is expiring soon (90 days)
        """
        # Send renewal notice to tenant
        self.send_renewal_notice(lease)

        # Generate renewal offer
        renewal_offer = self.generate_renewal_offer(lease)

        # Create renewal task for property manager
        self.create_task("Review renewal for lease", lease.id)

    def on_notice_given(self, lease):
        """
        Actions when tenant gives notice to vacate
        """
        # Schedule move-out inspection
        self.schedule_move_out_inspection(lease)

        # Create marketing listing for unit
        self.create_listing(lease.unit_id)

        # Send move-out checklist to tenant
        self.send_move_out_checklist(lease)

    def on_lease_expired(self, lease):
        """
        Actions when lease expires
        """
        # Stop rent charges
        self.cancel_recurring_rent(lease)

        # Process security deposit refund
        self.process_security_deposit_refund(lease)

        # Update unit status to vacant
        self.update_unit_status(lease.unit_id, "vacant")

        # Archive lease documents
        self.archive_lease(lease)
```

### AWS Step Functions Implementation

```json
{
  "Comment": "Lease Lifecycle Workflow",
  "StartAt": "CreateDraftLease",
  "States": {
    "CreateDraftLease": {
      "Type": "Task",
      "Resource": "arn:aws:lambda:us-east-1:123456789012:function:CreateDraftLease",
      "Next": "SendForSignatures"
    },
    "SendForSignatures": {
      "Type": "Task",
      "Resource": "arn:aws:lambda:us-east-1:123456789012:function:SendForSignatures",
      "Next": "WaitForSignatures"
    },
    "WaitForSignatures": {
      "Type": "Task",
      "Resource": "arn:aws:states:::lambda:invoke.waitForTaskToken",
      "Parameters": {
        "FunctionName": "WaitForSignatures",
        "Payload": {
          "lease_id.$": "$.lease_id",
          "task_token.$": "$$.Task.Token"
        }
      },
      "Next": "CheckAllSigned"
    },
    "CheckAllSigned": {
      "Type": "Choice",
      "Choices": [
        {
          "Variable": "$.all_signed",
          "BooleanEquals": true,
          "Next": "ActivateLease"
        }
      ],
      "Default": "SendReminderAndWait"
    },
    "SendReminderAndWait": {
      "Type": "Wait",
      "Seconds": 259200,
      "Next": "WaitForSignatures"
    },
    "ActivateLease": {
      "Type": "Task",
      "Resource": "arn:aws:lambda:us-east-1:123456789012:function:ActivateLease",
      "Next": "ScheduleRentCharges"
    },
    "ScheduleRentCharges": {
      "Type": "Task",
      "Resource": "arn:aws:lambda:us-east-1:123456789012:function:ScheduleRentCharges",
      "End": true
    }
  }
}
```

## Automated Rent Posting

### Monthly Rent Posting Workflow

```python
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime

class AutomatedRentPosting:
    """
    Automated monthly rent charge posting
    """

    def __init__(self, db_session, scheduler: BackgroundScheduler):
        self.db = db_session
        self.scheduler = scheduler

    def schedule_rent_posting(self, lease):
        """
        Schedule monthly rent posting for lease
        """
        # Post rent on 1st of each month (or lease-specific date)
        rent_due_day = lease.rent_due_day_of_month or 1

        job_id = f"rent_posting_{lease.id}"

        # Schedule monthly job
        self.scheduler.add_job(
            func=self.post_rent_for_lease,
            args=[lease.id],
            trigger='cron',
            day=rent_due_day,
            hour=0,
            minute=0,
            id=job_id,
            replace_existing=True,
            start_date=lease.lease_start_date,
            end_date=lease.lease_end_date
        )

    def post_rent_for_lease(self, lease_id):
        """
        Post rent charge for specific lease
        """
        lease = self.db.query(Lease).get(lease_id)

        # Check if lease is active
        if lease.status != LeaseStatus.ACTIVE:
            return

        # Create rent charge
        charge = Charge(
            lease_id=lease.id,
            tenant_id=lease.tenant_id,
            charge_type="rent",
            amount=lease.monthly_rent_amount,
            due_date=datetime.now().replace(day=lease.rent_due_day_of_month),
            post_date=datetime.now(),
            description=f"Rent - {datetime.now().strftime('%B %Y')}"
        )

        self.db.add(charge)
        self.db.commit()

        # Send rent due notification
        self.send_rent_due_notification(lease)

    def post_late_fees(self):
        """
        Automatically post late fees for overdue rent
        """
        grace_period_days = 5  # Typical grace period

        # Find overdue charges
        overdue_charges = self.db.query(Charge).filter(
            Charge.charge_type == "rent",
            Charge.due_date < datetime.now() - timedelta(days=grace_period_days),
            Charge.balance > 0,
            ~Charge.late_fee_posted
        ).all()

        for charge in overdue_charges:
            lease = charge.lease

            # Calculate late fee
            late_fee_amount = self.calculate_late_fee(lease, charge)

            # Create late fee charge
            late_fee = Charge(
                lease_id=lease.id,
                tenant_id=lease.tenant_id,
                charge_type="late_fee",
                amount=late_fee_amount,
                due_date=datetime.now(),
                post_date=datetime.now(),
                description=f"Late Fee - Rent {charge.due_date.strftime('%B %Y')}"
            )

            self.db.add(late_fee)

            # Mark original charge as having late fee posted
            charge.late_fee_posted = True

            self.db.commit()

            # Send late fee notification
            self.send_late_fee_notification(lease, late_fee_amount)

    def calculate_late_fee(self, lease, charge):
        """
        Calculate late fee based on lease terms
        """
        if lease.late_fee_type == "percentage":
            return charge.amount * (lease.late_fee_percentage / 100)
        elif lease.late_fee_type == "flat":
            return lease.late_fee_flat_amount
        else:
            # Default: 5% or $50, whichever is greater
            percentage_fee = charge.amount * 0.05
            return max(percentage_fee, 50.00)
```

## Lease Renewal Workflows

### Automated Renewal Process

```python
class LeaseRenewalWorkflow:
    """
    Automated lease renewal workflow
    """

    def trigger_renewal_workflow(self, lease):
        """
        Start renewal workflow 90 days before expiration
        """
        # Check if already in renewal process
        if lease.renewal_process_started:
            return

        # Generate renewal offer
        renewal_offer = self.generate_renewal_offer(lease)

        # Send renewal notice to tenant
        self.send_renewal_notice(lease, renewal_offer)

        # Update lease status
        lease.status = LeaseStatus.PENDING_RENEWAL
        lease.renewal_process_started = True
        lease.renewal_offer_sent_date = datetime.utcnow()

        # Schedule follow-up reminders
        self.schedule_renewal_reminders(lease)

    def generate_renewal_offer(self, lease):
        """
        Generate renewal offer based on market conditions
        """
        # Get market rent for unit
        market_rent = self.get_market_rent(lease.unit_id)

        # Get tenant score (payment history, violations)
        tenant_score = self.calculate_tenant_score(lease.tenant_id)

        # Calculate renewal rent
        if tenant_score >= 90:
            # Excellent tenant - minimal increase
            renewal_rent = min(
                lease.monthly_rent_amount * 1.02,  # 2% max increase
                market_rent * 0.98  # 98% of market
            )
        elif tenant_score >= 75:
            # Good tenant - moderate increase
            renewal_rent = min(
                lease.monthly_rent_amount * 1.05,  # 5% max increase
                market_rent * 0.99
            )
        else:
            # Problematic tenant - market rent
            renewal_rent = market_rent

        renewal_offer = {
            "current_rent": lease.monthly_rent_amount,
            "market_rent": market_rent,
            "offered_rent": renewal_rent,
            "increase_percentage": (renewal_rent - lease.monthly_rent_amount) / lease.monthly_rent_amount * 100,
            "lease_term_months": 12,
            "concessions": self.calculate_concessions(lease, tenant_score),
            "offer_expiration_date": datetime.utcnow() + timedelta(days=30)
        }

        return renewal_offer

    def schedule_renewal_reminders(self, lease):
        """
        Schedule automated reminders for renewal decision
        """
        # Reminder schedule: T-75, T-60, T-45, T-30 days
        reminder_days = [75, 60, 45, 30]

        for days_before_expiration in reminder_days:
            reminder_date = lease.lease_end_date - timedelta(days=days_before_expiration)

            self.scheduler.add_job(
                func=self.send_renewal_reminder,
                args=[lease.id],
                trigger='date',
                run_date=reminder_date,
                id=f"renewal_reminder_{lease.id}_{days_before_expiration}"
            )

    def process_renewal_decision(self, lease, decision: str):
        """
        Process tenant's renewal decision
        """
        if decision == "accept":
            # Create renewal lease
            new_lease = self.create_renewal_lease(lease)

            # Send for signatures
            self.send_for_signatures(new_lease)

            # Update original lease
            lease.status = LeaseStatus.RENEWED
            lease.renewal_lease_id = new_lease.id

        elif decision == "decline":
            # Tenant is moving out
            lease.status = LeaseStatus.NOTICE_GIVEN
            lease.notice_given_date = datetime.utcnow()

            # Start move-out process
            self.start_move_out_workflow(lease)

        elif decision == "negotiate":
            # Create task for property manager
            self.create_negotiation_task(lease)

    def create_renewal_lease(self, original_lease):
        """
        Create new lease for renewal
        """
        new_lease = Lease(
            property_id=original_lease.property_id,
            unit_id=original_lease.unit_id,
            tenant_id=original_lease.tenant_id,
            lease_type="renewal",
            original_lease_id=original_lease.id,
            lease_start_date=original_lease.lease_end_date + timedelta(days=1),
            lease_end_date=original_lease.lease_end_date + timedelta(days=365),
            monthly_rent_amount=original_lease.renewal_offer["offered_rent"],
            status=LeaseStatus.DRAFT
        )

        self.db.add(new_lease)
        self.db.commit()

        return new_lease
```

## Move-In/Move-Out Automation

### Move-In Checklist Workflow

```python
class MoveInWorkflow:
    """
    Automated move-in process
    """

    def start_move_in_workflow(self, lease):
        """
        Initiate move-in workflow
        """
        # Create move-in checklist
        checklist = self.create_move_in_checklist(lease)

        # Send to property manager
        self.assign_checklist(checklist, lease.property_manager_id)

        # Schedule move-in inspection
        self.schedule_move_in_inspection(lease)

        # Send move-in packet to tenant
        self.send_move_in_packet(lease)

    def create_move_in_checklist(self, lease):
        """
        Create move-in checklist items
        """
        checklist_items = [
            "Verify tenant ID and lease",
            "Collect first month's rent",
            "Collect security deposit",
            "Issue keys and access cards",
            "Conduct unit walk-through",
            "Document unit condition (photos)",
            "Provide tenant handbook",
            "Set up utility accounts",
            "Provide parking permit (if applicable)",
            "Explain building amenities",
            "Provide emergency contact info"
        ]

        checklist = MoveInChecklist(
            lease_id=lease.id,
            items=[
                ChecklistItem(description=item, completed=False)
                for item in checklist_items
            ]
        )

        self.db.add(checklist)
        self.db.commit()

        return checklist

    def complete_checklist_item(self, checklist_id, item_id):
        """
        Mark checklist item as complete
        """
        item = self.db.query(ChecklistItem).get(item_id)
        item.completed = True
        item.completed_at = datetime.utcnow()
        item.completed_by = get_current_user()

        self.db.commit()

        # Check if all items complete
        checklist = self.db.query(MoveInChecklist).get(checklist_id)
        if all(item.completed for item in checklist.items):
            self.finalize_move_in(checklist.lease)

    def finalize_move_in(self, lease):
        """
        Finalize move-in process
        """
        # Activate lease
        lease.status = LeaseStatus.ACTIVE
        lease.move_in_date = datetime.utcnow().date()

        # Start rent posting schedule
        self.schedule_rent_posting(lease)

        # Send welcome email
        self.send_welcome_email(lease)

        self.db.commit()
```

## Event-Driven Patterns

### Event Bus Architecture

```python
from dataclasses import dataclass
from typing import Callable, List
import json

@dataclass
class LeaseEvent:
    """
    Lease domain event
    """
    event_type: str
    lease_id: str
    timestamp: datetime
    data: dict

class LeaseEventBus:
    """
    Event bus for lease events
    """

    def __init__(self):
        self.subscribers = {}

    def subscribe(self, event_type: str, handler: Callable):
        """
        Subscribe to lease events
        """
        if event_type not in self.subscribers:
            self.subscribers[event_type] = []

        self.subscribers[event_type].append(handler)

    def publish(self, event: LeaseEvent):
        """
        Publish lease event
        """
        # Get subscribers for this event type
        handlers = self.subscribers.get(event.event_type, [])

        # Execute all handlers
        for handler in handlers:
            try:
                handler(event)
            except Exception as e:
                # Log error but don't fail publishing
                log_error(f"Event handler failed: {e}")

# Create global event bus
event_bus = LeaseEventBus()

# Subscribe handlers
event_bus.subscribe("lease.activated", send_welcome_email_handler)
event_bus.subscribe("lease.activated", post_first_rent_handler)
event_bus.subscribe("lease.activated", update_unit_status_handler)

event_bus.subscribe("lease.expired", process_security_deposit_handler)
event_bus.subscribe("lease.expired", archive_lease_handler)

# Publish events
def activate_lease(lease):
    # Activate lease
    lease.status = LeaseStatus.ACTIVE
    db.commit()

    # Publish event
    event = LeaseEvent(
        event_type="lease.activated",
        lease_id=lease.id,
        timestamp=datetime.utcnow(),
        data={"lease": lease.to_dict()}
    )

    event_bus.publish(event)
```

### AWS EventBridge Integration

```python
import boto3

class EventBridgePublisher:
    """
    Publish lease events to AWS EventBridge
    """

    def __init__(self, event_bus_name="proptech-events"):
        self.client = boto3.client('events')
        self.event_bus_name = event_bus_name

    def publish_lease_event(self, event: LeaseEvent):
        """
        Publish event to EventBridge
        """
        response = self.client.put_events(
            Entries=[
                {
                    'Source': 'proptech.leases',
                    'DetailType': event.event_type,
                    'Detail': json.dumps(event.data),
                    'EventBusName': self.event_bus_name
                }
            ]
        )

        return response

# Event consumers can subscribe via EventBridge rules
# Example: Trigger Lambda function on "lease.activated" events
```

## Integration with Accounting

### Accounting Sync Workflow

```python
class AccountingIntegration:
    """
    Sync lease transactions to accounting system (QuickBooks, Yardi)
    """

    def sync_lease_charges_to_gl(self, lease_id):
        """
        Sync lease charges to general ledger
        """
        charges = self.db.query(Charge).filter_by(
            lease_id=lease_id,
            synced_to_gl=False
        ).all()

        for charge in charges:
            # Map charge to GL account
            gl_account = self.map_charge_to_gl_account(charge.charge_type)

            # Create GL entry
            gl_entry = {
                "account": gl_account,
                "debit": charge.amount if charge.amount > 0 else 0,
                "credit": abs(charge.amount) if charge.amount < 0 else 0,
                "description": charge.description,
                "reference": f"LEASE-{lease_id}-CHARGE-{charge.id}",
                "date": charge.post_date
            }

            # Post to accounting system
            self.post_to_accounting_system(gl_entry)

            # Mark as synced
            charge.synced_to_gl = True

        self.db.commit()

    def map_charge_to_gl_account(self, charge_type):
        """
        Map charge type to GL account
        """
        gl_mapping = {
            "rent": "4100",  # Rental Income
            "late_fee": "4200",  # Late Fee Income
            "pet_rent": "4150",  # Pet Rent Income
            "parking": "4160",  # Parking Income
            "utilities": "4170"  # Utility Reimbursement
        }

        return gl_mapping.get(charge_type, "4000")  # Default income account
```

## Approval Chains

### Multi-Level Approval Workflow

```python
class ApprovalWorkflow:
    """
    Multi-level approval for commercial leases
    """

    def request_approval(self, lease, approval_type="standard"):
        """
        Request approval for lease
        """
        # Define approval chain based on lease value
        if lease.total_lease_value > 1000000:
            approval_chain = ["property_manager", "regional_manager", "vp_operations", "cfo"]
        elif lease.total_lease_value > 500000:
            approval_chain = ["property_manager", "regional_manager", "vp_operations"]
        else:
            approval_chain = ["property_manager", "regional_manager"]

        # Create approval request
        approval_request = ApprovalRequest(
            lease_id=lease.id,
            approval_type=approval_type,
            approval_chain=approval_chain,
            current_approver_index=0,
            status="pending"
        )

        self.db.add(approval_request)
        self.db.commit()

        # Notify first approver
        self.notify_approver(approval_request)

    def approve(self, approval_request_id, approver_id, decision: str, notes: str = None):
        """
        Record approval decision
        """
        approval_request = self.db.query(ApprovalRequest).get(approval_request_id)

        # Record decision
        approval = Approval(
            approval_request_id=approval_request_id,
            approver_id=approver_id,
            decision=decision,
            notes=notes,
            timestamp=datetime.utcnow()
        )

        self.db.add(approval)

        if decision == "approved":
            # Move to next approver
            approval_request.current_approver_index += 1

            if approval_request.current_approver_index >= len(approval_request.approval_chain):
                # All approvals complete
                approval_request.status = "approved"
                self.finalize_lease_approval(approval_request.lease)
            else:
                # Notify next approver
                self.notify_approver(approval_request)

        elif decision == "rejected":
            # Approval rejected
            approval_request.status = "rejected"
            self.notify_rejection(approval_request)

        self.db.commit()
```

---

## References

1. **AWS Step Functions**: https://aws.amazon.com/step-functions/
2. **Temporal.io**: https://temporal.io/
3. **Camunda BPMN**: https://camunda.com/

---

*This document is maintained by the PropTech Architecture Committee. For questions or updates, contact architecture@proptech.com.*
