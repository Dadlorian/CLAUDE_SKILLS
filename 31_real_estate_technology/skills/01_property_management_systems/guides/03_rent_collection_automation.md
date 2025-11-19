# Rent Collection Automation Guide

## Overview
Automate rent collection to improve cash flow, reduce delinquency, and minimize administrative overhead.

## Setup Autopay

### Enable Autopay for Existing Tenants

**Step 1: Configure Autopay Settings**
```
Settings → Rent Collection → Autopay
- Enable autopay: Yes
- Default charge date: 1st of month
- Retry failed payments: Yes (Days 3, 5, 7)
- Send confirmation emails: Yes
```

**Step 2: Invite Tenants to Enroll**
```
Tenants → Select All → Actions → Send Autopay Invitation
```

**Email Template**:
```
Subject: Never Miss Rent Day - Set Up Autopay!

Hi [Tenant Name],

Make rent day easier! Set up autopay and never worry about late fees again.

Benefits:
✓ Automatic payment on the 1st
✓ No checks or money orders needed
✓ Cancel anytime
✓ Email confirmation each month

Set up now: [Portal Link]

Questions? Call us at (555) 123-4567.
```

**Adoption Targets**:
- Month 1: 30-40%
- Month 3: 50-60%
- Month 6: 70-80%

### Autopay Implementation Code

```javascript
async function enrollInAutopay(leaseId, paymentMethodId) {
  try {
    // Create autopay subscription
    const autopay = await db.autopay.create({
      lease_id: leaseId,
      payment_method_id: paymentMethodId,
      charge_day: 1, // 1st of month
      amount_type: 'full_balance', // or 'fixed_amount'
      status: 'active',
      enrolled_date: new Date()
    });

    // Update lease record
    await db.leases.update({
      where: { id: leaseId },
      data: { autopay_enabled: true }
    });

    // Send confirmation
    await sendEmail(lease.tenant.email, {
      template: 'autopay_confirmation',
      data: {
        charge_day: 1,
        amount: lease.total_monthly_rent
      }
    });

    return { success: true, autopay_id: autopay.id };
  } catch (error) {
    console.error('Autopay enrollment failed:', error);
    return { success: false, error: error.message };
  }
}
```

## Automated Payment Processing

### Daily Processing Schedule

**6:00 AM** - Process autopay charges
```javascript
// Cron job: 0 6 * * *
async function processAutopayCharges() {
  const today = new Date().getDate();

  // Find all autopay subscriptions due today
  const dueAutopays = await db.autopay.findMany({
    where: {
      status: 'active',
      charge_day: today
    },
    include: {
      lease: {
        include: { tenant: true, unit: true }
      },
      payment_method: true
    }
  });

  console.log(`Processing ${dueAutopays.length} autopay charges`);

  for (const autopay of dueAutopays) {
    try {
      // Get amount due
      const balance = await getLeaseBalance(autopay.lease_id);
      const amountToCharge = autopay.amount_type === 'full_balance'
        ? balance
        : autopay.fixed_amount;

      if (amountToCharge <= 0) {
        console.log(`No balance due for lease ${autopay.lease_id}`);
        continue;
      }

      // Process payment
      const payment = await processPayment({
        lease_id: autopay.lease_id,
        amount: amountToCharge,
        payment_method_id: autopay.payment_method_id,
        source: 'autopay'
      });

      // Log success
      await db.autopay_history.create({
        autopay_id: autopay.id,
        payment_id: payment.id,
        amount: amountToCharge,
        status: 'success',
        processed_at: new Date()
      });

      // Send confirmation
      await sendEmail(autopay.lease.tenant.email, {
        template: 'autopay_success',
        data: {
          amount: amountToCharge,
          last4: autopay.payment_method.last4,
          new_balance: balance - amountToCharge
        }
      });
    } catch (error) {
      console.error(`Autopay failed for lease ${autopay.lease_id}:`, error);

      // Log failure
      await db.autopay_history.create({
        autopay_id: autopay.id,
        amount: amountToCharge,
        status: 'failed',
        error_message: error.message,
        processed_at: new Date()
      });

      // Notify tenant
      await sendEmail(autopay.lease.tenant.email, {
        template: 'autopay_failed',
        data: {
          amount: amountToCharge,
          error: error.message,
          portal_url: `https://portal.example.com/payments`
        }
      });

      // Schedule retry if applicable
      if (shouldRetry(error)) {
        await scheduleRetry(autopay.id, 3); // Retry in 3 days
      }
    }
  }
}
```

**8:00 AM** - Send rent reminders (non-autopay tenants)
```javascript
async function sendRentReminders() {
  const today = new Date();
  const dueDate = today.getDate();

  // Different reminders based on date
  if (dueDate === 28) {
    // 3 days before due date (for month-end)
    await sendReminders('upcoming');
  } else if (dueDate === 1) {
    // Due date
    await sendReminders('due_today');
  } else if (dueDate === 6) {
    // After grace period
    await sendReminders('overdue');
  }
}

async function sendReminders(reminderType) {
  const leases = await db.leases.findMany({
    where: {
      lease_status: 'active',
      autopay_enabled: false
    },
    include: {
      tenant: true,
      unit: true,
      ledger: true
    }
  });

  for (const lease of leases) {
    const balance = calculateBalance(lease.ledger);

    if (balance > 0) {
      const template = {
        'upcoming': 'rent_reminder_upcoming',
        'due_today': 'rent_reminder_due',
        'overdue': 'rent_reminder_overdue'
      }[reminderType];

      await sendEmail(lease.tenant.email, {
        template: template,
        data: {
          tenant_name: lease.tenant.first_name,
          amount_due: balance,
          due_date: 'December 1, 2024',
          portal_url: `https://portal.example.com/pay`
        }
      });

      // Also send SMS for overdue
      if (reminderType === 'overdue') {
        await sendSMS(lease.tenant.phone,
          `Rent of $${balance} is past due. Pay now at portal.example.com/pay`
        );
      }
    }
  }
}
```

## Late Fee Automation

### Automatic Late Fee Application

```javascript
// Run daily at 9:00 AM
async function applyLateFees() {
  const today = new Date();
  const gracePeriodEnd = 5; // 5th of month

  if (today.getDate() !== gracePeriodEnd + 1) {
    return; // Only run on day after grace period
  }

  const overdueLeases = await db.leases.findMany({
    where: {
      lease_status: 'active'
    },
    include: {
      tenant: true,
      unit: true,
      ledger: true,
      property: true
    }
  });

  for (const lease of overdueLeases) {
    const balance = calculateBalance(lease.ledger);

    // Check if rent is unpaid
    const currentMonthRent = lease.ledger.find(
      entry => entry.charge_code === 'RENT' &&
               entry.transaction_date >= startOfMonth(today)
    );

    if (balance > 0 && currentMonthRent) {
      // Calculate late fee
      const lateFeePolicy = lease.property.late_fee_policy;
      let lateFee;

      if (lateFeePolicy.type === 'flat') {
        lateFee = lateFeePolicy.amount;
      } else if (lateFeePolicy.type === 'percentage') {
        lateFee = lease.base_rent * (lateFeePolicy.percentage / 100);
      } else {
        lateFee = Math.max(
          lateFeePolicy.flat_amount,
          lease.base_rent * (lateFeePolicy.percentage / 100)
        );
      }

      // Post late fee
      await db.ledger.create({
        lease_id: lease.id,
        transaction_date: today,
        transaction_type: 'charge',
        charge_code: 'LATE',
        amount: lateFee,
        description: `Late fee for ${monthName(today)} rent`,
        auto_generated: true
      });

      console.log(`Applied $${lateFee} late fee to lease ${lease.id}`);

      // Notify tenant
      await sendEmail(lease.tenant.email, {
        template: 'late_fee_applied',
        data: {
          late_fee: lateFee,
          total_due: balance + lateFee,
          portal_url: `https://portal.example.com/pay`
        }
      });
    }
  }
}
```

## Payment Reconciliation

### Daily Bank Reconciliation

```javascript
async function reconcilePayments() {
  // Get yesterday's payments from Stripe
  const yesterday = new Date();
  yesterday.setDate(yesterday.getDate() - 1);

  const stripePayments = await stripe.charges.list({
    created: {
      gte: Math.floor(yesterday.getTime() / 1000),
      lt: Math.floor(new Date().getTime() / 1000)
    },
    limit: 100
  });

  // Get payments in our database
  const dbPayments = await db.ledger.findMany({
    where: {
      transaction_date: yesterday,
      transaction_type: 'payment'
    }
  });

  // Reconcile
  const mismatches = [];

  for (const stripePayment of stripePayments.data) {
    const dbPayment = dbPayments.find(
      p => p.external_transaction_id === stripePayment.id
    );

    if (!dbPayment) {
      mismatches.push({
        type: 'missing_in_db',
        stripe_id: stripePayment.id,
        amount: stripePayment.amount / 100
      });
    } else if (dbPayment.amount !== -(stripePayment.amount / 100)) {
      mismatches.push({
        type: 'amount_mismatch',
        stripe_id: stripePayment.id,
        stripe_amount: stripePayment.amount / 100,
        db_amount: -dbPayment.amount
      });
    }
  }

  if (mismatches.length > 0) {
    console.error('Payment reconciliation issues:', mismatches);
    await alertAdmin('Payment Reconciliation Failed', mismatches);
  } else {
    console.log('✓ All payments reconciled successfully');
  }
}
```

## Best Practices

### 1. Incentivize Autopay
- $25-$50 discount for autopay enrollment
- Waive first late fee for autopay users
- Highlight convenience in communications

### 2. Multiple Payment Options
- ACH (free for tenant)
- Credit/debit card (with fee disclosure)
- Check (at office)
- Money order

### 3. Clear Communication
- Transparent fee structure
- Advance notice of due dates
- Immediate payment confirmations

### 4. Flexible Policies
- Payment plans for hardship cases
- Grace period (3-5 days)
- Clear escalation timeline

### 5. Monitor Metrics
- Collection rate (target: >98%)
- Autopay adoption (target: >75%)
- Average days to collect (target: <5 days)
- Delinquency rate (target: <2%)

Automated rent collection improves cash flow predictability and reduces administrative burden while maintaining positive tenant relationships.
