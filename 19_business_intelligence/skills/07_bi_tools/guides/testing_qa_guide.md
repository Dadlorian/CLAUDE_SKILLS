# Testing & QA Guide for BI

## Testing Types

### 1. Unit Testing (Individual Components)
**What**: Test single calculations, filters, parameters
**When**: During development
**Who**: Developer

### 2. Integration Testing (Connected Components)
**What**: Test data sources, dashboard actions, drilldowns
**When**: After component integration
**Who**: Developer + QA

### 3. User Acceptance Testing (End-to-End)
**What**: Business users validate functionality
**When**: Before production deployment
**Who**: Business users + QA

### 4. Performance Testing
**What**: Load time, concurrency, scalability
**When**: Before production, quarterly
**Who**: Performance team

## Test Plan Template

```markdown
# Test Plan: Sales Dashboard

## Scope
- Dashboard: Executive Sales Overview
- Environment: QA
- Test Period: Nov 20-22, 2024
- Testers: John Doe, Jane Smith

## Test Cases

### TC001: Revenue Calculation
**Objective**: Verify revenue totals are accurate
**Steps**:
1. Open dashboard
2. Select date: Nov 1-30, 2024
3. Note revenue value
4. Compare to source system
**Expected**: Values match within $100
**Actual**: [To be filled]
**Status**: [Pass/Fail]

### TC002: Regional Filter
**Objective**: Filter works correctly
**Steps**:
1. Select "West" region filter
2. Verify all charts update
3. Check detail table shows only West
**Expected**: Only West data displayed
**Actual**: [To be filled]
**Status**: [Pass/Fail]
```

## Automated Testing

### Data Validation Tests
```sql
-- Test: Daily sales total matches source
SELECT
    source.total_sales,
    dashboard.total_sales,
    ABS(source.total_sales - dashboard.total_sales) as variance
FROM (
    SELECT SUM(amount) as total_sales
    FROM source_system.sales
    WHERE sale_date = '2024-11-15'
) source
CROSS JOIN (
    SELECT SUM(amount) as total_sales
    FROM warehouse.sales
    WHERE sale_date = '2024-11-15'
) dashboard
WHERE ABS(source.total_sales - dashboard.total_sales) > 100;
-- Should return 0 rows if passing
```

### Calculation Tests (dbt example)
```sql
-- models/schema.yml
version: 2

models:
  - name: sales_metrics
    columns:
      - name: revenue
        tests:
          - not_null
          - positive_value
      - name: profit_margin
        tests:
          - accepted_range:
              min_value: 0
              max_value: 1
```

## Performance Testing

### Load Testing
```python
# Simulate concurrent users
import requests
import concurrent.futures

def load_dashboard(user_id):
    response = requests.get(
        f"{dashboard_url}?user={user_id}",
        headers={'Authorization': f'Bearer {token}'}
    )
    return response.elapsed.total_seconds()

# Test with 50 concurrent users
with concurrent.futures.ThreadPoolExecutor(max_workers=50) as executor:
    results = list(executor.map(load_dashboard, range(50)))

print(f"Average load time: {sum(results)/len(results):.2f}s")
print(f"Max load time: {max(results):.2f}s")
```

## QA Checklist

### Data Accuracy
- [ ] Calculations match documentation
- [ ] Totals reconcile with source
- [ ] Filters apply correctly
- [ ] Date logic works (YTD, MTD, etc.)
- [ ] Null values handled
- [ ] Edge cases tested (zero, negative, extreme values)

### Functionality
- [ ] All filters work
- [ ] Dashboard actions function
- [ ] Drill-downs navigate correctly
- [ ] Parameters update visuals
- [ ] Exports work (PDF, Excel, CSV)
- [ ] Subscriptions deliver
- [ ] Alerts trigger correctly

### User Experience
- [ ] Clear titles and labels
- [ ] Helpful tooltips
- [ ] Intuitive navigation
- [ ] Consistent formatting
- [ ] Readable on target devices
- [ ] Accessible (WCAG AA)

### Performance
- [ ] Loads < 5 seconds
- [ ] Smooth interactions
- [ ] No timeout errors
- [ ] Handles expected concurrency
- [ ] Memory usage acceptable

### Security
- [ ] RLS working correctly
- [ ] Users see only their data
- [ ] Sensitive data masked
- [ ] External sharing blocked (if required)
- [ ] Audit logging active

## Regression Testing

### When to Run
- Before production deployment
- After platform upgrade
- Monthly (for critical dashboards)

### Automated Regression Suite
```python
# pytest example
def test_revenue_calculation():
    expected = get_from_source_system('2024-11-15')
    actual = get_from_dashboard('2024-11-15')
    assert abs(expected - actual) < 100, f"Revenue mismatch: {expected} vs {actual}"

def test_dashboard_loads():
    start = time.time()
    response = load_dashboard()
    load_time = time.time() - start
    assert load_time < 5, f"Dashboard too slow: {load_time}s"
    assert response.status_code == 200
```

## Bug Tracking

### Bug Report Template
```markdown
**Title**: Revenue filter not working on mobile

**Severity**: High
**Priority**: P1
**Environment**: Production
**Reporter**: Jane Smith
**Date**: 2024-11-15

**Steps to Reproduce**:
1. Open dashboard on iPhone
2. Apply revenue filter
3. Observe chart doesn't update

**Expected**: Chart filters to selected range
**Actual**: No change in chart

**Screenshots**: [Attach]
**Impact**: Mobile users cannot filter data
```

## Resources
- dbt Testing: https://docs.getdbt.com/docs/build/tests
- Selenium (web automation): https://www.selenium.dev/
- pytest: https://docs.pytest.org/
