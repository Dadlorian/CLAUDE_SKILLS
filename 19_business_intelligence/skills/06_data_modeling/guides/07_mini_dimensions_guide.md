# Mini-Dimensions Implementation Guide

## Purpose
Separate rapidly changing attributes from main dimension to avoid SCD Type 2 dimension explosion.

## Problem: Dimension Explosion
Customer with demographics changing monthly:
- Age updates yearly
- Credit score updates monthly  
- Income band changes occasionally

Result: 12+ new dimension rows per customer per year!

## Solution: Mini-Dimension

### Structure
```sql
DIM_CUSTOMER (stable, Type 2 if needed)
- customer_key (durable)
- customer_id
- customer_name
- birth_date
- signup_date

DIM_CUSTOMER_DEMOGRAPHICS (mini-dimension)
- demographics_key (PK)
- age_range (not exact age)
- income_band
- credit_score_band
- customer_segment

FACT_SALES
- customer_key (stable reference)
- demographics_key (demographics at time of sale)
```

## Implementation Steps

1. **Identify Rapidly Changing Attributes**
   - Updates frequently (daily, weekly, monthly)
   - Large dimension would explode with Type 2

2. **Create Banded Attributes**
   - Age → Age ranges (18-24, 25-34, 35-44)
   - Credit score → Bands (Poor, Fair, Good, Excellent)
   - Income → Bands (Low, Medium, High, Very High)

3. **Pre-Generate Combinations**
   ```sql
   -- All age × income × credit combinations
   INSERT INTO DIM_CUSTOMER_DEMOGRAPHICS
   SELECT 
     ROW_NUMBER() OVER (ORDER BY age, income, credit),
     age_range, income_band, credit_score_band,
     CASE -- derive segment from bands
       WHEN income='High' AND credit='Excellent' THEN 'Platinum'
       WHEN income IN ('High','Medium') THEN 'Gold'
       ELSE 'Silver'
     END as segment
   FROM ref_age_ranges
   CROSS JOIN ref_income_bands  
   CROSS JOIN ref_credit_bands;
   ```

4. **Load Facts with Both Keys**
   ```sql
   INSERT INTO FACT_SALES
   SELECT
     c.customer_key, -- stable
     d.demographics_key, -- current demographics
     s.amount
   FROM staging.sales s
   JOIN DIM_CUSTOMER c ON s.customer_id = c.customer_id
   JOIN DIM_CUSTOMER_DEMOGRAPHICS d ON
     s.age_range = d.age_range AND
     s.income_band = d.income_band;
   ```

## Benefits
- Prevents dimension explosion
- Maintains historical demographic accuracy
- Stable customer key for long-term tracking
- Pre-generated combinations support fast lookup

## Best Practices
- Use ranges/bands, not exact values
- Pre-generate all combinations (typically < 1000 rows)
- Include derived segmentation
- Document banding rules clearly

