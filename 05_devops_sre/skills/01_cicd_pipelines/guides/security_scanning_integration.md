# Security Scanning Integration Guide

## Introduction

Security scanning in CI/CD pipelines helps identify vulnerabilities early in the development process. This guide covers implementing multiple types of security scanning: SAST, DAST, dependency scanning, secret scanning, and container scanning.

## Types of Security Scanning

| Type | What It Scans | When to Run | Examples |
|------|---------------|-------------|----------|
| **SAST** | Source code for vulnerabilities | On every commit | SonarQube, Semgrep |
| **DAST** | Running application | After deployment | OWASP ZAP, Burp Suite |
| **Dependency Scanning** | Third-party libraries | On every commit | Snyk, npm audit |
| **Secret Scanning** | Hardcoded secrets | On every commit | GitLeaks, TruffleHog |
| **Container Scanning** | Docker images | After image build | Trivy, Clair |
| **License Scanning** | Open source licenses | On every commit | FOSSA, License Finder |

## Part 1: Static Application Security Testing (SAST)

SAST analyzes source code without executing it to find security vulnerabilities.

### Option 1: SonarQube

#### Setup SonarQube Server

```bash
# Using Docker
docker run -d --name sonarqube \
  -p 9000:9000 \
  -e SONAR_ES_BOOTSTRAP_CHECKS_DISABLE=true \
  sonarqube:latest
```

Access at `http://localhost:9000` (default credentials: admin/admin)

#### GitHub Actions Integration

```yaml
name: SonarQube Scan

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  sonarqube:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0  # Full history for better analysis

      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: '18'

      - name: Install dependencies
        run: npm ci

      - name: Run tests with coverage
        run: npm test -- --coverage

      - name: SonarQube Scan
        uses: sonarsource/sonarqube-scan-action@master
        env:
          SONAR_TOKEN: ${{ secrets.SONAR_TOKEN }}
          SONAR_HOST_URL: ${{ secrets.SONAR_HOST_URL }}

      - name: SonarQube Quality Gate
        uses: sonarsource/sonarqube-quality-gate-action@master
        timeout-minutes: 5
        env:
          SONAR_TOKEN: ${{ secrets.SONAR_TOKEN }}
```

#### GitLab CI Integration

```yaml
sonarqube-check:
  stage: test
  image:
    name: sonarsource/sonar-scanner-cli:latest
    entrypoint: [""]
  variables:
    SONAR_USER_HOME: "${CI_PROJECT_DIR}/.sonar"
    GIT_DEPTH: "0"
  cache:
    key: "${CI_JOB_NAME}"
    paths:
      - .sonar/cache
  script:
    - sonar-scanner
  allow_failure: true
  only:
    - main
    - develop
    - merge_requests
```

Create `sonar-project.properties`:
```properties
sonar.projectKey=my-project
sonar.projectName=My Project
sonar.projectVersion=1.0
sonar.sources=src
sonar.tests=tests
sonar.javascript.lcov.reportPaths=coverage/lcov.info
sonar.coverage.exclusions=**/*.test.js,**/*.spec.js
```

#### Jenkins Integration

```groovy
stage('SonarQube Analysis') {
    steps {
        script {
            def scannerHome = tool 'SonarScanner'
            withSonarQubeEnv('SonarQube') {
                sh "${scannerHome}/bin/sonar-scanner"
            }
        }
    }
}

stage('Quality Gate') {
    steps {
        timeout(time: 5, unit: 'MINUTES') {
            waitForQualityGate abortPipeline: true
        }
    }
}
```

### Option 2: Semgrep (Fast, Open Source)

#### GitHub Actions

```yaml
name: Semgrep

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  semgrep:
    runs-on: ubuntu-latest
    container:
      image: returntocorp/semgrep

    steps:
      - uses: actions/checkout@v4

      - name: Run Semgrep
        run: semgrep scan --config=auto --sarif > semgrep-results.sarif

      - name: Upload results to GitHub Security
        uses: github/codeql-action/upload-sarif@v2
        with:
          sarif_file: semgrep-results.sarif
```

#### GitLab CI

```yaml
semgrep:
  stage: test
  image: returntocorp/semgrep
  script:
    - semgrep scan --config=auto --json > semgrep-results.json
  artifacts:
    reports:
      sast: semgrep-results.json
```

## Part 2: Dependency Scanning

Scan third-party dependencies for known vulnerabilities.

### Option 1: npm audit (Node.js)

#### GitHub Actions

```yaml
name: Dependency Scan

on: [push, pull_request]

jobs:
  dependency-scan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-node@v4
        with:
          node-version: '18'

      - name: Install dependencies
        run: npm ci

      - name: Run npm audit
        run: npm audit --audit-level=moderate
        continue-on-error: true

      - name: Generate audit report
        run: npm audit --json > npm-audit.json
        continue-on-error: true

      - name: Upload audit results
        uses: actions/upload-artifact@v4
        with:
          name: npm-audit-report
          path: npm-audit.json
```

#### GitLab CI

```yaml
dependency-scan:
  stage: test
  image: node:18
  script:
    - npm ci
    - npm audit --audit-level=moderate
  allow_failure: true
```

### Option 2: Snyk

#### GitHub Actions

```yaml
name: Snyk Security Scan

on: [push, pull_request]

jobs:
  snyk:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Run Snyk to check for vulnerabilities
        uses: snyk/actions/node@master
        env:
          SNYK_TOKEN: ${{ secrets.SNYK_TOKEN }}
        with:
          args: --severity-threshold=high

      - name: Upload Snyk results to GitHub Security
        uses: github/codeql-action/upload-sarif@v2
        with:
          sarif_file: snyk.sarif
```

#### GitLab CI

```yaml
snyk-scan:
  stage: test
  image: node:18
  before_script:
    - npm install -g snyk
  script:
    - npm ci
    - snyk auth $SNYK_TOKEN
    - snyk test --severity-threshold=high
    - snyk monitor  # Send results to Snyk dashboard
  allow_failure: true
```

#### Jenkins

```groovy
stage('Snyk Security Scan') {
    steps {
        snykSecurity(
            snykInstallation: 'Snyk',
            snykTokenId: 'snyk-api-token',
            severity: 'high',
            failOnIssues: false
        )
    }
}
```

### Option 3: OWASP Dependency-Check

#### GitHub Actions

```yaml
name: OWASP Dependency Check

on: [push, pull_request]

jobs:
  dependency-check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Run OWASP Dependency Check
        uses: dependency-check/Dependency-Check_Action@main
        with:
          project: 'my-project'
          path: '.'
          format: 'HTML'
          args: >
            --failOnCVSS 7
            --enableRetired

      - name: Upload results
        uses: actions/upload-artifact@v4
        with:
          name: dependency-check-report
          path: reports/dependency-check-report.html
```

## Part 3: Secret Scanning

Detect hardcoded secrets and credentials in code.

### Option 1: GitLeaks

#### GitHub Actions

```yaml
name: Secret Scanning

on: [push, pull_request]

jobs:
  gitleaks:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0

      - name: Run Gitleaks
        uses: gitleaks/gitleaks-action@v2
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
          GITLEAKS_LICENSE: ${{ secrets.GITLEAKS_LICENSE }}
```

#### GitLab CI

```yaml
gitleaks:
  stage: test
  image: zricethezav/gitleaks:latest
  script:
    - gitleaks detect --source . --verbose --redact
  allow_failure: false  # Fail pipeline if secrets found
```

#### Jenkins

```groovy
stage('Secret Scanning') {
    steps {
        sh '''
            docker run --rm -v $(pwd):/path zricethezav/gitleaks:latest \
              detect --source /path --verbose --redact
        '''
    }
}
```

### Custom .gitleaks.toml Configuration

```toml
title = "Gitleaks config"

[extend]
useDefault = true

[[rules]]
id = "custom-api-key"
description = "Custom API Key"
regex = '''(?i)api[_-]?key[_-]?[=:]\s*['"]?[a-z0-9]{32,}['"]?'''

[[rules]]
id = "aws-access-key"
description = "AWS Access Key"
regex = '''AKIA[0-9A-Z]{16}'''

[allowlist]
description = "Allowlist"
paths = [
  '''\.git/''',
  '''node_modules/''',
  '''vendor/''',
]
```

### Option 2: TruffleHog

```yaml
# GitHub Actions
name: TruffleHog Scan

on: [push, pull_request]

jobs:
  trufflehog:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0

      - name: TruffleHog Scan
        uses: trufflesecurity/trufflehog@main
        with:
          path: ./
          base: main
          head: HEAD
```

## Part 4: Container Security Scanning

Scan Docker images for vulnerabilities.

### Option 1: Trivy

#### GitHub Actions

```yaml
name: Container Scan

on:
  push:
    branches: [ main ]

jobs:
  build-and-scan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Build Docker image
        run: docker build -t myapp:${{ github.sha }} .

      - name: Run Trivy vulnerability scanner
        uses: aquasecurity/trivy-action@master
        with:
          image-ref: 'myapp:${{ github.sha }}'
          format: 'sarif'
          output: 'trivy-results.sarif'
          severity: 'CRITICAL,HIGH'

      - name: Upload Trivy results to GitHub Security
        uses: github/codeql-action/upload-sarif@v2
        with:
          sarif_file: 'trivy-results.sarif'

      - name: Fail on high/critical vulnerabilities
        uses: aquasecurity/trivy-action@master
        with:
          image-ref: 'myapp:${{ github.sha }}'
          format: 'table'
          exit-code: '1'
          ignore-unfixed: true
          severity: 'CRITICAL,HIGH'
```

#### GitLab CI

```yaml
container-scan:
  stage: test
  image: docker:latest
  services:
    - docker:dind
  variables:
    DOCKER_DRIVER: overlay2
    IMAGE: $CI_REGISTRY_IMAGE:$CI_COMMIT_SHA
  before_script:
    - docker login -u $CI_REGISTRY_USER -p $CI_REGISTRY_PASSWORD $CI_REGISTRY
  script:
    - docker build -t $IMAGE .
    - docker run --rm -v /var/run/docker.sock:/var/run/docker.sock
        aquasec/trivy image --severity HIGH,CRITICAL $IMAGE
```

#### Jenkins

```groovy
stage('Build Docker Image') {
    steps {
        script {
            docker.build("myapp:${env.BUILD_NUMBER}")
        }
    }
}

stage('Scan Docker Image') {
    steps {
        sh """
            docker run --rm -v /var/run/docker.sock:/var/run/docker.sock \
              aquasec/trivy image --severity HIGH,CRITICAL \
              myapp:${env.BUILD_NUMBER}
        """
    }
}
```

### Option 2: Clair

```yaml
# GitLab CI with Clair
include:
  - template: Container-Scanning.gitlab-ci.yml

container_scanning:
  variables:
    CS_IMAGE: $CI_REGISTRY_IMAGE:$CI_COMMIT_SHA
```

## Part 5: Dynamic Application Security Testing (DAST)

Test running applications for vulnerabilities.

### OWASP ZAP

#### GitHub Actions

```yaml
name: DAST Scan

on:
  workflow_dispatch:
  schedule:
    - cron: '0 2 * * *'  # Daily at 2 AM

jobs:
  zap-scan:
    runs-on: ubuntu-latest
    steps:
      - name: ZAP Baseline Scan
        uses: zaproxy/action-baseline@v0.7.0
        with:
          target: 'https://staging.example.com'
          rules_file_name: '.zap/rules.tsv'
          cmd_options: '-a'

      - name: Upload ZAP results
        uses: actions/upload-artifact@v4
        with:
          name: zap-report
          path: report_html.html
```

#### GitLab CI

```yaml
dast:
  stage: test
  image: owasp/zap2docker-stable
  script:
    - mkdir -p /zap/wrk
    - zap-baseline.py -t https://staging.example.com -r zap-report.html
  artifacts:
    paths:
      - zap-report.html
    expire_in: 1 week
  only:
    - schedules
```

#### Create ZAP Rules File (.zap/rules.tsv)

```tsv
10010	IGNORE	(Cookie No HttpOnly Flag)
10011	IGNORE	(Cookie Without Secure Flag)
```

## Part 6: License Compliance Scanning

### FOSSA

#### GitHub Actions

```yaml
name: License Scan

on: [push, pull_request]

jobs:
  fossa:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Run FOSSA scan
        uses: fossas/fossa-action@main
        with:
          api-key: ${{ secrets.FOSSA_API_KEY }}
```

### License Checker (Node.js)

```yaml
license-check:
  stage: test
  image: node:18
  script:
    - npm ci
    - npx license-checker --production --onlyAllow "MIT;Apache-2.0;BSD-3-Clause;ISC"
```

## Part 7: Comprehensive Security Pipeline

### Complete Example (GitHub Actions)

```yaml
name: Security Pipeline

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]
  schedule:
    - cron: '0 2 * * *'  # Daily scans

jobs:
  # SAST
  sast:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: returntocorp/semgrep-action@v1

  # Dependency Scanning
  dependency-scan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: snyk/actions/node@master
        env:
          SNYK_TOKEN: ${{ secrets.SNYK_TOKEN }}

  # Secret Scanning
  secret-scan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0
      - uses: gitleaks/gitleaks-action@v2

  # Container Scanning
  container-scan:
    runs-on: ubuntu-latest
    needs: [sast, dependency-scan, secret-scan]
    steps:
      - uses: actions/checkout@v4
      - run: docker build -t myapp:${{ github.sha }} .
      - uses: aquasecurity/trivy-action@master
        with:
          image-ref: 'myapp:${{ github.sha }}'
          exit-code: '1'
          severity: 'CRITICAL,HIGH'

  # DAST (only on schedule)
  dast:
    runs-on: ubuntu-latest
    if: github.event_name == 'schedule'
    steps:
      - uses: zaproxy/action-baseline@v0.7.0
        with:
          target: 'https://staging.example.com'

  # Security Report
  security-report:
    runs-on: ubuntu-latest
    needs: [sast, dependency-scan, secret-scan, container-scan]
    if: always()
    steps:
      - name: Create summary
        run: |
          echo "## Security Scan Results" >> $GITHUB_STEP_SUMMARY
          echo "- SAST: ${{ needs.sast.result }}" >> $GITHUB_STEP_SUMMARY
          echo "- Dependencies: ${{ needs.dependency-scan.result }}" >> $GITHUB_STEP_SUMMARY
          echo "- Secrets: ${{ needs.secret-scan.result }}" >> $GITHUB_STEP_SUMMARY
          echo "- Container: ${{ needs.container-scan.result }}" >> $GITHUB_STEP_SUMMARY
```

### Complete Example (GitLab CI)

```yaml
stages:
  - security
  - build
  - test

include:
  - template: Security/SAST.gitlab-ci.yml
  - template: Security/Dependency-Scanning.gitlab-ci.yml
  - template: Security/Secret-Detection.gitlab-ci.yml
  - template: Security/Container-Scanning.gitlab-ci.yml

variables:
  SAST_EXCLUDED_PATHS: "spec, test, tests, tmp"
  SECURE_LOG_LEVEL: "info"

# Additional custom scans
semgrep-sast:
  stage: security
  image: returntocorp/semgrep
  script:
    - semgrep scan --config=auto --json > semgrep-results.json
  artifacts:
    reports:
      sast: semgrep-results.json

snyk-dependency-scan:
  stage: security
  image: node:18
  before_script:
    - npm install -g snyk
  script:
    - npm ci
    - snyk auth $SNYK_TOKEN
    - snyk test --json > snyk-results.json
  artifacts:
    reports:
      dependency_scanning: snyk-results.json
  allow_failure: true

gitleaks-secrets:
  stage: security
  image: zricethezav/gitleaks:latest
  script:
    - gitleaks detect --source . --verbose --redact --report-path gitleaks-report.json
  artifacts:
    reports:
      secret_detection: gitleaks-report.json

trivy-container-scan:
  stage: test
  image: docker:latest
  services:
    - docker:dind
  dependencies:
    - build
  script:
    - docker run --rm -v /var/run/docker.sock:/var/run/docker.sock
        aquasec/trivy image --exit-code 1 --severity CRITICAL,HIGH $CI_REGISTRY_IMAGE:$CI_COMMIT_SHA
```

## Part 8: Handling Security Issues

### Failing the Pipeline

```yaml
# GitHub Actions - Strict mode
- name: Security scan (strict)
  run: npm audit --audit-level=moderate
  # No continue-on-error - will fail pipeline

# GitLab CI - Strict mode
security-scan:
  script:
    - npm audit --audit-level=moderate
  allow_failure: false
```

### Warning Without Failing

```yaml
# GitHub Actions - Warning mode
- name: Security scan (warning)
  run: npm audit --audit-level=moderate
  continue-on-error: true

# GitLab CI - Warning mode
security-scan:
  script:
    - npm audit --audit-level=moderate
  allow_failure: true
```

### Conditional Failure

```groovy
// Jenkins - Fail only on critical/high
stage('Security Scan') {
    steps {
        script {
            def result = sh(
                script: 'trivy image --severity CRITICAL,HIGH myapp:latest',
                returnStatus: true
            )
            if (result != 0) {
                error "Critical or High vulnerabilities found!"
            }

            // Still run low/medium scan but don't fail
            sh 'trivy image --severity LOW,MEDIUM myapp:latest'
        }
    }
}
```

## Part 9: Security Dashboard & Reporting

### GitHub Security Advisories

Results automatically appear in:
- Security tab → Code scanning alerts
- Security tab → Dependabot alerts
- Pull request checks

### GitLab Security Dashboard

View at: Security & Compliance → Vulnerability Report

### Custom Reporting

```yaml
# GitHub Actions - Generate custom report
- name: Generate security report
  run: |
    echo "# Security Scan Report" > security-report.md
    echo "## Date: $(date)" >> security-report.md
    echo "" >> security-report.md
    echo "## npm audit" >> security-report.md
    npm audit --json | jq -r '.vulnerabilities | to_entries[] | "- \(.key): \(.value.severity)"' >> security-report.md

- name: Comment PR with report
  uses: actions/github-script@v6
  with:
    script: |
      const fs = require('fs');
      const report = fs.readFileSync('security-report.md', 'utf8');
      github.rest.issues.createComment({
        issue_number: context.issue.number,
        owner: context.repo.owner,
        repo: context.repo.repo,
        body: report
      });
```

## Part 10: Best Practices

### 1. Run Different Scans at Different Times

- **On every commit**: SAST, secret scanning
- **On PR**: SAST, dependency scanning, secret scanning
- **Before deploy**: Full security suite
- **Scheduled**: DAST, full dependency scan

### 2. Set Appropriate Thresholds

```yaml
# Fail on high/critical, warn on medium/low
- run: npm audit --audit-level=high
```

### 3. Keep Scanners Updated

```yaml
# Use latest versions
uses: aquasecurity/trivy-action@master  # or pin to specific version
```

### 4. Suppress False Positives

```yaml
# Trivy ignore file (.trivyignore)
CVE-2021-12345  # False positive, not applicable to our use case
```

### 5. Monitor and Act on Results

- Set up notifications for security issues
- Regular review of security dashboards
- Create tickets for remediation
- Track time-to-fix metrics

## Resources

- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [CIS Docker Benchmark](https://www.cisecurity.org/benchmark/docker)
- [NIST Secure Software Development Framework](https://csrc.nist.gov/publications/detail/sp/800-218/final)
- [Snyk Documentation](https://docs.snyk.io/)
- [Trivy Documentation](https://aquasecurity.github.io/trivy/)

## Conclusion

Security scanning should be an integral part of your CI/CD pipeline. Start with the basics (SAST and dependency scanning), then gradually add more sophisticated scans. Remember:

- **Shift left**: Find security issues early
- **Automate everything**: Don't rely on manual scans
- **Act on results**: Scanning without remediation is pointless
- **Balance security and velocity**: Don't let perfect be the enemy of good
- **Educate your team**: Security is everyone's responsibility
