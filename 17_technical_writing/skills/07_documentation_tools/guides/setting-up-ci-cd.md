# Automated Builds and Deployment Guide

## Overview

Continuous Integration and Continuous Deployment (CI/CD) automates the process of testing, building, and deploying your documentation site. This guide covers setting up automated workflows using GitHub Actions.

## Prerequisites

- Docusaurus documentation project in GitHub repository
- Familiarity with GitHub workflows and YAML syntax
- Deployment target (GitHub Pages, Netlify, Vercel, or AWS)
- Node.js project setup with package.json

## Part 1: GitHub Actions Basics

### What is GitHub Actions?

GitHub Actions is a CI/CD platform that:
- Runs automated workflows on GitHub events
- Executes custom build and deploy scripts
- Provides built-in secrets management
- Offers free minutes for public repositories
- Integrates seamlessly with GitHub repositories

### Workflow Structure

```yaml
# .github/workflows/deploy.yml
name: Deploy Documentation

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Setup Node.js
        uses: actions/setup-node@v3
        with:
          node-version: '18'
      - name: Install dependencies
        run: npm install
      - name: Build site
        run: npm run build
```

## Part 2: Setting Up GitHub Actions

### Step 1: Create Workflow File

Create `.github/workflows/deploy.yml`:

```yaml
name: Build and Deploy Documentation

on:
  push:
    branches:
      - main
      - develop
  pull_request:
    branches:
      - main

jobs:
  build:
    runs-on: ubuntu-latest

    steps:
      - name: Checkout code
        uses: actions/checkout@v3

      - name: Setup Node.js
        uses: actions/setup-node@v3
        with:
          node-version: '18'
          cache: 'npm'

      - name: Install dependencies
        run: npm install --frozen-lockfile

      - name: Lint and test
        run: npm run test

      - name: Build documentation
        run: npm run build

      - name: Upload build artifacts
        uses: actions/upload-artifact@v3
        with:
          name: documentation-build
          path: build/
          retention-days: 5
```

### Step 2: Add Environment Variables

Create `.github/workflows/config.yml` with environment setup:

```yaml
env:
  NODE_ENV: production
  NODE_OPTIONS: --max_old_space_size=4096
  NPM_REGISTRY: https://registry.npmjs.org/

jobs:
  setup:
    runs-on: ubuntu-latest
    steps:
      - name: Check Node version
        run: node --version && npm --version
```

## Part 3: Building Documentation

### Complete Build Workflow

```yaml
# .github/workflows/build.yml
name: Build Documentation

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  build:
    runs-on: ubuntu-latest

    strategy:
      matrix:
        node-version: [16.x, 18.x]

    steps:
      - name: Checkout repository
        uses: actions/checkout@v3
        with:
          fetch-depth: 0

      - name: Setup Node.js ${{ matrix.node-version }}
        uses: actions/setup-node@v3
        with:
          node-version: ${{ matrix.node-version }}
          cache: 'npm'

      - name: Cache npm dependencies
        uses: actions/cache@v3
        with:
          path: ~/.npm
          key: ${{ runner.os }}-node-${{ hashFiles('**/package-lock.json') }}
          restore-keys: |
            ${{ runner.os }}-node-

      - name: Install dependencies
        run: |
          npm ci --no-optional
          npm audit --audit-level=moderate

      - name: Lint code
        run: npm run lint
        continue-on-error: true

      - name: Run tests
        run: npm run test
        continue-on-error: true

      - name: Build documentation
        run: npm run build

      - name: Verify build output
        run: |
          if [ ! -d "build" ]; then
            echo "Build directory not found!"
            exit 1
          fi

      - name: Check for broken links
        run: npm run build:check-links
        continue-on-error: true

      - name: Upload coverage reports
        uses: codecov/codecov-action@v3
        if: matrix.node-version == '18.x'
        with:
          files: ./coverage/coverage-final.json

      - name: Save build artifacts
        uses: actions/upload-artifact@v3
        if: success()
        with:
          name: build-${{ matrix.node-version }}
          path: build/
          retention-days: 7
```

### Add Build Scripts to package.json

```json
{
  "scripts": {
    "build": "docusaurus build",
    "build:check-links": "docusaurus build --check-links",
    "lint": "eslint docs src --fix",
    "test": "jest",
    "start": "docusaurus start",
    "serve": "docusaurus serve"
  }
}
```

## Part 4: Deployment to GitHub Pages

### Setup GitHub Pages Deployment

```yaml
# .github/workflows/deploy-github-pages.yml
name: Deploy to GitHub Pages

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

permissions:
  contents: read
  pages: write
  id-token: write

concurrency:
  group: pages
  cancel-in-progress: false

jobs:
  build:
    runs-on: ubuntu-latest

    steps:
      - name: Checkout code
        uses: actions/checkout@v3

      - name: Setup Node.js
        uses: actions/setup-node@v3
        with:
          node-version: '18'
          cache: 'npm'

      - name: Install dependencies
        run: npm ci

      - name: Build site
        run: npm run build

      - name: Setup Pages
        uses: actions/configure-pages@v3

      - name: Upload artifact
        uses: actions/upload-pages-artifact@v2
        with:
          path: './build'

  deploy:
    if: github.ref == 'refs/heads/main' && github.event_name == 'push'
    environment:
      name: github-pages
      url: ${{ steps.deployment.outputs.page_url }}
    runs-on: ubuntu-latest
    needs: build

    steps:
      - name: Deploy to GitHub Pages
        id: deployment
        uses: actions/deploy-pages@v2
```

### Configure Repository Settings

In GitHub repository settings:

1. Go to **Settings → Pages**
2. Select **GitHub Actions** as deployment source
3. Configure branch protection rules:

```yaml
# Repository settings
- Require branches to be up to date before merging
- Require status checks to pass before merging
- Require code reviews before merging
- Require CODEOWNERS approval
```

## Part 5: Deployment to Netlify

### Setup Netlify Deployment

```yaml
# .github/workflows/deploy-netlify.yml
name: Deploy to Netlify

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  build-and-deploy:
    runs-on: ubuntu-latest

    steps:
      - name: Checkout code
        uses: actions/checkout@v3

      - name: Setup Node.js
        uses: actions/setup-node@v3
        with:
          node-version: '18'
          cache: 'npm'

      - name: Install dependencies
        run: npm ci

      - name: Build documentation
        run: npm run build

      - name: Deploy to Netlify
        uses: nwtgck/actions-netlify@v2
        with:
          publish-dir: './build'
          production-branch: main
          github-token: ${{ secrets.GITHUB_TOKEN }}
          deploy-message: 'Deploy from GitHub Actions'
          enable-pull-request-comment: true
          enable-commit-comment: true
          overwrites-pull-request-comment: true
        env:
          NETLIFY_AUTH_TOKEN: ${{ secrets.NETLIFY_AUTH_TOKEN }}
          NETLIFY_SITE_ID: ${{ secrets.NETLIFY_SITE_ID }}
        timeout-minutes: 1
```

### Configure Netlify Secrets

In GitHub repository secrets (Settings → Secrets):

1. **NETLIFY_AUTH_TOKEN**: From Netlify dashboard → User settings → Applications
2. **NETLIFY_SITE_ID**: From Netlify site settings → General → API ID

### Netlify Configuration File

Create `netlify.toml`:

```toml
[build]
  command = "npm run build"
  publish = "build"

[build.environment]
  NODE_VERSION = "18.0.0"
  NODE_ENV = "production"

# Redirect rules
[[redirects]]
  from = "/*"
  to = "/index.html"
  status = 200

# Custom headers
[[headers]]
  for = "/*"
  [headers.values]
    X-Frame-Options = "DENY"
    X-Content-Type-Options = "nosniff"
    Referrer-Policy = "strict-origin"
```

## Part 6: Deployment to Vercel

### Setup Vercel Deployment

```yaml
# .github/workflows/deploy-vercel.yml
name: Deploy to Vercel

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest

    steps:
      - name: Checkout code
        uses: actions/checkout@v3

      - name: Setup Node.js
        uses: actions/setup-node@v3
        with:
          node-version: '18'
          cache: 'npm'

      - name: Install Vercel CLI
        run: npm install -g vercel

      - name: Install dependencies
        run: npm ci

      - name: Build documentation
        run: npm run build

      - name: Deploy to Vercel
        run: vercel --prod
        env:
          VERCEL_TOKEN: ${{ secrets.VERCEL_TOKEN }}
          VERCEL_ORG_ID: ${{ secrets.VERCEL_ORG_ID }}
          VERCEL_PROJECT_ID: ${{ secrets.VERCEL_PROJECT_ID }}
```

### Vercel Configuration

Create `vercel.json`:

```json
{
  "buildCommand": "npm run build",
  "outputDirectory": "build",
  "public": true,
  "env": {
    "NODE_ENV": "production"
  },
  "regions": ["iad1"],
  "functions": {
    "api/**/*.js": {
      "maxDuration": 60
    }
  }
}
```

## Part 7: Advanced Workflows

### Multi-Stage Pipeline

```yaml
name: Complete CI/CD Pipeline

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  # Stage 1: Quality checks
  quality:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
        with:
          node-version: '18'
          cache: 'npm'
      - run: npm ci
      - run: npm run lint
      - run: npm run test

  # Stage 2: Build
  build:
    needs: quality
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
        with:
          node-version: '18'
          cache: 'npm'
      - run: npm ci
      - run: npm run build
      - uses: actions/upload-artifact@v3
        with:
          name: build
          path: build/

  # Stage 3: Security scanning
  security:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Run Snyk security scan
        uses: snyk/actions/node@master
        env:
          SNYK_TOKEN: ${{ secrets.SNYK_TOKEN }}

  # Stage 4: Deploy
  deploy:
    needs: [build, quality, security]
    if: github.ref == 'refs/heads/main' && github.event_name == 'push'
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/download-artifact@v3
        with:
          name: build
          path: build/
      - name: Deploy to production
        run: echo "Deploying to production..."
```

### Pull Request Preview Deployments

```yaml
name: Preview Deploy

on:
  pull_request:
    branches: [main]

jobs:
  preview-deploy:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
        with:
          node-version: '18'
          cache: 'npm'

      - run: npm ci
      - run: npm run build

      - name: Deploy preview
        id: deploy-preview
        run: |
          echo "PREVIEW_URL=https://pr-${{ github.event.number }}.example.com" >> $GITHUB_OUTPUT

      - name: Comment PR with preview URL
        uses: actions/github-script@v6
        with:
          script: |
            github.rest.issues.createComment({
              issue_number: context.issue.number,
              owner: context.repo.owner,
              repo: context.repo.repo,
              body: '🚀 Preview deployed at: ${{ steps.deploy-preview.outputs.PREVIEW_URL }}'
            })
```

## Part 8: Monitoring and Notifications

### Slack Notifications

```yaml
- name: Notify Slack on success
  if: success()
  uses: slackapi/slack-github-action@v1.24.0
  with:
    payload: |
      {
        "text": "Documentation deployed successfully",
        "blocks": [
          {
            "type": "section",
            "text": {
              "type": "mrkdwn",
              "text": ":rocket: Documentation deployed!\n*Repository:* ${{ github.repository }}\n*Commit:* ${{ github.sha }}"
            }
          }
        ]
      }
  env:
    SLACK_WEBHOOK_URL: ${{ secrets.SLACK_WEBHOOK_URL }}

- name: Notify Slack on failure
  if: failure()
  uses: slackapi/slack-github-action@v1.24.0
  with:
    payload: |
      {
        "text": "Documentation build failed",
        "blocks": [
          {
            "type": "section",
            "text": {
              "type": "mrkdwn",
              "text": ":x: Build failed for ${{ github.repository }}\n*Branch:* ${{ github.ref }}\n*Commit:* ${{ github.sha }}"
            }
          }
        ]
      }
  env:
    SLACK_WEBHOOK_URL: ${{ secrets.SLACK_WEBHOOK_URL }}
```

### Email Notifications

Configure in GitHub:
1. Settings → Actions → Workflow permissions
2. Enable "Send notifications for failed workflow runs"

## Part 9: Secrets Management

### Adding GitHub Secrets

1. Go to **Settings → Secrets and variables → Actions**
2. Click **New repository secret**
3. Add secrets:

```
GITHUB_TOKEN (auto-provided)
NETLIFY_AUTH_TOKEN
NETLIFY_SITE_ID
VERCEL_TOKEN
VERCEL_ORG_ID
VERCEL_PROJECT_ID
SLACK_WEBHOOK_URL
```

### Using Secrets in Workflows

```yaml
- name: Use secret
  run: echo "Using secret value"
  env:
    MY_SECRET: ${{ secrets.MY_SECRET }}
```

## Part 10: Troubleshooting

### Common Issues and Solutions

**Workflow not triggering:**
```yaml
# Ensure correct branch names
on:
  push:
    branches: [main]  # Check exact branch name
```

**Out of memory during build:**
```yaml
env:
  NODE_OPTIONS: --max_old_space_size=4096

- name: Build with increased memory
  run: npm run build
```

**Slow builds:**
```yaml
- uses: actions/setup-node@v3
  with:
    cache: 'npm'  # Cache npm dependencies
```

**Artifact size issues:**
```yaml
- uses: actions/upload-artifact@v3
  with:
    path: build/
    retention-days: 5  # Clean up after 5 days
```

## Best Practices

1. **Cache Dependencies**: Use action caching to speed up builds
2. **Matrix Strategy**: Test against multiple Node versions
3. **Conditional Deployment**: Only deploy on main branch
4. **Secrets Security**: Never log or expose secrets
5. **Artifact Cleanup**: Set retention periods for artifacts
6. **Status Checks**: Require checks pass before merging
7. **Notifications**: Alert team of build failures
8. **Documentation**: Document your CI/CD setup

## Resources

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [GitHub Actions Marketplace](https://github.com/marketplace?type=actions)
- [Workflow Syntax](https://docs.github.com/en/actions/using-workflows/workflow-syntax-for-github-actions)
- [Netlify Deployment](https://docs.netlify.com/cli/get-started/)
- [Vercel Deployment](https://vercel.com/docs)

## Next Steps

After setting up CI/CD:
- Monitor workflow runs and optimize performance
- Set up deployment approvals for production
- Configure rollback strategies
- Implement performance monitoring
- Add status badges to README
