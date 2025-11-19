# Periodic Snapshot Fact Tables Guide

## Purpose
Capture state at regular time intervals.

## Characteristics
- One row per entity per period
- Regular intervals (daily, weekly, monthly)
- Dense (rows for all periods)
- Semi-additive measures (balances, levels)
- Predictable row growth

## Examples
- Daily account balances
- Weekly inventory levels
- Monthly sales summaries
- End-of-day positions

## Design

### Grain Declaration
"One row per [entity] per [time period]"

Example: "One row per account per day"

### Structure
```sql
FACT_ACCOUNT_BALANCE_DAILY
- balance_key (PK)
- date_key
- account_key
- customer_key
- branch_key
-- Balances (semi-additive)
- beginning_balance
- ending_balance
- average_daily_balance
- minimum_balance
- maximum_balance
-- Activity (additive)
- transaction_count
- deposit_count
- withdrawal_count
- total_deposits
- total_withdrawals
```

## Semi-Additive Facts

**Problem**: Balances cannot be summed across time
```sql
-- WRONG: Don't sum balances across dates
SELECT SUM(ending_balance)
FROM FACT_ACCOUNT_BALANCE_DAILY;
-- This counts the same money multiple times!
```

**Correct Usage**:
```sql
-- Sum across accounts for one day
SELECT date, SUM(ending_balance) as total_balance
FROM FACT_ACCOUNT_BALANCE_DAILY
WHERE date_key = 20240615
GROUP BY date;

-- Average balance over time for one account
SELECT account_number, AVG(ending_balance) as avg_balance
FROM FACT_ACCOUNT_BALANCE_DAILY f
JOIN DIM_ACCOUNT a ON f.account_key = a.account_key
WHERE a.account_number = 'ACC123'
  AND date_key BETWEEN 20240601 AND 20240630
GROUP BY account_number;
```

## Loading Pattern

Daily snapshot:
```sql
-- Truncate and reload for the day (idempotent)
DELETE FROM FACT_ACCOUNT_BALANCE_DAILY
WHERE date_key = 20240615;

INSERT INTO FACT_ACCOUNT_BALANCE_DAILY
SELECT 
  balance_key_seq.NEXTVAL,
  20240615,
  a.account_key,
  c.customer_key,
  b.branch_key,
  snapshot.beginning_balance,
  snapshot.ending_balance,
  snapshot.average_balance,
  snapshot.transaction_count
FROM source.daily_account_snapshot snapshot
JOIN DIM_ACCOUNT a ON snapshot.account_id = a.account_id
JOIN DIM_CUSTOMER c ON a.customer_key = c.customer_key
JOIN DIM_BRANCH b ON a.branch_key = b.branch_key;
```

## Use Cases
- Account balances (banking)
- Inventory levels (retail, manufacturing)
- Headcount (HR)
- Capacity utilization
- Key performance indicators (KPIs)

## Best Practices
- Regular, predictable intervals
- Document semi-additive nature
- Include both snapshot and activity facts
- Provide example queries for users
- Consider creating views for last value

