# Flaky Test Remediation Template

Use this template to systematically identify, analyze, and fix flaky tests in your test suite.

---

## What Are Flaky Tests?

**Definition**: Tests that pass or fail non-deterministically with the same code, producing inconsistent results.

**Impact**:
- Erodes trust in test suite
- Slows down development (re-running tests)
- Masks real bugs
- Wastes engineering time debugging
- Blocks CI/CD pipelines

**Target**: <5% flaky test rate (industry best practice from Google, Microsoft)

---

## Current Flaky Test Assessment

### Flakiness Metrics

**Overall Statistics**:
- Total tests: _____
- Flaky tests: _____
- Flaky test rate: _____%
- Tests quarantined: _____
- Average re-runs per test: _____

**Flakiness by Category**:
| Category | Total Tests | Flaky | Flaky % |
|----------|-------------|-------|---------|
| Unit | _____ | _____ | _____% |
| Integration | _____ | _____ | _____% |
| E2E | _____ | _____ | _____% |
| API | _____ | _____ | _____% |

**Top Flaky Tests**:
1. Test name: _____ | Flaky rate: _____%
2. Test name: _____ | Flaky rate: _____%
3. Test name: _____ | Flaky rate: _____%
4. Test name: _____ | Flaky rate: _____%
5. Test name: _____ | Flaky rate: _____%

---

## Common Causes of Flakiness

### 1. Timing Issues (Most Common - ~60%)

**Cause**: Tests depend on timing/delays instead of explicit waits

**Anti-patterns**:
```typescript
// ❌ BAD - Fixed delay (arbitrary wait)
await page.waitForTimeout(5000);
await sleep(3000);

// ❌ BAD - Implicit wait (global timeout)
await browser.implicitlyWait(10000);
```

**Solutions**:
```typescript
// ✅ GOOD - Explicit wait for condition
await page.waitForSelector('[data-testid="result"]', {
  state: 'visible',
  timeout: 10000
});

// ✅ GOOD - Wait for network idle
await page.goto(url, { waitUntil: 'networkidle' });

// ✅ GOOD - Wait for specific response
await page.waitForResponse(resp =>
  resp.url().includes('/api/data') && resp.status() === 200
);

// ✅ GOOD - Wait for element state
await expect(page.locator('.result')).toBeVisible();
await expect(page.locator('.result')).toHaveText('Success');

// ✅ GOOD - Custom wait with retry
async function waitForCondition(condition, timeout = 10000) {
  const startTime = Date.now();
  while (Date.now() - startTime < timeout) {
    if (await condition()) return true;
    await sleep(100);
  }
  throw new Error('Condition not met within timeout');
}
```

### 2. Shared State / Test Dependencies (~20%)

**Cause**: Tests share data or depend on execution order

**Anti-patterns**:
```typescript
// ❌ BAD - Shared global state
let testUser = { email: 'test@example.com' };

test('create user', async () => {
  testUser = await createUser(testUser);
});

test('login user', async () => {
  // Depends on previous test!
  await login(testUser.email);
});

// ❌ BAD - Shared database records
test('update user', async () => {
  await db.users.update({ id: 1 }, { name: 'Updated' });
});

test('verify user', async () => {
  const user = await db.users.findOne({ id: 1 });
  // Might find updated user from previous test!
});
```

**Solutions**:
```typescript
// ✅ GOOD - Isolated test data
test('create and login user', async () => {
  // Each test creates its own data
  const uniqueEmail = `user-${Date.now()}-${Math.random()}@example.com`;
  const testUser = await createUser({ email: uniqueEmail });
  await login(testUser.email);
});

// ✅ GOOD - Cleanup between tests
beforeEach(async () => {
  // Fresh state for each test
  await db.clean(['users', 'orders']);
  testUser = await UserFactory.create();
});

afterEach(async () => {
  // Cleanup after test
  await db.deleteUser(testUser.id);
});

// ✅ GOOD - Test isolation with unique IDs
test('user workflow', async () => {
  const testId = `test-${uuid()}`;
  const user = await createUser({
    email: `${testId}@example.com`
  });
  // This user is unique to this test
});
```

### 3. External Dependencies (~10%)

**Cause**: Tests depend on external services (APIs, databases, network)

**Anti-patterns**:
```typescript
// ❌ BAD - Real external API call
test('fetch user data', async () => {
  const response = await fetch('https://real-api.com/users/1');
  // Flaky if API is down or slow!
});

// ❌ BAD - Shared test database
test('create order', async () => {
  await db.orders.create({ userId: 1, amount: 100 });
  // Flaky if database is slow or other tests interfere
});
```

**Solutions**:
```typescript
// ✅ GOOD - Mock external dependencies
beforeEach(async () => {
  await page.route('**/api/external/**', route => {
    route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({ id: 1, name: 'Test User' })
    });
  });
});

// ✅ GOOD - Use test doubles
test('process payment', async () => {
  const mockPaymentGateway = {
    charge: jest.fn().mockResolvedValue({ success: true })
  };
  const result = await processPayment(100, mockPaymentGateway);
  expect(result.success).toBe(true);
});

// ✅ GOOD - Containerized test database
// docker-compose.yml for test database
// Isolated, fast, reproducible
```

### 4. Race Conditions (~5%)

**Cause**: Tests assume operations complete in a specific order

**Anti-patterns**:
```typescript
// ❌ BAD - Parallel operations without coordination
test('concurrent updates', async () => {
  await Promise.all([
    updateUser(1, { name: 'Alice' }),
    updateUser(1, { name: 'Bob' })
  ]);
  const user = await getUser(1);
  expect(user.name).toBe('Bob'); // Flaky! Which one wins?
});

// ❌ BAD - No wait for async operation
test('async operation', async () => {
  triggerAsyncOperation(); // Don't await!
  const result = await checkResult();
  expect(result).toBeDefined(); // Flaky!
});
```

**Solutions**:
```typescript
// ✅ GOOD - Proper async/await
test('async operation', async () => {
  await triggerAsyncOperation();
  const result = await checkResult();
  expect(result).toBeDefined();
});

// ✅ GOOD - Explicit ordering
test('sequential updates', async () => {
  await updateUser(1, { name: 'Alice' });
  await updateUser(1, { name: 'Bob' });
  const user = await getUser(1);
  expect(user.name).toBe('Bob');
});

// ✅ GOOD - Wait for all operations
test('parallel operations', async () => {
  await Promise.all([
    operation1(),
    operation2(),
    operation3()
  ]);
  // Now all are complete
  const results = await getResults();
  expect(results.length).toBe(3);
});
```

### 5. Resource Constraints (~3%)

**Cause**: Tests fail when system resources are limited

**Anti-patterns**:
```typescript
// ❌ BAD - Assumes unlimited resources
test('process large dataset', async () => {
  const data = generateData(10000000); // 10M records
  await processData(data);
  // Might fail due to memory constraints
});

// ❌ BAD - Parallel tests overwhelming system
// 100 browser instances at once
```

**Solutions**:
```typescript
// ✅ GOOD - Reasonable data sizes
test('process dataset', async () => {
  const data = generateData(1000); // Reasonable size
  await processData(data);
});

// ✅ GOOD - Control parallel execution
// playwright.config.ts
export default {
  workers: process.env.CI ? 4 : 2, // Limit workers
  fullyParallel: false, // Run serially if needed
};

// ✅ GOOD - Resource cleanup
afterEach(async () => {
  await cleanupTempFiles();
  await closeConnections();
  await clearCache();
});
```

### 6. Browser/Environment Specific (~2%)

**Cause**: Tests behave differently across browsers or environments

**Anti-patterns**:
```typescript
// ❌ BAD - Assumes specific browser behavior
test('animation timing', async () => {
  await page.click('.button');
  await sleep(500); // Animation duration, browser-specific!
  await expect(page.locator('.modal')).toBeVisible();
});

// ❌ BAD - Environment-specific paths
const filePath = 'C:\\Users\\test\\data.txt'; // Windows only!
```

**Solutions**:
```typescript
// ✅ GOOD - Wait for final state, not animation
test('modal appears', async () => {
  await page.click('.button');
  await expect(page.locator('.modal')).toBeVisible();
  // Don't care about animation timing
});

// ✅ GOOD - Cross-platform paths
import path from 'path';
const filePath = path.join(__dirname, 'data', 'test.txt');

// ✅ GOOD - Test in multiple browsers
test.describe('cross-browser', () => {
  ['chromium', 'firefox', 'webkit'].forEach(browserType => {
    test(`works in ${browserType}`, async ({ browser }) => {
      // Test implementation
    });
  });
});
```

---

## Flaky Test Detection

### Automated Detection

**CI/CD Integration**:
```yaml
# .github/workflows/flaky-detection.yml
name: Flaky Test Detection

on:
  schedule:
    - cron: '0 0 * * *'  # Daily

jobs:
  detect-flaky:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Run tests 10 times
        run: |
          for i in {1..10}; do
            npm test -- --reporter=json > results-$i.json
          done

      - name: Analyze flakiness
        run: |
          python scripts/detect-flaky.py results-*.json

      - name: Report flaky tests
        run: |
          python scripts/report-flaky.py > flaky-report.md

      - name: Create issue if flaky tests found
        uses: actions/github-script@v6
        with:
          script: |
            const fs = require('fs');
            const report = fs.readFileSync('flaky-report.md', 'utf8');
            if (report.includes('FLAKY')) {
              github.rest.issues.create({
                owner: context.repo.owner,
                repo: context.repo.repo,
                title: 'Flaky tests detected',
                body: report,
                labels: ['flaky-tests', 'quality']
              });
            }
```

**Flaky Test Analyzer**:
```python
# detect-flaky.py
import json
import sys
from collections import defaultdict

def analyze_flakiness(result_files):
    test_results = defaultdict(lambda: {'pass': 0, 'fail': 0})

    for file in result_files:
        with open(file) as f:
            results = json.load(f)
            for test in results['tests']:
                if test['status'] == 'passed':
                    test_results[test['name']]['pass'] += 1
                else:
                    test_results[test['name']]['fail'] += 1

    flaky_tests = []
    for test_name, results in test_results.items():
        total = results['pass'] + results['fail']
        if results['pass'] > 0 and results['fail'] > 0:
            flaky_rate = results['fail'] / total
            flaky_tests.append({
                'name': test_name,
                'pass': results['pass'],
                'fail': results['fail'],
                'flaky_rate': flaky_rate
            })

    return sorted(flaky_tests, key=lambda x: x['flaky_rate'], reverse=True)

if __name__ == '__main__':
    flaky_tests = analyze_flakiness(sys.argv[1:])

    if flaky_tests:
        print("FLAKY TESTS DETECTED:")
        for test in flaky_tests:
            print(f"  - {test['name']}: {test['flaky_rate']:.1%} flaky")
            print(f"    Pass: {test['pass']}, Fail: {test['fail']}")
        sys.exit(1)
    else:
        print("No flaky tests detected")
        sys.exit(0)
```

### Manual Detection

**Look for patterns**:
- Tests that fail occasionally in CI but pass locally
- Tests that require re-runs to pass
- Tests that fail with "timeout" errors
- Tests that fail with "element not found" errors
- Tests that fail intermittently in nightly runs

---

## Remediation Process

### Step 1: Identify Flaky Test

**Gather information**:
- [ ] Test name and location
- [ ] Failure frequency (X out of Y runs)
- [ ] Failure messages/errors
- [ ] Environment (CI vs local, browser, OS)
- [ ] Recent changes to test or code

### Step 2: Reproduce Flakiness

**Run test multiple times**:
```bash
# Run test 100 times to reproduce
for i in {1..100}; do
  npm test -- tests/flaky-test.spec.ts
  if [ $? -ne 0 ]; then
    echo "Failed on iteration $i"
    break
  fi
done
```

**Debug mode**:
```bash
# Run with debug output
DEBUG=* npm test -- tests/flaky-test.spec.ts

# Run with Playwright debug
npx playwright test --debug tests/flaky-test.spec.ts

# Run with video recording
npx playwright test --video=on tests/flaky-test.spec.ts
```

### Step 3: Root Cause Analysis

**Questions to ask**:
1. **Timing**: Does the test use sleeps or fixed delays?
2. **State**: Does the test share data with other tests?
3. **External deps**: Does the test call real APIs or services?
4. **Race conditions**: Are there async operations without awaits?
5. **Resources**: Does the test require specific CPU/memory?
6. **Environment**: Does it fail only in CI or specific browsers?

**Checklist**:
- [ ] Review test code for anti-patterns
- [ ] Check for shared state or global variables
- [ ] Verify all async operations are awaited
- [ ] Look for network calls to external services
- [ ] Check resource usage during test
- [ ] Compare local vs CI environment differences

### Step 4: Implement Fix

**Timing fixes**:
```typescript
// Before: Fixed delay
await page.waitForTimeout(5000);

// After: Explicit wait
await page.waitForSelector('[data-testid="result"]', { state: 'visible' });
```

**State isolation fixes**:
```typescript
// Before: Shared state
let userId = 1;

// After: Unique per test
const userId = `user-${uuid()}`;
```

**External dependency fixes**:
```typescript
// Before: Real API call
const response = await fetch('https://api.example.com/data');

// After: Mocked
await page.route('**/api/**', route => {
  route.fulfill({ status: 200, body: mockData });
});
```

### Step 5: Verify Fix

**Run test multiple times**:
```bash
# Run 100 times to verify stability
for i in {1..100}; do
  npm test -- tests/formerly-flaky-test.spec.ts
  if [ $? -ne 0 ]; then
    echo "Still flaky! Failed on iteration $i"
    exit 1
  fi
done

echo "Success! Test passed 100/100 times"
```

**Monitor in CI**:
- [ ] Merge fix
- [ ] Monitor test for 1 week
- [ ] Verify 0% flaky rate
- [ ] Remove from quarantine

---

## Flaky Test Management

### Quarantine Strategy

**When to quarantine**:
- Flaky rate >10%
- Blocking CI/CD pipeline
- Root cause not immediately fixable
- While investigating

**How to quarantine**:
```typescript
// Option 1: Skip test temporarily
test.skip('flaky test - quarantined #123', async () => {
  // Test code
});

// Option 2: Mark as flaky (Playwright)
test.describe.configure({ retries: 3 });
test('potentially flaky test', async () => {
  // Will retry up to 3 times
});

// Option 3: Separate CI job
// Only run quarantined tests in separate job
// Don't block main pipeline
```

**Quarantine tracking**:
| Test Name | Quarantined Date | Reason | Issue | Owner | Status |
|-----------|------------------|--------|-------|-------|--------|
| test-name | 2025-11-01 | Timing issue | #123 | Alice | In Progress |
| test-name | 2025-11-05 | External API | #124 | Bob | Fixed |

**Quarantine rules**:
- [ ] Create GitHub issue for each quarantined test
- [ ] Assign owner
- [ ] Set fix deadline (< 2 weeks)
- [ ] Review quarantined tests weekly
- [ ] Maximum 5% of tests can be quarantined

### Retry Strategy

**When to use retries**:
- ⚠️ Use sparingly - retries mask problems, don't fix them
- Only for genuinely intermittent infrastructure issues
- Not for application code flakiness

**Retry configuration**:
```typescript
// playwright.config.ts
export default {
  // Retry failed tests in CI only
  retries: process.env.CI ? 2 : 0,

  // Per-test retry
  use: {
    // Video only on retry
    video: 'retain-on-failure',
    // Screenshot on failure
    screenshot: 'only-on-failure',
  }
};

// Specific test with retry
test.describe.configure({ retries: 3 });
test('flaky test', async () => {
  // Will retry up to 3 times if fails
});
```

**Retry monitoring**:
- Track which tests are being retried
- Alert if retry rate increases
- Investigate tests that always need retries

---

## Prevention Strategies

### Code Review Checklist

**For every new test, verify**:
- [ ] No fixed delays (sleep, waitForTimeout)
- [ ] All async operations awaited
- [ ] Unique test data (no shared state)
- [ ] External dependencies mocked
- [ ] Proper cleanup (beforeEach/afterEach)
- [ ] Reasonable timeouts
- [ ] Explicit waits for conditions

### Test Writing Guidelines

**DO**:
- ✅ Use explicit waits (`waitForSelector`, `waitForResponse`)
- ✅ Create unique test data per test
- ✅ Mock external dependencies
- ✅ Clean up test data after each test
- ✅ Use data-testid attributes for selectors
- ✅ Wait for final state, not intermediate steps
- ✅ Make tests hermetic (isolated)

**DON'T**:
- ❌ Use fixed delays (sleep, waitForTimeout)
- ❌ Share data between tests
- ❌ Call real external APIs
- ❌ Depend on test execution order
- ❌ Use fragile CSS selectors
- ❌ Assume timing of async operations
- ❌ Leave test data behind

### Automated Linting

**ESLint rule for no-wait-for-timeout**:
```javascript
// .eslintrc.js
module.exports = {
  rules: {
    'playwright/no-wait-for-timeout': 'error',
    'playwright/no-useless-await': 'error',
    'jest/no-disabled-tests': 'warn'
  }
};
```

---

## Metrics & Monitoring

### Flakiness Dashboard

**Key Metrics**:
- Total flaky test count
- Flaky test rate (%)
- Tests in quarantine
- Average retry count
- Time wasted on flaky tests

**Dashboard Panels**:

**Panel 1: Flaky Test Trend**
```
Line graph showing flaky test % over time
Target line at 5%
Alert if >5%
```

**Panel 2: Top Flaky Tests**
```
Table showing:
- Test name
- Flaky rate
- Last failure date
- Owner
- Status
```

**Panel 3: Flaky Test Impact**
```
- CI/CD time wasted on retries
- Developer hours spent debugging
- Pipeline blocks caused
```

### Weekly Flaky Test Report

**Report format**:
```markdown
# Flaky Test Report - Week of [Date]

## Summary
- Total tests: _____
- Flaky tests: _____
- Flaky rate: _____%
- Change from last week: +/-_____%

## New Flaky Tests (This Week)
1. [test-name] - Flaky rate: ___% - Owner: ___
2. [test-name] - Flaky rate: ___% - Owner: ___

## Fixed Flaky Tests (This Week)
1. [test-name] - Fixed by [PR#] - Thanks @username!
2. [test-name] - Fixed by [PR#] - Thanks @username!

## Still Quarantined
1. [test-name] - Issue #___ - Days in quarantine: ___
2. [test-name] - Issue #___ - Days in quarantine: ___

## Action Items
- [ ] Fix test X by [date]
- [ ] Investigate test Y
- [ ] Review quarantined tests
```

---

## Success Criteria

Flaky test remediation is successful when:

- [ ] **Flaky rate <5%** - Industry best practice
- [ ] **No tests in quarantine >2 weeks** - Fix or delete
- [ ] **Zero tolerance for new flaky tests** - Block in code review
- [ ] **Automated detection in place** - Daily flaky test runs
- [ ] **Team understanding** - Everyone knows how to prevent flakiness
- [ ] **CI/CD reliability** - Tests trusted by team
- [ ] **Documentation** - Guidelines and examples available

---

## Resources

### Tools

**Flaky Test Detection**:
- Playwright Test Retry
- Jest Retry
- Flaky Test Management tools

**Debugging**:
- Playwright Inspector
- Browser DevTools
- Video recordings
- Trace viewer

### References

**Best Practices**:
- [Google Testing Blog - Flaky Tests](https://testing.googleblog.com/search/label/flake)
- [Microsoft - Combating Flaky Tests](https://devblogs.microsoft.com/)
- [Playwright - Best Practices](https://playwright.dev/docs/best-practices)

**Research**:
- "An Empirical Analysis of Flaky Tests" (IEEE)
- "Understanding Flaky Tests" (ACM)

---

**Template Version**: 1.0
**Last Updated**: 2025-11-19
**Next Review**: Monthly
