# Security Testing Tools - Quick Reference

## SAST (Static Application Security Testing)

### SonarQube
```bash
# Run SonarQube scan
sonar-scanner \
  -Dsonar.projectKey=myproject \
  -Dsonar.sources=./src \
  -Dsonar.host.url=https://sonarqube.example.com \
  -Dsonar.login=$SONAR_TOKEN

# Quality gate check
sonar-scanner \
  -Dsonar.qualitygate.wait=true \
  -Dsonar.qualitygate.timeout=300
```

### Semgrep
```bash
# Auto-detect languages and scan
semgrep --config=auto .

# Scan with specific rulesets
semgrep --config=p/owasp-top-ten \
  --config=p/security-audit \
  --json --output=results.json

# Custom rules
semgrep --config=rules/custom-rules.yml src/
```

### CodeQL
```bash
# Create database
codeql database create myapp-db --language=javascript

# Run analysis
codeql database analyze myapp-db \
  javascript-security-and-quality.qls \
  --format=sarif-latest \
  --output=results.sarif

# Query specific vulnerability
codeql query run queries/sql-injection.ql \
  --database=myapp-db
```

## DAST (Dynamic Application Security Testing)

### OWASP ZAP
```bash
# Quick scan
zap-cli quick-scan --self-contained \
  --start-options '-config api.key=12345' \
  https://app.example.com

# Full scan with authentication
zap-cli open-url https://app.example.com
zap-cli spider https://app.example.com
zap-cli active-scan https://app.example.com
zap-cli report -o zap-report.html -f html
```

### Burp Suite
```bash
# Command-line scan
java -jar burp-rest-api.jar \
  --project-file=project.burp \
  --config-file=scan-config.json

# Scan specific URL
burp-cli scan \
  --url https://app.example.com \
  --scan-type active \
  --report-file report.html
```

### Nuclei
```bash
# Scan with all templates
nuclei -u https://app.example.com \
  -t exposures/ -t cves/ -t vulnerabilities/ \
  -severity critical,high,medium

# Custom templates
nuclei -u https://app.example.com \
  -t custom-templates/ \
  -json -o results.json
```

## SCA (Software Composition Analysis)

### Snyk
```bash
# Test all projects
snyk test --all-projects \
  --severity-threshold=high \
  --json > snyk-results.json

# Monitor for new vulnerabilities
snyk monitor

# Fix vulnerabilities automatically
snyk fix
```

### OWASP Dependency-Check
```bash
# Scan dependencies
dependency-check \
  --scan ./target \
  --format JSON \
  --format HTML \
  --suppression suppression.xml \
  --out reports/
```

### npm audit / pip-audit
```bash
# Node.js
npm audit --audit-level=moderate
npm audit fix

# Python
pip-audit --fix
```

## Container Scanning

### Trivy
```bash
# Scan container image
trivy image \
  --severity HIGH,CRITICAL \
  --format json \
  myapp:latest

# Scan filesystem
trivy fs --security-checks vuln,config .

# Scan Kubernetes
trivy k8s --report summary cluster
```

### Grype
```bash
# Scan image
grype myapp:latest \
  --fail-on critical \
  --output json > grype-results.json

# Scan SBOM
syft myapp:latest -o json > sbom.json
grype sbom:sbom.json
```

## Secret Scanning

### GitLeaks
```bash
# Scan repository
gitleaks detect --source . \
  --report-path gitleaks-report.json

# Scan commits
gitleaks protect --staged
```

### TruffleHog
```bash
# Scan git history
trufflehog git https://github.com/org/repo \
  --json --only-verified

# Scan filesystem
trufflehog filesystem /path/to/code \
  --json > secrets.json
```

## CI/CD Integration

### GitHub Actions
```yaml
name: Security Scan
on: [push, pull_request]

jobs:
  security:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: SAST - Semgrep
        uses: returntocorp/semgrep-action@v1

      - name: SCA - Snyk
        uses: snyk/actions/node@master
        env:
          SNYK_TOKEN: ${{ secrets.SNYK_TOKEN }}

      - name: Secrets - GitLeaks
        uses: gitleaks/gitleaks-action@v2

      - name: Container - Trivy
        uses: aquasecurity/trivy-action@master
        with:
          image-ref: myapp:${{ github.sha }}
```

## Comparison Matrix

| Tool | Type | Languages | Speed | Accuracy | Cost |
|------|------|-----------|-------|----------|------|
| SonarQube | SAST | 27+ | Medium | High | Free/Paid |
| Semgrep | SAST | 30+ | Fast | High | Free/Paid |
| CodeQL | SAST | 10+ | Slow | Very High | Free (OSS) |
| OWASP ZAP | DAST | All | Medium | Medium | Free |
| Burp Suite | DAST | All | Medium | High | Paid |
| Snyk | SCA | All | Fast | High | Free/Paid |
| Trivy | Container | All | Fast | High | Free |

---

**Best Practice**: Use multiple tools in combination for comprehensive coverage.
