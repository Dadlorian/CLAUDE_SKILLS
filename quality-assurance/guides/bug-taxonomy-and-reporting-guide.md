# Bug Taxonomy and Reporting Guide

**Complete guide for bug classification, reporting, and lifecycle management**

---

## Table of Contents

1. [Bug Fundamentals](#bug-fundamentals)
2. [Bug Classification](#bug-classification)
3. [Bug Severity and Priority](#bug-severity-and-priority)
4. [Bug Report Template](#bug-report-template)
5. [Bug Lifecycle](#bug-lifecycle)
6. [Bug Taxonomies](#bug-taxonomies)
7. [Root Cause Analysis](#root-cause-analysis)
8. [Bug Metrics](#bug-metrics)

---

## Bug Fundamentals

### What is a Bug?

**Definition**: A bug is a deviation between actual and expected behavior of a software system.

**Types of Deviations**:
- **Functional**: Feature doesn't work as specified
- **Performance**: Feature works but too slowly
- **Security**: Vulnerability or unauthorized access
- **Usability**: Feature works but is confusing/difficult
- **Compatibility**: Works in some environments, not others
- **Data Integrity**: Incorrect data stored/displayed

### Bug vs. Enhancement

| Bug | Enhancement |
|-----|-------------|
| System doesn't meet requirements | New feature request |
| Documented behavior broken | Undocumented behavior desired |
| Regression from previous version | Improvement to existing feature |
| Security vulnerability | Performance optimization (if not broken) |
| Example: Login button doesn't work | Example: Add "Remember Me" checkbox |

---

## Bug Classification

### By Severity

**Critical (P0)**
- System crash/data loss
- Security vulnerability (RCE, SQL injection)
- Cannot complete core user journey
- Production down
- Financial loss/legal liability

**Examples**:
```
BUG-001: Payment processing fails for all transactions (100% failure rate)
BUG-002: SQL injection in login form allows unauthorized access
BUG-003: Server crashes when uploading files >1MB
BUG-004: User data exposed in API response (PII leak)
```

**High (P1)**
- Major feature not working
- Workaround is difficult
- Affects many users
- Data corruption (recoverable)

**Examples**:
```
BUG-005: Search returns no results for any query
BUG-006: Unable to edit profile information
BUG-007: Email notifications not being sent
BUG-008: Shopping cart items disappear after 5 minutes
```

**Medium (P2)**
- Minor feature not working
- Easy workaround available
- Affects some users
- Cosmetic issues affecting usability

**Examples**:
```
BUG-009: Date picker doesn't allow keyboard input (can type manually)
BUG-010: Pagination shows "NaN" when no results
BUG-011: Button text overflows on mobile devices
BUG-012: Tooltip displays incorrect information
```

**Low (P3)**
- Cosmetic issues
- Affects very few users
- No functional impact
- Nice-to-have fixes

**Examples**:
```
BUG-013: Icon misaligned by 2px
BUG-014: Typo in footer copyright text
BUG-015: Inconsistent button hover color
BUG-016: Console warning (no user impact)
```

### By Priority

**Priority = (Severity × Frequency × Visibility)**

| Priority | When to Fix | Examples |
|----------|-------------|----------|
| **P0 - Critical** | Immediately (hotfix) | Production down, data loss, security breach |
| **P1 - High** | This sprint/iteration | Core feature broken, major UX issue |
| **P2 - Medium** | Next sprint | Minor feature broken, workaround available |
| **P3 - Low** | Backlog | Cosmetic, edge case, low impact |

**Priority Matrix**:

| Severity ↓ / Frequency → | Rare | Occasional | Frequent |
|---------------------------|------|------------|----------|
| **Critical** | P1 | P0 | P0 |
| **High** | P2 | P1 | P1 |
| **Medium** | P3 | P2 | P2 |
| **Low** | P3 | P3 | P3 |

---

## Bug Severity and Priority

### Severity Assessment

**Ask these questions**:
1. **Does it prevent core functionality?** → Critical/High
2. **Can users work around it easily?** → If yes, lower severity
3. **How many users affected?** → More users = higher severity
4. **Is data at risk?** → Critical
5. **Is there a security risk?** → Critical
6. **Does it block testing?** → High

### Examples of Severity/Priority Mismatch

**High Severity, Low Priority**:
```
BUG: System crashes when entering 1000+ character username
Severity: High (crash)
Priority: Low (no one enters 1000 char names)
Reason: Edge case, unlikely to occur
```

**Low Severity, High Priority**:
```
BUG: CEO's name misspelled on homepage
Severity: Low (typo)
Priority: High (visible to everyone, embarrassing)
Reason: High visibility, business impact
```

**Medium Severity, Critical Priority**:
```
BUG: Black Friday sale price not displaying
Severity: Medium (display issue)
Priority: Critical (today is Black Friday!)
Reason: Time-sensitive, business critical
```

---

## Bug Report Template

### Professional Bug Report

```markdown
**Bug ID**: BUG-2847
**Title**: Unable to complete checkout with PayPal payment method
**Reported By**: Jane Doe (QA Engineer)
**Date**: 2025-11-19
**Environment**: Staging
**Version**: 2.5.3

---

## Severity & Priority
**Severity**: High
**Priority**: P1
**Type**: Functional
**Component**: Payment Processing
**Frequency**: Always (100%)

---

## Description
Users cannot complete checkout when selecting PayPal as payment method. The "Complete Purchase" button becomes disabled after PayPal selection and clicking it has no effect.

---

## Impact
- Blocks all PayPal transactions (30% of our payment volume)
- Estimated revenue loss: $10,000/day
- Affects production users as of version 2.5.3 deployment

---

## Steps to Reproduce
1. Add any product to cart
2. Navigate to checkout page
3. Fill shipping information
4. Select "PayPal" as payment method
5. Click "Complete Purchase" button

**Actual Result**:
- Button becomes disabled
- No API call made (verified in Network tab)
- No error message displayed
- User stuck on checkout page

**Expected Result**:
- User redirected to PayPal authorization page
- After approval, order completed successfully
- Confirmation email sent

---

## Test Data
**Product**: Widget Pro (SKU: WDG-001)
**User**: test@example.com
**Cart Total**: $99.99
**Shipping**: Standard (US)
**Payment Method**: PayPal

---

## Environment Details
**Browser**: Chrome 120.0.6099.109
**OS**: Windows 11
**Screen Resolution**: 1920x1080
**Network**: WiFi, 100 Mbps
**Server**: staging-api-01.example.com

---

## Reproducibility
**Frequency**: 100% (10/10 attempts)
**First Observed**: 2025-11-19 09:30 AM EST
**Regression**: Yes (worked in version 2.5.2)

---

## Attachments
- Screenshot: checkout_paypal_error.png
- Video: checkout_flow_reproduction.mp4
- Network HAR file: network_trace.har
- Console Logs: browser_console.txt

---

## Console Errors
```
TypeError: Cannot read property 'initPayPal' of undefined
    at CheckoutPage.handlePaymentSelect (checkout.js:347)
    at HTMLButtonElement.onclick (checkout.js:412)
```

---

## Network Activity
```
No API call to /api/payments/paypal/initiate
Expected: POST /api/payments/paypal/initiate with cart ID
```

---

## Related Information
**Related Bugs**: BUG-2801 (PayPal integration issues in 2.5.3)
**Related PR**: #3492 (PayPal SDK update)
**Related Story**: US-1847 (Update payment providers)

---

## Suggested Fix
Investigation shows PayPal SDK initialization code was removed in commit abc123. Need to restore PayPal.init() call in checkout.js line 95.

---

## Workaround
Users can select "Credit Card" payment method as alternative. Not ideal but functional until fix deployed.

---

## Business Impact
**Revenue Impact**: High - $10K/day
**User Impact**: High - 30% of users prefer PayPal
**Customer Complaints**: 15 support tickets in 2 hours
**Social Media**: 3 negative tweets mentioning issue
```

### Quick Bug Report (For Minor Issues)

```markdown
**Bug**: Search autocomplete shows results from deleted products

**Severity**: Medium | **Priority**: P2

**Steps**:
1. Search for "laptop"
2. Observe autocomplete suggestions

**Expected**: Only active products
**Actual**: Includes deleted products (greyed out in DB)

**Environment**: Production, Chrome 120, macOS

**Screenshot**: autocomplete_deleted_products.png
```

---

## Bug Lifecycle

### Bug States

```
┌──────────┐
│   NEW    │ ← Bug reported
└────┬─────┘
     │
     ↓
┌──────────┐
│ ASSIGNED │ ← Assigned to developer
└────┬─────┘
     │
     ↓
┌──────────┐
│   OPEN   │ ← Developer investigating
└────┬─────┘
     │
     ├─→ IN PROGRESS → Developer fixing
     │
     ├─→ FIXED → Fix implemented, ready for test
     │
     ├─→ VERIFIED → QA verified fix works
     │
     ├─→ CLOSED → Issue resolved
     │
     ├─→ REOPEN → Fix didn't work, back to OPEN
     │
     ├─→ DUPLICATE → Same as another bug
     │
     ├─→ WONTFIX → Decided not to fix
     │
     └─→ CANNOT REPRODUCE → Cannot replicate issue
```

### State Transition Rules

**NEW → ASSIGNED**
- Triaged by QA Lead
- Assigned to appropriate developer
- Severity/Priority confirmed

**ASSIGNED → OPEN**
- Developer accepts bug
- Investigation begins

**OPEN → IN PROGRESS**
- Developer starts implementing fix
- Links to feature branch

**IN PROGRESS → FIXED**
- Fix implemented
- Unit tests added
- Code reviewed and merged
- Deployed to test environment

**FIXED → VERIFIED**
- QA retests bug
- Confirms fix works
- Tests related functionality
- No regressions introduced

**VERIFIED → CLOSED**
- Fix deployed to production
- Monitoring confirms no issues
- Release notes updated

**Any State → REOPEN**
- Bug reoccurs
- Fix incomplete
- Regression found

**Any State → DUPLICATE**
- Found to be duplicate of existing bug
- Link to original bug

**Any State → WONTFIX**
- Out of scope
- Design decision
- Cost > benefit
- Documented as known limitation

**Any State → CANNOT REPRODUCE**
- Cannot replicate with provided steps
- Request more information from reporter
- Close if no response in 7 days

---

## Bug Taxonomies

### IEEE Standard Classification

#### 1. By Type

**Functional Bugs**
```
F01: Incorrect calculation/logic
F02: Missing functionality
F03: Incorrect functionality
F04: Extra/unwanted functionality
F05: Data validation issues
F06: Error handling problems

Example:
- F01: Tax calculated as 15% instead of 13%
- F02: "Export to PDF" button missing
- F03: Delete button deletes wrong item
```

**Interface Bugs**
```
I01: UI rendering issues
I02: Layout problems
I03: Accessibility issues
I04: Localization/i18n problems
I05: API contract violations

Example:
- I01: Button overlaps text on mobile
- I03: Images missing alt text
- I05: API returns 200 with error in body
```

**Performance Bugs**
```
P01: Slow response time
P02: Memory leak
P03: CPU/resource usage
P04: Scalability issues
P05: Database query optimization

Example:
- P01: Search takes 30 seconds
- P02: Memory increases 100MB/hour
- P05: N+1 query problem
```

**Security Bugs**
```
S01: Authentication bypass
S02: Authorization issues
S03: Data exposure
S04: Injection vulnerabilities
S05: XSS vulnerabilities
S06: CSRF vulnerabilities
S07: Insecure configuration

Example:
- S01: Can access admin panel without login
- S03: API exposes user passwords
- S04: SQL injection in search
```

**Compatibility Bugs**
```
C01: Browser compatibility
C02: OS compatibility
C03: Device compatibility
C04: API version compatibility
C05: Database compatibility

Example:
- C01: Works in Chrome, broken in Safari
- C03: Crash on iPhone 12 Pro Max
- C04: API v2 client can't call v1 endpoint
```

**Data Bugs**
```
D01: Data corruption
D02: Data loss
D03: Incorrect data displayed
D04: Data migration issues
D05: Data synchronization issues

Example:
- D01: User profile contains invalid JSON
- D02: Orders deleted instead of archived
- D05: Changes in mobile app don't sync to web
```

#### 2. By Root Cause

**Requirements Bugs** (35% of bugs)
```
R01: Requirement missing
R02: Requirement ambiguous
R03: Requirement incorrect
R04: Requirements conflict

Example:
- R02: "User-friendly" not defined - implemented differently
- R04: Req-A says "required", Req-B says "optional"
```

**Design Bugs** (25%)
```
D01: Architectural flaw
D02: Algorithm error
D03: Inadequate error handling
D04: Missing edge case handling

Example:
- D02: Sorting algorithm O(n²) instead of O(n log n)
- D04: Didn't handle negative numbers
```

**Coding Bugs** (30%)
```
C01: Syntax error
C02: Logic error
C03: Typo/copy-paste error
C04: Off-by-one error
C05: Null pointer exception
C06: Memory leak
C07: Race condition

Example:
- C02: Used && instead of ||
- C04: Loop from 0 to length (should be length-1)
- C07: Two threads modifying same variable
```

**Environment Bugs** (5%)
```
E01: Configuration error
E02: Dependency version mismatch
E03: Infrastructure issue
E04: Third-party service failure

Example:
- E01: Wrong database connection string
- E02: Requires Node 18, deployed with Node 16
```

**Testing Bugs** (5%)
```
T01: Test script error
T02: Test data issue
T03: Test environment issue
T04: False positive/negative

Example:
- T01: Test expects wrong status code
- T02: Test user account doesn't exist
```

### OWASP Security Bug Classification

```
OWASP Top 10 (2023):

A01: Broken Access Control
- Missing authorization checks
- IDOR (Insecure Direct Object Reference)
- Privilege escalation

A02: Cryptographic Failures
- Weak encryption
- Unencrypted sensitive data
- Weak key generation

A03: Injection
- SQL injection
- NoSQL injection
- Command injection
- LDAP injection

A04: Insecure Design
- Missing security controls
- Threat modeling gaps
- Insecure design patterns

A05: Security Misconfiguration
- Default credentials
- Unnecessary features enabled
- Verbose error messages

A06: Vulnerable and Outdated Components
- Unpatched libraries
- Deprecated dependencies
- Unknown component versions

A07: Identification and Authentication Failures
- Weak password policies
- Session fixation
- No multi-factor authentication

A08: Software and Data Integrity Failures
- Insecure CI/CD
- Code injection
- Insecure deserialization

A09: Security Logging and Monitoring Failures
- No audit logs
- Logs not monitored
- Inadequate alerting

A10: Server-Side Request Forgery (SSRF)
- Unvalidated URLs
- Internal network access
- Cloud metadata exposure
```

---

## Root Cause Analysis

### 5 Whys Technique

**Example Bug**: Users logged out unexpectedly

```
Bug: Users logged out after 5 minutes

Why #1: Why are users logged out?
→ Session expires after 5 minutes

Why #2: Why does session expire after 5 minutes?
→ Session timeout set to 300 seconds

Why #3: Why is timeout set to 300 seconds?
→ Environment variable SESSION_TIMEOUT=300

Why #4: Why is environment variable set to 300?
→ Copied from development environment

Why #5: Why did we copy dev config to production?
→ No separate config management for environments

ROOT CAUSE: Lack of environment-specific configuration management
FIX: Implement environment-specific configs (dev: 5min, prod: 30min)
PREVENTION: Add config validation in deployment pipeline
```

### Fishbone Diagram (Ishikawa)

```
                            Bug: Payment Fails
                                   |
                                   |
    People          Process        |        Technology
      |               |             |             |
      |               |             |             |
  No training    No testing    Old library   Slow server
  for payment    of payment    version       response
      |               |             |             |
      |               |             |             |
      └───────────────┴─────────────┴─────────────┘
                          |
                    Root Causes
```

### Bug Pattern Analysis

**Pattern**: Off-by-one errors

```
Occurrences:
- BUG-145: Array access out of bounds
- BUG-223: Loop processes one extra item
- BUG-456: Pagination shows page 0
- BUG-789: Last item not processed

Root Cause: Team unfamiliar with 0-indexed arrays
Prevention:
- Training on array indexing
- Linter rule for array bounds
- Code review checklist item
```

---

## Bug Metrics

### Key Metrics

**1. Bug Density**
```
Formula: Bugs / KLOC (thousands of lines of code)

Example:
Total Bugs: 45
Code Size: 15,000 lines
Bug Density: 45 / 15 = 3 bugs/KLOC

Industry Average: 1-5 bugs/KLOC
Good: < 2 bugs/KLOC
Poor: > 10 bugs/KLOC
```

**2. Defect Escape Rate**
```
Formula: Production Bugs / Total Bugs

Example:
Production Bugs: 5
Total Bugs Found: 50
Escape Rate: 5 / 50 = 10%

Target: < 5%
Warning: > 10%
Critical: > 20%
```

**3. Mean Time to Detect (MTTD)**
```
Formula: Σ(Bug Found Date - Bug Introduced Date) / Number of Bugs

Example:
Bug introduced: Jan 1
Bug found: Jan 15
MTTD: 14 days

Target: < 7 days
Warning: > 30 days
```

**4. Mean Time to Resolve (MTTR)**
```
Formula: Σ(Bug Fixed Date - Bug Reported Date) / Number of Bugs

Example:
Bug reported: Jan 15
Bug fixed: Jan 18
MTTR: 3 days

Target by Severity:
- Critical: < 4 hours
- High: < 2 days
- Medium: < 1 week
- Low: < 1 month
```

**5. Bug Age**
```
Formula: Current Date - Bug Reported Date

Distribution:
- 0-7 days: 60% (healthy)
- 8-30 days: 30% (acceptable)
- 31-90 days: 8% (concerning)
- 90+ days: 2% (critical)

Action: Close or re-prioritize bugs > 90 days
```

**6. Reopen Rate**
```
Formula: Reopened Bugs / Fixed Bugs

Example:
Bugs Fixed: 100
Bugs Reopened: 15
Reopen Rate: 15%

Target: < 10%
Warning: > 20%
```

**7. Bug Trends**
```
Weekly Bug Metrics:

Week | New | Fixed | Open | Trend
-----|-----|-------|------|------
W1   | 20  | 15    | 100  | +5
W2   | 18  | 25    | 93   | -7
W3   | 15  | 20    | 88   | -5
W4   | 22  | 18    | 92   | +4

Healthy: Fixed >= New
Concerning: New consistently > Fixed
```

### Bug Distribution Charts

**By Severity**
```
Critical: ███ 5%
High:     ██████████ 20%
Medium:   ████████████████████ 45%
Low:      ███████████████ 30%
```

**By Component**
```
Frontend:  ████████████ 30%
Backend:   ████████████████ 40%
Database:  ████ 10%
API:       ██████████ 20%
```

**By Type**
```
Functional:     ███████████████ 40%
Performance:    ████ 10%
Security:       ██ 5%
UI/UX:          ██████████ 25%
Compatibility:  ████████ 20%
```

---

## Best Practices

### Writing Bug Reports

✅ **DO**:
- Use clear, descriptive titles
- Include detailed steps to reproduce
- Provide expected vs actual results
- Attach screenshots/videos
- Include environment details
- Test in multiple environments
- Check for duplicates first
- Classify severity/priority accurately
- Link to related bugs/stories
- Suggest potential fixes (if known)

❌ **DON'T**:
- Write "It doesn't work" (vague)
- Skip reproduction steps
- Report multiple bugs in one ticket
- Exaggerate severity for attention
- Assume everyone knows the context
- Report bugs without verification
- Use subjective language ("ugly", "weird")
- Forget to attach promised files
- Report UI suggestions as bugs
- Duplicate existing bugs

### Bug Report Quality Checklist

**Before Submitting**:
- [ ] Can you reproduce it 100% of the time?
- [ ] Have you tested in multiple environments?
- [ ] Have you checked for existing duplicates?
- [ ] Is the title clear and specific?
- [ ] Are steps to reproduce detailed and accurate?
- [ ] Have you attached screenshots/videos?
- [ ] Is severity classification appropriate?
- [ ] Have you included environment details?
- [ ] Is expected behavior clearly stated?
- [ ] Have you linked related tickets?

---

**Guide Version**: 1.0
**Last Updated**: 2025-11-19
**References**: IEEE 1044, ISTQB Glossary, ISO/IEC/IEEE 29119, OWASP
