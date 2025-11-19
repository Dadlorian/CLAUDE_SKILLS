# Setting Up Your First CI/CD Pipeline

## Introduction

This guide walks you through setting up your first CI/CD pipeline from scratch. We'll cover Jenkins, GitLab CI, and GitHub Actions with real-world examples.

## Prerequisites

- Source code repository
- Basic understanding of your project's build process
- Access to a CI/CD platform
- Basic command-line knowledge

## Part 1: Planning Your Pipeline

### Step 1: Define Your Pipeline Stages

Before writing any code, map out what your pipeline needs to do:

```
Build → Test → Quality Check → Deploy
```

**Common stages:**
- **Build**: Compile code, install dependencies
- **Test**: Unit tests, integration tests
- **Quality**: Linting, code coverage, security scans
- **Deploy**: Deploy to environments (dev, staging, production)

### Step 2: Identify Requirements

Create a checklist:

- [ ] What language/framework? (Node.js, Python, Java, Go, etc.)
- [ ] What dependencies need to be installed?
- [ ] What tests need to run?
- [ ] What artifacts need to be produced?
- [ ] Where will the application be deployed?
- [ ] What secrets/credentials are needed?

### Step 3: Choose Your CI/CD Platform

| Platform | Best For | Key Advantage |
|----------|----------|---------------|
| **GitHub Actions** | GitHub projects | Native integration, free for public repos |
| **GitLab CI** | GitLab projects | Integrated DevOps platform |
| **Jenkins** | Enterprise, on-premise | Highly customizable, plugin ecosystem |

## Part 2: GitHub Actions Setup

### Step 1: Create Workflow Directory

```bash
mkdir -p .github/workflows
```

### Step 2: Create Your First Workflow

Create `.github/workflows/ci.yml`:

```yaml
name: CI Pipeline

# Trigger on push and pull requests to main
on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  build-and-test:
    runs-on: ubuntu-latest

    steps:
      # Step 1: Checkout code
      - name: Checkout repository
        uses: actions/checkout@v4

      # Step 2: Setup environment (Node.js example)
      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: '18'
          cache: 'npm'

      # Step 3: Install dependencies
      - name: Install dependencies
        run: npm ci

      # Step 4: Run linter
      - name: Run linter
        run: npm run lint

      # Step 5: Run tests
      - name: Run tests
        run: npm test

      # Step 6: Build application
      - name: Build
        run: npm run build

      # Step 7: Upload artifacts
      - name: Upload build artifacts
        uses: actions/upload-artifact@v4
        with:
          name: build-artifacts
          path: dist/
          retention-days: 7
```

### Step 3: Add Status Badge to README

```markdown
![CI Status](https://github.com/username/repo/workflows/CI%20Pipeline/badge.svg)
```

### Step 4: Configure Secrets

1. Go to repository Settings → Secrets and variables → Actions
2. Click "New repository secret"
3. Add secrets (e.g., `AWS_ACCESS_KEY_ID`, `DEPLOY_TOKEN`)

### Step 5: Use Secrets in Workflow

```yaml
- name: Deploy
  env:
    AWS_ACCESS_KEY_ID: ${{ secrets.AWS_ACCESS_KEY_ID }}
    AWS_SECRET_ACCESS_KEY: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
  run: |
    aws s3 sync dist/ s3://my-bucket/
```

### Step 6: Test Your Pipeline

```bash
# Commit and push
git add .github/workflows/ci.yml
git commit -m "Add CI pipeline"
git push origin main
```

Check the "Actions" tab in your GitHub repository to see the pipeline run.

## Part 3: GitLab CI Setup

### Step 1: Create Pipeline Configuration

Create `.gitlab-ci.yml` in your repository root:

```yaml
# Define pipeline stages
stages:
  - build
  - test
  - deploy

# Global variables
variables:
  NODE_VERSION: "18"

# Default settings for all jobs
default:
  image: node:${NODE_VERSION}
  cache:
    key: ${CI_COMMIT_REF_SLUG}
    paths:
      - node_modules/
  before_script:
    - npm ci

# Build job
build:
  stage: build
  script:
    - npm run build
  artifacts:
    paths:
      - dist/
    expire_in: 1 week

# Lint job
lint:
  stage: test
  script:
    - npm run lint

# Test job
test:
  stage: test
  script:
    - npm test
  coverage: '/Lines\s*:\s*(\d+\.\d+)%/'
  artifacts:
    reports:
      junit: junit.xml
      coverage_report:
        coverage_format: cobertura
        path: coverage/cobertura-coverage.xml

# Deploy to staging
deploy-staging:
  stage: deploy
  script:
    - echo "Deploying to staging"
    - npm run deploy:staging
  environment:
    name: staging
    url: https://staging.example.com
  only:
    - develop

# Deploy to production
deploy-production:
  stage: deploy
  script:
    - echo "Deploying to production"
    - npm run deploy:production
  environment:
    name: production
    url: https://production.example.com
  only:
    - main
  when: manual  # Require manual approval
```

### Step 2: Configure CI/CD Variables

1. Go to Settings → CI/CD → Variables
2. Click "Add variable"
3. Add required variables (mark sensitive ones as "Masked" and "Protected")

Example variables:
- `AWS_ACCESS_KEY_ID`
- `AWS_SECRET_ACCESS_KEY`
- `DEPLOY_TOKEN`

### Step 3: Configure GitLab Runner

If using self-hosted runners:

```bash
# Install GitLab Runner
curl -L https://packages.gitlab.com/install/repositories/runner/gitlab-runner/script.deb.sh | sudo bash
sudo apt-get install gitlab-runner

# Register runner
sudo gitlab-runner register
```

Follow the prompts:
- GitLab URL: `https://gitlab.com/`
- Registration token: (from Settings → CI/CD → Runners)
- Description: `my-runner`
- Tags: `docker,linux`
- Executor: `docker`
- Default image: `alpine:latest`

### Step 4: Test Your Pipeline

```bash
git add .gitlab-ci.yml
git commit -m "Add CI/CD pipeline"
git push origin main
```

View pipeline in GitLab: Go to CI/CD → Pipelines

## Part 4: Jenkins Setup

### Step 1: Install Jenkins

```bash
# Ubuntu/Debian
wget -q -O - https://pkg.jenkins.io/debian-stable/jenkins.io.key | sudo apt-key add -
sudo sh -c 'echo deb http://pkg.jenkins.io/debian-stable binary/ > /etc/apt/sources.list.d/jenkins.list'
sudo apt-get update
sudo apt-get install jenkins

# Start Jenkins
sudo systemctl start jenkins
sudo systemctl enable jenkins
```

Access Jenkins at `http://localhost:8080`

### Step 2: Initial Setup

1. Get initial admin password:
```bash
sudo cat /var/lib/jenkins/secrets/initialAdminPassword
```

2. Install suggested plugins
3. Create first admin user

### Step 3: Install Required Plugins

Go to Manage Jenkins → Manage Plugins → Available

Install:
- Pipeline
- Git
- Docker Pipeline
- Blue Ocean (recommended for better UI)
- NodeJS Plugin (for Node.js projects)

### Step 4: Configure Tools

Go to Manage Jenkins → Global Tool Configuration

**Configure Node.js:**
- Add NodeJS
- Name: `NodeJS-18`
- Version: `18.x`

**Configure Git:**
- Usually auto-detected

### Step 5: Create Pipeline Job

1. Click "New Item"
2. Enter name: `my-app-pipeline`
3. Select "Pipeline"
4. Click OK

### Step 6: Configure Pipeline

In the pipeline configuration:

**General:**
- Description: "CI/CD pipeline for my application"

**Build Triggers:**
- ✓ GitHub hook trigger for GITScm polling (for GitHub)
- ✓ Poll SCM: `H/5 * * * *` (poll every 5 minutes as fallback)

**Pipeline:**
- Definition: Pipeline script from SCM
- SCM: Git
- Repository URL: `https://github.com/username/repo.git`
- Credentials: (add if private repo)
- Branch: `*/main`
- Script Path: `Jenkinsfile`

### Step 7: Create Jenkinsfile

Create `Jenkinsfile` in repository root:

```groovy
pipeline {
    agent any

    tools {
        nodejs 'NodeJS-18'
    }

    environment {
        // Environment variables
        NODE_ENV = 'production'
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Install Dependencies') {
            steps {
                sh 'npm ci'
            }
        }

        stage('Lint') {
            steps {
                sh 'npm run lint'
            }
        }

        stage('Test') {
            steps {
                sh 'npm test'
            }
            post {
                always {
                    junit 'junit.xml'
                }
            }
        }

        stage('Build') {
            steps {
                sh 'npm run build'
            }
        }

        stage('Archive Artifacts') {
            steps {
                archiveArtifacts artifacts: 'dist/**/*', fingerprint: true
            }
        }

        stage('Deploy to Staging') {
            when {
                branch 'develop'
            }
            steps {
                sh 'npm run deploy:staging'
            }
        }

        stage('Deploy to Production') {
            when {
                branch 'main'
            }
            steps {
                input message: 'Deploy to production?', ok: 'Deploy'
                sh 'npm run deploy:production'
            }
        }
    }

    post {
        always {
            cleanWs()
        }
        success {
            echo 'Pipeline succeeded!'
        }
        failure {
            echo 'Pipeline failed!'
            // Send notification
        }
    }
}
```

### Step 8: Configure Credentials

Go to Manage Jenkins → Manage Credentials

**Add credentials:**
1. Click "Global" → "Add Credentials"
2. Kind: Secret text (for API keys) or Username with password
3. ID: `aws-credentials` (reference this in Jenkinsfile)
4. Add secret value

**Use in Jenkinsfile:**
```groovy
stage('Deploy') {
    steps {
        withCredentials([usernamePassword(
            credentialsId: 'aws-credentials',
            usernameVariable: 'AWS_ACCESS_KEY',
            passwordVariable: 'AWS_SECRET_KEY'
        )]) {
            sh './deploy.sh'
        }
    }
}
```

### Step 9: Configure GitHub Webhook (Optional)

For automatic builds on push:

1. In GitHub repo, go to Settings → Webhooks
2. Click "Add webhook"
3. Payload URL: `http://jenkins-server:8080/github-webhook/`
4. Content type: `application/json`
5. Events: "Just the push event"
6. Save

### Step 10: Run Your Pipeline

1. Click "Build Now"
2. View progress in Blue Ocean or Classic UI
3. Check console output for each stage

## Part 5: Testing and Validation

### Test Checklist

- [ ] Pipeline triggers on push to correct branches
- [ ] All stages execute successfully
- [ ] Tests run and results are reported
- [ ] Artifacts are created and stored
- [ ] Deployment works to correct environment
- [ ] Notifications are sent on success/failure
- [ ] Pipeline fails appropriately on errors

### Common Issues and Solutions

#### Issue: Pipeline doesn't trigger automatically

**GitHub Actions:**
```yaml
# Check event triggers
on:
  push:
    branches: [ main ]  # Make sure branch name matches
```

**GitLab CI:**
```yaml
# Check workflow rules
workflow:
  rules:
    - if: '$CI_PIPELINE_SOURCE == "push"'
```

**Jenkins:**
- Verify webhook is configured
- Check SCM polling is enabled
- Verify Jenkins has network access to Git server

#### Issue: Dependencies not installing

**Solutions:**
```yaml
# GitHub Actions - Use cache
- uses: actions/setup-node@v4
  with:
    node-version: '18'
    cache: 'npm'  # Enable caching

# Use ci instead of install
- run: npm ci  # Cleaner install using package-lock.json
```

```yaml
# GitLab CI - Configure cache
cache:
  key: ${CI_COMMIT_REF_SLUG}
  paths:
    - node_modules/
```

#### Issue: Tests failing in CI but work locally

**Common causes:**
- Environment differences
- Missing environment variables
- Database not available
- Different Node.js/Python versions

**Solutions:**
```yaml
# Use services for databases
services:
  - postgres:13
  - redis:6

# Set environment variables
env:
  NODE_ENV: test
  DATABASE_URL: postgres://user:pass@localhost/testdb
```

#### Issue: Secrets not working

**GitHub Actions:**
```yaml
# Secrets are case-sensitive
env:
  API_KEY: ${{ secrets.API_KEY }}  # Must match exactly
```

**GitLab CI:**
- Check variable is not protected (unless on protected branch)
- Verify variable key matches usage

**Jenkins:**
- Check credential ID matches
- Verify credential is in correct scope (Global/System)

## Part 6: Adding Advanced Features

### Add Docker Build

**GitHub Actions:**
```yaml
- name: Build Docker image
  run: |
    docker build -t myapp:${{ github.sha }} .
    docker tag myapp:${{ github.sha }} myapp:latest

- name: Push to registry
  run: |
    echo "${{ secrets.DOCKER_PASSWORD }}" | docker login -u "${{ secrets.DOCKER_USERNAME }}" --password-stdin
    docker push myapp:${{ github.sha }}
    docker push myapp:latest
```

**GitLab CI:**
```yaml
build-docker:
  stage: build
  image: docker:latest
  services:
    - docker:dind
  script:
    - docker build -t $CI_REGISTRY_IMAGE:$CI_COMMIT_SHA .
    - docker login -u $CI_REGISTRY_USER -p $CI_REGISTRY_PASSWORD $CI_REGISTRY
    - docker push $CI_REGISTRY_IMAGE:$CI_COMMIT_SHA
```

### Add Slack Notifications

**GitHub Actions:**
```yaml
- name: Slack notification
  if: always()
  uses: 8398a7/action-slack@v3
  with:
    status: ${{ job.status }}
    text: 'Build ${{ job.status }}'
    webhook_url: ${{ secrets.SLACK_WEBHOOK }}
```

**Jenkins:**
```groovy
post {
    failure {
        slackSend color: 'danger',
                  message: "Build failed: ${env.JOB_NAME} #${env.BUILD_NUMBER}",
                  channel: '#ci-notifications'
    }
}
```

### Add Code Coverage

**GitHub Actions:**
```yaml
- name: Run tests with coverage
  run: npm test -- --coverage

- name: Upload coverage to Codecov
  uses: codecov/codecov-action@v3
  with:
    token: ${{ secrets.CODECOV_TOKEN }}
    files: ./coverage/lcov.info
```

## Part 7: Best Practices

### 1. Keep Pipelines Fast
- Use caching for dependencies
- Run tests in parallel
- Only run necessary steps

### 2. Security
- Never commit secrets to repository
- Use platform secret management
- Scan for vulnerabilities regularly

### 3. Reliability
- Set appropriate timeouts
- Implement retry logic for flaky operations
- Use specific versions for tools/images

### 4. Maintainability
- Use clear stage/job names
- Comment complex logic
- Keep configuration DRY (Don't Repeat Yourself)

### 5. Monitoring
- Set up notifications for failures
- Monitor pipeline execution times
- Track success/failure rates

## Next Steps

1. **Add more sophisticated testing**: Integration tests, E2E tests
2. **Implement deployment strategies**: Blue-green, canary deployments
3. **Add security scanning**: SAST, DAST, dependency scanning
4. **Optimize performance**: Better caching, parallel execution
5. **Add monitoring**: Pipeline metrics, deployment tracking

## Resources

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [GitLab CI/CD Documentation](https://docs.gitlab.com/ee/ci/)
- [Jenkins Documentation](https://www.jenkins.io/doc/)
- [CI/CD Best Practices](https://www.thoughtworks.com/continuous-integration)

## Troubleshooting Guide

### Enable Debug Logging

**GitHub Actions:**
Add repository secret: `ACTIONS_STEP_DEBUG` = `true`

**GitLab CI:**
Add variable: `CI_DEBUG_TRACE` = `true`

**Jenkins:**
Add to pipeline:
```groovy
options {
    timestamps()
    ansiColor('xterm')
}
```

### Get Help

- Check official documentation
- Search Stack Overflow
- Check platform status pages
- Review pipeline logs carefully
- Test locally with Docker when possible

## Conclusion

You now have a working CI/CD pipeline! This foundation can be extended with additional stages, improved testing, security scanning, and sophisticated deployment strategies.

Remember:
- Start simple, add complexity as needed
- Test your pipeline changes in a branch first
- Monitor and improve based on metrics
- Keep security in mind at every step
