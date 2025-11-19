# CI/CD Best Practices and Implementation Guide

Comprehensive guide to implementing robust CI/CD pipelines for modern software development.

## Table of Contents

1. [Pipeline Design Principles](#pipeline-design-principles)
2. [GitHub Actions](#github-actions)
3. [GitLab CI](#gitlab-ci)
4. [Jenkins](#jenkins)
5. [Security in CI/CD](#security-in-cicd)
6. [Best Practices](#best-practices)

## Pipeline Design Principles

### Key Concepts

1. **Fast Feedback**: Developers should get results quickly
2. **Fail Fast**: Stop on first error to save resources
3. **Parallelization**: Run independent jobs concurrently
4. **Caching**: Cache dependencies and build artifacts
5. **Idempotency**: Same input = same output
6. **Security**: Scan for vulnerabilities, secrets, and compliance

### Pipeline Stages

```
┌─────────┐    ┌─────────┐    ┌─────────┐    ┌─────────┐    ┌─────────┐
│  Build  │ -> │  Test   │ -> │Security │ -> │ Deploy  │ -> │  Verify │
└─────────┘    └─────────┘    └─────────┘    └─────────┘    └─────────┘
```

**Typical Stages**:
1. **Checkout**: Get code from repository
2. **Build**: Compile, bundle, containerize
3. **Test**: Unit, integration, E2E tests
4. **Security**: SAST, DAST, dependency scanning
5. **Deploy**: Deploy to staging/production
6. **Verify**: Smoke tests, health checks

## GitHub Actions

### Complete CI/CD Pipeline

**.github/workflows/ci-cd.yml**:
```yaml
name: CI/CD Pipeline

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]
  release:
    types: [published]

env:
  NODE_VERSION: '20'
  REGISTRY: ghcr.io
  IMAGE_NAME: ${{ github.repository }}

jobs:
  lint:
    name: Lint Code
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: ${{ env.NODE_VERSION }}
          cache: 'npm'

      - name: Install dependencies
        run: npm ci

      - name: Run ESLint
        run: npm run lint

      - name: Check formatting
        run: npm run format:check

  type-check:
    name: Type Check
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: ${{ env.NODE_VERSION }}
          cache: 'npm'

      - name: Install dependencies
        run: npm ci

      - name: Type check
        run: npm run type-check

  test:
    name: Test
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgres:16
        env:
          POSTGRES_PASSWORD: postgres
          POSTGRES_DB: test
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
        ports:
          - 5432:5432

      redis:
        image: redis:7-alpine
        options: >-
          --health-cmd "redis-cli ping"
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
        ports:
          - 6379:6379

    steps:
      - uses: actions/checkout@v4

      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: ${{ env.NODE_VERSION }}
          cache: 'npm'

      - name: Install dependencies
        run: npm ci

      - name: Run unit tests
        run: npm run test:unit -- --coverage

      - name: Run integration tests
        env:
          DATABASE_URL: postgresql://postgres:postgres@localhost:5432/test
          REDIS_URL: redis://localhost:6379
        run: npm run test:integration

      - name: Upload coverage
        uses: codecov/codecov-action@v3
        with:
          files: ./coverage/coverage-final.json
          flags: unittests
          name: codecov-umbrella

  security:
    name: Security Scanning
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Run Trivy vulnerability scanner
        uses: aquasecurity/trivy-action@master
        with:
          scan-type: 'fs'
          scan-ref: '.'
          format: 'sarif'
          output: 'trivy-results.sarif'

      - name: Upload Trivy results to GitHub Security
        uses: github/codeql-action/upload-sarif@v2
        with:
          sarif_file: 'trivy-results.sarif'

      - name: Run Snyk to check for vulnerabilities
        uses: snyk/actions/node@master
        env:
          SNYK_TOKEN: ${{ secrets.SNYK_TOKEN }}
        with:
          args: --severity-threshold=high

      - name: Check for secrets
        uses: trufflesecurity/trufflehog@main
        with:
          path: ./
          base: ${{ github.event.repository.default_branch }}
          head: HEAD

  build:
    name: Build Docker Image
    needs: [lint, type-check, test, security]
    runs-on: ubuntu-latest
    permissions:
      contents: read
      packages: write
    outputs:
      image-tag: ${{ steps.meta.outputs.tags }}
    steps:
      - uses: actions/checkout@v4

      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v3

      - name: Log in to Container Registry
        uses: docker/login-action@v3
        with:
          registry: ${{ env.REGISTRY }}
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}

      - name: Extract metadata
        id: meta
        uses: docker/metadata-action@v5
        with:
          images: ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}
          tags: |
            type=ref,event=branch
            type=ref,event=pr
            type=semver,pattern={{version}}
            type=semver,pattern={{major}}.{{minor}}
            type=sha,prefix={{branch}}-

      - name: Build and push
        uses: docker/build-push-action@v5
        with:
          context: .
          push: true
          tags: ${{ steps.meta.outputs.tags }}
          labels: ${{ steps.meta.outputs.labels }}
          cache-from: type=gha
          cache-to: type=gha,mode=max

  deploy-staging:
    name: Deploy to Staging
    needs: build
    if: github.ref == 'refs/heads/develop'
    runs-on: ubuntu-latest
    environment:
      name: staging
      url: https://staging.example.com
    steps:
      - uses: actions/checkout@v4

      - name: Configure AWS credentials
        uses: aws-actions/configure-aws-credentials@v4
        with:
          aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
          aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
          aws-region: us-east-1

      - name: Deploy to ECS
        run: |
          aws ecs update-service \
            --cluster staging-cluster \
            --service myapp-service \
            --force-new-deployment

      - name: Wait for deployment
        run: |
          aws ecs wait services-stable \
            --cluster staging-cluster \
            --services myapp-service

  deploy-production:
    name: Deploy to Production
    needs: build
    if: github.event_name == 'release'
    runs-on: ubuntu-latest
    environment:
      name: production
      url: https://example.com
    steps:
      - uses: actions/checkout@v4

      - name: Configure AWS credentials
        uses: aws-actions/configure-aws-credentials@v4
        with:
          aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
          aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
          aws-region: us-east-1

      - name: Blue/Green Deployment
        run: |
          # Deploy to green environment
          aws ecs update-service \
            --cluster production-cluster \
            --service myapp-green \
            --force-new-deployment

          # Wait for green to be healthy
          aws ecs wait services-stable \
            --cluster production-cluster \
            --services myapp-green

          # Switch traffic to green
          aws elbv2 modify-listener \
            --listener-arn ${{ secrets.LOAD_BALANCER_LISTENER_ARN }} \
            --default-actions Type=forward,TargetGroupArn=${{ secrets.GREEN_TARGET_GROUP_ARN }}

  smoke-test:
    name: Smoke Tests
    needs: [deploy-staging]
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Run smoke tests
        run: |
          npx playwright test --grep @smoke
        env:
          BASE_URL: https://staging.example.com

  notify:
    name: Notify Team
    needs: [deploy-staging, deploy-production]
    if: always()
    runs-on: ubuntu-latest
    steps:
      - name: Send Slack notification
        uses: slackapi/slack-github-action@v1
        with:
          payload: |
            {
              "text": "Deployment ${{ job.status }}: ${{ github.repository }}",
              "blocks": [
                {
                  "type": "section",
                  "text": {
                    "type": "mrkdwn",
                    "text": "Deployment *${{ job.status }}* for <${{ github.server_url }}/${{ github.repository }}|${{ github.repository }}>"
                  }
                },
                {
                  "type": "section",
                  "fields": [
                    {
                      "type": "mrkdwn",
                      "text": "*Branch:*\n${{ github.ref_name }}"
                    },
                    {
                      "type": "mrkdwn",
                      "text": "*Author:*\n${{ github.actor }}"
                    }
                  ]
                }
              ]
            }
        env:
          SLACK_WEBHOOK_URL: ${{ secrets.SLACK_WEBHOOK_URL }}
```

### Reusable Workflows

**.github/workflows/reusable-test.yml**:
```yaml
name: Reusable Test Workflow

on:
  workflow_call:
    inputs:
      node-version:
        required: false
        type: string
        default: '20'
      coverage-threshold:
        required: false
        type: number
        default: 80
    secrets:
      codecov-token:
        required: true

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-node@v4
        with:
          node-version: ${{ inputs.node-version }}
          cache: 'npm'

      - run: npm ci
      - run: npm test -- --coverage

      - name: Check coverage threshold
        run: |
          COVERAGE=$(jq '.total.lines.pct' coverage/coverage-summary.json)
          if (( $(echo "$COVERAGE < ${{ inputs.coverage-threshold }}" | bc -l) )); then
            echo "Coverage $COVERAGE% is below threshold ${{ inputs.coverage-threshold }}%"
            exit 1
          fi

      - uses: codecov/codecov-action@v3
        with:
          token: ${{ secrets.codecov-token }}
```

**Usage**:
```yaml
jobs:
  test:
    uses: ./.github/workflows/reusable-test.yml
    with:
      node-version: '20'
      coverage-threshold: 85
    secrets:
      codecov-token: ${{ secrets.CODECOV_TOKEN }}
```

## GitLab CI

### Complete Pipeline

**.gitlab-ci.yml**:
```yaml
stages:
  - prepare
  - test
  - security
  - build
  - deploy
  - verify

variables:
  DOCKER_DRIVER: overlay2
  DOCKER_TLS_CERTDIR: "/certs"
  NODE_VERSION: "20"

# Cache configuration
.node_cache:
  cache:
    key:
      files:
        - package-lock.json
    paths:
      - node_modules/
      - .npm/

# Prepare stage
install-dependencies:
  stage: prepare
  image: node:${NODE_VERSION}-alpine
  extends: .node_cache
  script:
    - npm ci --cache .npm --prefer-offline
  artifacts:
    paths:
      - node_modules/
    expire_in: 1 hour

# Test stage
lint:
  stage: test
  image: node:${NODE_VERSION}-alpine
  needs: [install-dependencies]
  script:
    - npm run lint
    - npm run format:check

type-check:
  stage: test
  image: node:${NODE_VERSION}-alpine
  needs: [install-dependencies]
  script:
    - npm run type-check

unit-tests:
  stage: test
  image: node:${NODE_VERSION}-alpine
  needs: [install-dependencies]
  services:
    - postgres:16
    - redis:7-alpine
  variables:
    POSTGRES_DB: test
    POSTGRES_USER: postgres
    POSTGRES_PASSWORD: postgres
    DATABASE_URL: postgresql://postgres:postgres@postgres:5432/test
    REDIS_URL: redis://redis:6379
  script:
    - npm run test:unit -- --coverage
  coverage: '/All files[^|]*\|[^|]*\s+([\d\.]+)/'
  artifacts:
    reports:
      coverage_report:
        coverage_format: cobertura
        path: coverage/cobertura-coverage.xml
    paths:
      - coverage/

# Security stage
sast:
  stage: security
  image: returntocorp/semgrep
  script:
    - semgrep scan --config auto --json --output semgrep-report.json
  artifacts:
    reports:
      sast: semgrep-report.json

dependency-scanning:
  stage: security
  image: node:${NODE_VERSION}-alpine
  needs: [install-dependencies]
  script:
    - npm audit --audit-level=moderate
    - npx snyk test --severity-threshold=high
  allow_failure: true

container-scanning:
  stage: security
  image: aquasec/trivy:latest
  script:
    - trivy fs --format json --output trivy-report.json .
  artifacts:
    reports:
      container_scanning: trivy-report.json

# Build stage
build-docker:
  stage: build
  image: docker:24
  services:
    - docker:24-dind
  needs: [lint, type-check, unit-tests]
  before_script:
    - docker login -u $CI_REGISTRY_USER -p $CI_REGISTRY_PASSWORD $CI_REGISTRY
  script:
    - |
      docker build \
        --cache-from $CI_REGISTRY_IMAGE:latest \
        --tag $CI_REGISTRY_IMAGE:$CI_COMMIT_SHA \
        --tag $CI_REGISTRY_IMAGE:$CI_COMMIT_REF_SLUG \
        --tag $CI_REGISTRY_IMAGE:latest \
        .
    - docker push $CI_REGISTRY_IMAGE:$CI_COMMIT_SHA
    - docker push $CI_REGISTRY_IMAGE:$CI_COMMIT_REF_SLUG
    - docker push $CI_REGISTRY_IMAGE:latest
  only:
    - main
    - develop

# Deploy stages
deploy-staging:
  stage: deploy
  image: alpine/k8s:1.28.0
  needs: [build-docker]
  environment:
    name: staging
    url: https://staging.example.com
  before_script:
    - kubectl config use-context staging-cluster
  script:
    - kubectl set image deployment/myapp myapp=$CI_REGISTRY_IMAGE:$CI_COMMIT_SHA -n staging
    - kubectl rollout status deployment/myapp -n staging --timeout=5m
  only:
    - develop

deploy-production:
  stage: deploy
  image: alpine/k8s:1.28.0
  needs: [build-docker]
  environment:
    name: production
    url: https://example.com
  when: manual
  before_script:
    - kubectl config use-context production-cluster
  script:
    - kubectl set image deployment/myapp myapp=$CI_REGISTRY_IMAGE:$CI_COMMIT_SHA -n production
    - kubectl rollout status deployment/myapp -n production --timeout=10m
  only:
    - main

# Verify stage
smoke-tests:
  stage: verify
  image: mcr.microsoft.com/playwright:v1.40.0
  needs: [deploy-staging]
  script:
    - npm ci
    - npx playwright test --grep @smoke
  environment:
    name: staging
  only:
    - develop
```

## Jenkins

### Declarative Pipeline

**Jenkinsfile**:
```groovy
pipeline {
    agent any

    environment {
        DOCKER_REGISTRY = 'docker.io'
        IMAGE_NAME = 'myorg/myapp'
        KUBECONFIG = credentials('kubeconfig')
    }

    options {
        timestamps()
        timeout(time: 1, unit: 'HOURS')
        buildDiscarder(logRotator(numToKeepStr: '10'))
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
                script {
                    env.GIT_COMMIT_SHORT = sh(
                        script: "git rev-parse --short HEAD",
                        returnStdout: true
                    ).trim()
                }
            }
        }

        stage('Install Dependencies') {
            steps {
                sh 'npm ci'
            }
        }

        stage('Parallel Tests') {
            parallel {
                stage('Lint') {
                    steps {
                        sh 'npm run lint'
                    }
                }

                stage('Type Check') {
                    steps {
                        sh 'npm run type-check'
                    }
                }

                stage('Unit Tests') {
                    steps {
                        sh 'npm run test:unit -- --coverage'
                        publishHTML([
                            reportDir: 'coverage',
                            reportFiles: 'index.html',
                            reportName: 'Coverage Report'
                        ])
                    }
                }
            }
        }

        stage('Security Scans') {
            parallel {
                stage('Dependency Audit') {
                    steps {
                        sh 'npm audit --audit-level=moderate'
                    }
                }

                stage('SAST') {
                    steps {
                        sh 'semgrep scan --config auto --json --output semgrep-report.json'
                    }
                }
            }
        }

        stage('Build Docker Image') {
            when {
                branch 'main'
            }
            steps {
                script {
                    docker.withRegistry("https://${DOCKER_REGISTRY}", 'docker-credentials') {
                        def image = docker.build("${IMAGE_NAME}:${GIT_COMMIT_SHORT}")
                        image.push()
                        image.push('latest')
                    }
                }
            }
        }

        stage('Deploy to Staging') {
            when {
                branch 'develop'
            }
            steps {
                sh """
                    kubectl set image deployment/myapp \
                        myapp=${IMAGE_NAME}:${GIT_COMMIT_SHORT} \
                        -n staging
                    kubectl rollout status deployment/myapp -n staging --timeout=5m
                """
            }
        }

        stage('Deploy to Production') {
            when {
                branch 'main'
            }
            steps {
                input message: 'Deploy to production?', ok: 'Deploy'
                sh """
                    kubectl set image deployment/myapp \
                        myapp=${IMAGE_NAME}:${GIT_COMMIT_SHORT} \
                        -n production
                    kubectl rollout status deployment/myapp -n production --timeout=10m
                """
            }
        }

        stage('Smoke Tests') {
            steps {
                sh 'npx playwright test --grep @smoke'
            }
        }
    }

    post {
        always {
            junit 'test-results/**/*.xml'
            cleanWs()
        }
        success {
            slackSend(
                color: 'good',
                message: "Build Successful: ${env.JOB_NAME} ${env.BUILD_NUMBER}"
            )
        }
        failure {
            slackSend(
                color: 'danger',
                message: "Build Failed: ${env.JOB_NAME} ${env.BUILD_NUMBER}"
            )
        }
    }
}
```

## Security in CI/CD

### Secrets Management

**1. Use Native Secret Stores**:
```yaml
# GitHub Actions
- name: Deploy
  env:
    API_KEY: ${{ secrets.API_KEY }}
  run: ./deploy.sh

# GitLab CI
deploy:
  script:
    - echo $API_KEY | ./deploy.sh
```

**2. External Secret Managers**:
```yaml
- name: Get secrets from Vault
  uses: hashicorp/vault-action@v2
  with:
    url: https://vault.example.com
    method: approle
    roleId: ${{ secrets.VAULT_ROLE_ID }}
    secretId: ${{ secrets.VAULT_SECRET_ID }}
    secrets: |
      secret/data/production database_url | DATABASE_URL ;
      secret/data/production api_key | API_KEY
```

### SAST (Static Application Security Testing)

```yaml
- name: Run Semgrep
  run: |
    semgrep scan \
      --config auto \
      --sarif \
      --output semgrep-report.sarif

- name: Run CodeQL
  uses: github/codeql-action/analyze@v2
  with:
    category: "/language:javascript"
```

### Dependency Scanning

```yaml
- name: Scan dependencies
  run: |
    # npm audit
    npm audit --audit-level=moderate

    # Snyk
    npx snyk test --severity-threshold=high

    # OWASP Dependency Check
    dependency-check \
      --project myapp \
      --scan . \
      --format HTML \
      --out dependency-check-report
```

### Container Scanning

```yaml
- name: Scan Docker image
  uses: aquasecurity/trivy-action@master
  with:
    image-ref: 'myapp:latest'
    format: 'sarif'
    output: 'trivy-results.sarif'
    severity: 'CRITICAL,HIGH'
```

## Best Practices

### 1. Pipeline Optimization

**Cache Dependencies**:
```yaml
- uses: actions/cache@v3
  with:
    path: |
      ~/.npm
      node_modules
    key: ${{ runner.os }}-node-${{ hashFiles('**/package-lock.json') }}
    restore-keys: |
      ${{ runner.os }}-node-
```

**Parallel Execution**:
```yaml
jobs:
  test:
    strategy:
      matrix:
        node: [18, 20, 21]
        os: [ubuntu-latest, windows-latest, macos-latest]
    runs-on: ${{ matrix.os }}
```

### 2. Environment Management

**Use Environments**:
```yaml
deploy:
  environment:
    name: production
    url: https://example.com
  # Requires approval before deploying
```

### 3. Deployment Strategies

**Blue/Green**:
```yaml
- name: Deploy to green
  run: kubectl apply -f k8s/green/

- name: Run tests on green
  run: ./test-green.sh

- name: Switch traffic to green
  run: kubectl patch service myapp -p '{"spec":{"selector":{"version":"green"}}}'

- name: Cleanup blue
  run: kubectl delete -f k8s/blue/
```

**Canary**:
```yaml
- name: Deploy canary (10% traffic)
  run: kubectl apply -f k8s/canary-10.yaml

- name: Monitor metrics
  run: ./monitor.sh --duration 10m

- name: Scale to 50%
  run: kubectl apply -f k8s/canary-50.yaml

- name: Full rollout
  run: kubectl apply -f k8s/production.yaml
```

### 4. Rollback Strategy

```yaml
- name: Deploy with rollback
  run: |
    kubectl apply -f k8s/deployment.yaml
    kubectl rollout status deployment/myapp --timeout=5m
  timeout-minutes: 10

- name: Rollback on failure
  if: failure()
  run: kubectl rollout undo deployment/myapp
```

### 5. Testing in CI/CD

```yaml
test:
  matrix:
    test-type: [unit, integration, e2e]
  steps:
    - run: npm run test:${{ matrix.test-type }}
```

## Monitoring CI/CD

### Pipeline Metrics

Track:
- Build duration
- Success/failure rate
- Deployment frequency
- Mean time to recovery (MTTR)
- Change failure rate

### Alerting

```yaml
- name: Alert on failure
  if: failure()
  uses: 8398a7/action-slack@v3
  with:
    status: ${{ job.status }}
    text: 'Pipeline failed!'
    webhook_url: ${{ secrets.SLACK_WEBHOOK }}
```

## Conclusion

A well-designed CI/CD pipeline:
- Provides fast feedback to developers
- Automates repetitive tasks
- Ensures consistent deployments
- Improves code quality through automated testing
- Enhances security through automated scanning
- Enables confident, frequent releases

Remember: Start simple and iterate. Don't try to implement everything at once.
