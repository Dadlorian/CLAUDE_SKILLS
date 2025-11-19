# Test Metrics and KPIs Guide

## Test Execution Metrics

**Test Pass Rate**: (Passed Tests / Total Tests) × 100
- Target: 95-100%
- Warning: < 90%
- Critical: < 80%

**Test Execution Time**: Total time to run all tests
- Unit Tests: < 5 minutes
- Integration Tests: < 15 minutes
- E2E Tests: < 30 minutes
- Full Suite: < 60 minutes

**Flaky Test Rate**: (Flaky Tests / Total Tests) × 100
- Target: < 5%
- Warning: 5-10%
- Critical: > 10%

**Test Coverage**: (Covered Lines / Total Lines) × 100
- Line Coverage: ≥ 80%
- Branch Coverage: ≥ 75%
- Function Coverage: ≥ 85%

## Defect Metrics

**Defect Density**: Defects / KLOC (thousand lines of code)
- Excellent: < 1
- Good: 1-3
- Average: 3-5
- Poor: > 5

**Defect Escape Rate**: (Production Defects / Total Defects) × 100
- Target: < 5%
- Warning: 5-10%
- Critical: > 10%

**Mean Time to Detect (MTTD)**: Average time from introduction to detection
- Target: < 7 days
- Warning: 7-30 days
- Critical: > 30 days

**Mean Time to Resolve (MTTR)**: Average time from detection to resolution
- Critical: < 4 hours
- High: < 2 days
- Medium: < 1 week
- Low: < 1 month

## Quality Indicators

**Bug Age Distribution**:
- 0-7 days: 60%+ (healthy)
- 8-30 days: 30%
- 31-90 days: < 8%
- 90+ days: < 2%

**Reopen Rate**: (Reopened Bugs / Fixed Bugs) × 100
- Target: < 10%
- Warning: 10-20%
- Critical: > 20%

**Test-to-Code Ratio**: (Lines of Test Code / Lines of Production Code)
- Unit Tests: 1:1 to 2:1
- Total Tests: 1.5:1 to 3:1

## DORA Metrics

**Deployment Frequency**: How often deployments occur
- Elite: Multiple per day
- High: Weekly to Monthly
- Medium: Monthly to Bi-annually
- Low: < Bi-annually

**Lead Time for Changes**: Time from commit to production
- Elite: < 1 hour
- High: 1 day to 1 week
- Medium: 1 week to 1 month
- Low: > 1 month

**Change Failure Rate**: % of deployments causing failure
- Elite: 0-15%
- High: 16-30%
- Medium: 31-45%
- Low: > 45%

**Time to Restore Service**: Time to recover from failure
- Elite: < 1 hour
- High: < 1 day
- Medium: 1 day to 1 week
- Low: > 1 week
