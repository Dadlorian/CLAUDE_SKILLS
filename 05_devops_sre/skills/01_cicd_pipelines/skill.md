# CI/CD Pipelines - Elite Professional Practices

**Automated software delivery from commit to production**

---

## Overview

You are an expert in designing, implementing, and optimizing CI/CD (Continuous Integration/Continuous Delivery) pipelines. Your expertise covers the complete automation of software builds, testing, and deployments, based on practices from industry leaders like Google, Netflix, Amazon, GitHub, GitLab, and other tier-1 organizations.

## Core Competencies

### Continuous Integration (CI)

**Principles**:
- Developers integrate code into trunk/main at least daily
- Every commit triggers an automated build
- Builds are fast (< 10 minutes ideal, < 30 minutes acceptable)
- Builds are reliable and repeatable
- Fail fast: stop on first failure for quick feedback

**Build Pipeline Stages**:
1. **Source Checkout**: Clone repository at specific commit
2. **Dependency Resolution**: Install libraries, packages, tools
3. **Compilation**: Compile code (for compiled languages)
4. **Unit Tests**: Fast, isolated tests (< 5 minutes)
5. **Static Analysis**: Linting, code quality, security scanning
6. **Artifact Creation**: Build Docker images, JAR files, binaries
7. **Artifact Storage**: Push to registry (Docker Hub, ECR, Artifactory)

### Continuous Delivery (CD)

**Principles**:
- Software is always in a deployable state
- Deployment to any environment is automated
- Build once, deploy many times (immutable artifacts)
- Environment parity (dev, staging, prod are similar)
- Progressive delivery (canary, blue-green, feature flags)

**Deployment Pipeline Stages**:
1. **Environment Preparation**: Provision infrastructure, configure services
2. **Artifact Deployment**: Deploy pre-built artifacts to environment
3. **Database Migrations**: Apply schema changes safely
4. **Configuration Management**: Apply environment-specific configs
5. **Smoke Tests**: Verify critical functionality works
6. **Integration Tests**: E2E tests in deployed environment
7. **Performance Tests**: Load and performance validation
8. **Security Scanning**: DAST, penetration testing
9. **Approval Gates**: Manual or automated approval for production
10. **Production Deployment**: Deploy to production with rollback capability
11. **Post-Deployment Validation**: Health checks, metrics verification
12. **Observability**: Monitor metrics, logs, traces

## Technology Stack

### CI/CD Platforms

**Jenkins**
- Open-source automation server
- Extensive plugin ecosystem (1,800+ plugins)
- Pipeline as Code (Jenkinsfile, Groovy DSL)
- Distributed builds with agents
- Integration with virtually every tool

**GitLab CI/CD**
- Integrated with GitLab SCM
- YAML-based pipeline definition (.gitlab-ci.yml)
- Built-in container registry and package registry
- Auto DevOps for zero-config pipelines
- Merge request pipelines and review apps

**GitHub Actions**
- Native GitHub automation
- YAML workflow definition
- Marketplace with 10,000+ actions
- Matrix builds for testing across platforms
- Reusable workflows and composite actions

**CircleCI**
- Cloud-native CI/CD
- Docker-first design
- Orbs for reusable configuration
- SSH debugging into failed builds
- Workflow orchestration

**ArgoCD**
- GitOps continuous delivery for Kubernetes
- Declarative GitOps CD
- Automated drift detection and sync
- Multi-cluster support
- Web UI and CLI

**Tekton**
- Kubernetes-native CI/CD framework
- Cloud Native Computing Foundation (CNCF) project
- Standardized CI/CD building blocks
- Reusable tasks and pipelines
- Integration with other CNCF projects

**Spinnaker**
- Multi-cloud continuous delivery
- Created by Netflix, contributed to Linux Foundation
- Advanced deployment strategies (canary, blue-green, rolling)
- Multi-cloud support (AWS, GCP, Azure, Kubernetes)
- Automated canary analysis

### Build Tools

**Language-Specific**:
- **Java/JVM**: Maven, Gradle, Ant
- **JavaScript/Node.js**: npm, Yarn, pnpm, Webpack, Vite
- **Python**: pip, Poetry, setuptools, build
- **Go**: go build, Mage
- **Rust**: Cargo
- **C/C++**: Make, CMake, Bazel
- **.NET**: MSBuild, dotnet CLI

**Multi-Language/Monorepo**:
- **Bazel**: Google's build system, fast and correct builds
- **Nx**: Monorepo build system with intelligent caching
- **Turborepo**: High-performance build system for JavaScript/TypeScript monorepos

### Artifact Repositories

**Container Registries**:
- Docker Hub, Amazon ECR, Google Container Registry (GCR), Azure Container Registry (ACR), GitHub Container Registry (GHCR)

**Package Repositories**:
- **Multi-Format**: JFrog Artifactory, Sonatype Nexus
- **Language-Specific**: npm registry, PyPI, Maven Central, NuGet

**Binary Artifacts**:
- AWS S3, Google Cloud Storage, Azure Blob Storage

### Testing Frameworks

**Unit Testing**:
- **Java**: JUnit, TestNG, Mockito
- **JavaScript**: Jest, Mocha, Vitest
- **Python**: pytest, unittest, mock
- **Go**: testing package, testify
- **C#**: NUnit, xUnit

**Integration Testing**:
- **API Testing**: Postman/Newman, REST Assured, Supertest
- **Database**: Testcontainers, in-memory databases
- **Contract Testing**: Pact, Spring Cloud Contract

**End-to-End Testing**:
- **Web**: Selenium, Playwright, Cypress, Puppeteer
- **Mobile**: Appium, Detox, XCUITest, Espresso
- **API**: Postman, REST Assured, k6

**Performance Testing**:
- k6, JMeter, Gatling, Locust, Artillery

**Security Testing**:
- **SAST**: SonarQube, Checkmarx, Semgrep, CodeQL
- **DAST**: OWASP ZAP, Burp Suite
- **Dependency Scanning**: Snyk, Dependabot, WhiteSource
- **Container Scanning**: Trivy, Snyk, Aqua, Clair
- **Secrets Detection**: GitGuardian, TruffleHog, Gitleaks

## Pipeline Design Patterns

### 1. Trunk-Based Development Pipeline

**Strategy**: All developers commit to trunk (main branch) frequently

```yaml
# .gitlab-ci.yml example
stages:
  - build
  - test
  - package
  - deploy-dev
  - deploy-staging
  - deploy-production

variables:
  IMAGE_TAG: $CI_COMMIT_SHA

# Build stage: compile and create artifacts
build:
  stage: build
  script:
    - mvn clean compile
  artifacts:
    paths:
      - target/
    expire_in: 1 hour

# Test stage: unit and integration tests
test:unit:
  stage: test
  script:
    - mvn test
  coverage: '/Total.*?([0-9]{1,3})%/'

test:integration:
  stage: test
  services:
    - postgres:14
  script:
    - mvn verify -P integration-tests

# Package stage: create Docker image
package:
  stage: package
  script:
    - docker build -t $CI_REGISTRY_IMAGE:$IMAGE_TAG .
    - docker push $CI_REGISTRY_IMAGE:$IMAGE_TAG

# Deploy to dev: automatic on every commit
deploy:dev:
  stage: deploy-dev
  script:
    - kubectl set image deployment/app app=$CI_REGISTRY_IMAGE:$IMAGE_TAG -n dev
  environment:
    name: development
    url: https://dev.example.com

# Deploy to staging: automatic on main branch
deploy:staging:
  stage: deploy-staging
  script:
    - kubectl set image deployment/app app=$CI_REGISTRY_IMAGE:$IMAGE_TAG -n staging
  environment:
    name: staging
    url: https://staging.example.com
  only:
    - main

# Deploy to production: manual approval required
deploy:production:
  stage: deploy-production
  script:
    - kubectl set image deployment/app app=$CI_REGISTRY_IMAGE:$IMAGE_TAG -n production
  environment:
    name: production
    url: https://example.com
  when: manual
  only:
    - main
```

### 2. Feature Branch Pipeline

**Strategy**: Feature development in branches, merge to main when complete

```yaml
# GitHub Actions example
name: CI/CD Pipeline

on:
  push:
    branches: [ main, 'feature/**' ]
  pull_request:
    branches: [ main ]

jobs:
  build-and-test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Set up Node.js
        uses: actions/setup-node@v3
        with:
          node-version: '18'
          cache: 'npm'

      - name: Install dependencies
        run: npm ci

      - name: Run linter
        run: npm run lint

      - name: Run unit tests
        run: npm test -- --coverage

      - name: Upload coverage
        uses: codecov/codecov-action@v3

      - name: Build application
        run: npm run build

  deploy-preview:
    needs: build-and-test
    if: github.event_name == 'pull_request'
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Deploy preview environment
        run: |
          # Create ephemeral preview environment
          ./scripts/deploy-preview.sh ${{ github.event.pull_request.number }}

      - name: Comment on PR
        uses: actions/github-script@v6
        with:
          script: |
            github.rest.issues.createComment({
              issue_number: context.issue.number,
              owner: context.repo.owner,
              repo: context.repo.repo,
              body: '✅ Preview deployed to https://pr-${{ github.event.pull_request.number }}.preview.example.com'
            })

  deploy-production:
    needs: build-and-test
    if: github.ref == 'refs/heads/main'
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Build and push Docker image
        run: |
          docker build -t myapp:${{ github.sha }} .
          docker tag myapp:${{ github.sha }} myregistry/myapp:latest
          docker push myregistry/myapp:${{ github.sha }}
          docker push myregistry/myapp:latest

      - name: Deploy to production
        run: |
          kubectl set image deployment/myapp myapp=myregistry/myapp:${{ github.sha }}
```

### 3. Monorepo Pipeline with Selective Builds

**Strategy**: Only build and test what changed

```yaml
# Using Nx for selective builds
name: Monorepo CI

on: [push, pull_request]

jobs:
  main:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
        with:
          fetch-depth: 0  # Full history for affected detection

      - name: Derive appropriate SHAs
        uses: nrwl/nx-set-shas@v3

      - name: Install dependencies
        run: npm ci

      - name: Run affected tests
        run: npx nx affected --target=test --parallel=3

      - name: Run affected builds
        run: npx nx affected --target=build --parallel=3

      - name: Run affected lints
        run: npx nx affected --target=lint --parallel=3
```

### 4. Security-First Pipeline

**Strategy**: Security scanning at every stage

```yaml
stages:
  - security-check
  - build
  - test
  - security-scan
  - deploy

# Secrets scanning: prevent credentials from being committed
secrets-scan:
  stage: security-check
  script:
    - gitleaks detect --source . --verbose
  allow_failure: false

# Dependency vulnerability scanning
dependency-scan:
  stage: security-check
  script:
    - npm audit --audit-level=moderate
    - snyk test --severity-threshold=high

# SAST: Static application security testing
sast:
  stage: test
  script:
    - semgrep --config=auto --error
  artifacts:
    reports:
      sast: gl-sast-report.json

# Container image scanning
container-scan:
  stage: security-scan
  script:
    - trivy image --severity HIGH,CRITICAL myapp:$CI_COMMIT_SHA
    - docker scan myapp:$CI_COMMIT_SHA

# DAST: Dynamic application security testing
dast:
  stage: security-scan
  script:
    - zap-baseline.py -t https://staging.example.com -r zap-report.html
  artifacts:
    paths:
      - zap-report.html

# Infrastructure security scanning
iac-scan:
  stage: security-check
  script:
    - tfsec .
    - checkov -d terraform/
```

## Best Practices

### 1. Pipeline Performance Optimization

**Parallelization**:
```yaml
# Run independent stages in parallel
test:
  parallel:
    matrix:
      - NODE_VERSION: [14, 16, 18]
        OS: [ubuntu, macos, windows]
```

**Caching**:
```yaml
# Cache dependencies between runs
cache:
  paths:
    - node_modules/
    - .npm/
  key:
    files:
      - package-lock.json
```

**Incremental Builds**:
- Only rebuild what changed (Bazel, Nx, Turborepo)
- Use build caches (Docker layer caching, Gradle cache)
- Parallelize test execution

**Resource Optimization**:
- Right-size CI runners (don't over-provision)
- Use spot instances for cost savings
- Shutdown preview environments after inactivity

### 2. Fast Feedback Loops

**Fail Fast**:
- Run fastest tests first (unit → integration → E2E)
- Stop pipeline on first failure
- Provide clear error messages

**Pipeline Visibility**:
- Status badges in README
- Slack/Teams notifications on failures
- Dashboard with pipeline metrics

**Developer Experience**:
- Local pipeline execution (act for GitHub Actions, gitlab-runner for GitLab)
- Pre-commit hooks for quick feedback
- Fast builds (< 10 minutes ideal)

### 3. Pipeline as Code

**Version Control**:
- Store pipeline definitions in Git (Jenkinsfile, .gitlab-ci.yml, .github/workflows)
- Review pipeline changes like code
- Test pipeline changes in feature branches

**Modularity**:
- Reusable pipeline components (GitHub Actions, GitLab includes, Jenkins shared libraries)
- DRY principles: don't repeat yourself
- Template pipelines for common patterns

**Documentation**:
- Comment complex pipeline logic
- Document pipeline stages and their purpose
- Link to runbooks for debugging

### 4. Security and Compliance

**Secrets Management**:
- Never hardcode secrets in pipeline code
- Use CI/CD platform secret management (GitHub Secrets, GitLab CI/CD Variables, Jenkins Credentials)
- Rotate secrets regularly
- Audit secret access

**Access Control**:
- Least privilege for CI/CD service accounts
- Protected branches require reviews
- Production deployments require approval
- Audit logs for all pipeline runs

**Compliance**:
- Evidence collection for audits (test results, security scans, approvals)
- Immutable audit trail
- Compliance gates (e.g., must pass security scan)

### 5. Deployment Strategies

**Blue-Green Deployment**:
- Maintain two identical environments
- Switch traffic atomically
- Instant rollback capability

**Canary Deployment**:
- Gradual rollout (1% → 10% → 50% → 100%)
- Monitor metrics during rollout
- Automated rollback on regression

**Feature Flags**:
- Deploy code dark, enable features progressively
- A/B testing and gradual rollout
- Kill switch for problematic features

**Database Migrations**:
- Backward-compatible migrations
- Separate migration from deployment
- Test migrations in staging first

## Metrics and Monitoring

### Pipeline Metrics

**Performance Metrics**:
- Build duration (p50, p95, p99)
- Queue time (time waiting for runner)
- Success rate (percentage of successful builds)
- Flakiness rate (tests that fail intermittently)

**DORA Metrics**:
- Deployment frequency (elite: multiple per day)
- Lead time for changes (elite: < 1 hour)
- Change failure rate (elite: 0-15%)
- Time to restore service (elite: < 1 hour)

**Cost Metrics**:
- CI/CD infrastructure costs
- Cost per build/deployment
- Resource utilization

### Monitoring Tools

**Dashboards**:
- Grafana for pipeline metrics visualization
- Built-in dashboards (GitLab CI/CD Analytics, GitHub Insights)
- Custom dashboards for team-specific metrics

**Alerts**:
- Alert on pipeline failures (Slack, email, PagerDuty)
- Alert on degraded performance (build time > threshold)
- Alert on security vulnerabilities found

## Troubleshooting Common Issues

### Slow Pipelines

**Diagnosis**:
- Identify bottleneck stages (which stage takes longest?)
- Check for sequential stages that could be parallel
- Review cache effectiveness

**Solutions**:
- Parallelize independent stages
- Optimize test execution (parallel tests, selective tests)
- Use faster build tools (Bazel, esbuild, swc)
- Increase runner resources

### Flaky Tests

**Diagnosis**:
- Track test failure patterns (which tests fail intermittently?)
- Check for timing issues, race conditions
- Review test isolation (are tests independent?)

**Solutions**:
- Quarantine flaky tests temporarily
- Fix or rewrite flaky tests
- Increase test timeouts for slow operations
- Use test retry mechanisms sparingly (fix root cause instead)

### Security Scan Failures

**Diagnosis**:
- Review security scan reports
- Identify vulnerable dependencies or code patterns

**Solutions**:
- Update dependencies to patched versions
- Apply security patches
- Suppress false positives with justification
- Refactor code to eliminate vulnerabilities

## Real-World Examples

### Google
- Trunk-based development with all code in monorepo
- Automated testing at massive scale (100M+ tests per day)
- Build and test infrastructure (Bazel, Forge)
- Continuous deployment with progressive rollouts

### Netflix
- Spinnaker for multi-cloud continuous delivery
- Automated canary analysis with statistical comparison
- Chaos engineering integrated into pipelines
- Fast feedback loops enable 4,000+ deployments per day

### Etsy
- Continuous deployment since 2009
- Deploys 50+ times per day to production
- Feature flags for progressive rollout
- ChatOps for deployment visibility

### Shopify
- Monorepo with selective builds (only build what changed)
- Comprehensive test suite with parallelization
- Shipit for deployment orchestration
- Focus on developer productivity

## Getting Started

### Checklist for New CI/CD Pipeline

- [ ] Pipeline runs on every commit
- [ ] Build is fast (< 10 minutes)
- [ ] Automated tests run in pipeline (unit, integration)
- [ ] Security scanning integrated (SAST, dependency scan, secrets scan)
- [ ] Artifacts are versioned and stored
- [ ] Deployment to staging is automated
- [ ] Production deployment has approval gate
- [ ] Rollback procedure is documented and tested
- [ ] Pipeline failures alert the team
- [ ] Pipeline metrics are tracked

### Learning Resources

**Books**:
- "Continuous Delivery" by Jez Humble and David Farley
- "The DevOps Handbook" - CI/CD practices
- "Accelerate" - Research on high-performing teams

**Documentation**:
- GitHub Actions Docs: https://docs.github.com/en/actions
- GitLab CI/CD Docs: https://docs.gitlab.com/ee/ci/
- Jenkins Documentation: https://www.jenkins.io/doc/
- ArgoCD Documentation: https://argo-cd.readthedocs.io/

**Courses**:
- "Continuous Delivery & DevOps" (Coursera)
- "CI/CD with Jenkins" (Udemy)
- "GitHub Actions" (LinkedIn Learning)

---

**Version**: 1.0
**Last Updated**: 2025-11-19
**Expertise Level**: Elite Professional
**Based on**: Industry practices from Google, Netflix, Amazon, GitHub, GitLab
