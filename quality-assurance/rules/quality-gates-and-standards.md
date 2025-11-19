# Quality Gates and Standards

**Comprehensive quality criteria for code, testing, and deployment**

---

## Table of Contents

1. [Quality Gates Overview](#quality-gates-overview)
2. [Code Quality Gates](#code-quality-gates)
3. [Test Quality Gates](#test-quality-gates)
4. [Deployment Quality Gates](#deployment-quality-gates)
5. [Performance Quality Gates](#performance-quality-gates)
6. [Security Quality Gates](#security-quality-gates)
7. [Quality Standards](#quality-standards)
8. [Enforcement and Automation](#enforcement-and-automation)

---

## Quality Gates Overview

### What are Quality Gates?

**Definition**: Quality gates are checkpoints in the development lifecycle where specific quality criteria must be met before proceeding to the next stage.

**Purpose**:
- Prevent defects from reaching production
- Ensure consistent quality standards
- Provide objective pass/fail criteria
- Enable automated quality checks
- Support continuous improvement

### Gate Hierarchy

```
┌─────────────────┐
│  Commit Gate    │ ← Pre-commit hooks, linting
└────────┬────────┘
         ↓
┌─────────────────┐
│    PR Gate      │ ← Code review, unit tests, coverage
└────────┬────────┘
         ↓
┌─────────────────┐
│   Merge Gate    │ ← Integration tests, build success
└────────┬────────┘
         ↓
┌─────────────────┐
│  Release Gate   │ ← E2E tests, performance, security
└────────┬────────┘
         ↓
┌─────────────────┐
│ Production Gate │ ← Smoke tests, monitoring, rollback ready
└─────────────────┘
```

---

## Code Quality Gates

### 1. Commit Gate (Pre-Commit)

**Enforced By**: Pre-commit hooks, Git hooks, Husky

**Criteria**:

| Check | Standard | Tool | Auto-Fix |
|-------|----------|------|----------|
| **Code Formatting** | Prettier/ESLint rules | Prettier, ESLint | Yes |
| **Linting** | Zero errors, < 5 warnings | ESLint, Pylint, RuboCop | Partial |
| **Type Checking** | Zero type errors | TypeScript, MyPy | No |
| **File Size** | < 500 lines per file | Custom script | No |
| **No Debug Code** | No console.log, debugger | ESLint rules | Yes |
| **No Secrets** | No API keys, passwords | git-secrets, trufflehog | No |
| **Commit Message** | Conventional Commits format | commitlint | No |

**Example Pre-Commit Hook**:
```bash
#!/bin/bash
# .git/hooks/pre-commit

echo "Running pre-commit checks..."

# 1. Format code
npm run format
if [ $? -ne 0 ]; then
  echo "❌ Code formatting failed"
  exit 1
fi

# 2. Lint code
npm run lint
if [ $? -ne 0 ]; then
  echo "❌ Linting failed"
  exit 1
fi

# 3. Type check
npm run type-check
if [ $? -ne 0 ]; then
  echo "❌ Type checking failed"
  exit 1
fi

# 4. Check for secrets
git-secrets --scan
if [ $? -ne 0 ]; then
  echo "❌ Secrets detected in code"
  exit 1
fi

# 5. Run unit tests for changed files
npm run test:changed
if [ $? -ne 0 ]; then
  echo "❌ Unit tests failed"
  exit 1
fi

echo "✅ All pre-commit checks passed"
exit 0
```

**Commit Message Standards** (Conventional Commits):
```
Format: <type>(<scope>): <subject>

Types:
- feat: New feature
- fix: Bug fix
- docs: Documentation
- style: Formatting, no code change
- refactor: Code restructuring
- test: Adding tests
- chore: Maintenance

Examples:
✅ feat(auth): add OAuth2 login support
✅ fix(payment): resolve PayPal checkout error
✅ docs(api): update authentication guide
❌ fixed stuff (vague)
❌ WIP (not descriptive)
```

### 2. Pull Request Gate

**Enforced By**: GitHub Actions, GitLab CI, Branch Protection Rules

**Criteria**:

| Check | Standard | Threshold | Blocker |
|-------|----------|-----------|---------|
| **Unit Tests** | All passing | 100% pass rate | Yes |
| **Code Coverage** | New code covered | ≥ 80% line coverage | Yes |
| **Code Review** | Approved by reviewer | 1+ approvals (2 for critical) | Yes |
| **No Merge Conflicts** | Clean merge to target branch | Zero conflicts | Yes |
| **Build Success** | Compiles without errors | Zero build errors | Yes |
| **Integration Tests** | All passing | 100% pass rate | Yes |
| **Security Scan** | No critical vulnerabilities | Zero critical/high | Yes |
| **Performance** | No degradation | < 10% slowdown | Yes |
| **Documentation** | Updated if needed | Required for new features | No |
| **Changelog** | Entry added | Required for user-facing changes | No |

**GitHub Branch Protection Example**:
```yaml
# .github/branch-protection.yml
branches:
  main:
    protection:
      required_status_checks:
        strict: true
        contexts:
          - "test / unit-tests"
          - "test / integration-tests"
          - "build / compile"
          - "security / scan"
          - "coverage / check"
      required_pull_request_reviews:
        required_approving_review_count: 2
        dismiss_stale_reviews: true
        require_code_owner_reviews: true
      required_linear_history: true
      enforce_admins: true
      restrictions:
        users: []
        teams: ["core-team"]
```

**Coverage Gate Example**:
```yaml
# .github/workflows/coverage.yml
- name: Check coverage
  run: |
    npm run test:coverage
    COVERAGE=$(cat coverage/coverage-summary.json | jq '.total.lines.pct')

    if (( $(echo "$COVERAGE < 80" | bc -l) )); then
      echo "❌ Coverage $COVERAGE% is below threshold 80%"
      exit 1
    fi

    echo "✅ Coverage $COVERAGE% meets threshold"
```

### 3. Code Review Standards

**Must Review**:
- [ ] **Functionality**: Does code work as intended?
- [ ] **Logic**: Is the logic correct and efficient?
- [ ] **Edge Cases**: Are edge cases handled?
- [ ] **Error Handling**: Are errors caught and handled properly?
- [ ] **Security**: No vulnerabilities (SQL injection, XSS, etc.)?
- [ ] **Performance**: No obvious performance issues?
- [ ] **Tests**: Are tests adequate and meaningful?
- [ ] **Readability**: Is code clear and well-commented?
- [ ] **Standards**: Follows team coding standards?
- [ ] **Documentation**: Updated docs for new features?

**Code Review Checklist**:
```markdown
## Functional Review
- [ ] Feature works as described in ticket
- [ ] Happy path tested
- [ ] Error paths tested
- [ ] Edge cases considered

## Code Quality
- [ ] DRY (Don't Repeat Yourself)
- [ ] SOLID principles followed
- [ ] No magic numbers (use constants)
- [ ] Clear variable/function names
- [ ] Appropriate comments (why, not what)
- [ ] No commented-out code

## Security
- [ ] Input validation present
- [ ] No SQL injection risks
- [ ] No XSS vulnerabilities
- [ ] No hardcoded secrets
- [ ] Sensitive data encrypted
- [ ] Authentication/authorization checked

## Performance
- [ ] No N+1 queries
- [ ] Efficient algorithms used
- [ ] Database indexes exist for queries
- [ ] API responses paginated
- [ ] Large files not loaded into memory

## Testing
- [ ] Unit tests added/updated
- [ ] Integration tests added if needed
- [ ] Test coverage ≥ 80%
- [ ] Tests are meaningful (not trivial)
- [ ] Mocks used appropriately

## Documentation
- [ ] README updated if needed
- [ ] API docs updated
- [ ] Comments explain complex logic
- [ ] Changelog entry added

## Backwards Compatibility
- [ ] API changes are backwards compatible
- [ ] Database migrations are reversible
- [ ] Feature flags used for breaking changes
```

**Review Response Time SLA**:
```
Priority | Max Response Time | Max Review Time
---------|-------------------|----------------
Critical | 2 hours           | 4 hours
High     | 4 hours           | 1 day
Medium   | 1 day             | 2 days
Low      | 2 days            | 1 week
```

---

## Test Quality Gates

### 1. Test Coverage Gate

**Line Coverage**: ≥ 80%
```javascript
// istanbul.config.js
module.exports = {
  coverageThreshold: {
    global: {
      branches: 80,
      functions: 80,
      lines: 80,
      statements: 80
    }
  }
};
```

**Branch Coverage**: ≥ 80%
```typescript
// Example: All branches must be tested
function calculateDiscount(total: number, isMember: boolean): number {
  // Branch 1: total > 100
  if (total > 100) {
    discount = 10;
  }

  // Branch 2: isMember
  if (isMember) {
    discount += 5;
  }

  return discount;
}

// Tests must cover all 4 combinations:
// 1. total > 100, isMember = true
// 2. total > 100, isMember = false
// 3. total ≤ 100, isMember = true
// 4. total ≤ 100, isMember = false
```

**Function Coverage**: ≥ 90%
```
All exported functions must have at least one test
Private/helper functions should be tested via public API
```

### 2. Test Quality Gate

**Criteria**:
```yaml
Test Quality Standards:

  Test Naming:
    ✅ "user can login with valid credentials"
    ❌ "test1", "testLogin"

  Test Independence:
    ✅ Each test can run standalone
    ❌ Tests depend on execution order

  Test Speed:
    ✅ Unit tests: < 100ms each
    ✅ Integration tests: < 5 seconds each
    ❌ Any test > 30 seconds (should be tagged as slow)

  Test Assertions:
    ✅ Specific assertions (expect(x).toBe(5))
    ❌ Vague assertions (expect(x).toBeTruthy())

  Test Data:
    ✅ Factories/fixtures for test data
    ❌ Hardcoded magic values

  Test Cleanup:
    ✅ beforeEach/afterEach for setup/teardown
    ❌ Leaving test data in database

  Flakiness:
    ✅ Pass rate > 99%
    ❌ Any test with < 95% pass rate (quarantine)
```

### 3. Test Pyramid Compliance

**Distribution Target**:
```
        /\
       /E2E\         10% - 20 E2E tests
      /------\
     /  API   \      20% - 40 API tests
    /----------\
   / UNIT TESTS \    70% - 140 unit tests
  /--------------\

Total: 200 tests
```

**Enforcement**:
```javascript
// test-pyramid-check.js
const testCounts = {
  unit: 140,
  integration: 40,
  e2e: 20
};

const total = testCounts.unit + testCounts.integration + testCounts.e2e;

const ratios = {
  unit: (testCounts.unit / total) * 100,
  integration: (testCounts.integration / total) * 100,
  e2e: (testCounts.e2e / total) * 100
};

// Check pyramid compliance
if (ratios.unit < 60 || ratios.unit > 80) {
  throw new Error(`Unit tests should be 60-80%, got ${ratios.unit}%`);
}

if (ratios.e2e > 15) {
  throw new Error(`E2E tests should be <15%, got ${ratios.e2e}%`);
}

console.log('✅ Test pyramid is balanced');
```

---

## Deployment Quality Gates

### 1. Pre-Deployment Gate

**Criteria**:

| Check | Standard | Tool | Blocker |
|-------|----------|------|---------|
| **All Tests Passing** | 100% pass rate | CI/CD | Yes |
| **Code Coverage** | ≥ 80% | CodeCov, Coveralls | Yes |
| **Security Scan** | Zero critical/high | Snyk, SonarQube | Yes |
| **Performance Test** | Within SLO | K6, JMeter | Yes |
| **Smoke Tests** | All passing | Playwright, Cypress | Yes |
| **Database Migrations** | Tested, reversible | Flyway, Liquibase | Yes |
| **Dependency Check** | No known vulnerabilities | npm audit, Dependabot | Yes |
| **Build Artifacts** | Signed and verified | Cosign, GPG | Yes |
| **Documentation** | Release notes updated | Manual check | No |
| **Rollback Plan** | Documented and tested | Manual check | Yes |

**Example Deployment Gate**:
```yaml
# .github/workflows/deploy.yml
name: Deploy to Production

on:
  push:
    tags:
      - 'v*'

jobs:
  pre-deployment-checks:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout
        uses: actions/checkout@v3

      - name: Run all tests
        run: npm test

      - name: Check coverage
        run: |
          npm run test:coverage
          COVERAGE=$(cat coverage/coverage-summary.json | jq '.total.lines.pct')
          if (( $(echo "$COVERAGE < 80" | bc -l) )); then
            echo "❌ Coverage below 80%"
            exit 1
          fi

      - name: Security scan
        run: |
          npm audit --production --audit-level=high
          if [ $? -ne 0 ]; then
            echo "❌ Security vulnerabilities found"
            exit 1
          fi

      - name: Performance test
        run: |
          k6 run tests/performance/load-test.js
          if [ $? -ne 0 ]; then
            echo "❌ Performance test failed"
            exit 1
          fi

      - name: Database migration test
        run: |
          npm run db:migrate:test
          npm run db:rollback:test

      - name: Build
        run: npm run build

      - name: Smoke tests
        run: npm run test:smoke

      - name: All gates passed
        run: echo "✅ All deployment gates passed"

  deploy:
    needs: pre-deployment-checks
    runs-on: ubuntu-latest
    steps:
      - name: Deploy to production
        run: ./deploy.sh production

      - name: Post-deployment smoke tests
        run: npm run test:smoke:production

      - name: Monitor for errors
        run: ./monitor-deployment.sh
```

### 2. Post-Deployment Gate

**Automated Checks** (first 30 minutes):
```yaml
Post-Deployment Monitoring:

  Health Checks:
    - API endpoints responding (200 OK)
    - Database connectivity
    - Cache connectivity
    - External service connectivity
    Threshold: 100% healthy

  Error Rate:
    - 5xx errors < 0.1%
    - 4xx errors < 5%
    Monitor: First 30 minutes
    Action: Rollback if threshold exceeded

  Performance:
    - p95 response time < 500ms
    - p99 response time < 1000ms
    Monitor: First 30 minutes
    Action: Alert if degraded, rollback if critical

  User Impact:
    - Active users not dropping
    - Session creation working
    - Critical user flows working
    Monitor: Continuously
    Action: Rollback if impact detected
```

**Rollback Criteria** (automatic):
```yaml
Automatic Rollback Triggers:

  Critical:
    - Error rate > 5%
    - Health check failing
    - p99 latency > 5 seconds
    - Database migrations failed
    Action: Immediate automatic rollback

  Warning:
    - Error rate > 1%
    - p95 latency > 1 second
    - Memory usage > 90%
    - CPU usage > 90%
    Action: Alert team, prepare rollback
```

---

## Performance Quality Gates

### Response Time SLOs

```yaml
API Endpoints:

  Critical Endpoints:
    p50: < 200ms
    p95: < 500ms
    p99: < 1000ms
    Examples: Login, Checkout, Search

  Standard Endpoints:
    p50: < 500ms
    p95: < 1000ms
    p99: < 2000ms
    Examples: Profile, Settings

  Background Jobs:
    p95: < 5 seconds
    p99: < 10 seconds
    Examples: Report generation, Email sending
```

**Enforcement**:
```javascript
// Performance test with K6
import http from 'k6/http';
import { check } from 'k6';

export const options = {
  thresholds: {
    'http_req_duration{endpoint:login}': ['p(95)<500', 'p(99)<1000'],
    'http_req_duration{endpoint:search}': ['p(95)<500', 'p(99)<1000'],
    'http_req_duration{endpoint:checkout}': ['p(95)<500', 'p(99)<1000'],
    'http_req_failed': ['rate<0.01'], // Error rate < 1%
  }
};

export default function() {
  const res = http.get('https://api.example.com/products', {
    tags: { endpoint: 'search' }
  });

  check(res, {
    'status is 200': (r) => r.status === 200,
    'response time OK': (r) => r.timings.duration < 500
  });
}
```

### Frontend Performance Gates

**Core Web Vitals** (Google):
```yaml
Largest Contentful Paint (LCP):
  Good: < 2.5s
  Needs Improvement: 2.5s - 4.0s
  Poor: > 4.0s
  Gate: Must be "Good"

First Input Delay (FID):
  Good: < 100ms
  Needs Improvement: 100ms - 300ms
  Poor: > 300ms
  Gate: Must be "Good"

Cumulative Layout Shift (CLS):
  Good: < 0.1
  Needs Improvement: 0.1 - 0.25
  Poor: > 0.25
  Gate: Must be "Good"
```

**Lighthouse CI**:
```yaml
# lighthouserc.json
{
  "ci": {
    "assert": {
      "preset": "lighthouse:recommended",
      "assertions": {
        "categories:performance": ["error", {"minScore": 0.9}],
        "categories:accessibility": ["error", {"minScore": 0.9}],
        "categories:best-practices": ["error", {"minScore": 0.9}],
        "categories:seo": ["warn", {"minScore": 0.8}],
        "first-contentful-paint": ["error", {"maxNumericValue": 2000}],
        "largest-contentful-paint": ["error", {"maxNumericValue": 2500}],
        "cumulative-layout-shift": ["error", {"maxNumericValue": 0.1}]
      }
    }
  }
}
```

### Resource Utilization Gates

```yaml
Production Services:

CPU Usage:
  Normal: < 50%
  Warning: 50-70%
  Critical: > 70%
  Gate: Deploy only if current < 50%

Memory Usage:
  Normal: < 60%
  Warning: 60-80%
  Critical: > 80%
  Gate: Deploy only if current < 60%

Database Connections:
  Normal: < 50% of pool
  Warning: 50-80%
  Critical: > 80%
  Gate: Deploy only if current < 50%

Disk Usage:
  Normal: < 70%
  Warning: 70-85%
  Critical: > 85%
  Gate: Alert if > 70%
```

---

## Security Quality Gates

### Security Scan Gates

**Dependency Vulnerabilities**:
```yaml
npm audit / Snyk / Dependabot:

Severity Thresholds:
  Critical: 0 allowed (blocker)
  High: 0 allowed (blocker)
  Medium: < 5 allowed (warning)
  Low: < 20 allowed (info)

Action:
  - Critical/High: Block deployment
  - Medium: Create ticket, deploy allowed
  - Low: Track, no action needed

Example:
  ✅ 0 critical, 0 high, 2 medium, 10 low → PASS
  ❌ 0 critical, 1 high, 0 medium, 0 low → FAIL
```

**SAST (Static Application Security Testing)**:
```yaml
SonarQube / CodeQL:

Code Smells:
  Critical: 0
  Major: < 10
  Minor: < 50

Bugs:
  Critical: 0
  Major: 0
  Minor: < 5

Vulnerabilities:
  Critical: 0
  Major: 0
  Minor: < 3

Security Hotspots:
  Review Rate: 100% reviewed
  To Review: 0
```

**DAST (Dynamic Application Security Testing)**:
```yaml
OWASP ZAP / Burp Suite:

Vulnerability Severity:
  Critical: 0 allowed
  High: 0 allowed
  Medium: < 5 allowed (with remediation plan)
  Low: < 20 allowed

Common Checks:
  - SQL Injection: 0 findings
  - XSS: 0 findings
  - CSRF: 0 findings
  - Authentication bypass: 0 findings
  - Sensitive data exposure: 0 findings
```

### Secrets Detection

```bash
# git-secrets pre-commit hook
git secrets --scan

# trufflehog
trufflehog --regex --entropy=True .

# gitleaks
gitleaks detect --source . --verbose

Threshold: ZERO secrets in code
Blockers:
  - API keys
  - Passwords
  - Private keys
  - Database connection strings
  - OAuth tokens
  - AWS credentials
```

---

## Quality Standards

### Code Style Standards

**JavaScript/TypeScript (ESLint + Prettier)**:
```javascript
// .eslintrc.js
module.exports = {
  extends: ['airbnb', 'prettier'],
  rules: {
    // Code Quality
    'complexity': ['error', 10],          // Max cyclomatic complexity
    'max-lines': ['error', 300],          // Max lines per file
    'max-lines-per-function': ['error', 50], // Max lines per function
    'max-params': ['error', 4],           // Max function parameters
    'max-depth': ['error', 3],            // Max nesting depth

    // Best Practices
    'no-console': 'error',                // No console.log in production
    'no-debugger': 'error',               // No debugger statements
    'no-var': 'error',                    // Use const/let, not var
    'prefer-const': 'error',              // Use const when possible
    'eqeqeq': ['error', 'always'],        // Use === instead of ==

    // TypeScript
    '@typescript-eslint/no-explicit-any': 'error',
    '@typescript-eslint/explicit-function-return-type': 'error',
  }
};
```

**Python (Black + Pylint)**:
```python
# .pylintrc
[MASTER]
max-line-length=100
max-module-lines=500

[BASIC]
good-names=i,j,k,x,y,z,df,db

[DESIGN]
max-args=5
max-attributes=10
max-branches=12
max-locals=15
max-statements=50
min-public-methods=1
max-public-methods=20

[REFACTORING]
max-nested-blocks=3
```

### Testing Standards

**Test Organization**:
```
tests/
├── unit/              # Fast, isolated tests
│   ├── services/
│   ├── utils/
│   └── models/
├── integration/       # Tests with dependencies
│   ├── api/
│   ├── database/
│   └── external/
├── e2e/              # Full user flows
│   ├── auth/
│   ├── checkout/
│   └── search/
└── performance/      # Load/stress tests
    ├── load/
    └── stress/
```

**Test Naming Convention**:
```typescript
// AAA Pattern: Arrange, Act, Assert

describe('UserService', () => {
  describe('createUser', () => {
    test('creates user with valid data', async () => {
      // Arrange
      const userData = { email: 'test@example.com' };

      // Act
      const user = await userService.createUser(userData);

      // Assert
      expect(user.id).toBeDefined();
      expect(user.email).toBe('test@example.com');
    });

    test('throws error for duplicate email', async () => {
      // Arrange
      await userService.createUser({ email: 'test@example.com' });

      // Act & Assert
      await expect(
        userService.createUser({ email: 'test@example.com' })
      ).rejects.toThrow('Email already exists');
    });
  });
});
```

---

## Enforcement and Automation

### CI/CD Pipeline with Gates

```yaml
# Complete pipeline with all gates
name: CI/CD Pipeline

on: [push, pull_request]

jobs:
  # Gate 1: Code Quality
  code-quality:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Setup Node.js
        uses: actions/setup-node@v3

      - name: Install dependencies
        run: npm ci

      - name: Format check
        run: npm run format:check

      - name: Lint
        run: npm run lint

      - name: Type check
        run: npm run type-check

  # Gate 2: Security
  security:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Dependency audit
        run: npm audit --production --audit-level=high

      - name: Secret scan
        uses: trufflesecurity/trufflehog@main

      - name: SAST scan
        uses: github/codeql-action/analyze@v2

  # Gate 3: Tests
  tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Unit tests
        run: npm run test:unit

      - name: Integration tests
        run: npm run test:integration

      - name: Coverage check
        run: |
          npm run test:coverage
          npx codecov

  # Gate 4: Build
  build:
    needs: [code-quality, security, tests]
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Build
        run: npm run build

      - name: Upload artifacts
        uses: actions/upload-artifact@v3
        with:
          name: build
          path: dist/

  # Gate 5: E2E Tests
  e2e:
    needs: build
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Start services
        run: docker-compose up -d

      - name: Run E2E tests
        run: npm run test:e2e

  # Gate 6: Performance
  performance:
    needs: build
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Performance test
        run: k6 run tests/performance/load-test.js

  # Gate 7: Deploy (only on main)
  deploy:
    if: github.ref == 'refs/heads/main'
    needs: [e2e, performance]
    runs-on: ubuntu-latest
    steps:
      - name: Deploy to staging
        run: ./deploy.sh staging

      - name: Smoke tests
        run: npm run test:smoke

      - name: Deploy to production
        run: ./deploy.sh production
```

### Quality Metrics Dashboard

```yaml
Quality Dashboard Metrics:

Code Quality:
  - Lines of Code
  - Code Coverage %
  - Code Smells
  - Technical Debt Hours
  - Duplicated Code %

Test Quality:
  - Total Tests
  - Test Pass Rate %
  - Flaky Test Rate %
  - Test Execution Time
  - Test Distribution (Pyramid)

Security:
  - Vulnerabilities (Critical/High/Medium/Low)
  - Security Hotspots
  - Dependency Vulnerabilities
  - Days Since Last Security Scan

Performance:
  - API Response Time (p95/p99)
  - Frontend Core Web Vitals
  - Resource Utilization %
  - Error Rate %

Deployment:
  - Deployment Frequency
  - Change Failure Rate %
  - Mean Time to Recovery (MTTR)
  - Lead Time for Changes
```

---

## Best Practices

### Quality Gate Best Practices

✅ **DO**:
- Automate all quality checks
- Make gates objective and measurable
- Fail fast (run quick checks first)
- Provide clear error messages
- Allow local testing before push
- Keep gates fast (< 10 min total)
- Version control gate configurations
- Monitor gate effectiveness
- Update gates based on learnings
- Document all quality standards

❌ **DON'T**:
- Make gates subjective
- Have manual gates that block automation
- Allow gates to become stale
- Set unrealistic thresholds
- Skip gates for "urgent" changes
- Ignore failing gates repeatedly
- Have gates that take > 30 minutes
- Create gates without buy-in
- Set and forget gates
- Make exceptions to gates

---

**Standards Version**: 1.0
**Last Updated**: 2025-11-19
**References**: ISO/IEC 25010, DORA Metrics, Google SRE, OWASP
