# Payment Gateway Integration Guide

**Version:** 2.5
**Last Updated:** 2025-01-15
**Status:** Active Standard
**Authority:** PropTech Payments Standards Committee
**References:** Stripe API, PayPal, Authorize.net, Yardi RentCafe Payments, PCI DSS v4.0

## Table of Contents

1. [Overview](#overview)
2. [Stripe Integration for Rent Collection](#stripe-integration-for-rent-collection)
3. [ACH Payment Processing](#ach-payment-processing)
4. [Recurring Payment Setup](#recurring-payment-setup)
5. [Split Payments](#split-payments)
6. [Refund Handling](#refund-handling)
7. [PCI DSS Compliance](#pci-dss-compliance)
8. [Webhook Handling](#webhook-handling)
9. [Fee Calculations](#fee-calculations)

## Overview

Payment processing is critical for property management, handling rent collection, security deposits, and other tenant charges. This guide covers integration with payment gateways following PCI DSS standards.

### Payment Methods in PropTech

| Method | Use Case | Processing Time | Fee Structure | Reversibility |
|--------|----------|----------------|---------------|---------------|
| **ACH/eCheck** | Rent payments | 3-5 business days | 0.8% ($5 cap) | Reversible (60 days) |
| **Credit Card** | One-time fees | Immediate | 2.9% + $0.30 | Chargeback (120 days) |
| **Debit Card** | Quick payments | Immediate | 2.9% + $0.30 | Limited chargebacks |
| **Wire Transfer** | Large deposits | Same day | $15-30 flat | Non-reversible |
| **Cash/Check** | Legacy | Manual | No fee | Non-reversible |

## Stripe Integration for Rent Collection

### Setup Stripe Account

```python
import stripe
from datetime import datetime, timedelta

stripe.api_key = "sk_live_..."

class StripePaymentService:
    def __init__(self, api_key):
        stripe.api_key = api_key

    def create_customer(self, tenant):
        """
        Create Stripe customer for tenant
        """
        customer = stripe.Customer.create(
            email=tenant.email,
            name=f"{tenant.first_name} {tenant.last_name}",
            phone=tenant.phone,
            metadata={
                "tenant_id": tenant.id,
                "lease_id": tenant.current_lease_id,
                "property_id": tenant.property_id
            }
        )

        # Save Stripe customer ID to database
        tenant.stripe_customer_id = customer.id
        tenant.save()

        return customer

    def add_payment_method(self, tenant, payment_method_id):
        """
        Attach payment method to customer
        """
        payment_method = stripe.PaymentMethod.attach(
            payment_method_id,
            customer=tenant.stripe_customer_id
        )

        # Set as default payment method
        stripe.Customer.modify(
            tenant.stripe_customer_id,
            invoice_settings={
                "default_payment_method": payment_method_id
            }
        )

        return payment_method

    def charge_rent_payment(self, lease, amount, description="Monthly rent"):
        """
        Process one-time rent payment
        """
        tenant = lease.tenant

        # Create payment intent
        payment_intent = stripe.PaymentIntent.create(
            amount=int(amount * 100),  # Convert to cents
            currency="usd",
            customer=tenant.stripe_customer_id,
            payment_method=tenant.default_payment_method_id,
            off_session=True,  # Customer not present
            confirm=True,
            description=description,
            metadata={
                "lease_id": lease.id,
                "tenant_id": tenant.id,
                "property_id": lease.property_id,
                "payment_type": "rent",
                "period": datetime.now().strftime("%Y-%m")
            },
            statement_descriptor="RENT PAYMENT",  # Appears on bank statement
            receipt_email=tenant.email
        )

        # Save payment record
        self.save_payment_record(
            lease_id=lease.id,
            stripe_payment_intent_id=payment_intent.id,
            amount=amount,
            status=payment_intent.status
        )

        return payment_intent

    def save_payment_record(self, lease_id, stripe_payment_intent_id, amount, status):
        """
        Save payment to database
        """
        from models import Payment

        payment = Payment.create(
            lease_id=lease_id,
            stripe_payment_intent_id=stripe_payment_intent_id,
            amount=amount,
            status=status,
            payment_date=datetime.now()
        )

        return payment
```

### Payment Intent Pattern

```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()

class CreatePaymentIntentRequest(BaseModel):
    lease_id: str
    amount: float
    payment_method_id: str

@app.post("/api/v1/payments/create-intent")
async def create_payment_intent(request: CreatePaymentIntentRequest):
    """
    Create payment intent for tenant portal
    """
    # Get lease and tenant
    lease = db.get_lease(request.lease_id)
    tenant = lease.tenant

    # Create payment intent
    intent = stripe.PaymentIntent.create(
        amount=int(request.amount * 100),
        currency="usd",
        customer=tenant.stripe_customer_id,
        payment_method=request.payment_method_id,
        setup_future_usage="off_session",  # Save for future use
        metadata={
            "lease_id": lease.id,
            "tenant_id": tenant.id
        }
    )

    return {
        "client_secret": intent.client_secret,
        "payment_intent_id": intent.id
    }

@app.post("/api/v1/payments/{payment_intent_id}/confirm")
async def confirm_payment(payment_intent_id: str):
    """
    Confirm payment after 3D Secure authentication
    """
    intent = stripe.PaymentIntent.confirm(payment_intent_id)

    if intent.status == "succeeded":
        # Update database
        update_payment_status(payment_intent_id, "completed")

    return {"status": intent.status}
```

## ACH Payment Processing

### ACH Direct Debit

```python
def setup_ach_payment_method(tenant, bank_account_token):
    """
    Add ACH bank account as payment method
    """
    # Create payment method from bank account token
    payment_method = stripe.PaymentMethod.create(
        type="us_bank_account",
        us_bank_account={
            "account_holder_type": "individual",
            "account_number": bank_account_token  # From Plaid or manual entry
        }
    )

    # Attach to customer
    stripe.PaymentMethod.attach(
        payment_method.id,
        customer=tenant.stripe_customer_id
    )

    # Verify bank account (micro-deposits)
    stripe.Customer.verify_source(
        tenant.stripe_customer_id,
        payment_method.id
    )

    return payment_method

def charge_via_ach(tenant, amount, description="Rent payment"):
    """
    Process ACH payment
    """
    payment_intent = stripe.PaymentIntent.create(
        amount=int(amount * 100),
        currency="usd",
        customer=tenant.stripe_customer_id,
        payment_method_types=["us_bank_account"],
        payment_method=tenant.ach_payment_method_id,
        confirm=True,
        description=description,
        metadata={
            "tenant_id": tenant.id,
            "payment_type": "rent_ach"
        }
    )

    # ACH payments take 5-7 business days to settle
    # Status will be "processing" initially

    return payment_intent
```

### Plaid Integration for Bank Verification

```python
from plaid import Client
from plaid.model.link_token_create_request import LinkTokenCreateRequest
from plaid.model.products import Products
from plaid.model.country_code import CountryCode

class PlaidBankVerification:
    def __init__(self, client_id, secret):
        self.client = Client(
            client_id=client_id,
            secret=secret,
            environment='production'
        )

    def create_link_token(self, user_id):
        """
        Create Plaid Link token for bank connection
        """
        request = LinkTokenCreateRequest(
            user={
                "client_user_id": user_id
            },
            client_name="PropTech Rent Payments",
            products=[Products("auth")],  # Bank account verification
            country_codes=[CountryCode("US")],
            language="en"
        )

        response = self.client.link_token_create(request)
        return response["link_token"]

    def exchange_public_token(self, public_token):
        """
        Exchange public token for access token
        """
        response = self.client.item_public_token_exchange(public_token)

        access_token = response["access_token"]
        item_id = response["item_id"]

        return access_token, item_id

    def get_bank_account_info(self, access_token):
        """
        Get bank account details for ACH setup
        """
        auth_response = self.client.auth_get(access_token)

        accounts = auth_response["accounts"]
        numbers = auth_response["numbers"]

        # Get checking accounts
        checking_accounts = [
            {
                "account_id": acc["account_id"],
                "account_name": acc["name"],
                "account_type": acc["subtype"],
                "routing_number": next(
                    (n["routing"] for n in numbers["ach"] if n["account_id"] == acc["account_id"]),
                    None
                ),
                "account_number": next(
                    (n["account"] for n in numbers["ach"] if n["account_id"] == acc["account_id"]),
                    None
                )
            }
            for acc in accounts if acc["subtype"] == "checking"
        ]

        return checking_accounts

    def create_stripe_bank_account_token(self, routing_number, account_number):
        """
        Create Stripe token from bank account details
        """
        token = stripe.Token.create(
            bank_account={
                "country": "US",
                "currency": "usd",
                "account_holder_name": "John Doe",
                "account_holder_type": "individual",
                "routing_number": routing_number,
                "account_number": account_number
            }
        )

        return token.id
```

## Recurring Payment Setup

### Subscription Model for Rent

```python
def create_rent_subscription(lease, monthly_rent_amount, start_date):
    """
    Set up recurring monthly rent payments
    """
    # Create price
    price = stripe.Price.create(
        unit_amount=int(monthly_rent_amount * 100),
        currency="usd",
        recurring={
            "interval": "month",
            "interval_count": 1
        },
        product_data={
            "name": f"Monthly Rent - {lease.unit.address}",
            "metadata": {
                "lease_id": lease.id
            }
        }
    )

    # Create subscription
    subscription = stripe.Subscription.create(
        customer=lease.tenant.stripe_customer_id,
        items=[{"price": price.id}],
        billing_cycle_anchor=int(start_date.timestamp()),
        collection_method="charge_automatically",
        days_until_due=None,  # Charge immediately
        metadata={
            "lease_id": lease.id,
            "property_id": lease.property_id,
            "unit_id": lease.unit_id
        }
    )

    # Save subscription ID
    lease.stripe_subscription_id = subscription.id
    lease.save()

    return subscription

def add_additional_fee_to_subscription(lease, fee_amount, description):
    """
    Add one-time fee to subscription (e.g., pet fee, parking)
    """
    subscription = stripe.Subscription.retrieve(lease.stripe_subscription_id)

    # Add invoice item
    stripe.InvoiceItem.create(
        customer=lease.tenant.stripe_customer_id,
        amount=int(fee_amount * 100),
        currency="usd",
        description=description,
        subscription=subscription.id
    )

def cancel_subscription_on_move_out(lease):
    """
    Cancel subscription when tenant moves out
    """
    stripe.Subscription.cancel(
        lease.stripe_subscription_id,
        prorate=True  # Prorate final month
    )
```

### Scheduled Payments (Alternative to Subscriptions)

```python
from apscheduler.schedulers.background import BackgroundScheduler

scheduler = BackgroundScheduler()

def schedule_monthly_rent_charge(lease):
    """
    Schedule recurring rent charges using scheduler
    """
    # Schedule for 1st of every month
    scheduler.add_job(
        func=lambda: charge_rent_for_lease(lease.id),
        trigger='cron',
        day=1,  # 1st of month
        hour=6,  # 6 AM
        id=f"rent_charge_{lease.id}",
        replace_existing=True
    )

def charge_rent_for_lease(lease_id):
    """
    Charge rent for specific lease
    """
    lease = db.get_lease(lease_id)

    # Check if lease is active
    if lease.status != "active":
        return

    # Charge rent
    payment_service = StripePaymentService()
    payment_intent = payment_service.charge_rent_payment(
        lease=lease,
        amount=lease.monthly_rent_amount,
        description=f"Rent - {datetime.now().strftime('%B %Y')}"
    )

    # If payment fails, send notification
    if payment_intent.status == "requires_action":
        send_payment_failure_notification(lease.tenant)

scheduler.start()
```

## Split Payments

### Multi-Owner Distribution

```python
def process_rent_with_split_payments(lease, payment_intent_id):
    """
    Split rent payment among multiple property owners
    """
    payment_intent = stripe.PaymentIntent.retrieve(payment_intent_id)

    if payment_intent.status != "succeeded":
        return

    # Get ownership distribution
    property_owners = db.get_property_owners(lease.property_id)

    # Total rent collected
    total_rent = payment_intent.amount / 100  # Convert from cents

    # Distribute to owners
    for owner in property_owners:
        owner_share = total_rent * (owner.ownership_percentage / 100)

        # Create transfer to owner's connected account
        transfer = stripe.Transfer.create(
            amount=int(owner_share * 100),
            currency="usd",
            destination=owner.stripe_connected_account_id,
            transfer_group=f"RENT_{lease.id}_{datetime.now().strftime('%Y%m')}",
            metadata={
                "lease_id": lease.id,
                "owner_id": owner.id,
                "ownership_percentage": owner.ownership_percentage
            }
        )

        # Record distribution
        db.create_owner_distribution(
            owner_id=owner.id,
            lease_id=lease.id,
            amount=owner_share,
            stripe_transfer_id=transfer.id
        )

def setup_owner_connected_account(owner):
    """
    Create Stripe Connect account for property owner
    """
    account = stripe.Account.create(
        type="express",  # Or "standard" for full control
        country="US",
        email=owner.email,
        capabilities={
            "card_payments": {"requested": True},
            "transfers": {"requested": True}
        },
        business_type="individual",
        individual={
            "first_name": owner.first_name,
            "last_name": owner.last_name,
            "email": owner.email,
            "phone": owner.phone
        },
        metadata={
            "owner_id": owner.id
        }
    )

    # Save connected account ID
    owner.stripe_connected_account_id = account.id
    owner.save()

    # Create account link for onboarding
    account_link = stripe.AccountLink.create(
        account=account.id,
        refresh_url="https://proptech.com/owner/connect/refresh",
        return_url="https://proptech.com/owner/connect/complete",
        type="account_onboarding"
    )

    return account_link.url
```

### Roommate Split Payments

```python
def create_split_payment_for_roommates(lease, total_amount, roommate_shares):
    """
    Split rent among roommates

    roommate_shares = [
        {"tenant_id": "tenant_1", "amount": 1200},
        {"tenant_id": "tenant_2", "amount": 1300}
    ]
    """
    payment_results = []

    for share in roommate_shares:
        tenant = db.get_tenant(share["tenant_id"])

        # Create payment intent for each roommate
        payment_intent = stripe.PaymentIntent.create(
            amount=int(share["amount"] * 100),
            currency="usd",
            customer=tenant.stripe_customer_id,
            payment_method=tenant.default_payment_method_id,
            off_session=True,
            confirm=True,
            description=f"Rent Share - {datetime.now().strftime('%B %Y')}",
            metadata={
                "lease_id": lease.id,
                "tenant_id": tenant.id,
                "payment_type": "rent_share",
                "total_rent": total_amount
            }
        )

        payment_results.append({
            "tenant_id": tenant.id,
            "amount": share["amount"],
            "payment_intent_id": payment_intent.id,
            "status": payment_intent.status
        })

    return payment_results
```

## Refund Handling

### Security Deposit Refund

```python
def process_security_deposit_refund(lease, refund_amount, deductions=None):
    """
    Refund security deposit with optional deductions

    deductions = [
        {"description": "Carpet cleaning", "amount": 150},
        {"description": "Wall repair", "amount": 75}
    ]
    """
    # Calculate net refund
    total_deductions = sum(d["amount"] for d in (deductions or []))
    net_refund = refund_amount - total_deductions

    if net_refund <= 0:
        # No refund due to deductions
        return None

    # Get original payment intent
    original_payment = db.get_security_deposit_payment(lease.id)

    # Create refund
    refund = stripe.Refund.create(
        payment_intent=original_payment.stripe_payment_intent_id,
        amount=int(net_refund * 100),
        reason="requested_by_customer",
        metadata={
            "lease_id": lease.id,
            "refund_type": "security_deposit",
            "original_deposit": refund_amount,
            "total_deductions": total_deductions,
            "net_refund": net_refund
        }
    )

    # Record refund and deductions
    db.create_refund_record(
        lease_id=lease.id,
        stripe_refund_id=refund.id,
        refund_amount=net_refund,
        deductions=deductions
    )

    # Send itemized statement to tenant
    send_security_deposit_statement(lease.tenant, refund_amount, deductions, net_refund)

    return refund

def send_security_deposit_statement(tenant, deposit_amount, deductions, net_refund):
    """
    Send itemized security deposit refund statement
    """
    email_body = f"""
    Security Deposit Refund Statement

    Original Deposit: ${deposit_amount:.2f}

    Deductions:
    """

    for deduction in (deductions or []):
        email_body += f"  - {deduction['description']}: ${deduction['amount']:.2f}\n"

    email_body += f"""
    Total Deductions: ${sum(d['amount'] for d in (deductions or [])):.2f}

    Net Refund: ${net_refund:.2f}

    Refund will be processed to your original payment method within 5-10 business days.
    """

    send_email(tenant.email, "Security Deposit Refund", email_body)
```

## PCI DSS Compliance

### Never Store Card Details

```python
# ❌ NEVER DO THIS - Storing card details violates PCI DSS
def save_card_details_WRONG(card_number, cvv, expiry):
    db.execute(
        "INSERT INTO payment_methods (card_number, cvv, expiry) VALUES (?, ?, ?)",
        (card_number, cvv, expiry)
    )

# ✅ CORRECT - Use Stripe tokens/payment methods
def save_payment_method_CORRECT(stripe_payment_method_id):
    """
    Save only Stripe payment method token
    """
    db.execute(
        "INSERT INTO payment_methods (stripe_payment_method_id, last_four, brand) VALUES (?, ?, ?)",
        (stripe_payment_method_id, "4242", "visa")
    )
```

### Stripe Elements (Client-Side)

```javascript
// Frontend: Collect card details securely
const stripe = Stripe('pk_live_...');
const elements = stripe.elements();
const cardElement = elements.create('card');

cardElement.mount('#card-element');

async function handlePayment() {
    // Create payment method
    const {paymentMethod, error} = await stripe.createPaymentMethod({
        type: 'card',
        card: cardElement,
        billing_details: {
            name: 'John Doe',
            email: 'john@example.com'
        }
    });

    if (error) {
        console.error(error);
        return;
    }

    // Send payment method ID to backend (not card details!)
    const response = await fetch('/api/v1/payments/create-intent', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({
            lease_id: 'lease_123',
            amount: 2500,
            payment_method_id: paymentMethod.id  // Only send token
        })
    });

    const {client_secret} = await response.json();

    // Confirm payment with 3D Secure
    const {error: confirmError} = await stripe.confirmCardPayment(client_secret);

    if (confirmError) {
        console.error(confirmError);
    } else {
        console.log('Payment successful!');
    }
}
```

### PCI Compliance Checklist

- [ ] Never log card numbers, CVVs, or full track data
- [ ] Use Stripe.js/Elements for card collection (client-side)
- [ ] Store only Stripe tokens/payment method IDs
- [ ] Implement TLS 1.2+ for all API calls
- [ ] Use strong passwords and 2FA for Stripe dashboard
- [ ] Regularly update dependencies
- [ ] Conduct annual PCI audit (if processing > $1M/year)
- [ ] Implement fraud detection (Stripe Radar)
- [ ] Monitor failed payment attempts

## Webhook Handling

### Stripe Webhook Events

```python
from flask import Flask, request
import stripe

app = Flask(__name__)

@app.route('/webhooks/stripe', methods=['POST'])
def stripe_webhook():
    """
    Handle Stripe webhook events
    """
    payload = request.data
    sig_header = request.headers.get('Stripe-Signature')
    webhook_secret = 'whsec_...'

    try:
        # Verify webhook signature
        event = stripe.Webhook.construct_event(
            payload, sig_header, webhook_secret
        )
    except ValueError:
        return 'Invalid payload', 400
    except stripe.error.SignatureVerificationError:
        return 'Invalid signature', 400

    # Handle event types
    if event['type'] == 'payment_intent.succeeded':
        payment_intent = event['data']['object']
        handle_payment_success(payment_intent)

    elif event['type'] == 'payment_intent.payment_failed':
        payment_intent = event['data']['object']
        handle_payment_failure(payment_intent)

    elif event['type'] == 'charge.refunded':
        charge = event['data']['object']
        handle_refund(charge)

    elif event['type'] == 'invoice.payment_succeeded':
        invoice = event['data']['object']
        handle_subscription_payment(invoice)

    return 'Success', 200

def handle_payment_success(payment_intent):
    """
    Payment succeeded - update database
    """
    lease_id = payment_intent['metadata']['lease_id']

    # Update payment status
    db.execute(
        "UPDATE payments SET status = 'completed', completed_at = NOW() WHERE stripe_payment_intent_id = ?",
        (payment_intent['id'],)
    )

    # Send receipt to tenant
    lease = db.get_lease(lease_id)
    send_payment_receipt(lease.tenant, payment_intent)

def handle_payment_failure(payment_intent):
    """
    Payment failed - notify tenant and property manager
    """
    lease_id = payment_intent['metadata']['lease_id']
    error_message = payment_intent.get('last_payment_error', {}).get('message', 'Payment failed')

    # Update payment status
    db.execute(
        "UPDATE payments SET status = 'failed', error_message = ? WHERE stripe_payment_intent_id = ?",
        (error_message, payment_intent['id'])
    )

    # Notify tenant
    lease = db.get_lease(lease_id)
    send_payment_failure_notification(lease.tenant, error_message)

    # Notify property manager
    send_admin_notification(f"Payment failed for lease {lease_id}: {error_message}")
```

## Fee Calculations

### Transaction Fee Structure

```python
class FeeCalculator:
    # Stripe fees (as of 2025)
    CREDIT_CARD_PERCENTAGE = 0.029  # 2.9%
    CREDIT_CARD_FIXED = 0.30
    ACH_PERCENTAGE = 0.008  # 0.8%
    ACH_CAP = 5.00

    def calculate_credit_card_fee(self, amount):
        """
        Calculate credit card processing fee
        """
        fee = (amount * self.CREDIT_CARD_PERCENTAGE) + self.CREDIT_CARD_FIXED
        return round(fee, 2)

    def calculate_ach_fee(self, amount):
        """
        Calculate ACH processing fee
        """
        fee = amount * self.ACH_PERCENTAGE
        return min(round(fee, 2), self.ACH_CAP)

    def calculate_total_with_fee(self, amount, payment_method):
        """
        Calculate total amount including processing fee
        """
        if payment_method == "credit_card":
            fee = self.calculate_credit_card_fee(amount)
        elif payment_method == "ach":
            fee = self.calculate_ach_fee(amount)
        else:
            fee = 0

        return {
            "base_amount": amount,
            "processing_fee": fee,
            "total_amount": amount + fee
        }

# Usage
calculator = FeeCalculator()

# Rent payment of $2,500
rent_payment = calculator.calculate_total_with_fee(2500, "credit_card")
# {
#   "base_amount": 2500,
#   "processing_fee": 72.80,  # (2500 * 0.029) + 0.30
#   "total_amount": 2572.80
# }

ach_payment = calculator.calculate_total_with_fee(2500, "ach")
# {
#   "base_amount": 2500,
#   "processing_fee": 5.00,  # Capped at $5
#   "total_amount": 2505.00
# }
```

### Convenience Fee Disclosure

```python
@app.post("/api/v1/payments/quote")
async def get_payment_quote(amount: float, payment_method: str):
    """
    Provide payment quote with fee disclosure
    """
    calculator = FeeCalculator()
    quote = calculator.calculate_total_with_fee(amount, payment_method)

    return {
        "amount": quote["base_amount"],
        "processing_fee": quote["processing_fee"],
        "total_amount": quote["total_amount"],
        "payment_method": payment_method,
        "fee_disclosure": f"A processing fee of ${quote['processing_fee']:.2f} will be added to this transaction."
    }
```

---

## References

1. **Stripe API Documentation**: https://stripe.com/docs/api
2. **Stripe Connect**: https://stripe.com/docs/connect
3. **PCI DSS Compliance**: https://www.pcisecuritystandards.org/
4. **Plaid API**: https://plaid.com/docs/
5. **ACH Network Rules**: https://www.nacha.org/

---

*This document is maintained by the PropTech Payments Standards Committee. For questions or updates, contact payments@proptech.com.*
