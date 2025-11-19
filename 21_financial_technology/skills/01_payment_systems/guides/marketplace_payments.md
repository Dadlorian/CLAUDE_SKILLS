# Marketplace Payments Guide

Building payment infrastructure for marketplaces including split payments, vendor payouts, and commission handling.

## Overview

Marketplace payments require sophisticated infrastructure to manage money flow between buyers, sellers, and the platform. Key challenges include split payments, escrow management, commission calculation, vendor payouts, and regulatory compliance across multiple jurisdictions.

## Core Architecture

### 1. Payment Flow Models

```python
from enum import Enum
from typing import List, Optional
from decimal import Decimal
from datetime import datetime, timedelta

class PaymentFlowType(Enum):
    SPLIT_PAYMENT = "split"  # Direct split at charge time
    HELD_IN_ESCROW = "escrow"  # Platform holds, releases later
    PLATFORM_COLLECT = "aggregate"  # Platform collects, pays out later

class MarketplaceTransaction:
    def __init__(self, order_id: str, buyer_id: str,
                 total_amount: Decimal, flow_type: PaymentFlowType):
        self.order_id = order_id
        self.buyer_id = buyer_id
        self.total_amount = total_amount
        self.flow_type = flow_type
        self.line_items: List[LineItem] = []
        self.platform_fee: Decimal = Decimal('0')
        self.payment_processor_fee: Decimal = Decimal('0')
        self.created_at = datetime.utcnow()

    def add_line_item(self, seller_id: str, amount: Decimal,
                      commission_rate: Decimal):
        """Add item from a seller"""
        commission = amount * commission_rate
        seller_payout = amount - commission

        line_item = LineItem(
            seller_id=seller_id,
            gross_amount=amount,
            commission=commission,
            net_payout=seller_payout
        )
        self.line_items.append(line_item)
        self.platform_fee += commission

    def calculate_splits(self) -> List['PaymentSplit']:
        """Calculate how payment should be split"""
        splits = []

        for item in self.line_items:
            splits.append(PaymentSplit(
                recipient_id=item.seller_id,
                amount=item.net_payout,
                type='seller_payout'
            ))

        # Platform fee split
        if self.platform_fee > 0:
            splits.append(PaymentSplit(
                recipient_id='platform',
                amount=self.platform_fee,
                type='platform_commission'
            ))

        return splits
```

### 2. Split Payment Implementation

```python
from stripe import StripeClient
from typing import Dict, Any

class SplitPaymentProcessor:
    """Process payments with automatic splits to multiple recipients"""

    def __init__(self, stripe_client: StripeClient):
        self.stripe = stripe_client

    async def process_split_payment(self, transaction: MarketplaceTransaction,
                                    payment_method_id: str) -> Dict[str, Any]:
        """Process payment with automatic split to sellers"""

        # Create payment intent with automatic transfer
        transfers = []
        for item in transaction.line_items:
            seller_account = await self._get_seller_connected_account(item.seller_id)

            transfers.append({
                'amount': int(item.net_payout * 100),  # Convert to cents
                'destination': seller_account.stripe_account_id
            })

        payment_intent = await self.stripe.payment_intents.create(
            amount=int(transaction.total_amount * 100),
            currency='usd',
            payment_method=payment_method_id,
            transfer_data={
                'destination': None  # Transfers handled separately
            },
            metadata={
                'order_id': transaction.order_id,
                'marketplace_transaction': True
            }
        )

        # Confirm payment
        confirmed = await self.stripe.payment_intents.confirm(
            payment_intent.id
        )

        # Create transfers after successful payment
        if confirmed.status == 'succeeded':
            transfer_results = []
            for transfer_data in transfers:
                transfer = await self.stripe.transfers.create(
                    amount=transfer_data['amount'],
                    currency='usd',
                    destination=transfer_data['destination'],
                    source_transaction=confirmed.charges.data[0].id,
                    metadata={
                        'order_id': transaction.order_id
                    }
                )
                transfer_results.append(transfer)

            return {
                'payment_intent': confirmed,
                'transfers': transfer_results,
                'status': 'completed'
            }

        return {
            'payment_intent': confirmed,
            'status': confirmed.status
        }
```

### 3. Escrow Management

```python
from dataclasses import dataclass
from enum import Enum

class EscrowStatus(Enum):
    HELD = "held"
    RELEASED = "released"
    REFUNDED = "refunded"
    DISPUTED = "disputed"

@dataclass
class EscrowHold:
    transaction_id: str
    seller_id: str
    amount: Decimal
    held_at: datetime
    release_at: datetime
    status: EscrowStatus
    dispute_id: Optional[str] = None

class EscrowManager:
    """Manage funds held in escrow until order completion"""

    def __init__(self, database, payment_processor):
        self.db = database
        self.processor = payment_processor
        self.default_hold_period = timedelta(days=7)

    async def create_escrow_hold(self, transaction: MarketplaceTransaction) -> List[EscrowHold]:
        """Create escrow holds for each seller in transaction"""
        holds = []

        for item in transaction.line_items:
            # Calculate release date based on product type
            hold_period = await self._get_hold_period(item.seller_id)
            release_at = datetime.utcnow() + hold_period

            hold = EscrowHold(
                transaction_id=transaction.order_id,
                seller_id=item.seller_id,
                amount=item.net_payout,
                held_at=datetime.utcnow(),
                release_at=release_at,
                status=EscrowStatus.HELD
            )

            await self.db.save_escrow_hold(hold)
            holds.append(hold)

        return holds

    async def release_escrow(self, transaction_id: str, seller_id: str):
        """Release funds from escrow to seller"""
        hold = await self.db.get_escrow_hold(transaction_id, seller_id)

        if hold.status != EscrowStatus.HELD:
            raise ValueError(f"Cannot release escrow in status {hold.status}")

        # Check if release conditions are met
        if not await self._can_release(hold):
            raise ValueError("Release conditions not met")

        # Process payout to seller
        payout = await self.processor.create_payout(
            seller_id=seller_id,
            amount=hold.amount,
            metadata={
                'transaction_id': transaction_id,
                'escrow_release': True
            }
        )

        # Update hold status
        hold.status = EscrowStatus.RELEASED
        await self.db.update_escrow_hold(hold)

        return payout

    async def _can_release(self, hold: EscrowHold) -> bool:
        """Check if escrow can be released"""
        # Check if hold period has elapsed
        if datetime.utcnow() < hold.release_at:
            return False

        # Check if there are any active disputes
        if await self.db.has_active_dispute(hold.transaction_id):
            return False

        # Check if order is marked as delivered/completed
        order_status = await self.db.get_order_status(hold.transaction_id)
        if order_status not in ['delivered', 'completed']:
            return False

        return True

    async def process_automatic_releases(self):
        """Background job to automatically release eligible escrow holds"""
        eligible_holds = await self.db.get_eligible_escrow_releases()

        for hold in eligible_holds:
            try:
                await self.release_escrow(hold.transaction_id, hold.seller_id)
            except Exception as e:
                logger.error(f"Failed to release escrow {hold.transaction_id}: {e}")
                await self._alert_ops_team(hold, e)
```

### 4. Commission Calculation

```python
from typing import Dict, Optional
from decimal import Decimal, ROUND_HALF_UP

class CommissionEngine:
    """Calculate marketplace commissions with tiered rates and special rules"""

    def __init__(self, database):
        self.db = database
        self.default_rate = Decimal('0.15')  # 15% default

    async def calculate_commission(self, seller_id: str, amount: Decimal,
                                   category: str) -> Decimal:
        """Calculate commission based on seller tier, amount, and category"""

        # Get seller's commission tier
        seller_tier = await self._get_seller_tier(seller_id)

        # Get base rate for tier
        base_rate = self._get_tier_rate(seller_tier)

        # Apply category-specific adjustments
        category_modifier = await self._get_category_modifier(category)
        effective_rate = base_rate * (1 + category_modifier)

        # Apply volume discounts
        monthly_volume = await self._get_seller_monthly_volume(seller_id)
        volume_discount = self._calculate_volume_discount(monthly_volume)
        effective_rate = effective_rate * (1 - volume_discount)

        # Calculate commission with minimum
        commission = (amount * effective_rate).quantize(
            Decimal('0.01'), rounding=ROUND_HALF_UP
        )

        # Apply minimum commission
        min_commission = Decimal('0.50')
        commission = max(commission, min_commission)

        return commission

    def _get_tier_rate(self, tier: str) -> Decimal:
        """Get commission rate for seller tier"""
        rates = {
            'new': Decimal('0.20'),      # 20% for new sellers
            'bronze': Decimal('0.15'),   # 15% standard
            'silver': Decimal('0.12'),   # 12% for high-volume
            'gold': Decimal('0.10'),     # 10% for premium sellers
            'platinum': Decimal('0.08')  # 8% for top sellers
        }
        return rates.get(tier, self.default_rate)

    def _calculate_volume_discount(self, monthly_volume: Decimal) -> Decimal:
        """Calculate discount based on monthly volume"""
        if monthly_volume >= 100000:
            return Decimal('0.02')  # 2% discount
        elif monthly_volume >= 50000:
            return Decimal('0.01')  # 1% discount
        return Decimal('0')

    async def _get_category_modifier(self, category: str) -> Decimal:
        """Get category-specific rate modifier"""
        modifiers = {
            'electronics': Decimal('-0.1'),  # 10% lower commission
            'digital_goods': Decimal('-0.2'),  # 20% lower commission
            'luxury': Decimal('0.1'),  # 10% higher commission
            'default': Decimal('0')
        }
        return modifiers.get(category, modifiers['default'])
```

### 5. Vendor Payout System

```python
from enum import Enum
from typing import List

class PayoutMethod(Enum):
    BANK_TRANSFER = "bank"
    INSTANT_PAYOUT = "instant"
    CHECK = "check"
    PAYPAL = "paypal"

class PayoutFrequency(Enum):
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    ON_DEMAND = "on_demand"

class VendorPayoutSystem:
    """Manage scheduled and on-demand payouts to vendors"""

    def __init__(self, payment_processor, database):
        self.processor = payment_processor
        self.db = database

    async def calculate_vendor_balance(self, seller_id: str) -> Dict[str, Decimal]:
        """Calculate vendor's available and pending balance"""

        # Get all completed transactions
        completed = await self.db.get_completed_transactions(seller_id)
        completed_amount = sum([t.net_payout for t in completed])

        # Get pending escrow holds
        pending_escrow = await self.db.get_pending_escrow(seller_id)
        pending_amount = sum([e.amount for e in pending_escrow])

        # Get already processed payouts
        paid_out = await self.db.get_total_payouts(seller_id)

        available_balance = completed_amount - paid_out
        pending_balance = pending_amount

        return {
            'available': available_balance,
            'pending': pending_balance,
            'lifetime_earnings': completed_amount + pending_amount
        }

    async def process_payout(self, seller_id: str,
                            amount: Optional[Decimal] = None,
                            method: PayoutMethod = PayoutMethod.BANK_TRANSFER) -> Dict:
        """Process payout to vendor"""

        # Get vendor payout settings
        vendor = await self.db.get_vendor(seller_id)
        balance = await self.calculate_vendor_balance(seller_id)

        # Determine payout amount
        if amount is None:
            amount = balance['available']
        elif amount > balance['available']:
            raise ValueError(f"Insufficient balance. Available: {balance['available']}")

        # Apply payout minimum
        minimum_payout = Decimal('10.00')
        if amount < minimum_payout:
            raise ValueError(f"Payout must be at least ${minimum_payout}")

        # Calculate fees
        fee = self._calculate_payout_fee(amount, method)
        net_amount = amount - fee

        # Process payout through payment processor
        if method == PayoutMethod.INSTANT_PAYOUT:
            payout = await self._process_instant_payout(vendor, net_amount)
        elif method == PayoutMethod.BANK_TRANSFER:
            payout = await self._process_bank_transfer(vendor, net_amount)
        elif method == PayoutMethod.PAYPAL:
            payout = await self._process_paypal_payout(vendor, net_amount)

        # Record payout
        await self.db.create_payout_record(
            seller_id=seller_id,
            amount=amount,
            fee=fee,
            net_amount=net_amount,
            method=method,
            payout_id=payout['id']
        )

        return {
            'payout_id': payout['id'],
            'amount': amount,
            'fee': fee,
            'net_amount': net_amount,
            'method': method,
            'status': payout['status']
        }

    def _calculate_payout_fee(self, amount: Decimal, method: PayoutMethod) -> Decimal:
        """Calculate fee for payout method"""
        fees = {
            PayoutMethod.BANK_TRANSFER: Decimal('0'),  # Free
            PayoutMethod.INSTANT_PAYOUT: amount * Decimal('0.01'),  # 1%
            PayoutMethod.PAYPAL: amount * Decimal('0.02'),  # 2%
            PayoutMethod.CHECK: Decimal('5.00')  # Flat $5
        }
        return fees.get(method, Decimal('0'))

    async def process_scheduled_payouts(self, frequency: PayoutFrequency):
        """Background job to process scheduled payouts"""
        vendors = await self.db.get_vendors_by_payout_frequency(frequency)

        for vendor in vendors:
            balance = await self.calculate_vendor_balance(vendor.id)

            # Check if balance meets minimum
            if balance['available'] >= vendor.minimum_payout:
                try:
                    await self.process_payout(
                        seller_id=vendor.id,
                        method=vendor.preferred_payout_method
                    )
                except Exception as e:
                    logger.error(f"Payout failed for vendor {vendor.id}: {e}")
                    await self._notify_vendor_payout_failure(vendor, e)
```

### 6. Multi-Currency Support

```python
from forex_python.converter import CurrencyRates

class MultiCurrencyMarketplace:
    """Handle multi-currency transactions and payouts"""

    def __init__(self, fx_provider):
        self.fx = fx_provider
        self.supported_currencies = ['USD', 'EUR', 'GBP', 'CAD', 'AUD']

    async def process_cross_currency_transaction(self,
                                                 buyer_currency: str,
                                                 seller_currency: str,
                                                 amount: Decimal) -> Dict:
        """Process transaction where buyer and seller use different currencies"""

        # Get real-time exchange rate
        exchange_rate = await self.fx.get_rate(buyer_currency, seller_currency)

        # Calculate amounts
        buyer_amount = amount  # Amount in buyer's currency
        seller_amount = amount * Decimal(str(exchange_rate))  # Convert to seller currency

        # Apply forex markup (platform profit)
        forex_markup = Decimal('0.01')  # 1% markup
        adjusted_rate = exchange_rate * (1 + forex_markup)
        adjusted_seller_amount = amount * Decimal(str(adjusted_rate))

        forex_profit = adjusted_seller_amount - seller_amount

        return {
            'buyer_currency': buyer_currency,
            'buyer_amount': buyer_amount,
            'seller_currency': seller_currency,
            'seller_amount': seller_amount,
            'exchange_rate': exchange_rate,
            'forex_profit': forex_profit,
            'adjusted_seller_amount': adjusted_seller_amount
        }
```

## Best Practices

### 1. Fee Transparency
```python
class FeeCalculator:
    """Transparent fee breakdown for all parties"""

    def calculate_transaction_fees(self, amount: Decimal) -> Dict:
        payment_processing = amount * Decimal('0.029') + Decimal('0.30')  # 2.9% + $0.30
        platform_commission = amount * Decimal('0.15')  # 15%
        seller_receives = amount - payment_processing - platform_commission

        return {
            'gross_amount': amount,
            'payment_processing_fee': payment_processing,
            'platform_commission': platform_commission,
            'seller_receives': seller_receives,
            'buyer_pays': amount
        }
```

### 2. Refund Handling
- Refund commission to platform account
- Handle partial refunds proportionally
- Reverse escrow holds if not released
- Adjust seller balances and payouts

### 3. Dispute Management
- Freeze escrow during disputes
- Support evidence submission
- Implement mediation workflow
- Handle chargebacks separately

### 4. Compliance
- **Tax Reporting**: Generate 1099-K forms for sellers
- **Know Your Customer**: Verify seller identities
- **Anti-Money Laundering**: Monitor transaction patterns
- **Payment Processor ToS**: Comply with Stripe Connect, PayPal, etc.

## Production Considerations

### Monitoring
```python
marketplace_metrics = {
    'total_gmv': 'Gross Merchandise Value',
    'platform_revenue': 'Total commissions earned',
    'payout_volume': 'Total paid to sellers',
    'escrow_balance': 'Total held in escrow',
    'average_commission_rate': 'Effective commission %',
    'payout_failure_rate': 'Failed payouts / total',
    'dispute_rate': 'Disputes / total transactions'
}
```

### Testing
- Test split payment scenarios
- Verify commission calculations
- Test escrow release conditions
- Validate payout processing
- Test cross-currency transactions
- Simulate refund scenarios

### Scalability
- Use async processing for payouts
- Batch similar payouts together
- Cache vendor balances
- Optimize escrow queries
- Use message queues for high volume

## Integration Example

```python
# Complete marketplace transaction flow
async def process_marketplace_order(order_data: dict):
    # Create transaction
    transaction = MarketplaceTransaction(
        order_id=order_data['order_id'],
        buyer_id=order_data['buyer_id'],
        total_amount=Decimal(order_data['total']),
        flow_type=PaymentFlowType.HELD_IN_ESCROW
    )

    # Add line items with commissions
    commission_engine = CommissionEngine(database)
    for item in order_data['items']:
        commission_rate = await commission_engine.calculate_commission(
            seller_id=item['seller_id'],
            amount=item['amount'],
            category=item['category']
        )
        transaction.add_line_item(
            seller_id=item['seller_id'],
            amount=item['amount'],
            commission_rate=commission_rate / item['amount']  # Rate as decimal
        )

    # Process payment
    processor = SplitPaymentProcessor(stripe_client)
    payment_result = await processor.process_split_payment(
        transaction,
        order_data['payment_method_id']
    )

    # Create escrow holds
    escrow_manager = EscrowManager(database, stripe_client)
    escrow_holds = await escrow_manager.create_escrow_hold(transaction)

    return {
        'transaction': transaction,
        'payment': payment_result,
        'escrow_holds': escrow_holds
    }
```

## References

- [Stripe Connect Documentation](https://stripe.com/docs/connect)
- [PayPal Marketplace Payments](https://developer.paypal.com/docs/marketplaces/)
- [Payment Orchestration Guide](../reference/payment_orchestration.md)
