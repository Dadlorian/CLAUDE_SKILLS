# CI/CD Playbook
## Continuous Integration & Continuous Deployment Guide

---

## 🎯 Overview

This playbook provides a **complete CI/CD implementation guide** based on industry best practices from Google, Netflix, Amazon, and other high-performing engineering organizations.

**Goal**: Enable safe, frequent deployments with automated quality gates and fast feedback loops.

---

## 📊 CI/CD Maturity Levels

### Level 0: Manual (Ad-hoc)
```yaml
Deployment Frequency: Weeks/Months
Lead Time: Days/Weeks
MTTR: Hours/Days
Change Failure Rate: > 30%

Characteristics:
- Manual testing
- Manual deployment
- No automation
- High risk
```

### Level 1: Basic CI
```yaml
Deployment Frequency: Weeks
Lead Time: Days
MTTR: Hours
Change Failure Rate: 15-30%

Characteristics:
- Automated tests
- Build automation
- Manual deployment
- Some risk
```

### Level 2: Full CI/CD
```yaml
Deployment Frequency: Daily
Lead Time: Hours
MTTR: Minutes/Hours
Change Failure Rate: 5-15%

Characteristics:
- Automated testing
- Automated deployment
- Some manual gates
- Lower risk
```

### Level 3: Elite (Target)
```yaml
Deployment Frequency: Multiple times per day
Lead Time: < 1 hour
MTTR: < 1 hour
Change Failure Rate: < 5%

Characteristics:
- Full automation
- Continuous deployment
- Comprehensive monitoring
- Minimal risk
```

---

## 🏗️ CI/CD Architecture

```
┌─────────────────────────────────────────────────────────┐
│ DEVELOPER WORKFLOW                                       │
├─────────────────────────────────────────────────────────┤
│ 1. Write Code                                            │
│ 2. Run Tests Locally                                     │
│ 3. Commit & Push                                         │
└──────────────────┬──────────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────────┐
│ CONTINUOUS INTEGRATION (CI)                              │
├─────────────────────────────────────────────────────────┤
│ Trigger: Push to any branch                             │
│                                                          │
│ Pipeline Steps:                                          │
│ ✅ 1. Checkout code                                     │
│ ✅ 2. Install dependencies                              │
│ ✅ 3. Lint & format check                               │
│ ✅ 4. Type checking                                      │
│ ✅ 5. Unit tests                                         │
│ ✅ 6. Integration tests                                  │
│ ✅ 7. Security scan (SAST)                              │
│ ✅ 8. Build artifacts                                    │
│ ✅ 9. Code coverage report                              │
│ ✅ 10. Upload artifacts                                  │
│                                                          │
│ Output: Build status (✅ Pass or ❌ Fail)               │
└──────────────────┬──────────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────────┐
│ CODE REVIEW                                              │
├─────────────────────────────────────────────────────────┤
│ Requires: CI passing + 1 approval                       │
└──────────────────┬──────────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────────┐
│ MERGE TO MAIN                                            │
├─────────────────────────────────────────────────────────┤
│ Trigger: PR merged                                       │
│ CI runs again on main branch                            │
└──────────────────┬──────────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────────┐
│ CONTINUOUS DEPLOYMENT (CD) - STAGING                     │
├─────────────────────────────────────────────────────────┤
│ Trigger: CI passing on main branch                      │
│                                                          │
│ Pipeline Steps:                                          │
│ ✅ 1. Deploy to staging environment                     │
│ ✅ 2. Run database migrations                           │
│ ✅ 3. Run E2E tests                                      │
│ ✅ 4. Run smoke tests                                    │
│ ✅ 5. Run security tests (DAST)                         │
│ ✅ 6. Run performance tests                             │
│ ✅ 7. Generate deployment report                        │
│                                                          │
│ Output: Staging deployment status                       │
└──────────────────┬──────────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────────┐
│ CONTINUOUS DEPLOYMENT (CD) - PRODUCTION                  │
├─────────────────────────────────────────────────────────┤
│ Trigger: Staging tests passing + approval (or automatic)│
│                                                          │
│ Pipeline Steps:                                          │
│ ✅ 1. Create deployment tag                             │
│ ✅ 2. Deploy using canary/blue-green strategy          │
│ ✅ 3. Run smoke tests in production                     │
│ ✅ 4. Monitor error rates                               │
│ ✅ 5. Monitor performance metrics                       │
│ ✅ 6. Gradual traffic increase (if canary)             │
│ ✅ 7. Complete rollout or rollback                      │
│                                                          │
│ Output: Production deployment status                    │
└──────────────────┬──────────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────────┐
│ MONITORING & OBSERVABILITY                               │
├─────────────────────────────────────────────────────────┤
│ • Error tracking (Sentry)                               │
│ • Performance monitoring (Datadog/New Relic)            │
│ • Logs aggregation (ELK/Splunk)                         │
│ • Metrics dashboard (Grafana)                           │
│ • Alerts (PagerDuty/Opsgenie)                           │
└─────────────────────────────────────────────────────────┘
```

---

## 🔧 Implementation Guide

### Phase 1: Basic CI Setup (Week 1-2)

**Goal**: Automated testing on every commit

**Steps**:

1. **Choose CI Platform**
   ```yaml
   Options:
   - GitHub Actions (recommended for GitHub)
   - GitLab CI (recommended for GitLab)
   - CircleCI (multi-platform)
   - Jenkins (self-hosted)
   ```

2. **Create CI Configuration**
   ```yaml
   # .github/workflows/ci.yml (GitHub Actions example)
   name: Continuous Integration

   on:
     push:
       branches: ['**']
     pull_request:
       branches: [main, develop]

   jobs:
     test:
       runs-on: ubuntu-latest

       steps:
         - name: Checkout code
           uses: actions/checkout@v3

         - name: Setup Node.js
           uses: actions/setup-node@v3
           with:
             node-version: '20'
             cache: 'npm'

         - name: Install dependencies
           run: npm ci

         - name: Lint
           run: npm run lint

         - name: Type check
           run: npm run type-check

         - name: Run tests
           run: npm test -- --coverage

         - name: Upload coverage
           uses: codecov/codecov-action@v3
           with:
             files: ./coverage/coverage-final.json
   ```

3. **Configure Branch Protection**
   ```yaml
   Settings → Branches → Add Rule:
   - Require pull request before merging
   - Require status checks to pass before merging
     ✅ CI (tests)
     ✅ Lint
     ✅ Type check
   - Require branches to be up to date
   - Restrict who can push to matching branches
   ```

### Phase 2: Build & Artifact Management (Week 3-4)

**Goal**: Create deployable artifacts

**Steps**:

1. **Add Build Step**
   ```yaml
   - name: Build
     run: npm run build

   - name: Upload build artifacts
     uses: actions/upload-artifact@v3
     with:
       name: build-${{ github.sha }}
       path: dist/
       retention-days: 7
   ```

2. **Docker Image Build** (if using containers)
   ```yaml
   - name: Build Docker image
     run: docker build -t myapp:${{ github.sha }} .

   - name: Push to registry
     run: |
       echo ${{ secrets.DOCKER_PASSWORD }} | docker login -u ${{ secrets.DOCKER_USERNAME }} --password-stdin
       docker push myapp:${{ github.sha }}
   ```

### Phase 3: Continuous Deployment - Staging (Week 5-6)

**Goal**: Automated deployment to staging environment

**Steps**:

1. **Create Staging Deployment Job**
   ```yaml
   deploy-staging:
     needs: test
     runs-on: ubuntu-latest
     if: github.ref == 'refs/heads/main'

     steps:
       - name: Download artifacts
         uses: actions/download-artifact@v3
         with:
           name: build-${{ github.sha }}

       - name: Deploy to staging
         run: |
           # Deploy using your platform (AWS, Heroku, etc.)
           aws s3 sync dist/ s3://staging-bucket/
           aws cloudfront create-invalidation --distribution-id $STAGING_DIST_ID --paths "/*"

       - name: Run smoke tests
         run: npm run test:smoke -- --url=https://staging.example.com

       - name: Notify Slack
         uses: slackapi/slack-github-action@v1
         with:
           payload: |
             {
               "text": "Deployed to staging: ${{ github.sha }}"
             }
   ```

2. **Add E2E Tests**
   ```yaml
   e2e-tests:
     needs: deploy-staging
     runs-on: ubuntu-latest

     steps:
       - name: Checkout code
         uses: actions/checkout@v3

       - name: Run E2E tests
         run: npm run test:e2e -- --url=https://staging.example.com

       - name: Upload test results
         if: always()
         uses: actions/upload-artifact@v3
         with:
           name: e2e-results
           path: test-results/
   ```

### Phase 4: Continuous Deployment - Production (Week 7-8)

**Goal**: Automated deployment to production with safety checks

**Steps**:

1. **Production Deployment (Manual Approval)**
   ```yaml
   deploy-production:
     needs: e2e-tests
     runs-on: ubuntu-latest
     environment:
       name: production
       url: https://example.com

     steps:
       - name: Download artifacts
         uses: actions/download-artifact@v3
         with:
           name: build-${{ github.sha }}

       - name: Deploy to production
         run: |
           aws s3 sync dist/ s3://production-bucket/
           aws cloudfront create-invalidation --distribution-id $PROD_DIST_ID --paths "/*"

       - name: Run smoke tests
         run: npm run test:smoke -- --url=https://example.com

       - name: Create release tag
         run: |
           git tag -a v${{ github.run_number }} -m "Release ${{ github.run_number }}"
           git push origin v${{ github.run_number }}

       - name: Notify team
         run: |
           # Send notifications
           curl -X POST $SLACK_WEBHOOK -d '{"text": "🚀 Deployed to production"}'
   ```

2. **Configure Environment Protection**
   ```yaml
   Settings → Environments → production:
   - Required reviewers: Add reviewers (e.g., tech leads)
   - Wait timer: 5 minutes (optional)
   - Deployment branches: Only main branch
   ```

### Phase 5: Advanced Deployment Strategies (Week 9-10)

**Blue-Green Deployment**:
```yaml
deploy-blue-green:
  steps:
    - name: Deploy to green environment
      run: deploy.sh green

    - name: Run smoke tests on green
      run: npm run test:smoke -- --url=https://green.example.com

    - name: Switch traffic to green
      run: update-load-balancer.sh green

    - name: Monitor for 10 minutes
      run: sleep 600 && check-metrics.sh

    - name: Decommission blue (if successful)
      run: decommission.sh blue
```

**Canary Deployment**:
```yaml
deploy-canary:
  steps:
    - name: Deploy canary (10% traffic)
      run: deploy-canary.sh --traffic=10

    - name: Monitor canary metrics
      run: monitor-metrics.sh --duration=300

    - name: Increase to 50% if healthy
      run: deploy-canary.sh --traffic=50

    - name: Monitor again
      run: monitor-metrics.sh --duration=300

    - name: Complete rollout (100%)
      run: deploy-canary.sh --traffic=100
```

---

## 🔒 Security in CI/CD

### Secret Management

**Don't**:
```yaml
❌ env:
     API_KEY: "sk_live_12345..." # Hardcoded secret
```

**Do**:
```yaml
✅ env:
     API_KEY: ${{ secrets.API_KEY }} # From GitHub Secrets

✅ - name: Load secrets from Vault
     run: vault kv get secret/app-config
```

### Security Scanning

```yaml
security:
  steps:
    # 1. Dependency scanning
    - name: Run npm audit
      run: npm audit --audit-level=high

    # 2. SAST (Static Application Security Testing)
    - name: Run Semgrep
      run: semgrep --config=auto

    # 3. Container scanning
    - name: Scan Docker image
      run: trivy image myapp:${{ github.sha }}

    # 4. Secret scanning
    - name: Scan for secrets
      uses: trufflesecurity/trufflehog@main

    # 5. License compliance
    - name: Check licenses
      run: npx license-checker --production --onlyAllow "MIT;Apache-2.0;BSD-3-Clause"
```

---

## 📊 CI/CD Metrics & Monitoring

### Key Metrics (DORA Metrics)

```yaml
1. Deployment Frequency:
   Measure: Deploys per day
   Elite: Multiple per day
   Target: Daily
   Track: Count successful production deployments

2. Lead Time for Changes:
   Measure: Commit to production time
   Elite: < 1 hour
   Target: < 1 day
   Track: Time from commit to deploy

3. Mean Time to Recovery (MTTR):
   Measure: Time to fix production issues
   Elite: < 1 hour
   Target: < 1 day
   Track: Time from incident to resolution

4. Change Failure Rate:
   Measure: % of deploys causing issues
   Elite: < 5%
   Target: < 15%
   Track: Failed deploys / total deploys
```

### Pipeline Health Metrics

```yaml
CI Build Time:
  Target: < 10 minutes
  Warning: > 15 minutes
  Critical: > 30 minutes

CI Success Rate:
  Target: > 95%
  Warning: < 90%
  Track: Successful builds / total builds

Flaky Tests:
  Target: < 1%
  Track: Tests that fail/pass inconsistently

Queue Time:
  Target: < 5 minutes
  Track: Time waiting for runner
```

---

## 🚨 Troubleshooting Guide

### Build Failures

**Problem**: Tests failing in CI but passing locally

**Diagnosis**:
```bash
# Check for environment differences
- Node/Python version mismatch
- Missing environment variables
- Different dependency versions
- Timezone issues
- Race conditions in tests
```

**Solutions**:
```yaml
# 1. Lock Node version
- uses: actions/setup-node@v3
  with:
    node-version-file: '.nvmrc'

# 2. Use exact dependency versions
- run: npm ci # Not npm install

# 3. Set timezone
- env:
    TZ: 'UTC'

# 4. Increase test timeout
- run: npm test -- --testTimeout=10000
```

### Slow Builds

**Problem**: CI taking too long

**Solutions**:
```yaml
# 1. Cache dependencies
- uses: actions/cache@v3
  with:
    path: ~/.npm
    key: ${{ runner.os }}-node-${{ hashFiles('**/package-lock.json') }}

# 2. Run tests in parallel
- run: npm test -- --maxWorkers=4

# 3. Split test suites
- name: Unit tests
  run: npm test -- --testPathPattern="unit"
- name: Integration tests
  run: npm test -- --testPathPattern="integration"

# 4. Use Docker layer caching
- uses: docker/build-push-action@v4
  with:
    cache-from: type=gha
    cache-to: type=gha,mode=max
```

### Deployment Failures

**Problem**: Deployment fails

**Rollback Procedure**:
```yaml
rollback:
  steps:
    - name: Identify last good deployment
      run: kubectl rollout history deployment/app

    - name: Rollback to previous version
      run: kubectl rollout undo deployment/app

    - name: Verify rollback
      run: kubectl rollout status deployment/app

    - name: Notify team
      run: send-alert.sh "Rolled back production"
```

---

## 📋 CI/CD Checklist

### Initial Setup
```markdown
- [ ] CI platform chosen and configured
- [ ] Tests run on every commit
- [ ] Linting enforced
- [ ] Code coverage tracked
- [ ] Branch protection enabled
- [ ] Required reviews configured
- [ ] Build artifacts created
- [ ] Deployment scripts created
```

### Security
```markdown
- [ ] Secrets stored securely (not in code)
- [ ] Dependency scanning enabled
- [ ] SAST tools integrated
- [ ] Container scanning (if using Docker)
- [ ] Access controls configured
- [ ] Audit logging enabled
```

### Deployment
```markdown
- [ ] Staging environment deployed automatically
- [ ] E2E tests run on staging
- [ ] Production deployment configured
- [ ] Rollback procedure documented
- [ ] Monitoring configured
- [ ] Alerts set up
- [ ] Runbook created
```

### Continuous Improvement
```markdown
- [ ] DORA metrics tracked
- [ ] Pipeline performance monitored
- [ ] Flaky tests identified and fixed
- [ ] Build time optimized
- [ ] Team trained on CI/CD process
```

---

## 🎓 Best Practices

### Do's ✅

1. **Keep pipelines fast** (< 10 minutes for CI)
2. **Fail fast** (run cheap checks first)
3. **Make builds reproducible** (same input = same output)
4. **Use caching** (dependencies, Docker layers)
5. **Parallelize tests** (faster feedback)
6. **Version everything** (config as code)
7. **Monitor pipeline health** (track metrics)
8. **Automate rollbacks** (quick recovery)
9. **Test the pipeline** (pipeline code is code too)
10. **Document the process** (runbooks, playbooks)

### Don'ts ❌

1. **Don't commit secrets** (use secret management)
2. **Don't skip tests** (defeats the purpose)
3. **Don't ignore flaky tests** (fix or delete them)
4. **Don't deploy on Friday afternoon** (unless necessary)
5. **Don't manually edit production** (always deploy via CI/CD)
6. **Don't ignore metrics** (data drives improvement)
7. **Don't have single point of failure** (redundancy)
8. **Don't forget monitoring** (observability is critical)

---

## 🔗 Related Resources

- [Deployment Playbook](../deployment/deployment-playbook.md)
- [Incident Response](../incident-response/incident-response-playbook.md)
- [Testing Guide](../../quality-assurance/testing/testing-pyramid.md)

---

**Version**: 1.0
**Last Updated**: 2025-11-19
**Maintained By**: DevOps Team
**Based On**: DORA research, Google SRE practices, DevOps Handbook
