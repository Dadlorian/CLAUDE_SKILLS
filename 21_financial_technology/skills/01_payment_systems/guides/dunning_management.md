# Dunning Management Guide

Implementing dunning systems to recover failed subscription payments with retry logic and customer communication.

## Overview

Dunning management is the process of communicating with customers to collect outstanding payments, particularly for failed recurring subscription charges. An effective dunning system can recover 30-70% of failed payments through strategic retry logic and customer communication.

## Core Components

### 1. Payment Failure Detection

```python
from enum import Enum
from datetime import datetime, timedelta
from typing import List, Optional

class FailureReason(Enum):
    INSUFFICIENT_FUNDS = "insufficient_funds"
    EXPIRED_CARD = "card_expired"
    CARD_DECLINED = "card_declined"
    FRAUD_SUSPECTED = "fraud_suspected"
    PROCESSING_ERROR = "processing_error"

class PaymentFailure:
    def __init__(self, subscription_id: str, customer_id: str,
                 amount: float, failure_reason: FailureReason):
        self.subscription_id = subscription_id
        self.customer_id = customer_id
        self.amount = amount
        self.failure_reason = failure_reason
        self.failed_at = datetime.utcnow()
        self.retry_count = 0
        self.next_retry = self.calculate_next_retry()

    def calculate_next_retry(self) -> datetime:
        """Calculate next retry based on failure type and retry count"""
        if self.failure_reason == FailureReason.INSUFFICIENT_FUNDS:
            # Try again in 3, 7, 14 days
            days = [3, 7, 14][min(self.retry_count, 2)]
            return datetime.utcnow() + timedelta(days=days)
        elif self.failure_reason == FailureReason.EXPIRED_CARD:
            # No automatic retry, wait for customer update
            return datetime.utcnow() + timedelta(days=30)
        else:
            # Standard retry: 1, 3, 7 days
            days = [1, 3, 7][min(self.retry_count, 2)]
            return datetime.utcnow() + timedelta(days=days)
```

### 2. Retry Strategy Engine

```python
from dataclasses import dataclass
from typing import Callable, Dict

@dataclass
class RetryStrategy:
    max_attempts: int
    retry_intervals: List[int]  # Days between retries
    smart_retry_enabled: bool
    use_card_account_updater: bool

class DunningEngine:
    def __init__(self, payment_gateway, notification_service):
        self.payment_gateway = payment_gateway
        self.notification_service = notification_service
        self.strategies = self._init_strategies()

    def _init_strategies(self) -> Dict[FailureReason, RetryStrategy]:
        """Define retry strategies per failure type"""
        return {
            FailureReason.INSUFFICIENT_FUNDS: RetryStrategy(
                max_attempts=4,
                retry_intervals=[3, 7, 14, 21],
                smart_retry_enabled=True,
                use_card_account_updater=False
            ),
            FailureReason.EXPIRED_CARD: RetryStrategy(
                max_attempts=1,
                retry_intervals=[30],
                smart_retry_enabled=False,
                use_card_account_updater=True
            ),
            FailureReason.CARD_DECLINED: RetryStrategy(
                max_attempts=3,
                retry_intervals=[1, 3, 7],
                smart_retry_enabled=True,
                use_card_account_updater=False
            )
        }

    async def process_failed_payment(self, failure: PaymentFailure):
        """Main dunning orchestration logic"""
        strategy = self.strategies.get(failure.failure_reason)

        if not strategy:
            # Default strategy
            strategy = self.strategies[FailureReason.CARD_DECLINED]

        # Check if we should retry
        if failure.retry_count >= strategy.max_attempts:
            await self._handle_final_failure(failure)
            return

        # Smart retry timing
        if strategy.smart_retry_enabled:
            next_retry = await self._calculate_smart_retry_time(failure)
        else:
            days = strategy.retry_intervals[min(failure.retry_count,
                                                 len(strategy.retry_intervals) - 1)]
            next_retry = datetime.utcnow() + timedelta(days=days)

        # Schedule retry
        await self._schedule_retry(failure, next_retry)

        # Send customer communication
        await self._send_dunning_email(failure)

        # Update card if needed
        if strategy.use_card_account_updater:
            await self._request_card_update(failure.customer_id)

    async def _calculate_smart_retry_time(self, failure: PaymentFailure) -> datetime:
        """Smart retry uses ML to predict best retry time"""
        customer_data = await self._get_customer_behavior(failure.customer_id)

        # Example: Retry when customer typically has funds
        if customer_data.get('payday_pattern'):
            next_payday = self._predict_next_payday(customer_data)
            return next_payday

        # Default to standard schedule
        return failure.calculate_next_retry()

    async def _schedule_retry(self, failure: PaymentFailure, retry_time: datetime):
        """Schedule the payment retry"""
        await self.payment_gateway.schedule_charge(
            customer_id=failure.customer_id,
            amount=failure.amount,
            scheduled_at=retry_time,
            metadata={
                'retry_count': failure.retry_count + 1,
                'original_failure': failure.failed_at.isoformat(),
                'dunning_sequence': True
            }
        )

        failure.retry_count += 1
        failure.next_retry = retry_time
        await self._save_failure_state(failure)
```

### 3. Customer Communication

```python
from jinja2 import Template
from enum import Enum

class DunningEmailType(Enum):
    FIRST_FAILURE = "first_failure"
    RETRY_NOTICE = "retry_notice"
    FINAL_WARNING = "final_warning"
    CARD_UPDATE_REQUEST = "card_update_request"
    SUCCESSFUL_RECOVERY = "successful_recovery"

class DunningCommunication:
    def __init__(self, email_service, sms_service):
        self.email_service = email_service
        self.sms_service = sms_service
        self.templates = self._load_templates()

    async def _send_dunning_email(self, failure: PaymentFailure):
        """Send appropriate email based on retry count and failure type"""
        customer = await self._get_customer(failure.customer_id)
        subscription = await self._get_subscription(failure.subscription_id)

        # Determine email type
        if failure.retry_count == 0:
            email_type = DunningEmailType.FIRST_FAILURE
        elif failure.retry_count >= 3:
            email_type = DunningEmailType.FINAL_WARNING
        else:
            email_type = DunningEmailType.RETRY_NOTICE

        # Prepare email content
        template = self.templates[email_type]
        subject, body = self._render_template(
            template,
            customer=customer,
            subscription=subscription,
            failure=failure,
            update_payment_url=self._generate_update_url(customer.id)
        )

        # Send email
        await self.email_service.send(
            to=customer.email,
            subject=subject,
            body=body,
            metadata={
                'dunning_sequence': True,
                'retry_count': failure.retry_count
            }
        )

        # Send SMS for high-value subscriptions
        if subscription.amount > 100:
            await self._send_sms_notification(customer, failure)

    def _render_template(self, template: Template, **context) -> tuple:
        """Render email template with personalized content"""
        subject_template = Template(template['subject'])
        body_template = Template(template['body'])

        subject = subject_template.render(**context)
        body = body_template.render(**context)

        return subject, body

    def _load_templates(self) -> Dict[DunningEmailType, dict]:
        """Load email templates for different dunning stages"""
        return {
            DunningEmailType.FIRST_FAILURE: {
                'subject': 'Payment Failed for {{ subscription.name }}',
                'body': '''
                Hi {{ customer.first_name }},

                We encountered an issue processing your payment for {{ subscription.name }}.

                Amount: ${{ failure.amount }}
                Reason: {{ failure.failure_reason.value }}

                Don't worry - we'll automatically try again in {{ retry_days }} days.
                To avoid any interruption, you can update your payment method here:
                {{ update_payment_url }}

                Best regards,
                {{ company_name }}
                '''
            },
            DunningEmailType.FINAL_WARNING: {
                'subject': 'Final Notice: Update Payment Method',
                'body': '''
                Hi {{ customer.first_name }},

                We've been unable to process payment for your {{ subscription.name }} subscription.
                Your account will be suspended in 7 days if we don't receive payment.

                Please update your payment method immediately:
                {{ update_payment_url }}

                If you have questions, contact our support team.

                Best regards,
                {{ company_name }}
                '''
            }
        }
```

### 4. Card Account Updater Integration

```python
class CardAccountUpdater:
    """Integrate with Visa VAU and Mastercard ABU to get updated card details"""

    def __init__(self, processor_client):
        self.processor_client = processor_client

    async def request_card_update(self, customer_id: str) -> bool:
        """Request updated card information from card networks"""
        payment_methods = await self._get_customer_payment_methods(customer_id)

        for pm in payment_methods:
            if pm.type != 'card' or not pm.is_expired:
                continue

            # Request update from processor (Stripe, Adyen, etc.)
            updated_card = await self.processor_client.request_card_update(
                payment_method_id=pm.id,
                last_four=pm.last_four,
                exp_month=pm.exp_month,
                exp_year=pm.exp_year
            )

            if updated_card:
                await self._update_payment_method(pm.id, updated_card)
                await self._notify_customer_of_update(customer_id)
                return True

        return False
```

### 5. Recovery Analytics

```python
from dataclasses import dataclass
from typing import List
import pandas as pd

@dataclass
class DunningMetrics:
    total_failures: int
    successful_recoveries: int
    recovery_rate: float
    average_recovery_time: float
    revenue_recovered: float
    revenue_lost: float

class DunningAnalytics:
    def __init__(self, database):
        self.db = database

    async def calculate_recovery_metrics(self, start_date, end_date) -> DunningMetrics:
        """Calculate dunning performance metrics"""
        failures = await self.db.get_payment_failures(start_date, end_date)

        total = len(failures)
        recovered = len([f for f in failures if f.status == 'recovered'])
        recovery_rate = recovered / total if total > 0 else 0

        # Calculate average time to recovery
        recovery_times = [
            (f.recovered_at - f.failed_at).total_seconds() / 86400
            for f in failures if f.status == 'recovered'
        ]
        avg_recovery_time = sum(recovery_times) / len(recovery_times) if recovery_times else 0

        # Calculate revenue impact
        revenue_recovered = sum([f.amount for f in failures if f.status == 'recovered'])
        revenue_lost = sum([f.amount for f in failures if f.status == 'failed_permanently'])

        return DunningMetrics(
            total_failures=total,
            successful_recoveries=recovered,
            recovery_rate=recovery_rate,
            average_recovery_time=avg_recovery_time,
            revenue_recovered=revenue_recovered,
            revenue_lost=revenue_lost
        )

    async def generate_recovery_report(self) -> pd.DataFrame:
        """Generate detailed recovery analysis by failure reason"""
        query = """
            SELECT
                failure_reason,
                COUNT(*) as total_failures,
                SUM(CASE WHEN status = 'recovered' THEN 1 ELSE 0 END) as recoveries,
                AVG(CASE WHEN status = 'recovered'
                    THEN EXTRACT(EPOCH FROM (recovered_at - failed_at))/86400
                    END) as avg_days_to_recovery,
                SUM(CASE WHEN status = 'recovered' THEN amount ELSE 0 END) as revenue_recovered
            FROM payment_failures
            WHERE failed_at >= NOW() - INTERVAL '90 days'
            GROUP BY failure_reason
        """

        df = await self.db.query_to_dataframe(query)
        df['recovery_rate'] = df['recoveries'] / df['total_failures']
        return df
```

## Best Practices

### 1. Timing Optimization
- **Insufficient Funds**: Retry early in the month after typical payday
- **Business Cards**: Retry Tuesday-Thursday during business hours
- **Weekend Retry**: Avoid Mondays (higher decline rates)
- **Time Zone Awareness**: Process retries in customer's local business hours

### 2. Communication Guidelines
- First failure: Friendly, informative tone
- Subsequent retries: More urgent, actionable
- Final notice: Clear consequences, easy resolution path
- Always provide one-click payment update link
- A/B test subject lines and messaging

### 3. Grace Period Management
```python
class GracePeriodManager:
    """Manage service access during dunning period"""

    GRACE_PERIODS = {
        'tier_basic': timedelta(days=7),
        'tier_pro': timedelta(days=14),
        'tier_enterprise': timedelta(days=30)
    }

    async def should_suspend_access(self, subscription) -> bool:
        """Determine if subscription access should be suspended"""
        if not subscription.in_dunning:
            return False

        grace_period = self.GRACE_PERIODS.get(
            subscription.tier,
            timedelta(days=7)
        )

        days_overdue = (datetime.utcnow() - subscription.payment_failed_at).days

        return days_overdue > grace_period.days
```

### 4. Churn Prevention
- Offer payment plan for large amounts
- Suggest plan downgrade instead of cancellation
- Provide customer success intervention for high-value customers
- Monitor customer engagement during dunning

## Production Considerations

### Compliance
- **PCI DSS**: Never store full card numbers in dunning logs
- **GDPR**: Respect communication preferences
- **CAN-SPAM**: Include unsubscribe option in dunning emails
- **State Laws**: Some states restrict dunning communication frequency

### Monitoring
```python
# Key metrics to monitor
dunning_metrics = {
    'recovery_rate': 'target >= 50%',
    'avg_retry_count': 'target <= 2.5',
    'email_open_rate': 'target >= 40%',
    'update_payment_rate': 'target >= 30%',
    'false_declines': 'target <= 5%'
}
```

### Testing
- Test retry logic with failed payment simulations
- Validate email delivery and rendering
- Test grace period calculations
- Verify card updater integration
- Load test dunning job processing

## Integration Example

```python
# Complete dunning workflow
async def main():
    dunning_engine = DunningEngine(
        payment_gateway=StripeGateway(),
        notification_service=EmailService()
    )

    # Process failed payments
    failed_payments = await get_failed_payments_for_processing()

    for failure in failed_payments:
        try:
            await dunning_engine.process_failed_payment(failure)
        except Exception as e:
            logger.error(f"Dunning error for {failure.customer_id}: {e}")
            await alert_ops_team(failure, e)

    # Generate daily report
    analytics = DunningAnalytics(database)
    metrics = await analytics.calculate_recovery_metrics(
        start_date=datetime.utcnow() - timedelta(days=30),
        end_date=datetime.utcnow()
    )

    await send_daily_dunning_report(metrics)
```

## References

- [Stripe Dunning Best Practices](https://stripe.com/docs/billing/revenue-recovery)
- [Recurly Dunning Management](https://docs.recurly.com/docs/dunning)
- [PCI DSS Compliance Guide](../reference/pci_dss.md)
