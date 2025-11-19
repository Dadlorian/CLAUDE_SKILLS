# Stripe Integration Guide

Complete guide to integrating Stripe payment processor for production payments.

## Client-Side Integration

```javascript
const stripe = Stripe('pk_live_...');
const elements = stripe.elements();
const cardElement = elements.create('card');
cardElement.mount('#card-element');

document.getElementById('payment-form').addEventListener('submit', async (e) => {
  e.preventDefault();

  const {token} = await stripe.createToken(cardElement);

  const response = await fetch('/charge', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({token: token.id, amount: 2000})
  });

  const result = await response.json();
  if (result.success) {
    console.log('Payment successful');
  }
});
```

## Server-Side Integration

```python
import stripe
stripe.api_key = "sk_live_..."

def charge_card(token, amount_cents):
    try:
        charge = stripe.Charge.create(
            amount=amount_cents,
            currency="usd",
            source=token,
            description="Example charge"
        )
        return {'success': True, 'id': charge.id}
    except stripe.error.CardError as e:
        return {'success': False, 'error': str(e)}
```

## Key Features
- PCI-compliant tokenization
- Recurring billing support
- 3D Secure integration
- Detailed webhook events
- Multi-currency support
- Global processor coverage
- Excellent success rates (96%+)

## Cost Structure
- US Card-present: 2.7% + $0.05
- US Card-not-present: 2.9% + $0.30
- International: 3.9% + $0.30
- Monthly fee: None (transaction-based only)

## Best For
- Startups and SMBs
- US-focused merchants
- High success rate priority
- Recurring billing needs
