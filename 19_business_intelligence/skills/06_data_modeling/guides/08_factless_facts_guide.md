# Factless Fact Tables Implementation Guide

## Purpose
Track events or conditions without numeric measurements.

## Two Types

### Type 1: Event Tracking
Records that an event occurred.

**Example: Student Attendance**
```sql
FACT_ATTENDANCE
- attendance_key (PK)
- date_key
- student_key
- course_key
- classroom_key
- instructor_key
-- No numeric facts!
```

**Queries**:
```sql
-- Days attended
SELECT COUNT(*)
FROM FACT_ATTENDANCE
WHERE student_key = 123;

-- Attendance rate
SELECT 
  s.student_name,
  COUNT(*) * 100.0 / (SELECT COUNT(DISTINCT date_key) FROM FACT_ATTENDANCE) as pct
FROM FACT_ATTENDANCE f
JOIN DIM_STUDENT s ON f.student_key = s.student_key
GROUP BY s.student_name;
```

### Type 2: Coverage/Eligibility
Records conditions or what could have happened.

**Example: Promotion Coverage**
```sql
FACT_PROMOTION_COVERAGE
- coverage_key (PK)
- promotion_key
- product_key
- store_key
- start_date_key
- end_date_key
```

**Queries**:
```sql
-- Products on promotion but no sales
SELECT p.product_name, prom.promotion_name
FROM FACT_PROMOTION_COVERAGE cov
JOIN DIM_PRODUCT p ON cov.product_key = p.product_key
JOIN DIM_PROMOTION prom ON cov.promotion_key = prom.promotion_key
WHERE NOT EXISTS (
  SELECT 1 FROM FACT_SALES s
  WHERE s.product_key = cov.product_key
    AND s.promotion_key = cov.promotion_key
    AND s.date_key BETWEEN cov.start_date_key AND cov.end_date_key
);
```

## Implementation

1. **Identify Event or Condition**
   - What occurrence to track?
   - No numeric measurements

2. **Define Grain**
   - One row per event occurrence
   - Or one row per condition instance

3. **Identify Dimensions**
   - All contextual who/what/where/when

4. **Optional: Add Dummy Fact**
   ```sql
   event_count INTEGER DEFAULT 1
   ```
   Makes some BI tools happier

## When to Use
- Tracking event occurrence (not measurements)
- Eligibility or conditions
- Promotion coverage
- Attendance/participation
- Qualifications/certifications

## Best Practices
- Clear grain declaration
- May include dummy fact (1) for counting
- Consider time effectivity for coverage
- Document query patterns for users

