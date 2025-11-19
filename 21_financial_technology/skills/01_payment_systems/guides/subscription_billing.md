# Subscription Billing Guide

Implementing recurring subscription billing with dunning, proration, plan changes, and cancellation management.

## Overview

Subscription billing is complex, requiring careful handling of recurring charges, plan changes, proration, trials, cancellations, and failed payments. This guide covers production-ready implementations for SaaS and subscription businesses.

## Core Components

### 1. Subscription Model

```python
from enum import Enum
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Optional, List

class BillingInterval(Enum):
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    ANNUAL = "annual"

class SubscriptionStatus(Enum):
    TRIAL = "trialing"
    ACTIVE = "active"
    PAST_DUE = "past_due"
    CANCELED = "canceled"
    UNPAID = "unpaid"
    PAUSED = "paused"

class Subscription:
    def __init__(self, customer_id: str, plan_id: str,
                 billing_interval: BillingInterval):
        self.id = generate_id()
        self.customer_id = customer_id
        self.plan_id = plan_id
        self.billing_interval = billing_interval
        self.status = SubscriptionStatus.TRIAL
        self.current_period_start = datetime.utcnow()
        self.current_period_end = self._calculate_period_end()
        self.trial_end: Optional[datetime] = None
        self.cancel_at_period_end = False
        self.canceled_at: Optional[datetime] = None
        self.items: List[SubscriptionItem] = []

    def _calculate_period_end(self) -> datetime:
        """Calculate end of current billing period"""
        start = self.current_period_start

        if self.billing_interval == BillingInterval.MONTHLY:
            return start + timedelta(days=30)
        elif self.billing_interval == BillingInterval.ANNUAL:
            return start + timedelta(days=365)
        elif self.billing_interval == BillingInterval.QUARTERLY:
            return start + timedelta(days=90)
        elif self.billing_interval == BillingInterval.WEEKLY:
            return start + timedelta(days=7)
        else:  # DAILY
            return start + timedelta(days=1)

class SubscriptionItem:
    """Individual line item in subscription"""
    def __init__(self, price_id: str, quantity: int = 1):
        self.id = generate_id()
        self.price_id = price_id
        self.quantity = quantity
        self.created_at = datetime.utcnow()
```

### 2. Subscription Creation with Trials

```python
class SubscriptionService:
    """Manage subscription lifecycle"""

    def __init__(self, payment_processor, database):
        self.processor = payment_processor
        self.db = database

    async def create_subscription(self, customer_id: str, plan_id: str,
                                 trial_days: int = 0,
                                 payment_method_id: Optional[str] = None) -> Subscription:
        """Create new subscription with optional trial"""

        # Get plan details
        plan = await self.db.get_plan(plan_id)

        # Create subscription
        subscription = Subscription(
            customer_id=customer_id,
            plan_id=plan_id,
            billing_interval=plan.billing_interval
        )

        # Add plan items
        for price in plan.prices:
            item = SubscriptionItem(price_id=price.id, quantity=1)
            subscription.items.append(item)

        # Set up trial if specified
        if trial_days > 0:
            subscription.trial_end = datetime.utcnow() + timedelta(days=trial_days)
            subscription.status = SubscriptionStatus.TRIAL

            # Schedule first charge at trial end
            await self._schedule_charge(
                subscription,
                scheduled_at=subscription.trial_end
            )
        else:
            # Charge immediately
            if not payment_method_id:
                raise ValueError("Payment method required for non-trial subscription")

            charge_result = await self._charge_subscription(
                subscription,
                payment_method_id
            )

            if charge_result['status'] == 'succeeded':
                subscription.status = SubscriptionStatus.ACTIVE
            else:
                subscription.status = SubscriptionStatus.UNPAID

        # Save subscription
        await self.db.save_subscription(subscription)

        return subscription

    async def _charge_subscription(self, subscription: Subscription,
                                   payment_method_id: str) -> dict:
        """Charge customer for subscription period"""

        amount = await self._calculate_subscription_amount(subscription)

        try:
            charge = await self.processor.create_charge(
                customer_id=subscription.customer_id,
                amount=amount,
                payment_method_id=payment_method_id,
                description=f"Subscription {subscription.id}",
                metadata={
                    'subscription_id': subscription.id,
                    'period_start': subscription.current_period_start.isoformat(),
                    'period_end': subscription.current_period_end.isoformat()
                }
            )

            # Create invoice
            await self._create_invoice(subscription, charge, amount)

            return charge

        except PaymentFailedException as e:
            # Start dunning process
            await self._initiate_dunning(subscription, e)
            raise

    async def _calculate_subscription_amount(self, subscription: Subscription) -> Decimal:
        """Calculate total amount for subscription"""
        total = Decimal('0')

        for item in subscription.items:
            price = await self.db.get_price(item.price_id)
            total += price.amount * item.quantity

        return total
```

### 3. Plan Changes with Proration

```python
class ProrationCalculator:
    """Calculate proration for plan changes"""

    def calculate_proration(self, old_plan: dict, new_plan: dict,
                          period_start: datetime, period_end: datetime,
                          change_date: datetime) -> Decimal:
        """Calculate proration credit/charge for plan change"""

        # Calculate time remaining in period
        total_period_seconds = (period_end - period_start).total_seconds()
        remaining_seconds = (period_end - change_date).total_seconds()
        fraction_remaining = remaining_seconds / total_period_seconds

        # Calculate unused credit from old plan
        old_amount_paid = Decimal(str(old_plan['amount']))
        unused_credit = old_amount_paid * Decimal(str(fraction_remaining))

        # Calculate charge for new plan (prorated)
        new_amount = Decimal(str(new_plan['amount']))
        prorated_new_charge = new_amount * Decimal(str(fraction_remaining))

        # Net amount to charge/credit
        net_amount = prorated_new_charge - unused_credit

        return net_amount

class SubscriptionService:
    async def change_plan(self, subscription_id: str, new_plan_id: str,
                         prorate: bool = True) -> dict:
        """Change subscription plan with optional proration"""

        subscription = await self.db.get_subscription(subscription_id)
        old_plan = await self.db.get_plan(subscription.plan_id)
        new_plan = await self.db.get_plan(new_plan_id)

        change_date = datetime.utcnow()

        if prorate:
            # Calculate proration
            calculator = ProrationCalculator()
            proration_amount = calculator.calculate_proration(
                old_plan=old_plan,
                new_plan=new_plan,
                period_start=subscription.current_period_start,
                period_end=subscription.current_period_end,
                change_date=change_date
            )

            # Charge/credit proration amount
            if proration_amount > 0:
                # Charge difference
                await self.processor.create_charge(
                    customer_id=subscription.customer_id,
                    amount=proration_amount,
                    description=f"Proration: Upgrade to {new_plan.name}"
                )
            elif proration_amount < 0:
                # Issue credit
                await self._issue_credit(
                    subscription.customer_id,
                    abs(proration_amount),
                    f"Proration: Downgrade to {new_plan.name}"
                )

        # Update subscription
        subscription.plan_id = new_plan_id
        await self.db.update_subscription(subscription)

        # Schedule next billing at current period end
        await self._schedule_next_billing(subscription)

        return {
            'subscription': subscription,
            'proration_amount': proration_amount if prorate else None,
            'next_billing_date': subscription.current_period_end
        }
```

### 4. Usage-Based Billing

```python
from typing import Dict

class UsageTracker:
    """Track metered usage for billing"""

    def __init__(self, database):
        self.db = database

    async def record_usage(self, subscription_id: str,
                          usage_type: str, quantity: int,
                          timestamp: Optional[datetime] = None):
        """Record usage event"""

        usage_record = {
            'subscription_id': subscription_id,
            'usage_type': usage_type,
            'quantity': quantity,
            'timestamp': timestamp or datetime.utcnow()
        }

        await self.db.save_usage_record(usage_record)

    async def get_period_usage(self, subscription_id: str,
                              period_start: datetime,
                              period_end: datetime) -> Dict[str, int]:
        """Get aggregated usage for billing period"""

        usage_records = await self.db.query_usage(
            subscription_id=subscription_id,
            start_date=period_start,
            end_date=period_end
        )

        # Aggregate by usage type
        aggregated = {}
        for record in usage_records:
            usage_type = record['usage_type']
            aggregated[usage_type] = aggregated.get(usage_type, 0) + record['quantity']

        return aggregated

class UsageBasedBilling:
    """Calculate charges for usage-based billing"""

    async def calculate_usage_charges(self, subscription: Subscription) -> Decimal:
        """Calculate charges based on metered usage"""

        tracker = UsageTracker(self.db)
        usage = await tracker.get_period_usage(
            subscription_id=subscription.id,
            period_start=subscription.current_period_start,
            period_end=subscription.current_period_end
        )

        total_charges = Decimal('0')

        for item in subscription.items:
            price = await self.db.get_price(item.price_id)

            if price.billing_scheme == 'tiered':
                charge = self._calculate_tiered_pricing(usage, price)
            elif price.billing_scheme == 'volume':
                charge = self._calculate_volume_pricing(usage, price)
            else:  # 'per_unit'
                quantity = usage.get(price.usage_type, 0)
                charge = Decimal(str(quantity)) * price.unit_amount

            total_charges += charge

        return total_charges

    def _calculate_tiered_pricing(self, usage: Dict, price: dict) -> Decimal:
        """Calculate cost using tiered pricing"""
        quantity = usage.get(price.usage_type, 0)
        total = Decimal('0')

        for tier in price.tiers:
            tier_start = tier['up_to_inclusive'] if 'up_to_inclusive' in tier else 0
            tier_end = tier.get('up_to', float('inf'))

            if quantity > tier_start:
                tier_quantity = min(quantity, tier_end) - tier_start
                tier_amount = Decimal(str(tier_quantity)) * Decimal(str(tier['unit_amount']))
                total += tier_amount

        return total
```

### 5. Cancellation Management

```python
class CancellationService:
    """Handle subscription cancellations"""

    async def cancel_subscription(self, subscription_id: str,
                                 cancel_immediately: bool = False,
                                 reason: Optional[str] = None) -> dict:
        """Cancel subscription"""

        subscription = await self.db.get_subscription(subscription_id)

        if cancel_immediately:
            # Cancel and refund remaining period
            subscription.status = SubscriptionStatus.CANCELED
            subscription.canceled_at = datetime.utcnow()

            # Calculate refund for unused time
            refund_amount = await self._calculate_cancellation_refund(subscription)

            if refund_amount > 0:
                await self.processor.create_refund(
                    subscription.customer_id,
                    amount=refund_amount,
                    reason="Subscription canceled"
                )

            subscription.current_period_end = datetime.utcnow()
        else:
            # Cancel at end of billing period
            subscription.cancel_at_period_end = True
            subscription.canceled_at = datetime.utcnow()

        # Record cancellation reason
        await self.db.save_cancellation_feedback(
            subscription_id=subscription_id,
            reason=reason,
            canceled_at=subscription.canceled_at
        )

        await self.db.update_subscription(subscription)

        return {
            'subscription': subscription,
            'cancel_immediately': cancel_immediately,
            'refund_amount': refund_amount if cancel_immediately else None,
            'access_until': subscription.current_period_end
        }

    async def _calculate_cancellation_refund(self, subscription: Subscription) -> Decimal:
        """Calculate pro-rated refund for cancellation"""

        # Get last invoice
        last_invoice = await self.db.get_latest_invoice(subscription.id)

        if not last_invoice:
            return Decimal('0')

        # Calculate unused portion
        total_period = (subscription.current_period_end -
                       subscription.current_period_start).total_seconds()
        used_period = (datetime.utcnow() -
                      subscription.current_period_start).total_seconds()
        unused_fraction = 1 - (used_period / total_period)

        # Calculate refund amount
        refund = Decimal(str(last_invoice.amount)) * Decimal(str(unused_fraction))

        return refund.quantize(Decimal('0.01'))
```

### 6. Subscription Analytics

```python
import pandas as pd
from dataclasses import dataclass

@dataclass
class SubscriptionMetrics:
    mrr: Decimal  # Monthly Recurring Revenue
    arr: Decimal  # Annual Recurring Revenue
    churn_rate: float
    customer_lifetime_value: Decimal
    active_subscriptions: int
    new_subscriptions: int
    canceled_subscriptions: int

class SubscriptionAnalytics:
    """Calculate subscription business metrics"""

    def __init__(self, database):
        self.db = database

    async def calculate_mrr(self, date: Optional[datetime] = None) -> Decimal:
        """Calculate Monthly Recurring Revenue"""

        if not date:
            date = datetime.utcnow()

        active_subscriptions = await self.db.get_active_subscriptions(date)
        mrr = Decimal('0')

        for sub in active_subscriptions:
            # Normalize to monthly amount
            plan = await self.db.get_plan(sub.plan_id)
            monthly_amount = self._normalize_to_monthly(
                plan.amount,
                plan.billing_interval
            )
            mrr += monthly_amount

        return mrr

    def _normalize_to_monthly(self, amount: Decimal,
                             interval: BillingInterval) -> Decimal:
        """Convert any billing interval to monthly amount"""

        if interval == BillingInterval.MONTHLY:
            return amount
        elif interval == BillingInterval.ANNUAL:
            return amount / 12
        elif interval == BillingInterval.QUARTERLY:
            return amount / 3
        elif interval == BillingInterval.WEEKLY:
            return amount * Decimal('4.33')  # Average weeks per month
        else:  # DAILY
            return amount * 30

    async def calculate_churn_rate(self, start_date: datetime,
                                  end_date: datetime) -> float:
        """Calculate customer churn rate for period"""

        start_count = await self.db.count_active_subscriptions(start_date)
        cancellations = await self.db.count_cancellations(start_date, end_date)

        if start_count == 0:
            return 0.0

        churn_rate = cancellations / start_count
        return round(churn_rate, 4)

    async def calculate_ltv(self) -> Decimal:
        """Calculate Customer Lifetime Value"""

        # Simple LTV = ARPA / Churn Rate
        mrr = await self.calculate_mrr()
        active_count = await self.db.count_active_subscriptions(datetime.utcnow())
        arpa = mrr / active_count if active_count > 0 else Decimal('0')

        # Get 90-day churn rate
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=90)
        churn_rate = await self.calculate_churn_rate(start_date, end_date)

        if churn_rate == 0:
            return Decimal('0')  # Avoid division by zero

        ltv = arpa / Decimal(str(churn_rate))
        return ltv.quantize(Decimal('0.01'))
```

## Best Practices

### 1. Trial Management
- Always collect payment method before trial ends
- Send trial ending reminders (7 days, 3 days, 1 day)
- Allow extended trials for engaged users
- Track trial conversion rates

### 2. Billing Cycle Optimization
- Align billing dates for easier accounting
- Offer annual plans with discount
- Bill in advance for predictable revenue
- Support multiple currencies

### 3. Failed Payment Recovery
- Implement smart retry logic (see dunning guide)
- Send payment failure notifications immediately
- Provide grace period before service suspension
- Offer payment plan for past-due amounts

### 4. Customer Communication
- Send invoice emails immediately after charge
- Provide detailed receipts with line items
- Notify before plan renewals
- Confirm plan changes and cancellations

## Production Considerations

### Monitoring
```python
subscription_metrics = {
    'mrr': 'Monthly Recurring Revenue',
    'churn_rate': 'Monthly churn %',
    'failed_charges': 'Failed charges last 24h',
    'trial_conversions': 'Trial to paid conversion %',
    'upgrade_rate': 'Plan upgrade %',
    'downgrade_rate': 'Plan downgrade %'
}
```

### Testing
- Test all plan change combinations
- Verify proration calculations
- Test cancellation refund logic
- Validate usage metering accuracy
- Test failed payment scenarios

### Compliance
- **PCI DSS**: Secure payment method storage
- **Tax**: Calculate and collect sales tax where required
- **SCA**: Support 3D Secure for EU customers
- **Refunds**: Honor refund policies and regulations

## References

- [Stripe Billing Documentation](https://stripe.com/docs/billing)
- [Dunning Management Guide](./dunning_management.md)
- [Payment Security Guide](./payment_security_guide.md)
